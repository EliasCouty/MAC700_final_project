import cv2
from ultralytics import YOLO
import numpy as np
import json
from shapely.geometry import Polygon
import time

#Function to look classify the state of the system depending on detected object positions
def check_zones(pen_in_tray , highlighter_in_tray, kit_misplaced, robot_state, human_state, confidence_scores):
    if r.masks is not None:
            for box, mask in zip(r.boxes, r.masks):
                label = class_names[int(box.cls[0])]
                confidence_scores.append(box.conf[0])
                polygon_points = mask.xy[0] 
                
                if len(polygon_points) >= 3: 
                    
                    object_polygon = Polygon(polygon_points)
                    
                    if label=="robot":
                        if danger_polygon.intersects(object_polygon):
                            robot_state = "Robot in danger zone"
                        else:
                            robot_state = "Robot outside danger zone"
                        
                    if label=='human':
                        human_state = "Human in frame"


                    if ((label == "Pen") or (label=="highlighter")) and not tray_polygon.contains(object_polygon):
                        kit_misplaced = True

                    if tray_polygon.contains(object_polygon):
                        if label == "Pen":
                            pen_in_tray += 1
                        if label == "highlighter":
                            highlighter_in_tray += 1

    return pen_in_tray, highlighter_in_tray, kit_misplaced, robot_state, human_state, confidence_scores


#Function to extract the zone from the json file automatically, making it easy to use diferent videos
def get_zones(filePath):
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
    
        if label == "Tray":
            tray_pts = formatted_points
            tray_polygon = Polygon(tray_pts.reshape(-1,2))
        elif label == "Danger":
            danger_pts = formatted_points
            danger_polygon = Polygon(danger_pts.reshape(-1,2))

    return tray_pts,tray_polygon,danger_pts,danger_polygon

#Specify AI model and video to use
model = YOLO(r'YOLO_model\weights\best.pt') 
video_path = r'Images\Real_World_Example.mp4'
cap = cv2.VideoCapture(video_path)

# Extract width and height of video
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#Create the window that will display the video
cv2.namedWindow("YOLO Speed Test", cv2.WINDOW_NORMAL)
cv2.resizeWindow("YOLO Speed Test", 1080, 720)

tray_pts,tray_polygon,danger_pts,danger_polygon = get_zones(r'Images\Video_Frame\Frame1_zones.json')

#Create an empty image the size of the video, and draw the zones on it
zone_overlay = np.zeros((frame_height, frame_width, 3),dtype=np.uint8)
cv2.fillPoly(zone_overlay, [danger_pts], (0,0,255))
cv2.fillPoly(zone_overlay, [tray_pts], (0,255,0))

#Initialisation of timeout detection
last_detection = time.time()
detection_threshold = 0.5 #Time before no_detection_timeout

#Main loop
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    #Run the model on each video frame
    results = model(frame,conf=0.65, stream=True)

    #Reset states for each loop
    pen_in_tray = 0
    highlighter_in_tray = 0
    kit_misplaced = False
    kitting_state = ""
    robot_state = "No robot in frame"
    human_state = "No human in frame"
    safety_state = "Nothing in frame"
    system_health = "OK"
    Detected = False
    confidence_scores = []

    for r in results:
        class_names = r.names
        frame = r.plot()
        pen_in_tray,highlighter_in_tray,kit_misplaced, robot_state, human_state, confidence_scores = check_zones(pen_in_tray,highlighter_in_tray, kit_misplaced, robot_state, human_state, confidence_scores)
        if len(r.boxes) > 0:
            Detected = True
        
    #Blend the live frame with the zones, to draw them on screen, alpha = 0 -> only display live frame, alpha = 1 -> only display zones
    alpha = 0.2
    cv2.addWeighted(zone_overlay, alpha, frame, 1 - alpha, 0, dst=frame)

    #Check for kitting state
    if kit_misplaced == True:
        kitting_state = "kit_misplaced"
    elif pen_in_tray == 0 and highlighter_in_tray == 0:
        kitting_state="kit_empty"
    elif pen_in_tray == 1 and highlighter_in_tray == 0:
        kitting_state="kit_partial, missing highlighter"
    elif pen_in_tray == 0 and highlighter_in_tray == 1:
        kitting_state="kit_partial, missing pen"
    elif pen_in_tray == 1 and highlighter_in_tray == 1:
        kitting_state="kit_ready"
    elif pen_in_tray > 1 and highlighter_in_tray <= 1 :
        kitting_state = "kit_overfilled"
    elif pen_in_tray <= 1 and highlighter_in_tray > 1:
        kitting_state = "kit_overfilled"
    else:
        kitting_state="kit_overfilled"

    #Check for safety state
    if (human_state == "Human in frame") and (robot_state == "No robot in frame"):
        safety_state = "OK"
    elif (human_state == 'Human in frame') and (robot_state == "Robot outside danger zone"):
        safety_state = "coexist_safe"
    elif (human_state == 'Human in frame') and (robot_state == "Robot in danger zone"):
        safety_state = "coexist_dangerous"
    elif (human_state == 'No human in frame') and (robot_state == "Robot in danger zone"):
        safety_state = "Robot_in_danger_zone"

    #Check for system health state
    if Detected == True:
        last_detection = time.time()
    elif (time.time()-last_detection)>detection_threshold:
        system_health = "no_detection_timeout"

    if len(confidence_scores)>0:
        average_confidence = sum(confidence_scores)/len(confidence_scores)
    if (average_confidence < 0.6) and (system_health == "OK"):
        system_health = "low_confidence_alert"
    


    #Print the states in the terminal
    print(f"Kitting state is {kitting_state} !")
    print(f"Safety state is {safety_state}")
    print(f"System health is {system_health} \n")

    #Write the states to a JSON file to allow the GUI to read the states
    snapshot = { "ts": time.time(),"kit": kitting_state,"safety": safety_state,"system_health": system_health }
    with open(r"states.json", "a") as f:
        f.write(json.dumps(snapshot) + "\n")

    # Display the final result
    cv2.imshow("YOLO Speed Test", frame)

    #If q is pressed, exit the video early
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

#Safely exit and shut down all windows
cap.release()
cv2.destroyAllWindows()