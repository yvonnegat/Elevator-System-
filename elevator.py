import tkinter as tk
import time
import threading

import threading
import time
from tkinter import Canvas, Tk, Label

class jkuatelevator:
    def __init__(self, canvas, x_offset, label, floor_range, color_scheme):
        self.canvas = canvas
        self.current_floor = 0
        self.x_offset = x_offset
        self.label = label
        self.floor_range = floor_range
        self.is_moving = False
        self.is_occupied = False
        self.color_scheme = color_scheme
        self.person_parts = []  # Store all parts of the person
        self.person_visible = False
        self.sound_effects = True  # Enable sound effects by default
        
        # Import sound if available
        try:
            from playsound import playsound
            self.playsound = playsound
            self.has_sound = True
        except ImportError:
            self.has_sound = False
        
        # Shaft background
        self.shaft_bg = self.canvas.create_rectangle(
            155 + x_offset, 50, 215 + x_offset, 601,
            fill="#e0e0e0", outline="#bdbdbd", width=1
        )

        # Elevator body and components
        self.lift_body = self.canvas.create_rectangle(
            160 + x_offset, 550, 210 + x_offset, 600,
            fill=color_scheme["body"], outline="#555555", width=1
        )
        self.lift_highlight = self.canvas.create_rectangle(
            162 + x_offset, 552, 208 + x_offset, 565,
            fill=color_scheme["highlight"], outline="", width=0
        )
        self.door_left = self.canvas.create_rectangle(
            160 + x_offset, 550, 185 + x_offset, 600,
            fill=color_scheme["door"], outline="#555555", width=1
        )
        self.door_right = self.canvas.create_rectangle(
            185 + x_offset, 550, 210 + x_offset, 600,
            fill=color_scheme["door"], outline="#555555", width=1
        )
        self.door_trim = self.canvas.create_line(
            185 + x_offset, 550, 185 + x_offset, 600,
            fill="#333333", width=1
        )
        self.panel = self.canvas.create_rectangle(
            175 + x_offset, 532, 195 + x_offset, 547,
            fill="#000000", outline="#444444", width=1
        )
        self.floor_indicator = self.canvas.create_text(
            185 + x_offset, 540,
            text="0", font=("Arial", 12, "bold"),
            fill=color_scheme["display_text"]
        )
        self.status_light = self.canvas.create_oval(
            195 + x_offset, 535, 200 + x_offset, 540,
            fill="#4caf50", outline="#333333"
        )
        self.door_label = self.canvas.create_text(
            185 + x_offset, 615,
            text=f"Elevator {label}", font=("Arial", 10),
            fill="#333333"
        )
        self.up_indicator = self.canvas.create_polygon(
            175 + x_offset, 555, 180 + x_offset, 555, 177.5 + x_offset, 551,
            fill="#444444", outline="", state="hidden"
        )
        self.down_indicator = self.canvas.create_polygon(
            190 + x_offset, 551, 195 + x_offset, 551, 192.5 + x_offset, 555,
            fill="#444444", outline="", state="hidden"
        )
        self.position_indicator = self.canvas.create_rectangle(
            450, 550 - 2, 455, 550 + 2,
            fill=color_scheme["accent"], outline="", tags=f"pos_indicator_{label}"
        )
        
        # Floor indicators
        for i in range(0, 11):
            y_pos = 550 - (i * 50)
            self.canvas.create_text(
                145 + x_offset, y_pos + 25,
                text=str(i), font=("Arial", 10, "bold"),
                fill="#333333"
            )
            # Floor lines
            self.canvas.create_line(
                155 + x_offset, y_pos + 50, 215 + x_offset, y_pos + 50,
                fill="#bdbdbd", dash=(2, 2)
            )

        # Waiting area beside elevator
        self.canvas.create_rectangle(
            115 + x_offset, 550, 155 + x_offset, 600,
            fill="#f5f5f5", outline="#dddddd", width=1
        )

        self.request_queue = []

    def play_sound(self, sound_type):
        """Play sound effects if enabled and sound library is available"""
        if not self.sound_effects or not self.has_sound:
            return
            
        try:
            if sound_type == "ding":
                self.playsound("elevator_ding.mp3", False)
            elif sound_type == "door_open":
                self.playsound("door_open.mp3", False)
            elif sound_type == "door_close":
                self.playsound("door_close.mp3", False)
            elif sound_type == "moving":
                self.playsound("elevator_moving.mp3", False)
        except Exception:
            # Silently fail if sound file not found
            pass

    def set_occupied(self, status):
        self.is_occupied = status
        color = "#f44336" if status else "#4caf50"
        self.canvas.itemconfig(self.status_light, fill=color)

    def process_request(self, target_floor, status_label):
        if target_floor in self.request_queue:
            return
        self.request_queue.append(target_floor)
        if not self.is_moving:
            self.process_queue(status_label)

    def process_queue(self, status_label):
        if not self.request_queue:
            self.set_occupied(False)
            return

        self.is_moving = True
        self.set_occupied(True)
        target_floor = self.request_queue.pop(0)
        self.move_lift(target_floor, status_label)

        if self.request_queue:
            threading.Timer(1.0, lambda: self.process_queue(status_label)).start()
        else:
            self.set_occupied(False)
            self.is_moving = False

    def move_lift(self, target_floor, status_label):
        if target_floor < 0 or target_floor > 10:
            status_label.config(text="Invalid floor. Enter between 0-10.", fg="red")
            return

        start_y = 550 - (self.current_floor * 50)
        end_y = 550 - (target_floor * 50)

        if start_y > end_y:
            self.canvas.itemconfig(self.up_indicator, state="normal", fill=self.color_scheme["display_text"])
            self.canvas.itemconfig(self.down_indicator, state="hidden")
        elif start_y < end_y:
            self.canvas.itemconfig(self.up_indicator, state="hidden")
            self.canvas.itemconfig(self.down_indicator, state="normal", fill=self.color_scheme["display_text"])

        # Open doors and show person entering at the starting floor
        self.open_doors()
        self.animate_person_entering(start_y)
        self.close_doors()

        if start_y != end_y:
            status_label.config(text=f"Elevator {self.label} moving to Floor {target_floor}...", fg=self.color_scheme["accent"])
            self.play_sound("moving")
            
            step = -2 if start_y > end_y else 2
            components = [
                self.lift_body, self.lift_highlight, self.door_left, self.door_right,
                self.door_trim, self.panel, self.floor_indicator, self.door_label,
                self.up_indicator, self.down_indicator, self.status_light
            ]

            # Add person components to the list if person is inside elevator
            # Note: Person should be inside but hidden during travel
            components.extend(self.person_parts)

            while abs(start_y - end_y) >= abs(step):
                for component in components:
                    self.canvas.move(component, 0, step)
                start_y += step
                self.canvas.coords(self.position_indicator, 450, start_y - 2, 455, start_y + 2)
                visual_floor = round((550 - start_y) / 50)
                self.canvas.itemconfig(self.floor_indicator, text=str(visual_floor))
                self.canvas.update()
                time.sleep(0.03)

            final_adjustment = end_y - start_y
            if final_adjustment != 0:
                for component in components:
                    self.canvas.move(component, 0, final_adjustment)
                self.canvas.coords(self.position_indicator, 450, end_y - 2, 455, end_y + 2)

        self.current_floor = target_floor
        self.canvas.itemconfig(self.floor_indicator, text=str(self.current_floor))
        self.canvas.itemconfig(self.up_indicator, state="hidden")
        self.canvas.itemconfig(self.down_indicator, state="hidden")
        status_label.config(text=f"Elevator {self.label} arrived at Floor {self.current_floor}", fg=self.color_scheme["accent"])

        # Open doors and show person exiting at the target floor
        self.open_doors()
        self.animate_person_exiting(end_y)
        self.close_doors()

    def create_person(self, x_base, y_base, visible=True):
        # Clear previous person parts
        for part in self.person_parts:
            self.canvas.delete(part)
        self.person_parts = []
        
        # Person colors
        skin_tone = "#FFD3AA"  # Light skin tone
        hair_color = "#3B3021"  # Brown hair
        shirt_color = "#5D9CEC"  # Blue shirt
        pants_color = "#434A54"  # Dark pants
        
        # Create new person (more detailed)
        # Head
        head = self.canvas.create_oval(
            x_base-5, y_base-20, x_base+5, y_base-10,
            fill=skin_tone, outline=skin_tone
        )
        # Hair
        hair = self.canvas.create_arc(
            x_base-5, y_base-20, x_base+5, y_base-10,
            start=0, extent=180, fill=hair_color, outline=hair_color
        )
        # Body
        body = self.canvas.create_rectangle(
            x_base-6, y_base-10, x_base+6, y_base+2,
            fill=shirt_color, outline=shirt_color
        )
        # Arms
        left_arm = self.canvas.create_line(
            x_base-6, y_base-8, x_base-8, y_base-3,
            fill=shirt_color, width=3
        )
        right_arm = self.canvas.create_line(
            x_base+6, y_base-8, x_base+8, y_base-3,
            fill=shirt_color, width=3
        )
        # Legs
        left_leg = self.canvas.create_line(
            x_base-3, y_base+2, x_base-4, y_base+10,
            fill=pants_color, width=3
        )
        right_leg = self.canvas.create_line(
            x_base+3, y_base+2, x_base+4, y_base+10,
            fill=pants_color, width=3
        )
        
        self.person_parts = [head, hair, body, left_arm, right_arm, left_leg, right_leg]
        self.person_visible = visible
        
        # Set visibility
        state = "normal" if visible else "hidden"
        for part in self.person_parts:
            self.canvas.itemconfig(part, state=state)
        
        return self.person_parts

    def open_doors(self):
        # Play sound effect
        self.play_sound("ding")
        self.play_sound("door_open")
        
        # Add sound effect indicator
        ding = self.canvas.create_text(
            185 + self.x_offset, 520,
            text="*ding*", font=("Arial", 8),
            fill="#888888"
        )
        
        # If person is inside elevator (but hidden), make them visible
        if self.person_parts and self.person_visible:
            for part in self.person_parts:
                self.canvas.itemconfig(part, state="normal")
        
        # Smooth door animation
        for i in range(12):
            self.canvas.move(self.door_left, -1, 0)
            self.canvas.move(self.door_right, 1, 0)
            self.canvas.update()
            time.sleep(0.02)
            
        # Remove ding text after a short delay
        self.canvas.update()
        time.sleep(0.3)
        self.canvas.delete(ding)

    def close_doors(self):
        # Play sound effect
        self.play_sound("door_close")
        
        # Hide person if they're inside the elevator
        if self.person_parts and self.person_visible:
            # Check if person is inside elevator by checking x-coordinate
            # This assumes elevator center is at 185 + x_offset
            # We'll consider the person "inside" if they're within 10 pixels of center
            person_coords = self.canvas.coords(self.person_parts[0])
            person_x = (person_coords[0] + person_coords[2]) / 2
            
            if abs(person_x - (185 + self.x_offset)) < 10:
                # Person is inside elevator, hide them when doors close
                for part in self.person_parts:
                    self.canvas.itemconfig(part, state="hidden")
        
        # Smooth door animation
        for i in range(12):
            self.canvas.move(self.door_left, 1, 0)
            self.canvas.move(self.door_right, -1, 0)
            self.canvas.update()
            time.sleep(0.02)

    def animate_person_entering(self, y_position):
        # Create person waiting outside
        person_x = 135 + self.x_offset
        person_y = y_position + 25
        
        # Create initial person
        self.create_person(person_x, person_y, True)
        self.canvas.update()
        time.sleep(0.5)
        
        # Person walking to elevator animation
        steps = 10
        step_size = (185 + self.x_offset - person_x) / steps
        
        for i in range(steps):
            # Move all parts of the person
            for part in self.person_parts:
                self.canvas.move(part, step_size, 0)
            
            # Add walking animation effect (slight up and down movement)
            up_down = 1 if i % 2 == 0 else -1
            for part in self.person_parts:
                self.canvas.move(part, 0, up_down)
                
            self.canvas.update()
            time.sleep(0.05)
            
            # Reset up/down movement
            for part in self.person_parts:
                self.canvas.move(part, 0, -up_down)
        
        # Person is now inside elevator
        self.person_visible = True
        
    def animate_person_exiting(self, y_position):
        # Make person visible again when doors open
        for part in self.person_parts:
            self.canvas.itemconfig(part, state="normal")
        
        # If no person exists, create one inside elevator first
        if not self.person_parts:
            person_x = 185 + self.x_offset
            person_y = y_position + 25
            self.create_person(person_x, person_y, True)
        else:
            # Update person's position to match current elevator position
            current_coords = self.canvas.coords(self.person_parts[0])
            current_y = (current_coords[1] + current_coords[3]) / 2
            y_diff = y_position + 25 - current_y + 5  # +5 to adjust for head height
            for part in self.person_parts:
                self.canvas.move(part, 0, y_diff)
        
        # Get current position
        person_x = 185 + self.x_offset
        person_y = y_position + 25
        
        # Animate walking out
        steps = 10
        step_size = (person_x - (135 + self.x_offset)) / steps
        
        for i in range(steps):
            # Move all parts of the person (negative step to move left)
            for part in self.person_parts:
                self.canvas.move(part, -step_size, 0)
            
            # Add walking animation
            up_down = 1 if i % 2 == 0 else -1
            for part in self.person_parts:
                self.canvas.move(part, 0, up_down)
                
            self.canvas.update()
            time.sleep(0.05)
            
            # Reset up/down movement
            for part in self.person_parts:
                self.canvas.move(part, 0, -up_down)
        
        # Add walking away animation (fade out effect)
        for i in range(3):
            time.sleep(0.1)
            # Step outside
            for part in self.person_parts:
                self.canvas.move(part, -5, 0)
            self.canvas.update()
        
        # Person has left the scene
        for part in self.person_parts:
            self.canvas.itemconfig(part, state="hidden")
        
        self.person_visible = False

