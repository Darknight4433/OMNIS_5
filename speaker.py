import os
import threading
import time
import uuid
import pygame
import asyncio
import edge_tts
import re
from gtts import gTTS

try:
    from cartesia import Cartesia
    HAS_CARTESIA = True
except ImportError:
    HAS_CARTESIA = False

try:
    from elevenlabs import save
    from elevenlabs.client import ElevenLabs
    HAS_ELEVEN = True
except ImportError:
    HAS_ELEVEN = False

# Shared state to check if speaker is active
_global_speaker_active = False
_stop_requested = False

def is_speaking():
    return _global_speaker_active

import shared_state

# Voice Mappings
VOICE_MAP = {
    "default": "en-US-GuyNeural",
    "William Shakespeare": "en-GB-SoniaNeural",
    "NASA Scientist": "en-US-ChristopherNeural",
    "a friendly Giant": "en-AU-WilliamNeural",
    "a hyper-logical robot": "en-US-SteffanNeural",
    "a playful child": "en-US-AnaNeural"
}

CARTESIA_VOICE_MAP = {
    "default": "3b554273-4299-48b9-9aaf-eefd438e3941",
    "William Shakespeare": "71a7ad14-091c-4e8e-a314-022ece01c121",
    "NASA Scientist": "d46abd1d-2d02-43e8-819f-51fb652c1c61",
    "a friendly Giant": "6a16c1f4-462b-44de-998d-ccdaa4125a0a",
    "a hyper-logical robot": "79f8b5fb-2cc8-479a-80df-29f7a7cf1a3e",
    "a playful child": "2ee87190-8f84-4925-97da-e52547f9462c"
}

ELEVEN_VOICE_MAP = {
    "default": "9BWtsMINqrJLrRacOk9x",
    "William Shakespeare": "5Q0t7uMcjvnagumLfvZi",
    "NASA Scientist": "pNInz6obpgDQGcFmaJgB",
    "a friendly Giant": "FGY2WhTYpPnrIDTdsKH5",
    "a hyper-logical robot": "CwhRBWXzGAHq8TQ4Fs17",
    "a playful child": "ThT5KcBeYPX3keUQqHPh"
}

def get_voice():
    persona = getattr(shared_state, 'current_personality', 'default')
    return VOICE_MAP.get(persona, VOICE_MAP["default"])

async def generate_edge_tts(text, filename):
    voice = get_voice()
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

def generate_cartesia_tts(text, filename):
    if not HAS_CARTESIA: return False
    try:
        api_key = os.environ.get('CARTESIA_API_KEY')
        if not api_key:
            try:
                import secrets_local
                api_key = getattr(secrets_local, 'CARTESIA_API_KEY', None)
            except ImportError: pass
        if not api_key: return False
        client = Cartesia(api_key=api_key)
        persona = getattr(shared_state, 'current_personality', 'default')
        voice_id = CARTESIA_VOICE_MAP.get(persona, CARTESIA_VOICE_MAP["default"])
        data = client.tts.bytes(model_id="sonic-2", transcript=text, voice_id=voice_id, output_format={"container": "mp3", "bit_rate": 128000, "sample_rate": 44100})
        with open(filename, "wb") as f: f.write(data)
        return True
    except Exception as e:
        print(f"Cartesia Error: {e}")
        return False

current_eleven_key_index = 0

def generate_elevenlabs_tts(text, filename):
    if not HAS_ELEVEN: return False
    global current_eleven_key_index
    keys = []
    env_key = os.environ.get('ELEVENLABS_API_KEY')
    if env_key: keys.append(env_key)
    try:
        import secrets_local
        if hasattr(secrets_local, 'ELEVENLABS_KEYS'):
            for k in secrets_local.ELEVENLABS_KEYS:
                if k and k not in keys: keys.append(k)
        elif hasattr(secrets_local, 'ELEVENLABS_API_KEY'):
            keys.append(secrets_local.ELEVENLABS_API_KEY)
    except: pass
    if not keys: return False
    
    attempts = 0
    while attempts < len(keys):
        key = keys[current_eleven_key_index]
        try:
            client = ElevenLabs(api_key=key)
            persona = getattr(shared_state, 'current_personality', 'default')
            voice_id = ELEVEN_VOICE_MAP.get(persona, ELEVEN_VOICE_MAP["default"])
            audio = client.text_to_speech.convert(text=text, voice_id=voice_id, model_id="eleven_turbo_v2")
            save(audio, filename)
            return True
        except Exception as e:
            if "quota" in str(e).lower() or "401" in str(e).lower():
                current_eleven_key_index = (current_eleven_key_index + 1) % len(keys)
                attempts += 1
            else: return False
    return False

