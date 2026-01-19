import os
import threading
import time
import uuid
import pygame
import asyncio
import edge_tts
from gtts import gTTS
try:
    from cartesia import Cartesia
    HAS_CARTESIA = True
except ImportError:
    HAS_CARTESIA = False

# Shared state to check if speaker is active
_global_speaker_active = False
_stop_requested = False

def is_speaking():
    return _global_speaker_active

import shared_state

# Voice Mapping for Personalities
VOICE_MAP = {
    "default": "en-US-GuyNeural",
    "William Shakespeare": "en-GB-SoniaNeural",
    "NASA Scientist": "en-US-ChristopherNeural",
    "a friendly Giant": "en-AU-WilliamNeural",
    "a hyper-logical robot": "en-US-SteffanNeural",
    "a playful child": "en-US-AnaNeural"
}

# Cartesia Voice IDs (Sonic 2.0)
CARTESIA_VOICE_MAP = {
    "default": "3b554273-4299-48b9-9aaf-eefd438e3941", # Indian Lady
    "William Shakespeare": "71a7ad14-091c-4e8e-a314-022ece01c121", # British Reading Lady
    "NASA Scientist": "d46abd1d-2d02-43e8-819f-51fb652c1c61", # Newsman
    "a friendly Giant": "6a16c1f4-462b-44de-998d-ccdaa4125a0a", # Friendly Brazilian (Deep)
    "a hyper-logical robot": "79f8b5fb-2cc8-479a-80df-29f7a7cf1a3e", # Nonfiction Man
    "a playful child": "2ee87190-8f84-4925-97da-e52547f9462c" # Child
}

def get_voice():
    persona = getattr(shared_state, 'current_personality', 'default')
    return VOICE_MAP.get(persona, VOICE_MAP["default"])

async def generate_edge_tts(text, filename):
    voice = get_voice()
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

def generate_cartesia_tts(text, filename):
    if not HAS_CARTESIA:
        return False
    try:
        # Check for key in secrets_local or env
        api_key = os.environ.get('CARTESIA_API_KEY')
        if not api_key:
            try:
                import secrets_local
                api_key = getattr(secrets_local, 'CARTESIA_API_KEY', None)
            except ImportError: pass
        
        if not api_key:
            return False

        client = Cartesia(api_key=api_key)
        persona = getattr(shared_state, 'current_personality', 'default')
        voice_id = CARTESIA_VOICE_MAP.get(persona, CARTESIA_VOICE_MAP["default"])
        
        data = client.tts.bytes(
            model_id="sonic-2",
            transcript=text,
            voice_id=voice_id,
            output_format={
                "container": "mp3",
                "bit_rate": 128000,
                "sample_rate": 44100,
            },
        )
        with open(filename, "wb") as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"Cartesia TTS Error: {e}")
        return False

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
                    
                    # SPEED OPTIMIZATION...
                    short_phrases = ["yes?", "ok.", "hello!", "hi.", "welcome."]
                    text_lower = text_to_speak.lower().strip()
                    
                    if len(text_to_speak) < 25 or any(p in text_lower for p in short_phrases):
                        if speak_offline(text_to_speak):
                             _global_speaker_active = False 
                             continue 

                    filename = f"speak_{uuid.uuid4()}.mp3"
                    
                    # 1. Try Cartesia Sonic 2.0 (Premium)
                    generated = generate_cartesia_tts(text_to_speak, filename)
                    
                    # 2. Fallback to Edge-TTS (Neural)
                    if not generated:
                        try:
                            asyncio.run(generate_edge_tts(text_to_speak, filename))
                            generated = True
                        except Exception as e:
                            print(f"Edge-TTS failed: {e}")

                    # 3. Last fallback to gTTS
                    if not generated:
                        print("Falling back to gTTS...")
                        v = getattr(shared_state, 'current_voice_settings', {"accent": "com"})
                        tld = v.get("accent", "com")
                        tts = gTTS(text=text_to_speak, lang='en', tld=tld)
                        tts.save(filename)

                    # 2. Play Audio (Cross Platform)
                    try:
                        import audio_config
                        card_index = getattr(audio_config, 'SPEAKER_CARD_INDEX', 1)
                    except ImportError:
                        card_index = 1

                    device_str = f"hw:{card_index},0"
                    
                    if os.name != 'nt':
                         os.environ['AUDIODEV'] = device_str
                         os.environ['SDL_PATH_ALSA_DEVICE'] = device_str
                         os.environ['SDL_ALSA_DEVICE'] = device_str

                    played = False
                    if os.name != 'nt':
                        try:
                            res = os.system(f"mpg123 -q -a {device_str} {filename} > /dev/null 2>&1")
                            if res == 0:
                                played = True
                        except:
                            pass

                    if not played:
                        try:
                            if not pygame.mixer.get_init():
                                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
                            
                            pygame.mixer.music.load(filename)
                            pygame.mixer.music.play()
                            
                            while pygame.mixer.music.get_busy() and not _stop_requested:
                                time.sleep(0.1)
                            
                            if _stop_requested:
                                pygame.mixer.music.stop()

                            try:
                                if hasattr(pygame.mixer.music, 'unload'):
                                    pygame.mixer.music.unload()
                            except:
                                pass
                        except Exception as e:
                            print(f"Pygame Audio Error: {e}")
                    
                    if os.path.exists(filename):
                        try:
                            os.remove(filename)
                        except:
                            pass

                except Exception as e:
                    print(f"Speaker Error: {e}")
                finally:
                    _stop_requested = False 
                    _global_speaker_active = False
            else:
                time.sleep(0.1)

    def speak(self, text):
        self.lock.acquire()
        self.queue.append(text)
        self.lock.release()

    def stop(self):
        self.running = False

# Global helpers
_global_speaker_thread = None

def init_speaker_thread():
    global _global_speaker_thread
    if _global_speaker_thread is None:
        _global_speaker_thread = GTTSThread()
        _global_speaker_thread.start()
    return _global_speaker_thread

def stop_speech():
    global _stop_requested
    _stop_requested = True

def speak(text):
    global _stop_requested
    _stop_requested = False 
    s = init_speaker_thread()
    s.speak(text)

def is_speaking():
    return _global_speaker_active