def select_lift(floor):
    # Original logic preserved exactly
    if 0 <= floor <= 5:
        return elevator_A
    elif 5 < floor <= 8:
        return elevator_B
    elif 8 < floor <= 10:
        return elevator_C
    return None

def go_to_floor(floor):
    elevator = select_lift(floor)
    if elevator:
        if elevator.is_occupied:
            status_label.config(text=f"Elevator {elevator.label} is occupied. Please wait.", fg="orange")
            # Add to queue but don't start moving
            elevator.request_queue.append(floor)
        else:
            # Start processing immediately if elevator is available
            elevator.process_request(floor, status_label)
    else:
        status_label.config(text="Invalid floor selection.", fg="red")

# Create the main window
root = tk.Tk()
root.title("JKUAT Modern Elevator Simulation")
root.geometry("1000x700")
root.configure(bg="#f5f5f5")

# Main canvas for simulation
canvas = tk.Canvas(root, width=500, height=650, bg="#f0f0f0", highlightthickness=1, highlightbackground="#cccccc")
canvas.pack(side=tk.LEFT, padx=0, pady=0)

# Control panel frame
control_frame = tk.Frame(root, width=500, height=650, bg="#ffffff")
control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
control_frame.pack_propagate(False)

# Title with modern styling
title_label = tk.Label(
    control_frame, 
    text="JKUAT Elevator System", 
    font=("Helvetica", 22, "bold"),
    bg="#ffffff",
    fg="#2c3e50",
    pady=15
)
title_label.pack(pady=20)

