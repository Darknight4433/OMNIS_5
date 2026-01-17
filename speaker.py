import os
import threading
import time
import uuid
import pygame
from gtts import gTTS

# Shared state to check if speaker is active
_global_speaker_active = False

def is_speaking():
    return _global_speaker_active

import shared_state

def speak_offline(text):
    """Fast offline TTS using espeak-ng"""
    try:
        # Get settings from shared_state
        v = getattr(shared_state, 'current_voice_settings', {"pitch": 50, "speed": 175})
        pitch = v.get("pitch", 50)
        speed = v.get("speed", 160)
        
        # Use espeak-ng for instant feedback
        os.system(f"espeak-ng -s {speed} -p {pitch} '{text}' > /dev/null 2>&1")
        return True
    except:
        return False

class GTTSThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = []
        self.lock = threading.Lock()
        self.running = True

    def run(self):
        global _global_speaker_active
        while self.running:
            text_to_speak = None
            
            self.lock.acquire()
            if self.queue:
                text_to_speak = self.queue.pop(0)
            self.lock.release()

            if text_to_speak:
                _global_speaker_active = True
                try:
                    # Global stop flag
                    global _stop_requested
                    
                    # Fetch voice settings
                    v = getattr(shared_state, 'current_voice_settings', {"accent": "com"})
                    tld = v.get("accent", "com")

                    # SPEED OPTIMIZATION: Use offline TTS for short common phrases
                    # This makes greetings and basic ACKs instant.
                    short_phrases = ["yes?", "ok.", "hello!", "hi.", "welcome."]
                    text_lower = text_to_speak.lower().strip()
                    
                    if len(text_to_speak) < 25 or any(p in text_lower for p in short_phrases):
                        if speak_offline(text_to_speak):
                             _global_speaker_active = False # Reset immediately if offline speak handled it
                             continue # Skip the rest of the online TTS process

                    # 1. Generate Audio file (High Quality for AI answers)
                    filename = f"speak_{uuid.uuid4()}.mp3"
                    tts = gTTS(text=text_to_speak, lang='en', tld=tld)
                    tts.save(filename)

                    # 2. Play Audio (Cross Platform)
                    # Load configuration if it exists
                    try:
                        import audio_config
                        card_index = getattr(audio_config, 'SPEAKER_CARD_INDEX', 1)
                    except ImportError:
                        card_index = 1

                    device_str = f"hw:{card_index},0"
                    
                    # For Raspberry Pi USB speakers
                    if os.name != 'nt':
                         os.environ['AUDIODEV'] = device_str
                         os.environ['SDL_PATH_ALSA_DEVICE'] = device_str
                         os.environ['SDL_ALSA_DEVICE'] = device_str

                    # Try mpg123 first on Linux if available (more reliable for MP3 on Pi)
                    played = False
                    if os.name != 'nt':
                        try:
                            # Try to use mpg123 which handles card selection well
                            res = os.system(f"mpg123 -q -a {device_str} {filename} > /dev/null 2>&1")
                            if res == 0:
                                played = True
                        except:
                            pass

                    if not played:
                        try:
                            # Re-initialize mixer if needed
                            if not pygame.mixer.get_init():
                                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
                            
                            pygame.mixer.music.load(filename)
                            pygame.mixer.music.play()
                            
                            while pygame.mixer.music.get_busy() and not _stop_requested:
                                time.sleep(0.1)
                            
                            if _stop_requested:
                                pygame.mixer.music.stop()
                                print("Speaker: Playback interrupted.")

                            try:
                                if hasattr(pygame.mixer.music, 'unload'):
                                    pygame.mixer.music.unload()
                            except:
                                pass
                        except Exception as e:
                            print(f"Pygame Audio Error: {e}")
                    
                    # Cleanup
                    if os.path.exists(filename):
                        try:
                            os.remove(filename)
                        except:
                            pass

                except Exception as e:
                    print(f"Speaker Error: {e}")
                finally:
                    _stop_requested = False # Reset stop request after processing
                    _global_speaker_active = False
            else:
                time.sleep(0.1)

    def speak(self, text):
        self.lock.acquire()
        self.queue.append(text)
        self.lock.release()

    def stop(self):
        self.running = False

# Global helper for main.py
_global_speaker_thread = None

def init_speaker_thread():
    global _global_speaker_thread
    if _global_speaker_thread is None:
        _global_speaker_thread = GTTSThread()
        _global_speaker_thread.start()
    return _global_speaker_thread

def stop_speech():
    """Request speaking to stop immediately."""
    global _stop_requested
    _stop_requested = True
    print("Speaker: Stop requested.")

def speak(text):
    """Global speak function called by main.py"""
    global _stop_requested
    _stop_requested = False # Reset stop request when a new speech is initiated
    s = init_speaker_thread()
    s.speak(text)

def is_speaking():
    """Global check if anything is being spoken."""
    return any(t.name == "GTTSThread" and t.is_alive() for t in threading.enumerate())
