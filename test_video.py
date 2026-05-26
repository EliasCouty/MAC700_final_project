import cv2
from ultralytics import YOLO
import numpy as np
import json
from shapely.geometry import Polygon

# 1. Load your model
model = YOLO(r'Models\V2\weights\best.pt') 

# 2. Open the video file (Highly recommended to use the RAW Basler video here!)
video_path = r'C:\Users\couty\Desktop\ScreenRecord.mp4'
cap = cv2.VideoCapture(video_path)

cv2.namedWindow("YOLO Speed Test", cv2.WINDOW_NORMAL)
cv2.resizeWindow("YOLO Speed Test", 1920, 1080)

# Load JSON coordinates
json_path = r'C:\Users\couty\Desktop\screenRecord - frame at 0m0s.json'
with open(json_path, 'r') as file:
    data = json.load(file)

tray_pts = None
danger_pts = None

for shape in data["shapes"]:
    label = shape["label"]
    points_list = shape["points"]
    
    np_points = np.array(points_list, dtype=np.int32)
    formatted_points = np_points.reshape((-1, 1, 2)) #Adapt to the format wanted by openCV
    
    # Note: Ensure these match your JSON casing exactly (e.g., "Danger zone" vs "Danger Zone")
    if label == "Tray":
        tray_pts = formatted_points
    elif label == "Danger":
        danger_pts = formatted_points

print("Tray points found:", tray_pts is not None)
print("Danger zone points found:", danger_pts is not None)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Step 1: Run YOLO inference on the clean frame
    # This prevents the gray polygon overlay from throwing off the AI's detection accuracy
    results = model(frame, stream=True)

    # Step 2: Get the annotated frame (with boxes and labels) from YOLO
    annotated_frame = frame.copy()
    for r in results:
        annotated_frame = r.plot()
    
    # Step 3: Draw the semi-transparent danger zone ON TOP of the final output
    # Create a copy of the annotated frame to draw the solid zone on
    zone_overlay = annotated_frame.copy()
    cv2.fillPoly(zone_overlay, [danger_pts], (0,0,255))
    cv2.fillPoly(zone_overlay, [tray_pts], (0,255,0))
        
    # Blend the solid zone overlay back into the annotated frame
    alpha = 0.07  # Transparency transparency factor (0.0 = invisible, 1.0 = solid)
    cv2.addWeighted(zone_overlay, alpha, annotated_frame, 1 - alpha, 0, dst=annotated_frame)

    # Display the final combined result
    cv2.imshow("YOLO Speed Test", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()