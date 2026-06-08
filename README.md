This work was done for my MAC700 (machine vision and AI) class during my Erasmus semester at University West in Sweden.

This is a programm meant to check the states of a kitting process, as well as the safety of the user and the system.
First, I had to train an AI model to do segmentation on two different obejcts. I chose to do pens and highlighters. The model also needed to detect the human operator as well as the robot arm.
I took over 300 images and labeled them using X-AnyLabbeling. This allowed me to train my own YOLO segmentation modle, using yoloV8-seg as a base.

The assignement was to detect several states and inform the user about them :
- Kitting states : empty, partial (only 1 pen or highlighter), ready (1 pen and 1 highlighter), overfilled (2 or more of a single item) or misplaced (item outside of work zone)
- Safety state : Safe (no human in frame and robot outside of danger zone), coexist_safe (human and robot in frame, robot outside of danger zone) and coexist_dangerous (robot in danger zone and human in frame)
- System health : no detection timeout (x seconds since last detection) and low confidence alert (average object confidence below a chosen threshold)

I implemented this using Python and OpenCV. I created a program that reads every frame in a video, run the custom YOLO model and writes the states inside the terminal and inside a JSON file as well. 
The JSON can then be read by another python program that will show the current state in an easier to read GUI. 
