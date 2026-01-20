import os
import pickle
import cv2
import numpy as np
import cvzone
import face_recognition
import time
from speaker import speak, is_speaking
from sr_class import SpeechRecognitionThread
import shared_state
from greeting_manager import GreetingManager
from head_controller import init_head
from gesture_manager import GestureManager
from gesture_manager import GestureManager
from emotion_manager import EmotionManager
from ui_manager import UIManager
import shared_state

# Adapter for SR thread
class SpeakerAdapter:
    def speak(self, text):
        speak(text)
    def stop(self):
        # Implementation to stop current playback if possible
        # For now, we can just signal the speaker module
        from speaker import stop_speech
        stop_speech()

speaker_adapter = SpeakerAdapter()

# Global Configuration
FACE_MATCH_TOLERANCE = float(os.environ.get('FACE_MATCH_TOLERANCE', '0.50'))
MAX_FACES = int(os.environ.get('FACE_MAX_FACES', '4'))
FRAME_SKIP = 5  # Increased for speed (Process face every 5 frames)
RESIZE_FACTOR = 0.20 # Downscale more (0.20 instead of 0.25)

# Initialize Greeting Manager
greeter = GreetingManager()

# Load Resources
print("Loading Resources...")
try:
    imgBackground = cv2.imread('Resources/background.png')
    folderModePath = 'Resources/Modes'
    imgModeList = [cv2.imread(os.path.join(folderModePath, p)) for p in sorted(os.listdir(folderModePath))]
except Exception as e:
    print(f"Warning: Could not load background/modes: {e}")
    imgBackground = np.zeros((720, 1280, 3), np.uint8) # Fallback black screen
    imgModeList = []

# Load Encodings
print("Loading Encoded File...")
try:
    with open(r'images/encoded_file.p', 'rb') as f:
        encode_list_known_with_ids = pickle.load(f)
    encode_list_known, studentIds = encode_list_known_with_ids
    print(f"Loaded {len(studentIds)} people.")
except Exception as e:
    print(f"Error loading encodings: {e}")
    encode_list_known, studentIds = [], []

# Reset shared state
try:
    shared_state.awaiting_name = False
except:
    pass