def split_text_to_sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.!?\n]) +', text) if s.strip()]

def speak_offline(text):
    try:
        import audio_config
        card_index = getattr(audio_config, 'SPEAKER_CARD_INDEX', 1)
        v = getattr(shared_state, 'current_voice_settings', {"pitch": 50, "speed": 175})
        # Use -a to specify card for espeak-ng
        os.system(f"espeak-ng -a {card_index} -s {v.get('speed', 160)} -p {v.get('pitch', 50)} '{text}' > /dev/null 2>&1")
        return True
    except: return False

class GTTSThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.pending_queue = []
        self.playback_queue = []
        self.is_generating = False
        self.lock = threading.Lock()
        self.running = True

    def run(self):
        global _global_speaker_active
        
        def generator_loop():
            while self.running:
                text_to_gen = None
                self.lock.acquire()
                if self.pending_queue:
                    text_to_gen = self.pending_queue.pop(0)
                    self.is_generating = True
                else:
                    self.is_generating = False
                self.lock.release()
                
                if text_to_gen:
                    fn = f"speak_{uuid.uuid4()}.mp3"
                    try:
                        if not generate_elevenlabs_tts(text_to_gen, fn):
                            if not generate_cartesia_tts(text_to_gen, fn):
                                try: asyncio.run(generate_edge_tts(text_to_gen, fn))
                                except:
                                    v = getattr(shared_state, 'current_voice_settings', {"accent": "com"})
                                    gTTS(text=text_to_gen, lang='en', tld=v.get('accent', 'com')).save(fn)
                        
                        self.lock.acquire()
                        self.playback_queue.append(fn)
                        self.lock.release()
                    except Exception as e: print(f"Gen Error: {e}")
                else: time.sleep(0.05)

        threading.Thread(target=generator_loop, daemon=True).start()

        while self.running:
            fn = None
            self.lock.acquire()
            if self.playback_queue: fn = self.playback_queue.pop(0)
            self.lock.release()

            if fn:
                _global_speaker_active = True
                try:
                    import audio_config
                    card_index = getattr(audio_config, 'SPEAKER_CARD_INDEX', 1)
                    # Using plughw for better compatibility with different sample rates
                    device_str = f"plughw:{card_index},0"
                    
                    played = False
                    if os.name != 'nt':
                        res = os.system(f"mpg123 -q -a {device_str} {fn} > /dev/null 2>&1")
                        if res == 0: played = True

                    if not played:
                        if not pygame.mixer.get_init():
                            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
                        pygame.mixer.music.load(fn)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy() and not _stop_requested: time.sleep(0.05)
                        if _stop_requested: pygame.mixer.music.stop()
                        if hasattr(pygame.mixer.music, 'unload'): pygame.mixer.music.unload()

                    if os.path.exists(fn): os.remove(fn)
                except Exception as e: print(f"Play Error: {e}")
            else:
                self.lock.acquire()
                if not self.pending_queue and not self.playback_queue and not self.is_generating:
                    _global_speaker_active = False
                self.lock.release()
                time.sleep(0.1)

    def speak(self, text):
        global _global_speaker_active
        _global_speaker_active = True
        sentences = split_text_to_sentences(text) if len(text) > 120 else [text]
        self.lock.acquire()
        self.pending_queue.extend(sentences)
        self.lock.release()

    def stop(self):
        global _stop_requested
        _stop_requested = True
        self.lock.acquire()
        self.pending_queue = []
        # We can't easily clear playback queue without deleting files
        self.lock.release()

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
    if _global_speaker_thread: _global_speaker_thread.stop()

def speak(text):
    global _stop_requested
    _stop_requested = False
    init_speaker_thread().speak(text)
