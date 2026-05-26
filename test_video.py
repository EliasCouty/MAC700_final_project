import cv2
from ultralytics import YOLO
import numpy as np
import json
from shapely.geometry import Point, Polygon

def check_zones(pen_in_tray , highlighter_in_tray, kit_misplaced):
    if r.masks is not None:
            for box, mask in zip(r.boxes, r.masks):
                label = class_names[int(box.cls[0])]
                
                # 1. Extract the boundary points of the mask
                polygon_points = mask.xy[0] 
                
                # A Shapely Polygon requires at least 3 points to form a shape
                if len(polygon_points) >= 3: 
                    
                    # 2. Create a Shapely Polygon for the exact shape of the object
                    object_polygon = Polygon(polygon_points)
                    
                    # 3. The New Magic Check: Does ANY part of the object overlap the zone?
                    if danger_polygon.intersects(object_polygon) and (label=="robot"):
                            print(f"⚠️ ALARM: A part of {label.upper()} entered the Danger Zone!")

                    if ((label == "Pen") or (label=="highlighter")) and not tray_polygon.contains(object_polygon):
                        kit_misplaced = True

                    if tray_polygon.contains(object_polygon):
                        if label == "Pen":
                            pen_in_tray += 1
                        if label == "highlighter":
                            highlighter_in_tray += 1
    return pen_in_tray, highlighter_in_tray, kit_misplaced



def get_zones(filePath):
    # Load JSON coordinates
    json_path = filePath
    with open(json_path, 'r') as file:
        data = json.load(file)

    tray_pts = None
    tray_polygon = None
    danger_pts = None
    danger_polygon = None

    for shape in data["shapes"]:
        label = shape["label"]
        points_list = shape["points"]
    
        np_points = np.array(points_list, dtype=np.int32)
        formatted_points = np_points.reshape((-1, 1, 2)) #Adapt to the format wanted by openCV
    
        # Note: Ensure these match your JSON casing exactly (e.g., "Danger zone" vs "Danger Zone")
        if label == "Tray":
            tray_pts = formatted_points
            tray_polygon = Polygon(tray_pts.reshape(-1,2))
        elif label == "Danger":
            danger_pts = formatted_points
            danger_polygon = Polygon(danger_pts.reshape(-1,2))

    return tray_pts,tray_polygon,danger_pts,danger_polygon

# 1. Load your model
model = YOLO(r'Models\V2\weights\best.pt') 

# 2. Open the video file (Highly recommended to use the RAW Basler video here!)
video_path = r'C:\Users\couty\Desktop\ScreenRecord.mp4'
cap = cv2.VideoCapture(video_path)

# Extract width and height (they return as floats, so cast them to integers)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

cv2.namedWindow("YOLO Speed Test", cv2.WINDOW_NORMAL)
cv2.resizeWindow("YOLO Speed Test", 1080, 720)

#print("Tray points found:", tray_pts is not None)
#print("Danger zone points found:", danger_pts is not None)

tray_pts,tray_polygon,danger_pts,danger_polygon = get_zones(r'C:\Users\couty\Desktop\screenRecord - frame at 0m0s.json')

zone_overlay = np.zeros((frame_height, frame_width, 3),dtype=np.uint8)
cv2.fillPoly(zone_overlay, [danger_pts], (0,0,255))
cv2.fillPoly(zone_overlay, [tray_pts], (0,255,0))

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Step 1: Run YOLO inference on the clean frame
    # This prevents the gray polygon overlay from throwing off the AI's detection accuracy
    results = model(frame,conf=0.6, stream=False)
    pen_in_tray = 0
    highlighter_in_tray = 0
    kit_misplaced = False
    kitting_state = ""

    for r in results:
        class_names = r.names
        frame = r.plot()
        pen_in_tray,highlighter_in_tray,kit_misplaced = check_zones(pen_in_tray,highlighter_in_tray, kit_misplaced)
        
    # Blend the solid zone overlay back into the annotated frame
    alpha = 0.2  # Transparency transparency factor (0.0 = invisible, 1.0 = solid)
    cv2.addWeighted(zone_overlay, alpha, frame, 1 - alpha, 0, dst=frame)

    if kit_misplaced == True:
        kitting_state = "Missplaced ⚠️"
    elif pen_in_tray == 0 and highlighter_in_tray == 0:
        kitting_state="Empty"
    elif pen_in_tray == 1 and highlighter_in_tray == 0:
        kitting_state="Partial"
    elif pen_in_tray == 0 and highlighter_in_tray == 1:
        kitting_state="Partial"
    elif pen_in_tray == 1 and highlighter_in_tray == 1:
        kitting_state="Ready"
    else:
        kitting_state="Invalid"

    print(f"Kitting state is {kitting_state} !")

    # Display the final combined result
    cv2.imshow("YOLO Speed Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()