# Instructions
instruction_label = tk.Label(
    control_frame,
    text="Select a floor to call an elevator:",
    font=("Helvetica", 12),
    bg="#ffffff",
    fg="#555555"
)
instruction_label.pack(pady=10)

# Create floor buttons with modern styling
button_frame = tk.Frame(control_frame, bg="#ffffff", pady=15)
button_frame.pack()

# Define elevator-specific colors for the buttons
button_colors = {
    "A": "#2c3e50",  # Blue/Dark
    "B": "#c0392b",  # Red
    "C": "#27ae60"   # Green
}

# Create elevator status indicators
elevator_status_frame = tk.Frame(control_frame, bg="#ffffff")
elevator_status_frame.pack(pady=15)

for label, color in button_colors.items():
    frame = tk.Frame(elevator_status_frame, bg="#ffffff", padx=10, pady=5)
    frame.pack(side=tk.LEFT, padx=10)
    
    indicator = tk.Canvas(frame, width=15, height=15, bg="#ffffff", highlightthickness=0)
    indicator.create_oval(2, 2, 13, 13, fill="#4caf50", outline="#333333", tags=f"status_{label}")
    indicator.pack(side=tk.LEFT, padx=5)
    
    tk.Label(frame, text=f"Elevator {label}", bg="#ffffff", fg=color, font=("Arial", 10, "bold")).pack(side=tk.LEFT)

