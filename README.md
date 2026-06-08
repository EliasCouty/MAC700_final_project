This work was done for my MAC700 (machine vision and AI) class during my Erasmus semester at University West in Sweden.

This is a program meant to check the states of a kitting process, as well as the safety of the user and the system.

https://github.com/user-attachments/assets/05e7daea-2dee-4784-ad03-877d7a94d84c

The assignment was to detect several states and inform the user about them:

| Category | State | Description |
| :--- | :--- | :--- |
| **Kitting states** | empty | No items in frame|
| | partial | Only 1 pen or 1 highlighter |
| | ready | 1 pen and 1 highlighter |
| | overfilled | 2 or more of a single item |
| | misplaced | At least 1 item outside of tray zone |
| **Safety state** | Safe | no human in frame and robot outside of danger zone |
| | coexist_safe | human and robot in frame, robot outside of danger zone |
| | coexist_dangerous | robot in danger zone and human in frame |
| **System health** | no detection timeout | x seconds since last detection |
| | low confidence alert | average object confidence below a chosen threshold |

First, I had to train an AI model to do segmentation on two different objects. I chose to do pens and highlighters. The model also needed to detect the human operator as well as the robot arm. I took over 300 images and labeled them using X-AnyLabeling. This allowed me to train my own YOLO segmentation model, using yoloV8-seg as a base.

Once my model was trained, I ran it on images to see how well it was working and then started working on the states detection. I implemented this using different libraries in Python:

- OpenCV : Frame by frame processing of the video and visual overlay of the zones
- Ultralytics : Used to run the YOLO segmentation on every frame
- Shapely : To check the intersection between objects and zones

For every frame of the video, my program will run the YOLO model, check if the detected objects intersect with the defined zones, determine the states, write the states in the terminal and JSON file and display the image containing the current frame, bounding boxes with confidence scores and zones. The GUI program will run at the same time, reading the last line of the JSON file to display the current states.

To run the code, you need to download the required libraries using the "requirements.txt" file and then launch the file "Launcher.py" to run both the Main and the GUI at the same time.

AI usage : The dataset collection, annotation, model training, code logic and system states were done entirely by myself. AI was used as a programming assistant to generate the GUI program, help with JSON data formatting and to understand some of the libraries that I had never used before. All of the code has been reviewed, understood and checked by myself.
