import subprocess
import sys
import time

YOLO_SCRIPT = "Main.py"
GUI_SCRIPT = "GUI.py"

print("Starting Kitting State Detection System...")

try:
    #Launches video detection
    yolo_process = subprocess.Popen([sys.executable, YOLO_SCRIPT])
    
    #Waits for the video to start and the JSON file to be created
    time.sleep(2) 
    
    #Launches GUI
    gui_process = subprocess.Popen([sys.executable, GUI_SCRIPT])
    
    # Keep the launcher alive to monitor the background scripts
    yolo_process.wait()
    gui_process.wait()

except KeyboardInterrupt:
    #if Ctrl + C pressed, shuts down everything
    yolo_process.terminate()
    gui_process.terminate()