for i in range(10, -1, -1):
    # Determine which elevator serves this floor for button color
    if i <= 5:
        btn_color = button_colors["A"]
    elif i <= 8:
        btn_color = button_colors["B"]
    else:
        btn_color = button_colors["C"]
        
    btn = tk.Button(
        button_frame,
        text=str(i),
        width=4,
        height=2,
        bg=btn_color,
        fg="white",
        font=("Arial", 12, "bold"),
        relief=tk.FLAT,
        cursor="hand2",
        command=lambda f=i: go_to_floor(f)
    )
    # Arrange buttons in a better layout
    if i > 5:
        btn.grid(row=0, column=10-i, padx=4, pady=4)
    else:
        btn.grid(row=1, column=5-i, padx=4, pady=4)

# Status label with modern styling
status_frame = tk.Frame(control_frame, bg="#ffffff", pady=15)
status_frame.pack(fill="x", padx=20)

status_label = tk.Label(
    status_frame,
    text="Select a floor to begin",
    font=("Arial", 12),
    bg="#f8f9fa",
    fg="#555555",
    wraplength=400,
    pady=10,
    borderwidth=1,
    relief="groove"
)
status_label.pack(fill="x", pady=20)

# Floor ranges info frame with modern styling
info_frame = tk.LabelFrame(
    control_frame, 
    text="Elevator Information", 
    bg="#ffffff", 
    fg="#2c3e50",
    font=("Arial", 12, "bold"),
    padx=20, 
    pady=15
)
info_frame.pack(pady=10, fill="x", padx=20)

