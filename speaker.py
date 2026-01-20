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

# ElevenLabs Voice IDs
ELEVEN_VOICE_MAP = {
    "default": "9BWtsMINqrJLrRacOk9x", # Aria
    "William Shakespeare": "5Q0t7uMcjvnagumLfvZi", # Paul (British)
    "NASA Scientist": "pNInz6obpgDQGcFmaJgB", # Adam (Deep/News)
    "a friendly Giant": "FGY2WhTYpPnrIDTdsKH5", # Laura (Deep/Calm) replace if needed
    "a hyper-logical robot": "CwhRBWXzGAHq8TQ4Fs17", # Roger
    "a playful child": "ThT5KcBeYPX3keUQqHPh" # Dorothy (British Child)
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


# ElevenLabs Rotation State
current_eleven_key_index = 0

def generate_elevenlabs_tts(text, filename):
    if not HAS_ELEVEN:
        return False
        
    global current_eleven_key_index
    
    # 1. Gather Keys
    keys = []
    
    # Check env
    env_key = os.environ.get('ELEVENLABS_API_KEY')
    if env_key: keys.append(env_key)
    
    # Check secrets_local / api_keys
    try:
        import secrets_local
        # Single key
        if hasattr(secrets_local, 'ELEVENLABS_API_KEY') and secrets_local.ELEVENLABS_API_KEY:
             if secrets_local.ELEVENLABS_API_KEY not in keys:
                 keys.append(secrets_local.ELEVENLABS_API_KEY)
        # Key List
        if hasattr(secrets_local, 'ELEVENLABS_KEYS'):
            for k in secrets_local.ELEVENLABS_KEYS:
                if k and k not in keys: keys.append(k)
    except ImportError: pass
    
    # Check api_keys.py (if exists)
    try:
        from api_keys import ELEVENLABS_KEYS as EXT_KEYS
        for k in EXT_KEYS:
            if k and k not in keys: keys.append(k)
    except ImportError: pass

    if not keys:
        return False

    attempts = 0
    max_attempts = len(keys)
    
    while attempts < max_attempts:
        key = keys[current_eleven_key_index]
        print(f"ElevenLabs: Using Key #{current_eleven_key_index + 1}")
        
        try:
            client = ElevenLabs(api_key=key)
            persona = getattr(shared_state, 'current_personality', 'default')
            voice_id = ELEVEN_VOICE_MAP.get(persona, ELEVEN_VOICE_MAP["default"])
            
            # Updated for ElevenLabs SDK v1.0+
            audio = client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_turbo_v2",
                output_format="mp3_44100_128",
            )
            save(audio, filename)
            return True
        except Exception as e:
            err_str = str(e).lower()
            if "quota" in err_str or "401" in err_str or "unauthorized" in err_str:
                print(f"⚠️ ElevenLabs Key #{current_eleven_key_index + 1} Failed (Quota/Auth). Rotating...")
                current_eleven_key_index = (current_eleven_key_index + 1) % len(keys)
                attempts += 1
            else:
                print(f"ElevenLabs Error: {e}")
                return False # Non-quota error (network etc), maybe don't rotate?
    
    print("❌ All ElevenLabs keys exhausted.")
    return False

import re

def split_text_to_sentences(text):
    """Splits text into sentences for parallel processing."""
    # Split by . ! ? but try to keep it reasonable
    sentences = re.split(r'(?<=[.!?]) +', text)
    return [s.strip() for s in sentences if s.strip()]

def speak_offline(text):
    """Fast offline TTS using espeak-ng"""
    try:
        v = getattr(shared_state, 'current_voice_settings', {"pitch": 50, "speed": 175})
        pitch = v.get("pitch", 50)
        speed = v.get("speed", 160)
        os.system(f"espeak-ng -s {speed} -p {pitch} '{text}' > /dev/null 2>&1")
        return True
    except:
        return False


class GTTSThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.pending_queue = []    # Text waiting to be generated
        self.playback_queue = []   # Filenames waiting to be played
        self.lock = threading.Lock()
        self.running = True

    def run(self):
        global _global_speaker_active
        
        # Background Generator Loop
        def generator_loop():
            while self.running:
                text_to_gen = None
                self.lock.acquire()
                if self.pending_queue:
                    text_to_gen = self.pending_queue.pop(0)
                self.lock.release()
                
                if text_to_gen:
                    filename = f"speak_{uuid.uuid4()}.mp3"
                    try:
                        # 1. Try ElevenLabs
                        generated = generate_elevenlabs_tts(text_to_gen, filename)
                        
                        # 2. Try Cartesia
                        if not generated:
                            generated = generate_cartesia_tts(text_to_gen, filename)
                        
                        # 3. Fallback to Edge-TTS
                        if not generated:
                            try:
                                asyncio.run(generate_edge_tts(text_to_gen, filename))
                                generated = True
                            except: pass
                            
                        # 4. Fallback to gTTS
                        if not generated:
                            v = getattr(shared_state, 'current_voice_settings', {"accent": "com"})
                            tts = gTTS(text=text_to_gen, lang='en', tld=v.get("accent", "com"))
                            tts.save(filename)
                            generated = True
                        
                        if generated:
                            self.lock.acquire()
                            self.playback_queue.append(filename)
                            self.lock.release()
                    except Exception as e:
                        print(f"Gen Error: {e}")
                else:
                    time.sleep(0.05)

        # Start generator in sub-thread
        gen_thread = threading.Thread(target=generator_loop)
        gen_thread.daemon = True
        gen_thread.start()

        # Main Playback Loop
        while self.running:
            filename_to_play = None
            self.lock.acquire()
            if self.playback_queue:
                filename_to_play = self.playback_queue.pop(0)
            self.lock.release()

            if filename_to_play:
                _global_speaker_active = True
                try:
                    import audio_config
                    card_index = getattr(audio_config, 'SPEAKER_CARD_INDEX', 1)
                    device_str = f"hw:{card_index},0"
                    
                    if os.name != 'nt':
                         os.environ['AUDIODEV'] = device_str
                         os.environ['SDL_PATH_ALSA_DEVICE'] = device_str

                    played = False
                    if os.name != 'nt':
                        try:
                            res = os.system(f"mpg123 -q -a {device_str} {filename_to_play} > /dev/null 2>&1")
                            if res == 0: played = True
                        except: pass

                    if not played:
                        try:
                            if not pygame.mixer.get_init():
                                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
                            pygame.mixer.music.load(filename_to_play)
                            pygame.mixer.music.play()
                            while pygame.mixer.music.get_busy() and not _stop_requested:
                                time.sleep(0.05)
                            if _stop_requested: pygame.mixer.music.stop()
                            if hasattr(pygame.mixer.music, 'unload'):
                                pygame.mixer.music.unload()
                        except Exception as e:
                            print(f"Pygame Play Error: {e}")

                    if os.path.exists(filename_to_play):
                        try: os.remove(filename_to_play)
                        except: pass
                except Exception as e:
                    print(f"Playback Error: {e}")
                finally:
                    # Don't reset _global_speaker_active yet if more is coming
                    pass
            else:
                # If nothing to play, check if we are still generating
                self.lock.acquire()
                if not self.pending_queue and not self.playback_queue:
                    _global_speaker_active = False
                self.lock.release()
                time.sleep(0.1)

    def speak(self, text):
        # Semantic splitting
        if len(text) > 120:
            sentences = split_text_to_sentences(text)
            self.lock.acquire()
            self.pending_queue.extend(sentences)
            self.lock.release()
        else:
            self.lock.acquire()
            self.pending_queue.append(text)
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
