#!/bin/bash

echo "========================================"
echo "  OMNIS Audio Output Verification"
echo "========================================"
echo ""

# Check current card configuration
echo "[1] Current audio_config.py setting:"
grep "SPEAKER_CARD_INDEX" audio_config.py
echo ""

# List available cards
echo "[2] Available audio cards:"
aplay -l | grep "^card"
echo ""

# Check Card 1 specifically
echo "[3] Checking Card 1 (USB PnP Sound Device):"
aplay -l | grep -A2 "^card 1"
echo ""

# Check volume and mute status
echo "[4] Checking volume/mute status for Card 1:"
amixer -c 1 get PCM 2>/dev/null || echo "  No PCM control found"
amixer -c 1 get Master 2>/dev/null || echo "  No Master control found"
echo ""

# Unmute and set volume
echo "[5] Unmuting Card 1 and setting volume to 100%..."
amixer -c 1 set PCM unmute 2>/dev/null
amixer -c 1 set PCM 100% 2>/dev/null
amixer -c 1 set Master unmute 2>/dev/null
amixer -c 1 set Master 100% 2>/dev/null
echo "  ✓ Volume commands sent"
echo ""

# Test with speaker-test
echo "[6] Testing Card 1 with speaker-test..."
echo "  You should hear 'Front Left, Front Right'"
echo "  Press Ctrl+C if it hangs..."
timeout 5 speaker-test -D plughw:1,0 -c2 -t wav -l1 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✅ Speaker test PASSED!"
else
    echo "  ❌ Speaker test FAILED!"
    echo ""
    echo "  Trying alternative device strings..."
    
    for device in "hw:1,0" "sysdefault:CARD=1" "default"; do
        echo "  Testing: $device"
        timeout 3 speaker-test -D $device -c2 -t wav -l1 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "  ✅ SUCCESS with $device!"
            break
        fi
    done
fi
echo ""

# Test with actual audio file
echo "[7] Testing with actual audio playback..."
if command -v mpg123 &> /dev/null; then
    # Create a test audio file
    python3 << 'EOF'
from gtts import gTTS
try:
    tts = gTTS(text="Audio test on card one", lang='en')
    tts.save("audio_test.mp3")
    print("  ✓ Test audio file created")
except Exception as e:
    print(f"  ✗ Error creating audio: {e}")
EOF

    if [ -f "audio_test.mp3" ]; then
        echo "  Playing with mpg123 on plughw:1,0..."
        mpg123 -q -a plughw:1,0 audio_test.mp3 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "  ✅ mpg123 playback SUCCESSFUL!"
        else
            echo "  ❌ mpg123 playback FAILED!"
            echo "  Trying with default device..."
            mpg123 -q audio_test.mp3 2>/dev/null
        fi
        rm -f audio_test.mp3
    fi
else
    echo "  ⚠️  mpg123 not found. Install with: sudo apt-get install mpg123"
fi
echo ""

echo "========================================"
echo "  Verification Complete"
echo "========================================"
echo ""
echo "If you heard sound in tests 6 or 7, audio is working!"
echo "If you heard NO sound:"
echo "  1. Check speaker is plugged in and powered on"
echo "  2. Check speaker volume knob (if it has one)"
echo "  3. Try a different USB port"
echo "  4. Check USB cable connection"
echo ""