# Color indicators for each elevator
elevator_a_color = tk.Frame(info_frame, width=15, height=15, bg="#2c3e50")
elevator_a_color.grid(row=0, column=0, padx=(0,10), pady=5)
tk.Label(info_frame, text="Elevator A: Floors 0-5", fg="#2c3e50", bg="#ffffff", font=("Arial", 11)).grid(row=0, column=1, sticky="w", pady=5)

elevator_b_color = tk.Frame(info_frame, width=15, height=15, bg="#c0392b")
elevator_b_color.grid(row=1, column=0, padx=(0,10), pady=5)
tk.Label(info_frame, text="Elevator B: Floors 6-8", fg="#c0392b", bg="#ffffff", font=("Arial", 11)).grid(row=1, column=1, sticky="w", pady=5)

elevator_c_color = tk.Frame(info_frame, width=15, height=15, bg="#27ae60")
elevator_c_color.grid(row=2, column=0, padx=(0,10), pady=5)
tk.Label(info_frame, text="Elevator C: Floors 9-10", fg="#27ae60", bg="#ffffff", font=("Arial", 11)).grid(row=2, column=1, sticky="w", pady=5)

# Legend for elevator status
legend_frame = tk.Frame(control_frame, bg="#ffffff")
legend_frame.pack(pady=10)

available_indicator = tk.Canvas(legend_frame, width=15, height=15, bg="#ffffff", highlightthickness=0)
available_indicator.create_oval(2, 2, 13, 13, fill="#4caf50", outline="#333333")
available_indicator.grid(row=0, column=0, padx=5, pady=2)
tk.Label(legend_frame, text="Available", bg="#ffffff").grid(row=0, column=1, sticky="w", pady=2)

occupied_indicator = tk.Canvas(legend_frame, width=15, height=15, bg="#ffffff", highlightthickness=0)
occupied_indicator.create_oval(2, 2, 13, 13, fill="#f44336", outline="#333333")
occupied_indicator.grid(row=1, column=0, padx=5, pady=2)
tk.Label(legend_frame, text="Occupied", bg="#ffffff").grid(row=1, column=1, sticky="w", pady=2)

# Draw building with all floors visible
# Advanced Building UI with sophisticated visual elements
# Configuration
building_height = 600
floor_height = 50
num_floors = 11
building_width = 450
left_margin = 70

# Create sky background with gradient effect
for y in range(0, 650, 2):
    shade = int(230 - (y / 650) * 50)
    color = f"#{shade:02x}{shade+15:02x}{shade+25:02x}"
    canvas.create_line(0, y, 600, y, fill=color, width=2)

