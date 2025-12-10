import threading
import time
import os
import speech_recognition as sr

from speaker import GTTSThread, is_speaking
from ai_response import get_chat_response
from school_data import get_school_answer_enhanced
import shared_state
from register_face import register_name


class SpeechRecognitionThread(threading.Thread):
    def __init__(self, speaker: GTTSThread):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()  # Event to signal stopping the thread
        self.speaker = speaker
        self.verbose = True  # Enable verbose logging
        self.conversation_active = False  # Conversation mode flag
        self.microphone = None  # Initialize microphone as None
        self.conversation_timeout = 15  # Timeout for conversation
        # Support multiple wake words; default is 'omnis' and 'hello'
        # You can add more by setting WAKE_WORDS environment variable (comma-separated)
        env_wake = os.environ.get('WAKE_WORDS')
        if env_wake:
            self.wake_words = [w.strip().lower() for w in env_wake.split(',') if w.strip()]
        else:
            self.wake_words = ['omnis', 'hello']
        self.recognizer = sr.Recognizer()  # Create a recognizer object
        # Don't set fixed threshold - let dynamic_energy_threshold auto-adjust

    def _open_microphone(self) -> bool:
        """Attempt to open the microphone and assign it to self.microphone.

        Returns True if microphone was opened, False otherwise.
        Prints a helpful message if no microphone is found or permissions blocked.
        """
        try:
            if self.microphone is None:
                # Attempt to instantiate the Microphone object
                self.microphone = sr.Microphone()
            return True
        except Exception as e:
            # Common errors: OSError when device missing, or permission errors
            print(f"[Microphone] Could not open microphone: {e}")
            print("Please ensure your microphone is connected and your OS has granted microphone permissions to Python.")
            print("On Windows: Settings → Privacy → Microphone. On Raspberry Pi: check audio device and driver.")
            return False

    def run(self) -> None:
        # Configure recognizer behavior
        self.recognizer.dynamic_energy_threshold = True

        if self.verbose:
            print("\n" + "=" * 50)
            print("🎤 VOICE RECOGNITION STARTED")
            print("=" * 50)
            print("Say 'OMNIS' followed by your question")
            print("Example: 'OMNIS, what is the weather?'")
            print("=" * 50 + "\n")

        # Wait until microphone can be opened
        while not self.stop_event.is_set() and not self._open_microphone():
            time.sleep(1)

        # Main listening loop
        while not self.stop_event.is_set():
            try:
                with self.microphone as source:
                    if self.verbose:
                        print("🔊 Adjusting for ambient noise... (Please wait)")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    if self.verbose:
                        print(f"   Noise level set to: {self.recognizer.energy_threshold}\n")

                    timeout_count = 0
                    while not self.stop_event.is_set():
                        if self.verbose:
                            if self.conversation_active:
                                print("👂 Listening (conversation mode)...")
                            else:
                                print("👂 Listening for 'OMNIS'...")

                        try:
                            audio_data = self.recognizer.listen(source, timeout=2, phrase_time_limit=4)

                            if self.verbose:
                                print("🔄 Processing audio...")

                            text = self.recognizer.recognize_google(audio_data)
                            if self.verbose:
                                print(f"📝 Heard: '{text}'")

                            # If the system is awaiting a name, treat this utterance as the name
                            if getattr(shared_state, 'awaiting_name', False):
                                name_spoken = text.strip()
                                # Reject common greetings or very short tokens to avoid accidental registration
                                greetings = {'hello', 'hi', 'hey', 'thanks', 'thank you'}
                                norm = name_spoken.lower().strip()
                                if not name_spoken or norm in greetings or len(''.join(ch for ch in norm if ch.isalpha())) < 2:
                                    # Don't register; give a quiet response and clear the awaiting flag
                                    print(f"[Register] Ignored unlikely name input: '{name_spoken}'")
                                    self.speaker.speak("I didn't catch a name. If you'd like to register, say 'Omnis, remember me as <your name>'")
                                    shared_state.awaiting_name = False
                                    shared_state.awaiting_encoding = None
                                    shared_state.awaiting_face_image = None
                                    # Skip normal processing for this turn
                                    continue

                                # Otherwise, proceed to register
                                print(f"[Register] Heard name: '{name_spoken}' - registering...")
                                enc = getattr(shared_state, 'awaiting_encoding', None)
                                img = getattr(shared_state, 'awaiting_face_image', None)
                                ok = register_name(name_spoken, enc, img)
                                if ok:
                                    self.speaker.speak(f"Thanks {name_spoken}, I will remember you.")
                                else:
                                    self.speaker.speak("Sorry, I couldn't save your name. Try again later.")
                                # Clear state after attempt
                                shared_state.awaiting_name = False
                                shared_state.awaiting_encoding = None
                                shared_state.awaiting_face_image = None
                                # Skip the normal question handling for this turn
                                continue

                            text_lower = text.lower()
                            tokens = text_lower.split()
                            
                            # In conversation mode, don't treat casual greetings as wake words
                            # Only check for wake words if NOT in conversation mode
                            if self.conversation_active:
                                has_wake_word = False  # Ignore wake words during conversation
                            else:
                                has_wake_word = any(w in tokens for w in self.wake_words)

                            if has_wake_word or self.conversation_active:
                                if has_wake_word:
                                    print("\n" + "=" * 50)
                                    print("✅ WAKE WORD DETECTED!")
                                    print("=" * 50 + "\n")
                                    self.speaker.speak("Yes, how can I help you?")
                                    self.conversation_active = True
                                else:
                                    print("\n💬 Follow-up question (no wake word needed)\n")

                                # Remove any wake word tokens from the captured text
                                question = text_lower
                                for w in self.wake_words:
                                    question = question.replace(w, "")
                                question = question.strip()
                                if question:
                                    print(f"❓ Question: {question}\n")
                                    if len(question.strip()) >= 3:
                                        print("🏫 Checking School Database...")
                                        school_ans = get_school_answer_enhanced(question)
                                        if school_ans:
                                            print(f"\n🏫 School Response: {school_ans}\n")
                                            print("🔊 Generating speech...")
                                            self.speaker.speak(school_ans)
                                        else:
                                            print("🤖 Getting AI response...")
                                            resp = get_chat_response(question)
                                            if isinstance(resp, dict) and 'choices' in resp:
                                                answer = resp['choices'][0]['message']['content']
                                                print(f"\n💬 AI Response: {answer}\n")
                                                print("🔊 Generating speech...")
                                                self.speaker.speak(answer)
                                            else:
                                                error_msg = resp.get('error', 'Unknown error') if isinstance(resp, dict) else str(resp)
                                                print(f"❌ Error: {error_msg}")
                                                if 'Gemini' in error_msg or 'not configured' in error_msg:
                                                    self.speaker.speak("Sorry, I cannot answer questions because the API is not configured.")
                                                else:
                                                    self.speaker.speak("Sorry, I couldn't process that question.")
                                    else:
                                        print(f"❓ Question too vague: '{question}'\n")
                                        self.speaker.speak("Could you please ask me a specific question? For example, ask about school rules, dress code, or fees.")

                                    print("💬 Ask another question (no wake word needed)\n")
                                    timeout_count = 0
                                else:
                                    if self.verbose:
                                        print("⏳ Waiting for your question...")
                            else:
                                if self.verbose:
                                    print("   (No wake word detected)\n")

                        except sr.WaitTimeoutError:
                            if self.conversation_active:
                                timeout_count += 1
                                if timeout_count >= 3:
                                    print("⏱️  Listening timeout - say 'OMNIS' to start again\n")
                                    self.conversation_active = False
                                    timeout_count = 0
                        except sr.UnknownValueError:
                            if self.verbose:
                                print("   (Didn't catch that)\n")
                        except sr.RequestError as ex:
                            print(f"❌ Speech recognition error: {ex}")
                            print("   Check your internet connection\n")
                        except Exception as e:
                            print(f"❌ Unexpected error: {e}")
                            print("   Pausing before retry...\n")
                            time.sleep(1)
            except Exception as e:
                print(f"❌ Critical Microphone Error: {e}")
                print("   Please check your microphone settings.")
            
    def stop(self):
        self.stop_event.set()
        if self.verbose:
            print("\n🛑 Voice recognition stopped\n")


if __name__ == '__main__':
    pass
