import cv2
import numpy as np
import time

class UIManager:
    def __init__(self):
        # Configuration
        self.font = cv2.FONT_HERSHEY_COMPLEX
        self.text_color = (255, 255, 255)
        self.bg_color = (0, 0, 0)
        self.accent_color = (0, 255, 0) # Green
        
        # Load Status Icons (Fallbacks to shapes if missing)
        self.icons = {}
        self._load_assets()
        
        # Animation State
        self.pulse_phase = 0
        self.last_subtitle = ""
        self.subtitle_timer = 0
        self.SUBTITLE_DURATION = 5 # seconds

    def _load_assets(self):
        # Placeholder for loading UI assets
        # In a real scenario, we would load .png files here
        pass

    def draw_status_bar(self, img, state="IDLE"):
        """
        Draws the system status (Listening, Speaking, etc.)
        State: IDLE, LISTENING, PROCESSING, SPEAKING
        """
        h, w, _ = img.shape
        
        # Status Box (Top Left or embedded)
        # Let's put it in the bottom left corner of the camera feed area (which is at 55, 162 usually)
        # But here we are drawing on the MAIN full image
        
        # Position: Top Right of Camera Feed area? 
        # Camera is usually placed at (55, 162) size (640, 480) -> Ends at (695, 642)
        
        # Let's draw it at the top of the screen overlaid on background
        color = (100, 100, 100)
        text = "IDLE"
        
        if state == "LISTENING":
            color = (0, 255, 255) # Yellow
            text = "Listening..."
            # Pulsing effect calculation
            self.pulse_phase += 0.2
            radius = int(10 + 5 * np.sin(self.pulse_phase))
            cv2.circle(img, (90, 190), radius, color, -1)
            
        elif state == "PROCESSING":
            color = (255, 50, 50) # Blue-ish
            text = "Thinking..."
            
        elif state == "SPEAKING":
            color = (0, 255, 0) # Green
            text = "Speaking..."
            
        # Draw Pills
        cv2.rectangle(img, (55, 130), (250, 160), (30, 30, 30), -1) # Background bar
        cv2.putText(img, text, (65, 153), self.font, 0.7, color, 1)

    def draw_subtitles(self, img, user_text=None, ai_text=None):
        """
        Draws subtitles at the bottom of the camera feed.
        """
        if user_text:
            self.last_subtitle = f"You: {user_text}"
            self.subtitle_timer = time.time() + self.SUBTITLE_DURATION
            
        if ai_text:
            self.last_subtitle = f"OMNIS: {ai_text}"
            self.subtitle_timer = time.time() + self.SUBTITLE_DURATION
            
        # Check expiry
        if time.time() > self.subtitle_timer:
            return # Expired

        # Draw
        text = self.last_subtitle
        (tw, th), _ = cv2.getTextSize(text, self.font, 0.8, 1)
        
        # Center X relative to Camera Feed (Start 55, Width 640 -> Center 375)
        cx = 55 + (640 // 2)
        tx = cx - (tw // 2)
        ty = 162 + 480 - 30 # Bottom of camera feed
        
        # Background for text (Semi-transparent look technically hard in pure OpenCV without overlay)
        # We'll just draw a black box
        padding = 10
        cv2.rectangle(img, (tx - padding, ty - th - padding), (tx + tw + padding, ty + padding), (0, 0, 0), -1)
        cv2.rectangle(img, (tx - padding, ty - th - padding), (tx + tw + padding, ty + padding), (255, 255, 255), 1)
        
        cv2.putText(img, text, (tx, ty), self.font, 0.8, (255, 255, 255), 1)

    def draw_face_box(self, img, bbox, name="Unknown", is_known=False):
        """
        Draws augmented reality face box.
        bbox: (x, y, w, h) relative to the screen, NOT the camera feed crop if possible.
        """
        x, y, w, h = bbox
        color = (0, 255, 0) if is_known else (0, 0, 255)
        
        # Fancy corners (using cv2 lines for a 'tech' look)
        l = 30 # length of corner line
        t = 5  # thickness
        
        # Top Left
        cv2.line(img, (x, y), (x + l, y), color, t)
        cv2.line(img, (x, y), (x, y + l), color, t)
        
        # Top Right
        cv2.line(img, (x + w, y), (x + w - l, y), color, t)
        cv2.line(img, (x + w, y), (x + w, y + l), color, t)
        
        # Bottom Left
        cv2.line(img, (x, y + h), (x + l, y + h), color, t)
        cv2.line(img, (x, y + h), (x, y + h - l), color, t)

        # Bottom Right
        cv2.line(img, (x + w, y + h), (x + w - l, y + h), color, t)
        cv2.line(img, (x + w, y + h), (x + w, y + h - l), color, t)
        
        # Name Tag
        if is_known:
            cv2.rectangle(img, (x, y - 35), (x + w, y), color, -1)
            cv2.putText(img, name, (x + 5, y - 5), self.font, 0.8, (255, 255, 255), 2)
