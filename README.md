# OMNIS Robot 🤖

AI-powered face recognition robot with voice assistant for MGM Model School.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- **Face Recognition** - Recognizes 16 students and staff members
- **Voice Assistant** - Wake word activation with "OMNIS"
- **Conversation Mode** - Follow-up questions without repeating wake word
- **School Knowledge Base** - 25+ MGM School-specific Q&A
- **AI Integration** - Google Gemini for general questions
- **Cross-Platform** - Works on Windows and Raspberry Pi

## 🎯 Demo

Say: **"OMNIS, who is our principal?"**
- Instant answer from school database
- No API calls needed for school questions
- Conversation continues without wake word

## 📋 Requirements

### Hardware
- Webcam or Pi Camera
- Microphone
- Windows PC or Raspberry Pi 3B+/4

### Software
- Python 3.10+
- OpenCV
- face-recognition library
- SpeechRecognition
- Google Gemini API key (optional, for general questions)

## 🚀 Quick Start

### Windows

```bash
# Clone repository
git clone https://github.com/Kavexa/OMNIS_ROBOT.git
cd OMNIS_ROBOT

# Install dependencies
pip install -r requirements.txt

# Run OMNIS
.\run_omnis.bat
```

### Raspberry Pi

```bash
# Clone repository
git clone https://github.com/Kavexa/OMNIS_ROBOT.git
cd OMNIS_ROBOT

# Run setup
chmod +x setup_pi.sh run_omnis.sh
./setup_pi.sh

# Run OMNIS
./run_omnis.sh
```

See [PI_SETUP.md](PI_SETUP.md) for detailed Pi instructions.

## 📖 Usage

1. **Show your face** to the camera
2. Wait for greeting: *"Hello [Name]!"*
3. Say: **"OMNIS, [your question]"**
4. Ask follow-up questions without "OMNIS"
5. Press `q` to quit

### Example Conversation
```
You: "OMNIS, who is our principal?"
OMNIS: "Dr Pooja S"

You: "When was MGM started?"
OMNIS: "Nineteen eighty three"

You: "How many students do we have?"
OMNIS: "Two thousand nine hundred"
```

## 🏫 School Knowledge Base

OMNIS knows about:
- Principal and staff
- School history and founding
- Student count and facilities
- Vision and tagline
- Important visitors
- And 20+ more topics!

## 🔧 Configuration

### Add Gemini API Key (Optional)

**Method 1: Using secrets_local.py (Recommended)**

1. Copy the example file:
   ```bash
   cp secrets_local.py.example secrets_local.py
   ```

2. Edit `secrets_local.py` and add your key:
   ```python
   GEMINI_KEY = 'your-api-key-here'
   ```

3. Get your API key from: https://makersuite.google.com/app/apikey

**Method 2: Using environment variables**

**Windows:** Edit `run_omnis.bat`
```batch
set GEMINI_KEY=your-api-key-here
```

**Raspberry Pi:** Edit `run_omnis.sh`
```bash
export GEMINI_KEY="your-api-key-here"
```

### Add New Faces

1. Add photo to `images/faces/[Name].jpg`
2. Run: `python EncodeGenerator.py`
3. Restart OMNIS

## 📁 Project Structure

```
OMNIS_ROBOT/
├── main.py              # Main application
├── FaceRecognition.py   # Face detection logic
├── sr_class.py          # Speech recognition
├── speaker.py           # Text-to-speech
├── school_data.py       # MGM School Q&A database
├── ai_response.py       # Gemini AI integration
├── secrets_local.py     # API key (create from .example)
├── run_omnis.bat        # Windows launcher
├── run_omnis.sh         # Pi launcher
├── setup_pi.sh          # Pi setup script
├── images/faces/        # Student photos
├── Resources/           # UI assets
└── PI_SETUP.md          # Raspberry Pi guide
```

## 🐛 Troubleshooting

### Voice not working?
```bash
python diagnose_voice.py
```

### Face not recognized?
- Ensure good lighting
- Look directly at camera
- Check if photo exists in `images/faces/`

### See full troubleshooting guide:
- [PI_SETUP.md](PI_SETUP.md) for Raspberry Pi
- [walkthrough.md](.gemini/antigravity/brain/.../walkthrough.md) for detailed fixes

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 👥 Credits

**Developed for:** MGM Model School  
**By:** Kavexa  
**Year:** 2024-2025

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check troubleshooting guides
- Review diagnostic scripts

---

**Made with ❤️ for MGM Model School**
