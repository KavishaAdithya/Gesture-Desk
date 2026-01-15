## Gesture Desk

A Python-based automation tool that utilizes Computer Vision (OpenCV & MediaPipe) to control Windows window management. By using specific hand gestures, users can move windows between monitors, snap them to split-screen layouts, maximize, or minimize them without touching the mouse or keyboard.

## Features

*   **Touchless Control:** Manage windows using only a webcam and hand gestures.
*   **Multi-Monitor Support:** Instantly send windows to Left or Right monitors.
*   **Window Snapping:** Supports Windows Snap layouts (Left/Right halves, Top/Bottom quadrants).
*   **State Machine Logic:** Uses a 3-stage system to ensure precise control and prevent accidental triggers.
*   **Visual Feedback:** Displays real-time FPS, hand skeleton tracking, and current gesture status on screen.
*   **Threaded Performance:** Separates video processing from gesture execution to ensure a smooth, lag-free video feed.

## Prerequisites

*   **Operating System:** Windows 10 or Windows 11
*   **Hardware:** A working Webcam.
*   **Python:** Version 3.8 or higher.

## Installation

1.  **Clone or Download** this repository.
2.  Ensure you have the helper file `HandtrackingModule.py` in the same directory as `main.py`.
3.  **Install Dependencies:**
    Open your terminal/command prompt and run:

    ```bash
    pip install opencv-python numpy pygetwindow pyautogui 
    pip install mediapipe==0.10.14
    ```

## How to Install

1. Open CMD and move into the Downloaded Folder
2. Type pyinstaller Window_manage.spec,press Enter


```

### The Workflow (State Machine)

The application operates on a **3-Stage State Machine**. You must perform gestures in sequence to achieve specific layouts.

#### 1. Root State (State 0)
This is the starting position. Selects the target monitor or basic window action.
*   **Index Finger:** Move Window to **Left Monitor**. (Transitions to State 1)
*   **Peace Sign (Index + Middle):** Move Window to **Right Monitor**. (Transitions to State 1)
*   **Spidey Sign (Index + Pinky + Thumb):** Focus on current window. (Transitions to State 1)
*   **Fist (0 Fingers Hand Detected):** Minimize Window. (Resets to Root)

#### 2. Positioning State (State 1)
Once a monitor is selected, choose the screen half.
*   **Index Finger:** Snap to **Left Half**. (Transitions to State 2)
*   **Peace Sign:** Snap to **Right Half**. (Transitions to State 2)
*   **All Fingers Open:** Maximize Window. (Resets to Root)

#### 3. Quadrant State (State 2)
Refine the snap to a specific corner (Quadrant).
*   **Index Finger:** Snap **Top**. (Finalizes action -> Resets to Root)
*   **Peace Sign:** Snap **Bottom**. (Finalizes action -> Resets to Root)

### Resetting
*   **No Hand (0 Fingers):** Resets the system back to the Root State immediately.

### Exiting
*   Press **'d'** on your keyboard while the video window is focused to stop the program.

## Project Structure

```text
├── main.py                # The main application entry point and state machine logic
├── HandtrackingModule.py  # (Required) Custom module for MediaPipe hand detection
└── README.md              # Project documentation
```

## Acknowledgments

*   **MediaPipe:** For the robust hand-tracking framework.
*   **OpenCV:** For image processing.
*   **PyAutoGUI:** For simulating keyboard shortcuts.