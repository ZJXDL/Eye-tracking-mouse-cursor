AI Eye-Controlled Mouse

A real-time computer vision application that lets you control your computer mouse using **eye movement and blinking**.

Using a standard webcam, the system detects facial landmarks and iris position with **MediaPipe**, estimates where the user is looking, maps that position to the screen, and moves the mouse cursor accordingly.

A sustained blink is detected using an **Eye Aspect Ratio (EAR)** calculation and converted into a mouse click.

> No specialized eye-tracking hardware required.

---

## ✨ Features

* 👁️ **Real-time iris tracking**
* 🖱️ **Hands-free mouse cursor control**
* 👀 **Blink-to-click interaction**
* 🎯 **Gaze coordinate remapping**
* 🧠 **MediaPipe Face Mesh landmark detection**
* 📉 **Exponential smoothing** for more stable cursor movement
* ⚡ Real-time processing with FPS monitoring
* 🛡️ Blink frame threshold and click cooldown to reduce accidental clicks
* 📷 Works with a standard webcam
* 💻 Uses the operating system's actual mouse cursor

---

## 🧠 How It Works

EyePilot processes the webcam stream through several stages:

```text
Webcam
   ↓
OpenCV Frame Capture
   ↓
MediaPipe Face Mesh
   ↓
Iris Landmark Detection
   ↓
Gaze Position Estimation
   ↓
Coordinate Remapping
   ↓
Exponential Smoothing
   ↓
Mouse Cursor Movement
```

At the same time:

```text
Eye Landmarks
   ↓
Eye Aspect Ratio (EAR)
   ↓
Blink Detection
   ↓
Frame Threshold
   ↓
Click Cooldown
   ↓
Mouse Click
```

### 1. Face & Iris Tracking

MediaPipe Face Mesh detects facial landmarks in real time.

The project uses iris landmarks:

```text
474, 475, 476, 477
```

The average position of these landmarks provides an approximate iris center.

### 2. Gaze Mapping

The detected iris position is normalized by MediaPipe.

Eye movement is then remapped from a calibrated region:

```text
X: 0.38 → 0.62
Y: 0.38 → 0.58
```

to the full screen resolution.

This allows relatively small eye movements to control the entire screen.

### 3. Cursor Smoothing

Raw gaze coordinates can be noisy.

EyePilot uses exponential smoothing:

```text
smoothed = α × target + (1 - α) × previous
```

The current configuration uses:

```text
SMOOTHING_ALPHA = 0.35
```

Higher values make the cursor more responsive.

Lower values make it smoother but introduce more lag.

### 4. Blink Detection

The project calculates an **Eye Aspect Ratio (EAR)** using facial landmarks.

Conceptually:

```text
EAR = vertical eye distance / horizontal eye distance
```

When the ratio drops below the blink threshold for several consecutive frames, a blink is detected.

Current configuration:

```text
BLINK_THRESHOLD = 0.20
BLINK_CONSEC_FRAMES = 3
```

A cooldown prevents a single blink from generating multiple clicks:

```text
CLICK_COOLDOWN_SEC = 0.6
```

---

## 🛠️ Tech Stack

| Technology   | Purpose                             |
| ------------ | ----------------------------------- |
| Python       | Core application                    |
| OpenCV       | Webcam capture and image processing |
| MediaPipe    | Face and iris landmark detection    |
| PyAutoGUI    | Mouse control                       |
| NumPy / Math | Numerical calculations              |
| Time         | FPS calculation and click timing    |

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/eyepilot.git
cd eyepilot
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install opencv-python mediapipe pyautogui
```

---

## ▶️ Running the Project

Start the application:

```bash
python eye_mouse.py
```

A webcam window should appear.

Move your eyes around the screen to control the cursor.

### Blink to click

Close your eye long enough for the configured blink threshold to be reached.

The application will trigger a mouse click.

### Exit

Press:

```text
Q
```

while the camera window is focused.

---

## ⚙️ Configuration

The main parameters are located near the top of the script.

### Cursor smoothing

```python
SMOOTHING_ALPHA = 0.35
```

Increase it for faster cursor response:

```python
SMOOTHING_ALPHA = 0.50
```

Decrease it for smoother movement:

```python
SMOOTHING_ALPHA = 0.20
```

### Blink sensitivity

```python
BLINK_THRESHOLD = 0.20
```

If blinks are not detected reliably, this value may need calibration.

### Blink duration

```python
BLINK_CONSEC_FRAMES = 3
```

Increasing this can reduce accidental clicks caused by noise.

### Click cooldown

```python
CLICK_COOLDOWN_SEC = 0.6
```

This prevents rapid repeated clicks.

### Gaze calibration

The current gaze mapping uses:

```python
GAZE_X_MIN = 0.38
GAZE_X_MAX = 0.62

GAZE_Y_MIN = 0.38
GAZE_Y_MAX = 0.58
```

These values are intended as an initial calibration and may need to be adjusted depending on the camera, user, lighting, and setup.

---

## 📁 Project Structure

```text
eyepilot/
│
├── eye_mouse.py
├── README.md
├── requirements.txt
├── .gitignore
└── LICENSE
```

---

## 🎯 Current Limitations

EyePilot is intentionally lightweight and uses a webcam rather than dedicated eye-tracking hardware.

Current limitations include:

* Gaze estimation is approximate rather than true optical gaze estimation.
* Calibration is manually configured.
* Lighting conditions can affect landmark detection.
* Camera position affects accuracy.
* Blinking is currently used as the primary click mechanism.
* Only one face is tracked.
* Cursor precision depends on webcam quality and user positioning.

---

## 🚀 Future Improvements

Possible upgrades include:

### 🎯 Automatic calibration

Replace the manually configured gaze box with an interactive calibration system.

For example:

```text
Look at ●
       ↓
Top-left
       ↓
Top-right
       ↓
Bottom-right
       ↓
Bottom-left
       ↓
Center
```

The application could learn the user's personal gaze range automatically.

### 👁️ Two-eye gaze estimation

Instead of relying primarily on one iris, combine both eyes to produce a more stable gaze estimate.

### 🖱️ Dwell clicking

Allow users to click by keeping their gaze over an object for a configurable amount of time.

```text
Look → Hold → Click
```

### 👆 Left / right click gestures

Potential interaction model:

```text
Blink       → Left click
Double blink → Double click
Long blink  → Right click
```

### 📊 Calibration UI

Add a graphical calibration interface displaying:

* Current gaze position
* Cursor position
* Calibration points
* Tracking confidence
* FPS

### 🧠 Better gaze estimation

A future version could use a learned gaze-estimation model instead of simple iris-coordinate remapping.

### 🖥️ Multi-monitor support

Extend screen mapping to support multiple displays.

---

## ⚠️ Safety / Control

Because it directly controls the operating-system mouse, it should be used carefully.

The application disables PyAutoGUI's default failsafe:

```python
pyautogui.FAILSAFE = False
```

This is useful for an eye-controlled interface but means moving the mouse to a screen corner will **not** automatically stop PyAutoGUI.

The application can be stopped by pressing:

```text
Q
```

in the camera window.

---

## 📸 Demo

A future version of this README can include a GIF demonstrating:

```text
Webcam
   ↓
Eye tracking
   ↓
Cursor movement
   ↓
Blink
   ↓
Mouse click
```

---

## 🧪 Project Goal

It was built as a practical computer vision project exploring how facial landmarks and iris tracking can be translated into human-computer interaction.

The project demonstrates the combination of:

**Computer Vision + Human-Computer Interaction + Real-Time Processing + Automation**

---

## 📜 License

MIT License