# Add subtle clouds
cloud_positions = [(120, 30), (320, 20), (520, 40)]
for x, y in cloud_positions:
    canvas.create_oval(x-30, y-10, x+30, y+10, fill="#ffffff", outline="#ffffff")
    canvas.create_oval(x-20, y-20, x+20, y, fill="#ffffff", outline="#ffffff")
    canvas.create_oval(x-10, y-5, x+40, y+15, fill="#ffffff", outline="#ffffff")

# Main building with 3D effect
# Building sides for 3D effect
canvas.create_polygon(
    building_width, 50,
    building_width + 30, 80,
    building_width + 30, building_height + 30,
    building_width, building_height,
    fill="#d0d0d0", outline="#555555", width=1
)

# Building top for 3D effect
canvas.create_polygon(
    left_margin, 50,
    left_margin + 30, 20,
    building_width + 30, 80,
    building_width, 50,
    fill="#e5e5e5", outline="#555555", width=1
)

# Main building facade with modern glass appearance
canvas.create_rectangle(left_margin, 50, building_width, building_height, fill="#e0e8f0", outline="#555555", width=2)

# Create reflective glass facade with gradient
for y in range(50, building_height, 5):
    opacity = int(150 + abs(((y - 50) / float(building_height - 50)) * 105 - 50))
    color = f"#{opacity:02x}{opacity+5:02x}{opacity+15:02x}"
    canvas.create_line(left_margin+1, y, building_width-1, y, fill=color, width=1)

# Add vertical structural elements
for x in range(left_margin + 40, building_width, 80):
    canvas.create_rectangle(x, 50, x + 15, building_height, fill="#c0c8d0", outline="#a0a8b0", width=1)
    # Add structural details
    for y in range(75, building_height, 50):
        canvas.create_rectangle(x-2, y-2, x+17, y+2, fill="#909090", outline="#707070", width=1)

# Rooftop structures with more detail
# Main roof
canvas.create_rectangle(left_margin + 20, 20, building_width - 20, 50, fill="#b0b0b0", outline="#909090", width=1)
# Mechanical room
canvas.create_rectangle(left_margin + 60, 5, left_margin + 140, 50, fill="#a0a0a0", outline="#808080", width=1)
# Communications tower
canvas.create_rectangle(building_width - 100, -30, building_width - 90, 50, fill="#909090", outline="#707070", width=1)
canvas.create_oval(building_width - 105, -40, building_width - 85, -20, fill="#a0a0a0", outline="#808080", width=1)

# Elevator shaft backgrounds with transparent glass effect
elevator_shafts = []
for x_offset in [0, 100, 200]:
    # Elevator glass
    shaft = canvas.create_rectangle(
        155 + x_offset, 50, 215 + x_offset, building_height, 
        fill="#d0e0e8", outline="#a0a8b0", width=1
    )
    # Elevator frame
    canvas.create_rectangle(
        153 + x_offset, 48, 217 + x_offset, building_height, 
        fill="", outline="#808890", width=2
    )
    # Add structural details
    for y in range(75, building_height, 50):
        canvas.create_line(155 + x_offset, y, 215 + x_offset, y, fill="#a0a8b0", width=1)
    
    elevator_shafts.append(shaft)

# Elevator cars with detailed styling
elevator_positions = [150, 300, 450]  # Different positions
elevator_cars = []
elevator_colors = ["#3a86ff", "#ff5a5f", "#43aa8b"]  # Different colors for each elevator

for i, x_offset in enumerate([0, 100, 200]):
    car_y = elevator_positions[i]
    
    # Elevator car background
    car = canvas.create_rectangle(
        158 + x_offset, car_y - 40, 212 + x_offset, car_y,
        fill=elevator_colors[i], outline="#555555", width=2
    )
    
    # Elevator door line
    canvas.create_line(
        185 + x_offset, car_y - 40, 185 + x_offset, car_y,
        fill="#555555", width=1
    )
    
    # Elevator number
    canvas.create_text(
        185 + x_offset, car_y - 20,
        text=f"E{i+1}",
        fill="white",
        font=("Arial", 12, "bold")
    )
    
    # Elevator status indicator
    status_colors = ["#22cc22", "#ffcc00", "#22cc22"]  # Green, Yellow, Green
    canvas.create_oval(
        195 + x_offset, car_y - 35, 205 + x_offset, car_y - 25,
        fill=status_colors[i], outline="#555555", width=1
    )
    
    elevator_cars.append(car)

