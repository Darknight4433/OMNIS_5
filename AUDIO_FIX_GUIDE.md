# OMNIS Audio Card Fix Guide

## Problem: No Sound After Card Change

If you're experiencing no audio output after changing the audio card, follow these steps:

## Quick Fix (Recommended)

Run the automated diagnostic tool on your Raspberry Pi:

```bash
python3 fix_audio_card.py
```

This tool will:
1. ✅ List all available audio cards
2. ✅ Detect USB audio devices automatically
3. ✅ Test each card for functionality
4. ✅ Check and fix mute/volume issues
5. ✅ Update `audio_config.py` with the correct card
6. ✅ Verify audio playback works

## Manual Fix

If you prefer to fix it manually:

### Step 1: Identify Your Audio Cards

```bash
aplay -l
```

This will show output like:
```
card 0: Headphones [bcm2835 Headphones], device 0: bcm2835 Headphones [bcm2835 Headphones]
card 1: vc4hdmi0 [vc4-hdmi-0], device 0: MAI PCM i2s-hifi-0 [MAI PCM i2s-hifi-0]
card 2: Device [USB PnP Sound Device], device 0: USB Audio [USB Audio]
card 3: Device [USB Audio Device], device 0: USB Audio [USB Audio]
```

**Look for your USB speaker** - it's usually labeled "USB Audio" or "USB PnP Sound Device"

### Step 2: Test the Card

Replace `X` with your card number (e.g., 2, 3):

```bash
speaker-test -D plughw:X,0 -c2 -t wav -l1
```

You should hear "Front Left, Front Right" if it works.

### Step 3: Check if Muted

```bash
amixer -c X scontrols
amixer -c X get PCM
```

If you see `[off]`, the card is muted. Unmute it:

```bash
amixer -c X set PCM unmute
amixer -c X set PCM 100%
amixer -c X set Master unmute
amixer -c X set Master 100%
```

### Step 4: Update Configuration

Edit `audio_config.py` and change the card number:

```python
# Audio configuration for OMNIS
SPEAKER_CARD_INDEX = 3  # Change this to your card number
```

### Step 5: Test with OMNIS

```bash
python3 test_speaker.py
```

## Common Issues & Solutions

### Issue 1: "Device or resource busy"
**Cause:** Another process (like PulseAudio) is using the audio device

**Solution:**
```bash
# Kill PulseAudio
pulseaudio -k

# Check what's using the device
fuser -v /dev/snd/*

# Kill the process if needed
sudo kill -9 <PID>
```

### Issue 2: "No such device"
**Cause:** Wrong card number or device not detected

**Solution:**
```bash
# Re-check card list
aplay -l

# Unplug and replug USB audio device
# Then check again with: aplay -l
```

### Issue 3: "Format not supported"
**Cause:** Using `hw:X,0` instead of `plughw:X,0`

**Solution:** Always use `plughw:X,0` which handles format conversion automatically

### Issue 4: Card number keeps changing
**Cause:** USB devices get assigned card numbers dynamically

**Solution:** Create an ALSA configuration file to fix the card order:

```bash
sudo nano /etc/modprobe.d/alsa-base.conf
```

Add:
```
options snd-usb-audio index=2
```

This forces USB audio to always be card 2.

## Verification Steps

After fixing, verify everything works:

1. **Test basic audio:**
   ```bash
   speaker-test -D plughw:X,0 -c2 -t wav -l1
   ```

2. **Test with actual speech:**
   ```bash
   python3 test_speaker.py
   ```

3. **Test with OMNIS:**
   ```bash
   python3 main.py
   ```
   Say "Hello OMNIS" and check if you hear a response.

## Current Configuration

Your current `audio_config.py` shows:
```python
SPEAKER_CARD_INDEX = 2
```

If you changed to card 3, you need to update this to:
```python
SPEAKER_CARD_INDEX = 3
```

## Need More Help?

Run the diagnostic tool for detailed information:
```bash
python3 fix_audio_card.py
```

Or check the detailed diagnostics:
```bash
python3 diagnose_speaker.py
python3 test_speaker_card3.py
```