def main():
    global imgBackground
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    
    mode_type = 0
    speech_thread = None
    
    # Trackers
    frame_count = 0
    current_faces = []      # Last detected face locations
    current_ids = []        # Last detected face IDs
    
    # Start Voice Listener Immediately (Always-on Assistant)
    print("Starting Voice Assistant...")
    try:
        speech_thread = SpeechRecognitionThread(speaker_adapter)
        speech_thread.daemon = True
        speech_thread.start()
    except Exception as e:
        print(f"Error starting voice: {e}")

    # Initialize Head Controller
    head = init_head()

    # Initialize Recognition Managers
    gesture_man = GestureManager()
    emotion_man = EmotionManager()

    # Initialize UI Manager
    ui = UIManager()
    
    # State tracking for UI
    last_user_text = ""
    last_ai_text = ""
    
    print("Starting OMNIS Main Loop...")
    
    try:
        while True:
            success, img = cap.read()
            if not success or img is None:
                if frame_count % 30 == 0:
                    print("⚠️ Warning: Camera not reading. Check connection.")
                # Create a black placeholder image so the GUI still shows up
                img = np.zeros((480, 640, 3), np.uint8)
                success = True
            
            frame_count += 1
            
            # --- VISION PIPELINE (Optimized) ---
            # Only run heavy Face Recognition every N frames
            if frame_count % FRAME_SKIP == 0:
                imgS = cv2.resize(img, (0, 0), None, RESIZE_FACTOR, RESIZE_FACTOR)
                imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
                
                try:
                    face_locs = face_recognition.face_locations(imgS)
                    # Limit faces to prevent lag
                    if len(face_locs) > MAX_FACES:
                        face_locs = face_locs[:MAX_FACES]
                        
                    if face_locs:
                        face_encs = face_recognition.face_encodings(imgS, face_locs)
                        
                        new_ids = []
                        for encodeFace in face_encs:
                            matches = face_recognition.compare_faces(encode_list_known, encodeFace, tolerance=FACE_MATCH_TOLERANCE)
                            face_dist = face_recognition.face_distance(encode_list_known, encodeFace)
                            
                            match_index = np.argmin(face_dist) if len(face_dist) > 0 else -1
                            
                            if match_index != -1 and matches[match_index]:
                                new_ids.append(studentIds[match_index])
                            else:
                                new_ids.append("Unknown")
                        
                        current_faces = face_locs
                        current_ids = new_ids
                        
                        # --- ACTIVE FACE TRACKING ---
                        # Track the largest face (usually the one closest/primary)
                        # face_locs is in (top, right, bottom, left) format
                        if current_faces:
                            top, right, bottom, left = current_faces[0]
                            cx = (left + right) // 2
                            cy = (top + bottom) // 2
                            # Calculate small frame dimensions
                            sh, sw, _ = imgS.shape
                            head.track_face(cx, cy, frame_w=sw, frame_h=sh)
                            # Sync speaking state for head gestures
                            head.set_speaking(is_speaking())
                        
                        # Update shared state for Voice Commands ("Who is here?")
                        shared_state.detected_people = current_ids
                        # Primary user (first face) for memory context
                        shared_state.active_user = current_ids[0] if current_ids else "Unknown"
                    else:
                        current_faces = []
                        current_ids = []
                        shared_state.detected_people = []
                        shared_state.active_user = "Unknown"
                        
                except Exception as e:
                    print(f"Face Rec Error: {e}")

            # --- GESTURE PIPELINE ---
            if frame_count % 3 == 0: # Check gestures more frequently than faces
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                gesture = gesture_man.detect_gesture(rgb_img)
                if gesture == "STOP" and is_speaking():
                    print("✋ Gesture STOP detected!")
                    from speaker import stop_speech
                    stop_speech()
                elif gesture == "THUMBS_UP" and not is_speaking():
                    # Optional: Quick interaction
                    pass
                
                # --- EMOTION (Mood) PIPELINE ---
                mood = emotion_man.detect_emotion(rgb_img)
                shared_state.active_user_mood = mood

            # --- HEAD TRACKING ---
            if head:
                head.set_speaking(is_speaking())
                if current_faces:
                    # Target the first face detected
                    y1, x2, y2, x1 = current_faces[0]
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    # Note: We pass resized coordinates (relative to RESIZE_FACTOR frame)
                    head.track_face(cx, cy)
            
            # --- DRAWING PIPELINE ---
            try:
                # Paste webcam feed
                imgBackground[162:162+480, 55:55+640] = img
                if imgModeList:
                    imgBackground[44:44+633, 808:808+414] = imgModeList[mode_type]
            except Exception:
                pass # Prevent crash if resize fails or bg image mismatch
            
            detected_person_for_greeting = None
            
            if current_faces:
                # We have faces (either fresh or cached from previous frame)
                for i, (y1, x2, y2, x1) in enumerate(current_faces):
                    # Scale back up (1 / 0.20 = 5)
                    y1, x2, y2, x1 = y1*5, x2*5, y2*5, x1*5
                    person_id = current_ids[i]
                    
                    if person_id != "Unknown":
                        # Known Face
                        mode_type = 1
                        bbox = (55+x1, 162+y1, x2 - x1, y2 - y1)
                        # Replaced with UIManager: imgBackground = cvzone.cornerRect(imgBackground, bbox=bbox, rt=0)
                        ui.draw_face_box(imgBackground, bbox, person_id, is_known=True)
                        
                        # Find the largest/main face to greet
                        detected_person_for_greeting = person_id
                        
                        # UI: Name
                        (w, h), _ = cv2.getTextSize(person_id, cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414 - w) / 2
                        cv2.putText(imgBackground, str(person_id), (808 + int(offset), 445), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                        
                        # UI: Image
                        img_path = f'images/faces/{person_id}.jpg'
                        if os.path.exists(img_path):
                            student_img = cv2.imread(img_path)
                            if student_img is not None:
                                try:
                                    student_img = cv2.resize(student_img, (216, 216))
                                    imgBackground[175:175 + 216, 909:909 + 216] = student_img
                                except: pass
                    
                    else:
                        # Unknown Face
                        mode_type = 0
                        # Replaced with UIManager
                        bbox = (55+x1, 162+y1, x2 - x1, y2 - y1)
                        ui.draw_face_box(imgBackground, bbox, "Unknown", is_known=False)
                        # cv2.rectangle(imgBackground, (55+x1, 162+y1), (55+x2, 162+y2), (0, 0, 255), 2)
                        
            else:
                mode_type = 0


            # --- GREETING PIPELINE ---
            # Don't interrupt if already speaking, listening, or thinking
            is_listening = speech_thread.is_listening if speech_thread else False
            
            if not is_speaking() and not is_listening:
                if detected_person_for_greeting:
                    # Case 1: We found a KNOWN person
                    greeting_text = greeter.get_greeting(detected_person_for_greeting)
                    if greeting_text:
                        print(f"Greeting: {greeting_text}")
                        speak(greeting_text)
                        
                        # Trigger Voice Listener if not active
                        if not (speech_thread and speech_thread.is_alive()):
                            try:
                                speech_thread = SpeechRecognitionThread(speaker_adapter)
                                speech_thread.daemon = True
                                speech_thread.start()
                            except: pass

                elif current_faces:
                    # Case 2: No known person, but FACES are present -> Greet Unknown
                    if greeter.should_greet("Unknown"):
                        msg = greeter.get_unknown_greeting()
                        speak(msg)

            # --- UI UPDATES (Status & Subtitles) ---
            
            # Determine Status
            current_status = "IDLE"
            if is_speaking():
                current_status = "SPEAKING"
            elif speech_thread and speech_thread.is_listening: 
                # Note: We need to expose 'is_listening' in sr_class or infer it
                current_status = "LISTENING"
            
            # Check for new text in shared_state (requires update in sr_class/ai_response to write to shared_state)
            if hasattr(shared_state, 'last_user_text') and shared_state.last_user_text != last_user_text:
                last_user_text = shared_state.last_user_text
                ui.draw_subtitles(imgBackground, user_text=last_user_text)
                
            if hasattr(shared_state, 'last_ai_text') and shared_state.last_ai_text != last_ai_text:
                last_ai_text = shared_state.last_ai_text
                ui.draw_subtitles(imgBackground, ai_text=last_ai_text)
                
            # Draw persistent elements
            ui.draw_status_bar(imgBackground, current_status)
            # Redraw active subtitle if timer is valid
            ui.draw_subtitles(imgBackground) # Calls refresh logic internally


            cv2.imshow("Face Attendance", imgBackground)
            if cv2.waitKey(1) == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        if speech_thread:
            speech_thread.stop()

if __name__ == "__main__":
    main()