# Ground floor entrance details
# Main entrance
canvas.create_rectangle(left_margin + 100, building_height - 80, left_margin + 180, building_height, 
                       fill="#404040", outline="#202020", width=2)
# Revolving door
canvas.create_oval(left_margin + 130, building_height - 60, left_margin + 150, building_height - 40,
                  fill="#a0c0e0", outline="#555555", width=2)
canvas.create_line(left_margin + 140, building_height - 60, left_margin + 140, building_height - 40, fill="#555555", width=2)
canvas.create_line(left_margin + 130, building_height - 50, left_margin + 150, building_height - 50, fill="#555555", width=2)

# Draw floor lines, labels and floor areas with enhanced styling
# floor_functions = [
    
# ]

for i in range(num_floors):
    floor_y = building_height - 50 - (i * floor_height)  # Floor 0 at bottom
    
    # Draw the floor line
    canvas.create_line(left_margin, floor_y, building_width, floor_y, fill="#a0a8b0", width=1)
    
    # Create fancy floor labels with background
    label_bg = canvas.create_rectangle(
        10, floor_y + floor_height//2 - 12, 
        left_margin - 5, floor_y + floor_height//2 + 12,
        fill="#e0e0e0", outline="#c0c0c0", width=1
    )
    
    canvas.create_text(
        left_margin - 15, floor_y + floor_height//2,
        text=f"FLOOR {i}",
        fill="#333333",
        font=("Arial", 10, "bold"),
        anchor="e"
    )
    
    # Add subtle floor coloring with gradient effect
    base_color = 245 if i % 2 == 0 else 235
    for y_offset in range(floor_height):
        # Create subtle gradient within each floor
        shade = base_color - int(abs(y_offset - floor_height/2) / (floor_height/2) * 10)
        color = f"#{shade:02x}{shade:02x}{shade+5:02x}"
        canvas.create_line(
            left_margin + 1, floor_y + y_offset, 
            building_width - 1, floor_y + y_offset,
            fill=color, width=1
        )
    
    # Add floor function labels with background
    function_bg = canvas.create_rectangle(
        left_margin + 20, floor_y + floor_height//2 - 10,
        left_margin + 140, floor_y + floor_height//2 + 10,
        fill="#f0f0f0", outline="#d0d0d0", width=1
    )
    
    canvas.create_text(
        left_margin + 80, floor_y + floor_height//2,
        text=[i],
        fill="#333333",
        font=("Arial", 9, "bold"),
        anchor="center"
    )
    
    # Add occupancy indicator for each floor
    occupancy = [90, 75, 60, 85, 70, 65, 40, 30, 80, 55, 20]  # Percentage occupancy
    
    # Occupancy bar background
    canvas.create_rectangle(
        building_width - 80, floor_y + floor_height//2 - 8,
        building_width - 20, floor_y + floor_height//2 + 8,
        fill="#e0e0e0", outline="#c0c0c0", width=1
    )
    
    # Occupancy bar fill
    occ_width = int(60 * occupancy[i] / 100)
    occ_color = "#22cc22" if occupancy[i] < 70 else "#ffcc00" if occupancy[i] < 90 else "#ff5a5f"
    
    canvas.create_rectangle(
        building_width - 80, floor_y + floor_height//2 - 8,
        building_width - 80 + occ_width, floor_y + floor_height//2 + 8,
        fill=occ_color, outline="", width=0
    )
    
    canvas.create_text(
        building_width - 50, floor_y + floor_height//2,
        text=f"{occupancy[i]}%",
        fill="#333333",
        font=("Arial", 8, "bold"),
        anchor="center"
    )

# Ground level with decorative elements
canvas.create_rectangle(left_margin - 40, building_height, building_width + 60, building_height + 5, 
                       fill="#a0a0a0", outline="#707070", width=1)

# Add trees and landscaping
for x in [left_margin - 30, left_margin + 30, building_width - 30, building_width + 30]:
    # Tree trunk
    canvas.create_rectangle(x-3, building_height - 30, x+3, building_height, fill="#805030", outline="#603020", width=1)
    # Tree foliage
    canvas.create_oval(x-15, building_height - 60, x+15, building_height - 20, fill="#407040", outline="#305030", width=1)

