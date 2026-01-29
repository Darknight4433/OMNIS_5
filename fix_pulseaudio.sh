#!/bin/bash
# Fix PulseAudio blocking OMNIS speaker

echo "=========================================="
echo "OMNIS PulseAudio Fix"
echo "=========================================="

echo ""
echo "[1/3] Stopping PulseAudio..."
pulseaudio --kill
sleep 1

echo "[2/3] Checking if PulseAudio is stopped..."
if pgrep -x "pulseaudio" > /dev/null; then
    echo "⚠️  PulseAudio still running, force killing..."
    killall -9 pulseaudio
    sleep 1
else
    echo "✅ PulseAudio stopped"
fi

echo "[3/3] Testing speaker on card 2..."
speaker-test -D plughw:2,0 -c2 -t wav -l1

echo ""
echo "=========================================="
echo "✅ Done! Now run: python3 main.py"
echo "=========================================="
echo ""
echo "Note: PulseAudio will auto-restart later."
echo "If you need to run this fix again, just run:"
echo "  ./fix_pulseaudio.sh"
