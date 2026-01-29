# OMNIS Audio Fix - Transfer Instructions

## Files Updated

The following files have been fixed on your Windows machine:

1. **audio_config.py** - Changed to use Card 1
2. **speaker.py** - Fixed mpg123 playback and error handling
3. **test_speaker_fix.py** - Test script to verify the fix

## How to Transfer Files to Raspberry Pi

### Option 1: Using Git (Recommended if you have git set up)

On your **Windows machine**:
```bash
cd "C:\Users\Vaishnavi L\OneDrive\Desktop\OMNIS_5"
git add audio_config.py speaker.py test_speaker_fix.py
git commit -m "Fix audio playback on Card 1"
git push
```

On your **Raspberry Pi**:
```bash
cd ~/OMNIS_5
git pull
```

### Option 2: Manual Copy via SCP

On your **Windows machine** (in PowerShell):
```powershell
cd "C:\Users\Vaishnavi L\OneDrive\Desktop\OMNIS_5"
scp audio_config.py speaker.py test_speaker_fix.py pi@raspberrypi.local:~/OMNIS_5/
```

### Option 3: Manual Edit on Pi

If the above don't work, you can manually edit the files on the Pi:

#### 1. Update audio_config.py
```bash
nano ~/OMNIS_5/audio_config.py
```

Change line 6 from:
```python
SPEAKER_CARD_INDEX = 2
```
to:
```python
SPEAKER_CARD_INDEX = 1
```

Save with `Ctrl+O`, `Enter`, then `Ctrl+X`

#### 2. The speaker.py fix is more complex - use git or scp for this file

## Testing the Fix

Once files are transferred, run on your **Raspberry Pi**:

```bash
cd ~/OMNIS_5
python3 test_speaker_fix.py
```

You should hear: "Testing OMNIS audio on card one"

If that works, run OMNIS:
```bash
python3 main.py
```

## What Was Fixed

1. **Card Configuration**: Changed from Card 2 (doesn't exist) to Card 1 (your USB speaker)
2. **mpg123 Handling**: Changed from `os.system()` to `subprocess.run()` for better error handling
3. **Error Suppression**: Added proper stderr/stdout redirection to suppress ALSA warnings
4. **Pygame Fallback**: Improved pygame mixer initialization with better ALSA-compatible settings

## Expected Behavior

- ✅ speaker-test works (you confirmed this)
- ✅ OMNIS should now play greetings and responses
- ⚠️ ALSA error messages will still appear but can be ignored (they're harmless)

## If It Still Doesn't Work

Run this diagnostic:
```bash
cd ~/OMNIS_5
which mpg123
```

If it says "not found", install it:
```bash
sudo apt-get update
sudo apt-get install mpg123
```

Then test again with `python3 test_speaker_fix.py`
