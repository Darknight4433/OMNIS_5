#!/usr/bin/env python3
"""
Quick audio verification for OMNIS - Run this on the Raspberry Pi
"""

import os
import subprocess
import sys

print("="*60)
print("  OMNIS Audio Output Quick Test")
print("="*60)

# Step 1: Check config
print("\n[1] Checking audio_config.py...")
try:
    import audio_config
    card = audio_config.SPEAKER_CARD_INDEX
    print(f"    Configured to use Card {card}")
except:
    print("    ⚠️  Could not read audio_config.py")
    card = 1

# Step 2: Unmute
print(f"\n[2] Unmuting Card {card}...")
os.system(f"amixer -c {card} set PCM unmute 2>/dev/null")
os.system(f"amixer -c {card} set PCM 100% 2>/dev/null")
os.system(f"amixer -c {card} set Master unmute 2>/dev/null")
os.system(f"amixer -c {card} set Master 100% 2>/dev/null")
print("    ✓ Unmute commands sent")

# Step 3: Test speaker
print(f"\n[3] Testing Card {card} with speaker-test...")
print("    You should hear 'Front Left, Front Right'")
print("    (This will take 3-4 seconds)")

ret = os.system(f"timeout 4 speaker-test -D plughw:{card},0 -c2 -t wav -l1 > /dev/null 2>&1")

if ret == 0:
    print("    ✅ AUDIO IS WORKING!")
    print("\n" + "="*60)
    print("  SUCCESS! Your speaker on Card", card, "is working!")
    print("="*60)
    print("\n  OMNIS should now be able to play audio.")
    print("  The ALSA errors you see are just warnings and can be ignored.")
    sys.exit(0)
else:
    print(f"    ❌ Test failed (code: {ret})")
    
    # Try alternative
    print("\n[4] Trying alternative device string...")
    ret = os.system(f"timeout 4 speaker-test -D hw:{card},0 -c2 -t wav -l1 > /dev/null 2>&1")
    
    if ret == 0:
        print("    ✅ Works with hw: device!")
        print("\n    Note: You may need to update speaker.py to use hw: instead of plughw:")
    else:
        print("    ❌ Still not working")
        print("\n" + "="*60)
        print("  TROUBLESHOOTING NEEDED")
        print("="*60)
        print("\n  Possible issues:")
        print("  1. Speaker not plugged in or powered off")
        print("  2. Wrong USB port (try a different one)")
        print("  3. USB cable issue")
        print("  4. Card number changed (run: aplay -l)")
        print("\n  Next steps:")
        print("  • Check physical connections")
        print("  • Run: aplay -l")
        print("  • Check if speaker has a power switch/volume knob")
        sys.exit(1)
