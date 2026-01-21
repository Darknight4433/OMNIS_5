# OMNIS on Raspberry Pi - Complete Setup Guide 🥧

## Prerequisites

- Raspberry Pi 3B+ or 4 (recommended: Pi 4 with 4GB RAM)
- Raspberry Pi OS installed
- Internet connection
- USB Microphone or Pi Camera with mic
- Speaker (3.5mm jack or HDMI audio)
- Optional: Pi Camera Module

## Step-by-Step Setup

### 1️⃣ Transfer Files to Raspberry Pi

**Option A: Using USB Drive**
```bash
# On Windows PC:
# 1. Copy entire OMNIS_ROBOT-main folder to USB drive
# 2. Plug USB into Raspberry Pi
# 3. On Pi, copy folder to home directory

cp -r /media/pi/USB_DRIVE/OMNIS_ROBOT-main ~/
cd ~/OMNIS_ROBOT-main
```

**Option B: Using SCP (if both on same network)**
```bash
# On Windows PC (PowerShell):
scp -r "C:\Users\Vaishnavi L\Downloads\OMNIS_ROBOT-main\OMNIS_ROBOT-main" pi@raspberrypi.local:~/

# Then on Pi:
cd ~/OMNIS_ROBOT-main
```

**Option C: Using Git (if you have a repository)**
```bash
# On Raspberry Pi:
cd ~
git clone https://github.com/your-username/OMNIS_ROBOT.git
cd OMNIS_ROBOT
```

### 2️⃣ Run Setup Script

```bash
cd ~/OMNIS_ROBOT-main

# Make setup script executable
chmod +x setup_pi.sh

# Run setup (this will take 5-10 minutes)
./setup_pi.sh
```

**What this installs:**
- Python 3 packages: opencv, face-recognition, speech recognition, gTTS, pygame
- Google Generative AI (Gemini)
- Audio libraries: portaudio, alsa-utils, pulseaudio
- System dependencies

### 3️⃣ Verify API Key

Your API key should already be in `secrets_local.py` if you copied the folder!

```bash
# Check if API key file exists
ls -la secrets_local.py

# If it doesn't exist, create it:
cp secrets_local.py.example secrets_local.py

# Edit if needed:
nano secrets_local.py
# Make sure it has: GEMINI_KEY = 'AIzaSyBiHVAHefkliGVBtA-L3BifjzQKJdUt2Qg'
```

### 4️⃣ Add Face Photos (Optional)

```bash
# Create faces directory if it doesn't exist
mkdir -p images/faces

# Copy your face photos (JPG format)
# Photos should be named: PersonName.jpg
# Example: Vaishnavi.jpg, Manish.jpg, etc.

# Generate face encodings
python3 EncodeGenerator.py
```

### 5️⃣ Test Audio Setup

**Test Microphone:**
```bash
# List audio devices
arecord -l

# Record 5-second test
arecord -d 5 test.wav

# Play it back
aplay test.wav
```

**Test Speaker:**
```bash
# Adjust volume
alsamixer
# Use arrow keys to adjust, ESC to exit

# Test speaker
# Press Ctrl+C to stop
```

**Set Audio Output:**
```bash
# For 3.5mm jack:
sudo raspi-config
# Navigate to: System Options → Audio → Headphones

# For HDMI:
# Navigate to: System Options → Audio → HDMI
```

### 6️⃣ Run OMNIS!

```bash
cd ~/OMNIS_ROBOT-main
python3 main.py
```

**Expected Output:**
```
✅ Gemini API Key Found: AIzaSyBi...
Loading Encoded File
Loaded 17 people: [...]
🎤 VOICE RECOGNITION STARTED
👂 Listening for 'OMNIS'...
```

### 7️⃣ Test Voice Recognition

Say clearly into the microphone:
```
"Hello, how are you?"
```

or

```
"OMNIS, what is AI?"
```

## Performance on Raspberry Pi

### Raspberry Pi 4 (4GB):
- ✅ Face detection: 2-3 FPS
- ✅ Speech recognition: Good
- ✅ TTS: 1-2 seconds
- ✅ Overall: Smooth

### Raspberry Pi 3B+:
- ⚠️ Face detection: 1-2 FPS
- ✅ Speech recognition: Good
- ✅ TTS: 2-3 seconds
- ⚠️ Overall: Usable but slower

## Optimization for Pi

If performance is slow, edit `secrets_local.py`:

```python
GEMINI_KEY = 'AIzaSyBiHVAHefkliGVBtA-L3BifjzQKJdUt2Qg'

import os
# Reduce for faster performance on Pi
os.environ['GEMINI_MAX_TOKENS'] = '200'  # Shorter responses
os.environ['RESPONSE_WORD_LIMIT'] = '20'  # Very brief
os.environ['FACE_MAX_FACES'] = '2'  # Process fewer faces
```

## Troubleshooting on Pi

### Issue: "No module named 'cv2'"
```bash
pip3 install opencv-python
# Or use Pi-optimized version:
sudo apt-get install python3-opencv
```

### Issue: "No module named 'google.generativeai'"
```bash
pip3 install google-generativeai
```

### Issue: Microphone not working
```bash
# Check if detected
arecord -l

# Test with diagnostic script
python3 diagnose_voice.py

# Check permissions
sudo usermod -a -G audio pi
```

### Issue: Camera not working
```bash
# Enable camera
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable

# Reboot
sudo reboot

# Test camera
raspistill -o test.jpg
```

### Issue: "Audio source must be entered before listening"
```bash
# Install PyAudio
sudo apt-get install python3-pyaudio

# Or build from source:
pip3 install pyaudio
```

## Auto-Start on Boot (Optional)

To make OMNIS start automatically when Pi boots:

```bash
# Create systemd service
sudo nano /etc/systemd/system/omnis.service
```

Add this content:
```ini
[Unit]
Description=OMNIS Voice Assistant
After=network.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/OMNIS_ROBOT-main
ExecStart=/usr/bin/python3 /home/pi/OMNIS_ROBOT-main/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable omnis.service
sudo systemctl start omnis.service

# Check status
sudo systemctl status omnis.service

# View logs
journalctl -u omnis.service -f
```

## Quick Reference Commands

```bash
# Start OMNIS
cd ~/OMNIS_ROBOT-main
python3 main.py

# Stop OMNIS
# Press 'q' in video window or Ctrl+C in terminal

# Update face encodings
python3 EncodeGenerator.py

# Test microphone
python3 diagnose_voice.py

# Check what's encoded
python3 -c "import pickle; print(pickle.load(open('encoded_file.p','rb'))[1])"

# View logs (if using systemd)
journalctl -u omnis.service -f
```

## File Locations on Pi

```
/home/pi/OMNIS_ROBOT-main/
├── main.py                 # Main program
├── setup_pi.sh            # Setup script (run once)
├── secrets_local.py       # Your API key (already configured!)
├── EncodeGenerator.py     # Generate face encodings
├── images/faces/          # Put face photos here
├── encoded_file.p         # Generated encodings
└── Resources/             # Background images
```

## Important Notes

✅ **API Key**: Already configured in `secrets_local.py` - no changes needed!
✅ **Wake Words**: "hello" and "omnis" both work
✅ **Optimized**: Fast 30-word responses, quick TTS
✅ **Portable**: Same code works on Windows and Pi

## Need Help?

1. Check `FINAL_CONFIG.md` for current settings
2. Run `python3 diagnose_voice.py` for audio issues
3. Check `README_PI.md` for detailed Pi troubleshooting

Enjoy OMNIS on your Raspberry Pi! 🥧🤖
