"""
OMNIS Voice Troubleshooting Guide
==================================

If voice isn't working, check these in order:

1. DO YOU SEE THESE MESSAGES?
   - "🎤 Starting Voice Recognition..."
   - "🔊 Adjusting for ambient noise..."
   - "👂 Listening for 'OMNIS'..."

2. IF YES, but it doesn't hear you:
   - Speak LOUDER
   - Say "OMNIS" very clearly
   - Check Windows microphone isn't muted
   - Try: "AVNISH" (common mishearing)

3. IF NO (messages don't appear):
   - Face not detected
   - Show your face to camera
   - Wait for green box

4. TEST MICROPHONE SEPARATELY:
   Run: python quick_mic_test.py

5. ENERGY THRESHOLD:
   If you see "Energy threshold: XXXX"
   - Should be 200-400 for quiet room
   - If > 1000, room is too noisy

Common Issues:
- Microphone muted in Windows
- Wrong microphone selected
- Background noise too loud
- Speaking too softly
"""
print(__doc__)