# Building foundation with more detailed structure
canvas.create_polygon(
    left_margin - 40, building_height + 5,
    building_width + 60, building_height + 5,
    building_width + 40, building_height + 20,
    left_margin - 20, building_height + 20,
    fill="#808080", outline="#707070", width=1
)

# Sidewalk
canvas.create_rectangle(0, building_height + 20, 600, building_height + 40, fill="#e0e0e0", outline="#c0c0c0", width=1)

# Add building name with elegant styling
name_bg = canvas.create_rectangle(
    left_margin + 50, 15,
    building_width - 50, 45,
    fill="#002050", outline="#001030", width=2
)

canvas.create_text(
    (left_margin + building_width) // 2, 30,
    text="JKUAT",
    fill="#ffffff",
    font=("Arial", 16, "bold")
)

# Status and Control Panel
panel_bg = canvas.create_rectangle(
    10, building_height + 50,
    580, building_height + 120,
    fill="#f0f0f0", outline="#c0c0c0", width=2
)

# Panel title
canvas.create_rectangle(
    10, building_height + 50,
    580, building_height + 70,
    fill="#002050", outline="#001030", width=1
)

canvas.create_text(
    295, building_height + 60,
    text="BUILDING MANAGEMENT SYSTEM",
    fill="#ffffff",
    font=("Arial", 12, "bold")
)

# Status indicators
indicators = [
    ("Elevator System", "#22cc22", "NORMAL"),
    ("Security System", "#22cc22", "ACTIVE"),
    ("Climate Control", "#ffcc00", "OPTIMIZING"),
    ("Power System", "#22cc22", "OPTIMAL"),
    ("Occupancy", "#ffcc00", "75%")
]

for i, (label, color, status) in enumerate(indicators):
    x_pos = 70 + i * 110
    
    # Indicator label
    canvas.create_text(
        x_pos, building_height + 85,
        text=label,
        fill="#333333",
        font=("Arial", 8),
        anchor="center"
    )
    
    # Status light
    canvas.create_oval(
        x_pos - 5, building_height + 95,
        x_pos + 5, building_height + 105,
        fill=color, outline="#555555", width=1
    )
    
    # Status text
    canvas.create_text(
        x_pos, building_height + 110,
        text=status,
        fill="#333333",
        font=("Arial", 9, "bold"),
        anchor="center"
    )

# Clock display
current_time = "14:30"
canvas.create_text(
    540, building_height + 95,
    text=current_time,
    fill="#333333",
    font=("Arial", 14, "bold"),
    anchor="center"
)

# Add interactive elements hint
canvas.create_text(
    295, building_height + 140,
    text="Click on elevators or floors to interact with the building system",
    fill="#555555",
    font=("Arial", 8, "italic"),
    anchor="w"
)

# Define modern color schemes for each elevator
elevator_colors = {
    "A": {
        "body": "#2c3e50",      # Main body color (dark blue)
        "door": "#34495e",      # Door color (slightly lighter)
        "highlight": "#3e5871",  # Highlight for 3D effect
        "accent": "#3498db",    # Accent color (bright blue)
        "display_text": "#3498db"  # Display text color
    },
    "B": {
        "body": "#c0392b",      # Main body color (dark red)
        "door": "#d14836",      # Door color
        "highlight": "#e57373",  # Highlight for 3D effect
        "accent": "#e74c3c",    # Accent color (bright red)
        "display_text": "#f39c12"  # Display text color (orange)
    },
    "C": {
        "body": "#27ae60",      # Main body color (dark green)
        "door": "#2ecc71",      # Door color
        "highlight": "#81c784",  # Highlight for 3D effect
        "accent": "#2ecc71",    # Accent color (bright green)
        "display_text": "#2ecc71"  # Display text color
    }
}

# Create elevators with realistic design
elevator_A = jkuatelevator(canvas, 0, "A", range(0, 6), elevator_colors["A"])
elevator_B = jkuatelevator(canvas, 100, "B", range(6, 9), elevator_colors["B"])
elevator_C = jkuatelevator(canvas, 200, "C", range(9, 11), elevator_colors["C"])

# Start the main event loop
root.mainloop()
