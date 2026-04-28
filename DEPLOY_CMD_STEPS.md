# Smart-Letters Deployment Guide (CMD)

This guide shows the exact step-by-step process to deploy and run this project using **Windows Command Prompt (cmd)**.

---

## 1) Open CMD in project folder

Press `Win + R`, type `cmd`, press Enter, then run:

```bat
cd /d C:\Users\utohb\Downloads\IOT
```

---

## 2) Check Python is installed

```bat
python --version
```

If this fails, install Python 3.10+ and make sure "Add Python to PATH" is enabled.

---

## 3) Create virtual environment

```bat
python -m venv .venv
```

Activate it:

```bat
.venv\Scripts\activate
```

You should see `(.venv)` at the left of your CMD line.

---

## 4) Install required packages

Run:

```bat
pip install eventlet python-socketio pyserial SpeechRecognition pyaudio
```

If `pyaudio` installation fails:
- update pip first:

```bat
python -m pip install --upgrade pip
```

- then try `pip install pyaudio` again.

---

## 5) Set your Arduino COM port

Open `voice_bridge.py` and make sure:

```python
ARDUINO_PORT = "COM3"
```

Change `"COM3"` to your actual port from Device Manager if needed.

---

## 6) Start the backend server

In CMD (inside project folder, with virtual env active):

```bat
python voice_bridge.py
```

Expected:
- Arduino connected message
- server starts on port `5000`
- voice recognition thread starts

Keep this CMD window open.

---

## 7) Open the web interface

Use one of these options:

### Option A (quick)
Double-click `index.html`.

### Option B (recommended)
Serve with Python HTTP server in a second CMD window:

```bat
cd /d C:\Users\utohb\Downloads\IOT
python -m http.server 8080
```

Then open:

`http://localhost:8080/index.html`

---

## 8) Test the system

1. Click mode buttons (`ALPHABET`, `NUMBERS`, `SHAPES`, `COLORS`).
2. Speak clearly.
3. Confirm:
   - recognized value appears on the web page
   - valid values are sent to Arduino

---

## 9) Run again next time

Every time you reopen CMD:

```bat
cd /d C:\Users\utohb\Downloads\IOT
.venv\Scripts\activate
python voice_bridge.py
```

Optional second CMD for UI server:

```bat
cd /d C:\Users\utohb\Downloads\IOT
python -m http.server 8080
```

---

## 10) Troubleshooting

- **Arduino not found**
  - close Arduino Serial Monitor
  - verify COM port in `voice_bridge.py`
  - reconnect USB cable

- **Mic not detecting voice**
  - check Windows microphone permissions
  - set correct input microphone in Windows Sound settings

- **Web page not updating**
  - confirm `python voice_bridge.py` is running
  - confirm socket URL in `index.html` points to `http://localhost:5000`

- **Port already in use**
  - stop old Python process or reboot
  - then run again

