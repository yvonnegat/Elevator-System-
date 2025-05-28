# 🛗 Multi-Elevator System (Python + Tkinter)

This is a desktop-based **Elevator Simulation System** built using **Python** and **Tkinter**. The application visualizes three elevator doors (A, B, and C), each with its own floor access limitations, simulating how real elevator dispatching works in a multi-elevator building.

---

## 🎥 Demo Video

👉 [Watch the Demo Video](https://your-video-link-here.com)  
*(Replace with your actual video link from YouTube, Google Drive, or Loom)*

---

## 🏗️ Elevator Configuration

| Elevator Door | Accessible Floors |
|---------------|-------------------|
| **Door A**     | Floors 0 to 5       |
| **Door B**     | Floors 0 to 8       |
| **Door C**     | Floors 0 to 10      |

Each elevator operates within its allowed floor range. The system intelligently handles floor requests and animates the elevators accordingly using Tkinter's GUI components.

---

## ⚙️ How It Works

- The GUI is built using the `tkinter` library and includes:
  - Elevator shafts
  - Doors and floors labeled clearly
  - Buttons for floor requests

- **Elevator Logic:**
  - The user requests an elevator to a specific floor.
  - The system checks which elevator(s) can access the requested floor.
  - The first available eligible elevator is dispatched.
  - Elevator movement is animated using timed updates.
  - Elevators can't move beyond their permitted range.

- **Multithreading:**
  - Uses Python `threading` to allow elevator animations and floor selection to run concurrently without freezing the interface.

---

## 💻 Installation & Running

### 🔧 Requirements

- Python 3.x
- No external libraries required (uses built-in `tkinter`, `threading`, and `time`)

### ▶️ To Run the App:

```bash
git clone https://github.com/yourusername/elevator-system.git
cd elevator-system
python elevator.py
