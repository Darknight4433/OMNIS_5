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
        # Status Box positioning (linked to camera feed at 55, 162)
        base_x, base_y = 55, 130
        
        color = (150, 150, 150)
        text = "IDLE"
        show_pulse = False
        
        if state == "LISTENING":
            color = (0, 255, 255) # Yellow
            text = "LISTENING"
            show_pulse = True
        elif state == "PROCESSING":
            color = (255, 150, 50) # Orange/Blue
            text = "THINKING"
        elif state == "SPEAKING":
            color = (0, 255, 0) # Green
            text = "SPEAKING"

        # Draw pill shadow/background
        cv2.rectangle(img, (base_x, base_y), (base_x + 200, base_y + 30), (20, 20, 20), -1)
        
        # Pulsing dot for listening
        if show_pulse:
            self.pulse_phase += 0.15
            radius = int(6 + 3 * np.sin(self.pulse_phase))
            cv2.circle(img, (base_x + 15, base_y + 15), radius, color, -1)
            text_x = base_x + 35
        else:
            text_x = base_x + 15

        cv2.putText(img, text, (text_x, base_y + 22), self.font, 0.6, color, 1, cv2.LINE_AA)

    def draw_subtitles(self, img, user_text=None, ai_text=None):
        """
        Draws subtitles at the bottom of the camera feed with transparency and clamping.
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

        text = self.last_subtitle
        
        # Overlay parameters
        overlay = img.copy()
        font_scale = 0.7
        thickness = 1 # Thinner stroke for cleaner look
        padding = 10
        
        # Calculate visual bounds (Camera area)
        cam_x, cam_y, cam_w, cam_h = 55, 162, 640, 480
        
        # Get text size
        (tw, th), baseline = cv2.getTextSize(text, self.font, font_scale, thickness)
        
        # Smart Center (Clamp to edges)
        cx = cam_x + (cam_w // 2)
        tx = cx - (tw // 2)
        
        # Clamp Left
        if tx < cam_x + 10: tx = cam_x + 10
        # Clamp Right (if text is too wide, this might push it left, effectively 'right aligning' to the edge)
        if tx + tw > cam_x + cam_w - 10: 
            # If text is REALLY too big, we might need to truncate
            if tw > cam_w - 20:
                # Simple truncation
                while tw > cam_w - 20 and len(text) > 0:
                     text = text[:-1]
                     (tw, th), _ = cv2.getTextSize(text, self.font, font_scale, thickness)
                tx = cam_x + 10
            else:
                tx = cam_x + cam_w - 10 - tw
        
        ty = cam_y + cam_h - 30 # 30 px from bottom of camera frame
        
        # Draw Semi-Transparent Box
        # box coords: (x1, y1), (x2, y2)
        cv2.rectangle(overlay, (tx - padding, ty - th - padding), (tx + tw + padding, ty + padding), (0, 0, 0), -1)
        
        alpha = 0.6
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
        
        # Draw Text
        cv2.putText(img, text, (tx, ty), self.font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

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
