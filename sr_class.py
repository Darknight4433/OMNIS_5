import threading
import time
import os
import ctypes
import random
import speech_recognition as sr

# --- ALSA SILENCER ---
# This prevents the massive log spam from ALSA/PortAudio
ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p)
def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

try:
    asound = ctypes.cdll.LoadLibrary('libasound.so.2')
    asound.snd_lib_error_set_handler(c_error_handler)
except:
    pass
# ---------------------

from speaker import GTTSThread, is_speaking
from ai_response import get_chat_response, get_chat_response_stream
from school_data import get_school_answer_enhanced
import shared_state
from register_face import register_name


class SpeechRecognitionThread(threading.Thread):
    def __init__(self, speaker: GTTSThread):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.speaker = speaker
        self.verbose = True
        self.conversation_active = False
        self.is_listening = False  # New flag for UI
        self.microphone = None
        self.conversation_timeout = 15
        env_wake = os.environ.get('WAKE_WORDS')
        if env_wake:
            self.wake_words = [w.strip().lower() for w in env_wake.split(',') if w.strip()]
        else:
            self.wake_words = ['omnis', 'hello', 'hey', 'amaze', 'thomas', 'promise', 'homeless', 'harness', 'almonds', 'omni']
        self.recognizer = sr.Recognizer()
        # SUPER SENSITIVITY SETTINGS
        self.recognizer.energy_threshold = 400
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15 # Better damping for noise
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 1.0  # More patient
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5 


    def _open_microphone(self) -> bool:
        # Debug: List all microphones
        print("\nSearching for microphones...")
        try:
            mics = sr.Microphone.list_microphone_names()
            for i, name in enumerate(mics):
                print(f"  [{i}] {name}")
        except:
            print("  (Could not list microphones)")

        # On Windows, using default (index=None) is usually best.
        # On Pi, we might need specific indices.
        indices_to_try = [None] # None = System Default
        
        # Add index 1, 0, 2 just in case
        for i in range(len(mics) if 'mics' in locals() else 3):
             if i not in indices_to_try: indices_to_try.append(i)

        # Common sample rates to try for Raspberry Pi / ALSA
        sample_rates = [16000, 44100, 48000, None]

        for idx in indices_to_try:
            for rate in sample_rates:
                try:
                    name = "Default" if idx is None else str(idx)
                    rate_str = f" @ {rate}Hz" if rate else " (Default Rate)"
                    print(f"[Microphone] Trying index {name}{rate_str}...")

                    # Force 16000Hz chunking for better recognition
                    self.microphone = sr.Microphone(device_index=idx, sample_rate=16000 if rate is None else rate, chunk_size=1024)

                    # Calibration
                    # Duration 1.0 is more stable than 0.5
                    with self.microphone as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=1.0)

                    print(f"✅ Mic Connected on Index {name}{rate_str}")
                    return True
                except Exception as e:
                    # print(f"   Failed index {idx} rate {rate}: {e}")
                    continue

        print("❌ Could not find any working microphone.")
        return False

    def run(self) -> None:
        print("\n" + "=" * 50)
        print("🎤 VOICE RECOGNITION STARTED")
        print("=" * 50)
        print("Say 'OMNIS' or 'HELLO' followed by your question")
        print("=" * 50 + "\n")

        while not self.stop_event.is_set() and not self._open_microphone():
            time.sleep(1)

        while not self.stop_event.is_set():
            try:
                # 1. Wait if speaking BEFORE opening the mic
                while is_speaking() and not self.stop_event.is_set():
                    # Reduced poll time from 0.5 to 0.1 for better responsiveness
                    time.sleep(0.1)
                
                # Small protective delay so it doesn't hear the end of its own voice
                if not self.stop_event.is_set():
                    time.sleep(0.6)
                    # Force a higher threshold briefly to clear any echo bias
                    # Reduced from 1500 to 300 to avoid being 'deaf'
                    self.recognizer.energy_threshold = max(self.recognizer.energy_threshold, 300)

                with self.microphone as source:
                    # Only adjust for noise if we aren't already in conversation
                    # or do it quickly to avoid missing the user
                    if not self.conversation_active:
                        # Only adjust if energy threshold is too low or not set
                        if self.recognizer.energy_threshold < 300:
                            print("🔊 Adjusting for ambient noise...")
                            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                            print(f"   (Auto-capping high noise: {self.recognizer.energy_threshold} -> 2000)")
                            self.recognizer.energy_threshold = 2000
                        
                        # Set minimum threshold higher to ignore background
                        if self.recognizer.energy_threshold < 300:
                             self.recognizer.energy_threshold = 300
                        print(f"   Noise level: {self.recognizer.energy_threshold}\n")

                    if self.conversation_active:
                        print("👂 Listening (conversation mode)...")
                    else:
                        print("👂 Listening for 'OMNIS'...")
                    
                    self.is_listening = True # Flag on
                    # shared_state.is_listening = True

                    try:
                        # Play a tiny start-listening blip (ALSA default)
                        os.system("aplay -q /usr/share/sounds/alsa/Front_Left.wav --duration=0.1 > /dev/null 2>&1")
                    except: pass

                    try:
                        # Double check speaker just before listening
                        if is_speaking():
                            continue

                        # Dynamic energy adjustment helps in noisy environments
                        audio_data = self.recognizer.listen(
                            source, 
                            timeout=5, 
                            phrase_time_limit=15
                        )
                        self.is_listening = False # Stopped listening, start processing
                        # shared_state.is_listening = False

                        # Skip processing if we started speaking while listening (rare but possible)
                        if is_speaking():
                            print("🔇 Discarding audio (speaker started)")
                            continue

                        print("🔄 Processing audio...")
                        text = self.recognizer.recognize_google(audio_data)
                        print(f"📝 Heard: '{text}'")
                        shared_state.last_user_text = text # Update UI
                        
                        # Fix common mishearings of "Omnis"
                        text_lower = text.lower()
                        text_lower = text_lower.replace("omni's", "omnis").replace("omni", "omnis").replace("omens", "omnis").replace("honest", "omnis")
                        
                        if getattr(shared_state, 'awaiting_name', False):
                            name_spoken = text.strip()
                            greetings = {'hello', 'hi', 'hey', 'thanks', 'thank you'}
                            norm = name_spoken.lower().strip()
                            if not name_spoken or norm in greetings or len(''.join(ch for ch in norm if ch.isalpha())) < 2:
                                self.speaker.speak("I didn't catch a name.")
                                shared_state.awaiting_name = False
                                shared_state.awaiting_encoding = None
                                shared_state.awaiting_face_image = None
                                continue
                            enc = getattr(shared_state, 'awaiting_encoding', None)
                            img = getattr(shared_state, 'awaiting_face_image', None)
                            ok = register_name(name_spoken, enc, img)
                            if ok:
                                self.speaker.speak(f"Thanks {name_spoken}, I will remember you.")
                            else:
                                self.speaker.speak(f"Sorry, I couldn't save your name.")
                            shared_state.awaiting_name = False
                            shared_state.awaiting_encoding = None
                            shared_state.awaiting_face_image = None
                            continue

                        tokens = text_lower.split()
                        
                        if self.conversation_active:
                            has_wake_word = False
                        else:
                            has_wake_word = any(w in tokens for w in self.wake_words)

                        if has_wake_word or self.conversation_active:
                            if has_wake_word:
                                 # Standard wake word response (unless we are silencing)
                                 pass 

                            question = text_lower
                            for w in self.wake_words:
                                question = question.replace(w, "")
                            question = question.strip()
                            
                            # --- VOICE COMMANDS ---
                            
                            # 1. SILENCE / STOP
                            if any(x in question for x in ["silence", "silent", "stop talking", "shut up", "hush"]):
                                print("\n🛑 SILENCE COMMAND DETECTED")
                                self.speaker.stop() # Stop current thread? Or just queue?
                                # We need a way to clear the queue in speaker.py really.
                                # For now, we just don't reply and reset state.
                                self.conversation_active = False 
                                # Maybe a quick ACK?
                                # self.speaker.speak("Ok.")
                                continue
                                
                            # 2. WHO IS HERE?
                            if any(x in question for x in ["who is here", "who are inside", "detect people", "guess me", "who am i"]):
                                people = getattr(shared_state, 'detected_people', [])
                                if not people:
                                    self.speaker.speak("I don't see anyone right now.")
                                else:
                                    # Filter out 'Unknown'
                                    knowns = [p for p in people if p != "Unknown"]
                                    unknown_count = people.count("Unknown")
                                    
                                    response_parts = []
                                    if knowns:
                                        names = ", ".join(knowns)
                                        response_parts.append(f"I can see {names}.")
                                    if unknown_count > 0:
                                        response_parts.append(f"and {unknown_count} unknown people.")
                                    
                                    if response_parts:
                                        self.speaker.speak(" ".join(response_parts))
                                    else:
                                        self.speaker.speak("I see some people, but I don't know their names.")
                                continue
                                
                            # 3. RESUME / CONTINUE
                            if any(x in question for x in ["continue", "speak again", "hello silence", "resume"]):
                                self.speaker.speak("Ok, I am listening.")
                                self.conversation_active = True
                                continue

                            # 4. PERSONALITY / EXPERT MODE
                            if any(x in question for x in ["act like", "be a", "expert mode", "become a"]):
                                # Detect persona
                                persona = "default"
                                voice_settings = {"pitch": 50, "speed": 175, "accent": "com"}

                                if "shakespeare" in question:
                                    persona = "William Shakespeare"
                                    voice_settings = {"pitch": 45, "speed": 150, "accent": "co.uk"}
                                elif "scientist" in question or "nasa" in question:
                                    persona = "NASA Scientist"
                                    voice_settings = {"pitch": 55, "speed": 180, "accent": "com"}
                                elif "giant" in question or "deep" in question:
                                    persona = "a friendly Giant"
                                    voice_settings = {"pitch": 25, "speed": 130, "accent": "com.au"}
                                elif "robot" in question or "monotone" in question:
                                    persona = "a hyper-logical robot"
                                    voice_settings = {"pitch": 50, "speed": 220, "accent": "com"}
                                elif "child" in question or "baby" in question:
                                    persona = "a playful child"
                                    voice_settings = {"pitch": 80, "speed": 200, "accent": "com"}
                                
                                if persona != "default":
                                    shared_state.current_personality = persona
                                    shared_state.current_voice_settings = voice_settings
                                    self.speaker.speak(f"Initializing {persona} mode. I am ready.")
                                    continue
                            
                            if any(x in question for x in ["be yourself", "reset personality", "normal mode"]):
                                shared_state.current_personality = "default"
                                shared_state.current_voice_settings = {"pitch": 50, "speed": 160, "accent": "com"}
                                self.speaker.speak("Resetting to default OMNIS personality. How can I help you?")
                                continue


                            if has_wake_word:
                               print("\n✅ WAKE WORD DETECTED!\n")
                               from speaker import speak_offline
                               speak_offline("Yes?") # Instant offline ack
                               self.conversation_active = True

                            
                            if question and len(question) >= 3:
                                print(f"❓ Question: {question}\n")
                                school_ans = get_school_answer_enhanced(question)
                                if school_ans:
                                    print(f"🏫 School Response: {school_ans}\n")
                                    self.speaker.speak(school_ans)
                                else:
                                    print("🤖 Getting AI response...")
                                    
                                    # --- THINKING FILLERS ---
                                    fillers = [
                                        "Hmm, let me think about that...",
                                        "Checking my memory banks...",
                                        "That's an interesting question. Let me see...",
                                        "One moment, I am searching for an answer.",
                                        "Let me check my school knowledge for you.",
                                        "Umm, interesting..."
                                    ]
                                    personality = getattr(shared_state, 'current_personality', 'default')
                                    if personality == "William Shakespeare":
                                         fillers = ["Let me consult the stars...", "A wondrous inquiry...", "Hark, let me ponder upon this..."]
                                    elif personality == "NASA Scientist":
                                         fillers = ["Let me process that through my calculations...", "Running data analysis...", "Analyzing trajectory..."]
                                    
                                    self.speaker.speak(random.choice(fillers))
                                    
                                    active_user = getattr(shared_state, 'active_user', 'Unknown')
                                    
                                    # Use Streaming for MUCH lower latency
                                    full_reply = ""
                                    first_sentence = True
                                    
                                    for sentence in get_chat_response_stream(question, user_id=active_user):
                                        if first_sentence:
                                            print(f"💬 AI Starting: {sentence}")
                                            first_sentence = False
                                        
                                        self.speaker.speak(sentence)
                                        full_reply += sentence + " "
                                        
                                        # Update UI incrementally or at end?
                                        # Incremental is better
                                        shared_state.last_ai_text = full_reply.strip()
                                    
                                    # Success beep
                                    try:
                                        os.system("aplay -q /usr/share/sounds/alsa/Front_Center.wav --duration=0.1 > /dev/null 2>&1")
                                    except: pass

                                    print(f"💬 Full Response to {active_user}: {full_reply.strip()}\n")
                                    # shared_state.last_ai_text = full_reply.strip() # Final update
                                
                                # Reset timeout on successful interaction
                                if 'timeout_count' not in locals(): timeout_count = 0
                                timeout_count = 0
                        else:
                            print("   (No wake word)\n")

                    except sr.WaitTimeoutError:
                        if self.conversation_active:
                            if 'timeout_count' not in locals(): timeout_count = 0
                            timeout_count += 1
                            if timeout_count >= 3:
                                print("⏱️ Timeout - say 'OMNIS' to start again\n")
                                self.conversation_active = False
                                timeout_count = 0
                    except sr.UnknownValueError:
                        print("   (Didn't catch that)\n")
                    except sr.RequestError as ex:
                        print(f"❌ Speech error: {ex}\n")
                    except Exception as e:
                        print(f"❌ Loop Error: {e}")
                        time.sleep(1)
            except Exception as e:
                print(f"❌ Microphone Error: {e}")
                time.sleep(2)
                
    def stop(self):
        self.stop_event.set()
        print("\n🛑 Voice recognition stopped\n")


if __name__ == '__main__':
    pass