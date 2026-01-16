
import time
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from head_controller import init_head
    
    print("🎯 OMNIS Head Test")
    print("Initializing servos on GPIO 17 (Pan) and 27 (Tilt)...")
    print("(Make sure 'sudo pigpiod' is running!)")
    
    head = init_head()
    time.sleep(1)
    
    print("\n↔️ Testing Pan (Left to Right)...")
    for pos in [1000, 2000, 1500]:
        print(f"  Moving to {pos}")
        head.target_pan = pos
        time.sleep(1.5)
        
    print("\n↕️ Testing Tilt (Up to Down - LIMITED)...")
    for pos in [1300, 1700, 1500]:
        print(f"  Moving to {pos}")
        head.target_tilt = pos
        time.sleep(1.5)
        
    print("\n✅ Servo Test Complete!")
    print("If they didn't move, check your wiring and ensure pigpiod is running.")
    
    head.stop()

except Exception as e:
    print(f"❌ Error during head test: {e}")
