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
        Draws multi-line subtitles at the bottom of the camera feed.
        """
        if user_text:
            self.last_subtitle = f"You: {user_text}"
            self.subtitle_timer = time.time() + self.SUBTITLE_DURATION
            
        if ai_text:
            self.last_subtitle = f"OMNIS: {ai_text}"
            self.subtitle_timer = time.time() + self.SUBTITLE_DURATION
            
        if time.time() > self.subtitle_timer:
            return

        text = self.last_subtitle
        cam_x, cam_y, cam_w, cam_h = 55, 162, 640, 480
        font_scale = 0.65
        thickness = 1
        padding = 10
        max_width = cam_w - (padding * 4)
        
        # --- Multi-line Wrapping Logic ---
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            (tw, th), _ = cv2.getTextSize(test_line, self.font, font_scale, thickness)
            
            if tw <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        
        # Calculate total height for background box
        (tw_sample, th_sample), baseline = cv2.getTextSize("Ay", self.font, font_scale, thickness)
        line_height = th_sample + padding
        total_h = len(lines) * line_height
        
        # Draw from bottom up
        base_ty = cam_y + cam_h - 40
        
        # Create overlay for transparency
        overlay = img.copy()
        
        for i, line in enumerate(reversed(lines)):
            (tw, th), _ = cv2.getTextSize(line, self.font, font_scale, thickness)
            tx = cam_x + (cam_w // 2) - (tw // 2)
            ty = base_ty - (i * line_height)
            
            # Background Rect
            cv2.rectangle(overlay, (tx - padding, ty - th - padding), (tx + tw + padding, ty + padding // 2), (0, 0, 0), -1)
            
        # Apply transparency
        alpha = 0.65
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
        
        # Draw actual text on top
        for i, line in enumerate(reversed(lines)):
            (tw, th), _ = cv2.getTextSize(line, self.font, font_scale, thickness)
            tx = cam_x + (cam_w // 2) - (tw // 2)
            ty = base_ty - (i * line_height)
            cv2.putText(img, line, (tx, ty), self.font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

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
