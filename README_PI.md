# OMNIS on Raspberry Pi - Setup & Usage Guide

## Quick Setup (First Time Only)

### 1. Transfer Files to Raspberry Pi
```bash
# On your Windows PC, copy the OMNIS folder to Pi
# Or clone from git if you have it in a repository
```

### 2. Run Setup Script
```bash
cd OMNIS
chmod +x setup_pi.sh
./setup_pi.sh
```

This installs:
- Python packages (opencv, face_recognition, speech_recognition, etc.)
- Audio libraries (portaudio, alsa-utils)
- All dependencies

### 3. Add Your Face Photos
```bash
# Put JPG photos in images/ folder
cp /path/to/your/photo.jpg images/YourName.jpg

# Generate encodings
python3 EncodeGenerator.py
```

### 4. Set Gemini API Key

**Method 1: Using secrets_local.py (Recommended)**
```bash
# Copy the example file
cp secrets_local.py.example secrets_local.py

# Edit the file
nano secrets_local.py

# Add your key:
GEMINI_KEY = 'your-actual-api-key-here'
```

**Method 2: Using run script**
```bash
# Edit the run script
nano run_omnis.sh

# Change this line:
export GEMINI_KEY="your-actual-api-key-here"
```

Get your API key from: https://makersuite.google.com/app/apikey

### 5. Make Run Script Executable
```bash
chmod +x run_omnis.sh
```

---

## Running OMNIS

### Start OMNIS
```bash
./run_omnis.sh
```

### Stop OMNIS
- Press `q` in the video window
- Or press `Ctrl+C` in terminal

---

## Raspberry Pi Specific Notes

### Camera Setup
The Pi camera should work automatically. If not:
```bash
# Enable camera in raspi-config
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
```

### Microphone Setup
```bash
# List audio devices
arecord -l

# Test microphone
arecord -d 5 test.wav
aplay test.wav

# If no sound, check volume
alsamixer
```

### Audio Output
```bash
# Set audio output to 3.5mm jack
sudo raspi-config
# Navigate to: System Options → Audio → Headphones

# Or set to HDMI
# Navigate to: System Options → Audio → HDMI
```

### Performance Tips
For better performance on Raspberry Pi:

1. **Reduce video resolution** (in main.py):
```python
# Change line ~56
imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # Already optimized
```

2. **Use Pi Camera instead of USB** (faster):
```python
# Install picamera
pip3 install picamera

# In main.py, replace:
cap = cv2.VideoCapture(0)
# With:
from picamera.array import PiRGBArray
from picamera import PiCamera
```

3. **Overclock Pi** (optional, advanced):
```bash
sudo raspi-config
# Performance Options → Overclock
```

---

## Autostart on Boot

To make OMNIS start automatically when Pi boots:

### 1. Create systemd service
```bash
sudo nano /etc/systemd/system/omnis.service
```

### 2. Add this content:
```ini
[Unit]
Description=OMNIS Voice Assistant
After=network.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/OMNIS
Environment="GEMINI_KEY=your-api-key-here"
ExecStart=/usr/bin/python3 /home/pi/OMNIS/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### 3. Enable and start service
```bash
sudo systemctl enable omnis.service
sudo systemctl start omnis.service

# Check status
sudo systemctl status omnis.service

# View logs
journalctl -u omnis.service -f
```

---

## Troubleshooting on Pi

### Issue: "No module named 'cv2'"
```bash
pip3 install opencv-python
# Or for Pi-optimized version:
sudo apt-get install python3-opencv
```

### Issue: "No module named 'face_recognition'"
```bash
# face_recognition needs dlib, which takes time to compile on Pi
pip3 install dlib
pip3 install face_recognition
# This may take 30+ minutes on Pi
```

### Issue: Microphone not working
```bash
# Check if detected
arecord -l

# Test recording
python3 test_voice.py

# Check permissions
sudo usermod -a -G audio pi
```

### Issue: Camera not working
```bash
# Enable camera
sudo raspi-config

# Test camera
raspistill -o test.jpg

# Check permissions
sudo usermod -a -G video pi
```

### Issue: "Illegal instruction" error
This means you need ARM-compatible packages:
```bash
# Use Pi-optimized packages
sudo apt-get install python3-opencv python3-numpy
```

---

## File Locations on Pi

```
/home/pi/OMNIS/
├── main.py              # Main program
├── run_omnis.sh         # Start script (use this!)
├── setup_pi.sh          # Setup script (run once)
├── test_voice.py        # Test microphone
├── EncodeGenerator.py   # Generate face encodings
├── images/              # Put face photos here
│   ├── Person1.jpg
│   └── Person2.jpg
├── secrets_local.py     # API key (create from .example)
└── Resources/           # Background images
```

---

## Performance Expectations

**Raspberry Pi 4 (4GB):**
- Face detection: ~2-3 FPS
- Speech recognition: Good
- TTS: Good
- Overall: Usable

**Raspberry Pi 3:**
- Face detection: ~1-2 FPS
- Speech recognition: Good
- TTS: Good
- Overall: Slower but works

**Raspberry Pi Zero:**
- Not recommended (too slow)

---

## Quick Commands Reference

```bash
# Start OMNIS
./run_omnis.sh

# Test voice
python3 test_voice.py

# Generate face encodings
python3 EncodeGenerator.py

# Check what's encoded
python3 -c "import pickle; print(pickle.load(open('encoded_file.p','rb'))[1])"

# Test camera
python3 -c "import cv2; cap=cv2.VideoCapture(0); print(cap.read()[0])"

# Check microphone
arecord -l

# Set API key for one session
export GEMINI_KEY="your-key"
python3 main.py
```

---

## Differences from Windows

| Feature | Windows | Raspberry Pi |
|---------|---------|--------------|
| Run script | `run_omnis.bat` | `./run_omnis.sh` |
| Python command | `python` | `python3` |
| Package manager | `pip` | `pip3` |
| Camera | Usually index 0 | Usually index 0 or Pi Camera |
| Audio | DirectSound | ALSA/PulseAudio |
| Performance | Fast | Moderate (depends on Pi model) |

---

## Next Steps

1. ✅ Run `./setup_pi.sh` to install dependencies
2. ✅ Add face photos to `images/` folder
3. ✅ Run `python3 EncodeGenerator.py`
4. ✅ Set up API key (edit `secrets_local.py` or `run_omnis.sh`)
5. ✅ Run `./run_omnis.sh`
6. ✅ Say "OMNIS, hello!" to test

Enjoy your OMNIS robot on Raspberry Pi! 🤖🥧
