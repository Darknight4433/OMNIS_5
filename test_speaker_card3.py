import os
import subprocess
import re

def test_speaker():
    print("========================================")
    print("      OMNIS Audio Diagnostic Tool")
    print("========================================")
    
    # 1. List cards
    print("\n[1] Checking available audio cards...")
    os.system("aplay -l")
    
    # 2. Try various device strings for Card 3
    # Error 524 often means the device is busy or format not supported by that specific string
    test_strings = [
        "plughw:3,0",
        "sysdefault:CARD=3",
        "hw:3,0",
        "dmix:CARD=3"
    ]
    
    print("\n[2] Testing different connection strings for Card 3...")
    
    found_working = False
    for ds in test_strings:
        print(f"\n--- Testing: {ds} ---")
        # -l 1: play once, -t wav: use voice, -c 2: stereo
        cmd = f"speaker-test -D {ds} -c2 -t wav -l1"
        ret = os.system(f"timeout 4 {cmd}")
        
        if ret == 0:
            print(f"✅ SUCCESS with {ds}!")
            found_working = ds
            break
        else:
            print(f"❌ Failed with {ds} (Return code: {ret})")

    if found_working:
        print("\n" + "="*40)
        print(f"RECOMMENDED SETTING: {found_working}")
        print("="*40)
        
        # Proactively update audio_config if we found a better string
        if "sysdefault" in found_working:
             print("Note: You might need to update speaker.py to use sysdefault instead of plughw.")
    else:
        print("\n❌ All Card 3 tests failed.")
        print("Possible reasons:")
        print("1. Card 3 is actually not the correct index (Check aplay -l above).")
        print("2. Another program (PulseAudio?) is locking the device.")
        print("3. The USB device is not getting enough power.")
        print("\nTry running: fuser -v /dev/snd/*")

if __name__ == "__main__":
    test_speaker()
