#!/bin/bash
# OMNIS Launcher - Silent Mode (Hides ALSA warnings)

# 1. Kill PulseAudio/Jack to free up the card
pkill pulseaudio
pkill jackd

# 2. Set Audio to Card 1 (USB) just in case
export ALSA_CARD=1

echo "----------------------------------------"
echo "🚀 Starting OMNIS (Log Spam Filtered)..."
echo "----------------------------------------"

# Run Python, filtering out the known ALSA spam lines
python3 main.py 2>&1 | grep -v "Expression 'GetExactSampleRate" | grep -v "connect(2) call to /dev/shm/jack" | grep -v "attempt to connect to server failed"

echo "----------------------------------------"
echo "🛑 OMNIS Stopped."
