# Gemini API Setup Guide

## ✅ Your API Key is Already Configured!

Your Gemini API key has been set up in `secrets_local.py` and will work on both Windows and Raspberry Pi.

## 📁 Files Created

1. **`secrets_local.py`** - Contains your API key (gitignored for security)
2. **`secrets_local.py.example`** - Template file for reference
3. **`run_omnis.bat.example`** - Windows run script template
4. **`run_omnis.sh.example`** - Raspberry Pi run script template

## 🚀 How to Run

### On Windows (Current PC)
```bash
python main.py
```

### On Raspberry Pi
```bash
# After copying files to Pi
python3 main.py
```

## 🔄 Transferring to Raspberry Pi

When you copy this project to your Raspberry Pi, the `secrets_local.py` file will come with it, so you don't need to configure anything again!

```bash
# On your Windows PC
# Copy the entire folder to Pi using SCP, USB, or git

# On Raspberry Pi
cd OMNIS_ROBOT-main
python3 main.py
```

## 🔑 Your API Key Location

The API key is stored in: `secrets_local.py`

This file:
- ✅ Is excluded from git (won't be committed)
- ✅ Works on Windows and Raspberry Pi
- ✅ Is automatically detected by the application
- ✅ Can be transferred with your project files

## 🛠️ If You Need to Change the API Key

Edit `secrets_local.py`:
```python
GEMINI_KEY = 'your-new-api-key-here'
```

## ✨ What's Fixed

1. ✅ API key permanently configured
2. ✅ Works on both Windows and Raspberry Pi
3. ✅ Feedback loop fixed (microphone won't hear speaker)
4. ✅ Documentation updated for Gemini API

## 🎤 Testing

Run the application:
```bash
python main.py
```

You should see:
```
✅ Gemini API Key Found: AIzaSyBi...
```

Then say: **"OMNIS, happy Diwali"**

The system will:
1. Respond to your greeting
2. Wait while speaking (no feedback loop!)
3. Resume listening after response completes

Enjoy! 🎉
