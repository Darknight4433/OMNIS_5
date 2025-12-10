# OMNIS Robot - Raspberry Pi App Setup 🥧

## 📋 Requirements

- Raspberry Pi 4 (2GB+ RAM minimum)
- Raspberry Pi OS (Bullseye or newer)
- USB Microphone
- USB Webcam or Pi Camera
- OpenAI API Key (✅ Already configured!)

## 🚀 Install as Desktop App (5 minutes)

### Step 1: Transfer Files to Pi

Open PowerShell on your Windows PC:
```powershell
# Replace 192.168.1.100 with your Pi's actual IP
scp -r "c:\Users\Vaishnavi L\OneDrive\Desktop\OMNIS" pi@192.168.1.100:/home/pi/

# Then SSH into Pi:
ssh pi@192.168.1.100
# Password: raspberry
```

### Step 2: Run Installation Script

```bash
cd ~/OMNIS/scripts
chmod +x install_pi_app.sh
./install_pi_app.sh
```

**This automatically:**
- ✅ Installs Python packages (opencv, face-recognition, openai, etc.)
- ✅ Installs system dependencies
- ✅ Creates **"OMNIS Robot"** desktop icon
- ✅ Configures auto-start on Pi boot

### Step 3: Launch OMNIS

**Option A: Desktop Icon (Easiest)**
1. Look for **"OMNIS Robot"** icon on desktop
2. Double-click to launch
3. Video window opens automatically

**Option B: Command Line**
```bash
cd ~/OMNIS
./run_omnis.sh
```

## 🎯 What You'll See

When OMNIS starts:
1. **Terminal opens** with startup messages
2. **Video window appears** showing camera feed
3. **Your face detected** - Green box around your face
4. **Greeting spoken** - "Hello [Name]! Welcome to MGM Model School robot."
5. **Listening** - System waits for your voice
6. **Ask anything** - Say: "OMNIS, tell me about MGM school"
7. **Robot responds** - Answers from school database or AI
8. **Ask follow-ups** - "What about the principal?" (no need to say OMNIS again)
9. **Exit** - Press 'q' in video window or Ctrl+C in terminal

## 🎤 Microphone Setup

### Quick Test
```bash
arecord -l                 # List audio devices
arecord -d 5 test.wav      # Record 5 seconds
aplay test.wav            # Play back
```

### Set Default Microphone
```bash
# Find your USB mic
arecord -l

# Edit config (change hw:2,0 to your device)
sudo nano /etc/asound.conf
```

Add this:
```
pcm.!default {
    type asym
    playback.pcm "speaker"
    capture.pcm "usb"
}
pcm.usb {
    type hw
    card 2
    device 0
}
```

Then reboot: `sudo reboot`

## 📹 Camera Setup

### Pi Camera Module
```bash
sudo raspi-config
# Interfacing Options > Camera > Enable
sudo reboot
```

### USB Webcam
```bash
# Test
fswebcam test.jpg
# Or on Pi 4:
libcamera-hello
```

## 🚀 Quick Setup

### Step 1: Transfer Files to Pi
```bash
# On your Windows PC, zip the OMNIS folder
# Then transfer to Pi via:
# - USB drive
# - SCP: scp -r OMNIS pi@raspberrypi.local:~/
# - Or download from GitHub if you pushed it
```

### Step 2: Run Setup Script
```bash
cd ~/OMNIS
chmod +x setup_pi.sh
./setup_pi.sh
```

This installs:
- Python 3 packages
- System dependencies (portaudio, cmake, etc.)
- Face recognition libraries

### Step 3: Configure API Key
```bash
nano run_omnis.sh
# Add your OpenAI API key on line 5
```

### Step 4: Run OMNIS
```bash
./run_omnis.sh
```

---

## 🔧 Manual Setup (if script fails)

### Install System Dependencies
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev
sudo apt-get install -y portaudio19-dev
sudo apt-get install -y cmake libatlas-base-dev
sudo apt-get install -y libopencv-dev python3-opencv
```

### Install Python Packages
```bash
pip3 install --upgrade pip
pip3 install opencv-python
pip3 install face-recognition
pip3 install numpy
pip3 install PyQt5
pip3 install SpeechRecognition
pip3 install gtts
pip3 install pygame
pip3 install cvzone
pip3 install pyaudio
pip3 install openai
```

### Fix PyAudio (if needed)
```bash
sudo apt-get install python3-pyaudio
```

---

## 🎤 Microphone Setup

### Test Microphone
```bash
# List audio devices
arecord -l

# Test recording
arecord -d 5 test.wav
aplay test.wav
```

### Set Default Microphone
```bash
# Edit ALSA config
nano ~/.asoundrc

# Add:
pcm.!default {
    type asym
    playback.pcm {
        type plug
        slave.pcm "hw:0,0"
    }
    capture.pcm {
        type plug
        slave.pcm "hw:1,0"  # Change 1,0 to your mic device
    }
}
```

---

## 📷 Camera Setup

### For USB Webcam
```bash
# Test camera
v4l2-ctl --list-devices
```

### For Pi Camera
```bash
# Enable Pi Camera
sudo raspi-config
# Interface Options -> Camera -> Enable

# Test
raspistill -o test.jpg
```

---

## 🏃 Running OMNIS

### One-Time Run
```bash
./run_omnis.sh
```

### Auto-Start on Boot
```bash
# Copy desktop file
cp scripts/faceapp_autostart.desktop ~/.config/autostart/

# Or add to crontab
crontab -e
# Add:
@reboot sleep 30 && cd /home/pi/OMNIS && ./run_omnis.sh
```

---

## 🐛 Troubleshooting

### "No module named 'cv2'"
```bash
pip3 install opencv-python
# Or
sudo apt-get install python3-opencv
```

### "No module named 'face_recognition'"
```bash
# This takes ~30 minutes on Pi
pip3 install face-recognition
```

### Microphone Not Working
```bash
# Check permissions
sudo usermod -a -G audio $USER

# Reboot
sudo reboot
```

### Camera Not Working
```bash
# Check permissions
sudo usermod -a -G video $USER

# For Pi Camera, enable in raspi-config
sudo raspi-config
```

### Low Performance
```bash
# Reduce face recognition frequency in main.py
# Process every 2nd or 3rd frame instead of every frame
```

---

## ⚡ Performance Tips

1. **Use Pi 4** - Much faster than Pi 3
2. **Overclock** - Safely boost CPU speed
3. **Reduce Resolution** - Lower camera resolution in main.py
4. **Skip Frames** - Process every 2nd frame for face recognition

---

## 📝 Quick Reference

**Start:** `./run_omnis.sh`
**Stop:** Press `q` in video window
**Logs:** Check terminal output
**API Key:** Edit `run_omnis.sh` line 5

---

**Ready to deploy on Pi!** 🥧
