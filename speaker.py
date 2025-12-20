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
                    # 1. Generate Audio file
                    filename = f"speak_{uuid.uuid4()}.mp3"
                    tts = gTTS(text=text_to_speak, lang='en', tld='com')
                    tts.save(filename)

                    # 2. Play Audio via Digital Pipe (Highest Reliability on Pi)
                    # Use mpg123 with alsa driver for better device control
                    # We use -o alsa to force ALSA instead of libao
                    cmd = f"mpg123 -q -o alsa --device hw:1,0 {filename}"
                    exit_code = os.system(cmd)
                    
                    if exit_code != 0:
                        # Fallback to the original pipe if mpg123 isn't working/custom config
                        os.system(f"mpg321 -q -w - {filename} | aplay -D plughw:1,0 -q")
                    
                    # Cleanup
                    if os.path.exists(filename):
                        os.remove(filename)

                except Exception as e:
                    print(f"Speaker Error: {e}")
                finally:
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

def speak(text):
    """Global speak function called by main.py"""
    s = init_speaker_thread()
    s.speak(text)
