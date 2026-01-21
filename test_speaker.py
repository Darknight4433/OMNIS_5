import os
import sys
import time

def test_speaker():
    print("========================================")
    print("Testing Speaker on Card 2 (USB PnP)")
    print("========================================")
    
    # -D plughw:2,0 : Device Card 2, Subdevice 0
    cmd = "speaker-test -D plughw:2,0 -c2 -t wav -l1"
    
    print(f"Running command: {cmd}")
    print("Listen for 'Front Left' and 'Front Right'...")
    
    # Kill pulseaudio briefly if it locks the device
    print("\n[Optional] If this fails, we may need to run 'pulseaudio -k' first.")
    
    ret = os.system(cmd)
    
    if ret == 0:
        print("\n✅ SUCCESS! Speaker is working on Card 2.")
    else:
        print(f"\n❌ Failed. Error code: {ret}")
        print("Try running: pulseaudio -k && speaker-test -D plughw:2,0 -c2 -t wav -l1")

if __name__ == "__main__":
    test_speaker()
