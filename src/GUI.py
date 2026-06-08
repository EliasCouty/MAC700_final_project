import tkinter as tk
import json
import os
from PIL import Image, ImageTk

# --- CONFIGURATION ---
JSONL_PATH = r"Config\states.json" 
LOGO_PATH = r"Images\hogskolan-vast-logo.png"

# Vibe Settings
BG_COLOR = "#D6E8F5"       # Soft light blue background
TEXT_COLOR = "#001B3A"     # Dark navy blue for text
FONT_TITLE = ("Segoe UI", 28, "bold")
FONT_LABEL = ("Segoe UI", 16)
FONT_STATE = ("Segoe UI", 32, "bold")
FONT_SUB = ("Segoe UI", 12)

def read_latest_state():
    """Reads the last line of the JSONL file to get the current states."""
    if not os.path.exists(JSONL_PATH):
        return "waiting...", "waiting...", "waiting..."
    
    try:
        with open(JSONL_PATH, 'r') as file:
            lines = file.readlines()
            if lines:
                latest_data = json.loads(lines[-1].strip())
                
                # --- 1. Extract Kitting ---
                # Grab the direct value assigned to "kit"
                kit_raw = latest_data.get("kit", "unknown")
                
                # Failsafe: if it accidentally comes through as a dictionary, extract 'state'
                if isinstance(kit_raw, dict):
                    kit_raw = kit_raw.get("state", "unknown")
                else:
                    kit_raw = str(kit_raw)
                    
                # Ensure the GUI receives "kit_partial" even if JSON just says "partial"
                if kit_raw not in ["unknown", "waiting..."] and not kit_raw.startswith("kit_"):
                    kit_state = f"kit_{kit_raw}"
                else:
                    kit_state = kit_raw
                
                # --- 2. Extract Safety ---
                # Grab the direct value assigned to "safety"
                safety_raw = latest_data.get("safety", "ok")
                
                if isinstance(safety_raw, dict):
                    alarms = safety_raw.get("active_alarms", [])
                    safety_state = alarms[0].get("type", "ok") if alarms else "ok"
                else:
                    safety_state = str(safety_raw)
                
                # --- 3. Extract Health ---
                # Grab the direct value assigned to "system_health"
                health_raw = latest_data.get("system_health", "unknown")
                
                if isinstance(health_raw, dict):
                    health_status = health_raw.get("status", "unknown")
                    warnings = health_raw.get("warnings", [])
                    if health_status != "ok" and warnings:
                        health_state = warnings[0]
                    else:
                        health_state = health_status
                else:
                    health_state = str(health_raw)
                
                return kit_state, safety_state, health_state
                
    except Exception as e:
        print(f"Error reading state: {e}")
    
    return "error", "error", "error"

def update_gui():
    """Fetches the latest states and updates the UI every 100ms."""
    kit, safety, health = read_latest_state()
    
    # --- 1. Update Kitting ---
    kit_label.config(text=kit.upper())
    if kit == "kit_ready":
        kit_label.config(fg="#2E7D32") # Green
    elif kit in ["kit_partial", "kit_misplaced", "kit_overfilled"]:
        kit_label.config(fg="#D84315") # Orange
    elif kit == "kit_empty":
        kit_label.config(fg=TEXT_COLOR) # Navy
    else:
        kit_label.config(fg="#555555") # Gray for waiting/unknown

    # --- 2. Update Safety ---
    safety_label.config(text=safety.upper().replace("_", " "))
    if safety == "ok":
        safety_label.config(fg="#2E7D32") # Green
    elif safety in ["coexist_safe", "robot_in_danger_zone"]:
        safety_label.config(fg="#D84315") # Orange (Warning)
    elif safety == "coexist_dangerous":
        safety_label.config(fg="#FF0000") # Red (Critical)
    else:
        safety_label.config(fg=TEXT_COLOR)

    # --- 3. Update Health ---
    health_label.config(text=health.upper().replace("_", " "))
    if health == "ok":
        health_label.config(fg="#2E7D32") # Green
    elif health == "low_confidence_alert":
        health_label.config(fg="#D84315") # Orange (Warning)
    elif health == "no_detection_timeout":
        health_label.config(fg="#FF0000") # Red (Critical)
    else:
        health_label.config(fg=TEXT_COLOR)

    # Loop refresh (100ms period matches the spec frequency perfectly)
    root.after(100, update_gui)


# --- SETUP THE WINDOW ---
root = tk.Tk()
root.title("Multi-Modal State Dashboard")
root.geometry("900x700")
root.configure(bg=BG_COLOR)

# Main Title
tk.Label(root, text="System State Dashboard", font=FONT_TITLE, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(20, 30))

# --- FRAME: Kitting ---
kit_frame = tk.Frame(root, bg=BG_COLOR)
kit_frame.pack(pady=10)
tk.Label(kit_frame, text="KITTING PIPELINE:", font=FONT_LABEL, bg=BG_COLOR, fg=TEXT_COLOR).pack()
kit_label = tk.Label(kit_frame, text="WAITING...", font=FONT_STATE, bg=BG_COLOR, fg=TEXT_COLOR)
kit_label.pack()

# --- FRAME: Safety ---
safety_frame = tk.Frame(root, bg=BG_COLOR)
safety_frame.pack(pady=10)
tk.Label(safety_frame, text="SAFETY INTERLOCK:", font=FONT_LABEL, bg=BG_COLOR, fg=TEXT_COLOR).pack()
safety_label = tk.Label(safety_frame, text="WAITING...", font=FONT_STATE, bg=BG_COLOR, fg=TEXT_COLOR)
safety_label.pack()

# --- FRAME: System Health ---
health_frame = tk.Frame(root, bg=BG_COLOR)
health_frame.pack(pady=10)
tk.Label(health_frame, text="SYSTEM HEALTH:", font=FONT_LABEL, bg=BG_COLOR, fg=TEXT_COLOR).pack()
health_label = tk.Label(health_frame, text="WAITING...", font=FONT_STATE, bg=BG_COLOR, fg=TEXT_COLOR)
health_label.pack()

# --- FOOTER ---
tk.Label(root, text="ELIAS COUTY - UNIVERSITY WEST - 2026", font=FONT_SUB, bg=BG_COLOR, fg=TEXT_COLOR).pack(side="bottom", pady=20)

# --- LOGO INTEGRATION ---
try:
    img = Image.open(LOGO_PATH)
    
    # Set how much you want to scale it down (0.2 means 20% of original size)
    scale_factor = 0.2 
    
    # Calculate new dimensions, keeping the exact same ratio
    new_width = int(img.width * scale_factor)
    new_height = int(img.height * scale_factor)
    
    # Apply the resize with a high-quality filter to prevent pixelation
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    logo_img = ImageTk.PhotoImage(img)
    logo_label = tk.Label(root, image=logo_img, bg=BG_COLOR)
    logo_label.image = logo_img 
    
    # Place anchors it perfectly to the bottom left corner
    logo_label.place(x=20, rely=1.0, y=-20, anchor="sw") 
except Exception as e:
    print(f"Could not load logo: {e}")

# Start the polling loop
update_gui()

# Run the application
root.mainloop()