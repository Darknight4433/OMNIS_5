import cv2
import mediapipe as mp
import numpy as np

class EmotionManager:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
    def detect_emotion(self, frame):
        """
        Detects basic emotion (Happy/Neutral) based on mouth landmarks.
        Returns: emotion_name (str)
        """
        results = self.face_mesh.process(frame)
        emotion = "Neutral"

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Landmark 61: Left mouth corner, 291: Right mouth corner
                # Landmark 0: Upper lip center, 17: Lower lip center
                lm = face_landmarks.landmark
                
                # Simple Smile Heuristic: Mouth Width vs Face Width
                # Mouth width
                m_width = abs(lm[61].x - lm[291].x)
                # Face width (approx between ears/cheeks 234 and 454)
                f_width = abs(lm[234].x - lm[454].x)
                
                ratio = m_width / f_width if f_width > 0 else 0
                
                # Heuristic threshold for a smile
                if ratio > 0.40:
                    emotion = "Happy"
                elif ratio < 0.32:
                    # Maybe sad if very small? Or just tight-lipped.
                    # For now, just Neutral.
                    emotion = "Neutral"
                    
        return emotion

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    em = EmotionManager()
    while True:
        ret, frame = cap.read()
        if not ret: break
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        e = em.detect_emotion(rgb_frame)
        cv2.putText(frame, f"Mood: {e}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow("Emotion Test", frame)
        if cv2.waitKey(1) == ord('q'): break
    cap.release()
    cv2.destroyAllWindows()
