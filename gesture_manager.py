import cv2
import numpy as np
try:
    import mediapipe as mp
    HAS_MEDIAPIPE = True
except ImportError:
    HAS_MEDIAPIPE = False
    print("⚠️ Warning: mediapipe not found. Gesture recognition will be disabled.")

class GestureManager:
    def __init__(self):
        self.enabled = HAS_MEDIAPIPE
        if self.enabled:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
            self.mp_draw = mp.solutions.drawing_utils
        
        # Gesture states
        self.current_gesture = None
        self.last_gesture_time = 0

    def detect_gesture(self, frame):
        """
        Detects hand gestures in the given frame.
        Returns: gesture_name (str) or None
        """
        if not self.enabled:
            return None
            
        results = self.hands.process(frame)
        gesture = None

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # 1. Open Palm (Stop) - All fingers extended
                if self._is_open_palm(hand_landmarks):
                    gesture = "STOP"
                # 2. Thumbs Up (Like)
                elif self._is_thumbs_up(hand_landmarks):
                    gesture = "THUMBS_UP"
                # 3. Thumbs Down (Dislike)
                elif self._is_thumbs_down(hand_landmarks):
                    gesture = "THUMBS_DOWN"
                
                # Optional: draw landmarks for debugging
                # self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        self.current_gesture = gesture
        return gesture

    def _is_open_palm(self, landmarks):
        # Index, Middle, Ring, Pinky tips are all above their respective PIP joints
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        return all(landmarks.landmark[t].y < landmarks.landmark[p].y for t, p in zip(tips, pips))

    def _is_thumbs_up(self, landmarks):
        # Thumb tip is above all other finger tips and thumb IP joint
        thumb_tip = landmarks.landmark[4]
        thumb_ip = landmarks.landmark[3]
        other_tips = [8, 12, 16, 20]
        return thumb_tip.y < thumb_ip.y and all(thumb_tip.y < landmarks.landmark[ot].y for ot in other_tips)

    def _is_thumbs_down(self, landmarks):
        # Thumb tip is below all other finger tips and thumb IP joint
        thumb_tip = landmarks.landmark[4]
        thumb_ip = landmarks.landmark[3]
        other_tips = [8, 12, 16, 20]
        return thumb_tip.y > thumb_ip.y and all(thumb_tip.y > landmarks.landmark[ot].y for ot in other_tips)

if __name__ == "__main__":
    # Test with camera
    cap = cv2.VideoCapture(0)
    gm = GestureManager()
    while True:
        ret, frame = cap.read()
        if not ret: break
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        g = gm.detect_gesture(rgb_frame)
        if g:
            cv2.putText(frame, g, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Gesture Test", frame)
        if cv2.waitKey(1) == ord('q'): break
    cap.release()
    cv2.destroyAllWindows()
