import os
import sys
import time

def test_speaker():
    print("========================================")
    print("Testing Speaker on Card 3 (plughw:3,0)")
    print("========================================")
    
    # Command to test stereo sound on card 3 using speaker-test
    # -D plughw:3,0 : Device Card 3, Subdevice 0 (with plug plugin for format conversion)
    # -c2 : 2 Channels
    # -t wav : Play a wav file (voice)
    # -l1 : Loop 1 time
    cmd = "speaker-test -D plughw:3,0 -c2 -t wav -l1"
    
    print(f"Running command: {cmd}")
    print("Listen for 'Front Left' and 'Front Right'...")
    
    # Using timeout to ensure it doesn't get stuck if something is wrong
    # 'timeout' command might not be on all windows/minimal linux, but standard on Pi
    full_cmd = f"timeout 5 {cmd}"
    
    ret = os.system(full_cmd)
    
    if ret == 0:
        print("\n✅ Command executed successfully.")
    else:
        print(f"\n❌ Command failed with return code {ret}.")
        print("Try running manually: speaker-test -D plughw:3,0 -c2 -t wav")

    print("\n========================================")
    print("To use 'espeak' on card 3:")
    print("espeak -a 3 'Hello world, this is card three'")
    print("========================================")

if __name__ == "__main__":
    test_speaker()
