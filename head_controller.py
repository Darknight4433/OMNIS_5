
import os
import time
import threading
import random
try:
    import pigpio
except ImportError:
    pigpio = None

# --- CONFIGURATION ---
PAN_PIN = 17    # Left/Right
TILT_PIN = 27   # Up/Down (Limited)

# Servo Pulse Widths (Typical: 500 to 2500)
# 1500 is usually the center (90 degrees)
PAN_RANGE = (500, 2500)  # 0 to 180 degrees
TILT_RANGE = (1200, 1800) # Restricted range (approx center +/- 30 deg)
CENTER_PWM = 1500

# Smoothing
SMOOTHING = 0.15 # 0 to 1. Closer to 0 is smoother/slower

class HeadController(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        
        # Initialize pigpio
        self.pi = None
        if pigpio:
            self.pi = pigpio.pi()
            if not self.pi.connected:
                print("⚠️ HeadController: pigpio daemon not running! Run 'sudo pigpiod'")
                self.pi = None
        else:
            print("⚠️ HeadController: pigpio module not found. Movement disabled.")

        # State
        self.current_pan = CENTER_PWM
        self.current_tilt = CENTER_PWM
        self.target_pan = CENTER_PWM
        self.target_tilt = CENTER_PWM
        
        self.last_face_time = 0
        self.is_speaking = False
        self.running = True

    def set_speaking(self, status):
        self.is_speaking = status

    def track_face(self, face_center_x, face_center_y, frame_w=160, frame_h=120):
        """
        Adjust targets based on face position in frame.
        Default 160x120 assumes the 0.25 resized frame from main.py
        """
        self.last_face_time = time.time()
        
        # Calculate offsets from center (-1 to 1)
        # Note: Inverted logic for pan/tilt based on standard mounting
        dx = (face_center_x - (frame_w / 2)) / (frame_w / 2)
        dy = (face_center_y - (frame_h / 2)) / (frame_h / 2)

        # Pan move (Left/Right)
        pan_step = dx * 80 # Sensitive adjustment
        self.target_pan -= pan_step
        
        # Tilt move (Up/Down) - dy is positive when face is lower than center
        tilt_step = dy * -60 
        self.target_tilt -= tilt_step

        # Apply Hard Limits
        self.target_pan = max(PAN_RANGE[0], min(PAN_RANGE[1], self.target_pan))
        self.target_tilt = max(TILT_RANGE[0], min(TILT_RANGE[1], self.target_tilt))

    def run(self):
        print("🤖 HeadController: Started movement loop.")
        while self.running:
            now = time.time()
            
            # 1. HANDLE GESTURES (When speaking)
            if self.is_speaking:
                # Add tiny random "breathing" movements
                self.target_pan += random.uniform(-5, 5)
                self.target_tilt += random.uniform(-3, 3)
            
            # 2. HANDLE IDLE SCANNING (No face for 5 seconds)
            elif now - self.last_face_time > 5.0:
                # Slow scan
                if int(now) % 10 == 0:
                    self.target_pan = random.uniform(PAN_RANGE[0] + 300, PAN_RANGE[1] - 300)
                    self.target_tilt = random.uniform(TILT_PWM_CENTER - 100, TILT_PWM_CENTER + 100)

            # 3. INTERPOLATE (Smooth movement)
            self.current_pan += (self.target_pan - self.current_pan) * SMOOTHING
            self.current_tilt += (self.target_tilt - self.current_tilt) * SMOOTHING

            # 4. EXECUTE HARDWARE MOVE
            if self.pi:
                try:
                    self.pi.set_servo_pulsewidth(PAN_PIN, int(self.current_pan))
                    self.pi.set_servo_pulsewidth(TILT_PIN, int(self.current_tilt))
                except:
                    pass
            
            time.sleep(0.02) # 50Hz update rate

    def stop(self):
        self.running = False
        if self.pi:
            self.pi.set_servo_pulsewidth(PAN_PIN, 0) # Release servos
            self.pi.set_servo_pulsewidth(TILT_PIN, 0)
            self.pi.stop()

# Helper for integration
TILT_PWM_CENTER = 1500
head = None

def init_head():
    global head
    if head is None:
        head = HeadController()
        head.start()
    return head
