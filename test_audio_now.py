#!/usr/bin/env python3
"""Quick test to verify Card 1 audio output"""

import os
import sys

print("="*50)
print("Testing Card 1 (USB PnP Sound Device)")
print("="*50)

# Test 1: speaker-test
print("\n[Test 1] Running speaker-test on Card 1...")
print("You should hear 'Front Left, Front Right'")
ret = os.system("speaker-test -D plughw:1,0 -c2 -t wav -l1")

if ret == 0:
    print("✅ Speaker test PASSED!")
else:
    print(f"❌ Speaker test FAILED (code: {ret})")
    print("\nTrying to unmute the card...")
    os.system("amixer -c 1 set PCM unmute")
    os.system("amixer -c 1 set PCM 100%")
    os.system("amixer -c 1 set Master unmute 2>/dev/null")
    os.system("amixer -c 1 set Master 100% 2>/dev/null")
    
    print("\nRetrying speaker test...")
    ret = os.system("speaker-test -D plughw:1,0 -c2 -t wav -l1")
    
    if ret == 0:
        print("✅ Speaker test PASSED after unmuting!")
    else:
        print("❌ Still failing. Check if speaker is plugged in and powered on.")
        sys.exit(1)

# Test 2: Test with actual TTS
print("\n[Test 2] Testing with actual audio playback...")
try:
    from gtts import gTTS
    
    test_file = "test_card1.mp3"
    tts = gTTS(text="Audio is now working on card one", lang='en')
    tts.save(test_file)
    
    print("Playing audio with mpg123...")
    ret = os.system(f"mpg123 -q -a plughw:1,0 {test_file}")
    
    if os.path.exists(test_file):
        os.remove(test_file)
    
    if ret == 0:
        print("✅ Audio playback SUCCESSFUL!")
        print("\n" + "="*50)
        print("SUCCESS! Card 1 is working correctly!")
        print("="*50)
        print("\nYour audio_config.py has been updated.")
        print("You can now run OMNIS with: python3 main.py")
    else:
        print(f"❌ Audio playback failed (code: {ret})")
        print("Make sure mpg123 is installed: sudo apt-get install mpg123")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("Make sure gtts is installed: pip3 install gtts")
