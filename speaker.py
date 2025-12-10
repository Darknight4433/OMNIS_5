import threading
import time
from pygame import mixer
from gtts import gTTS
import os
import uuid
from collections import deque


class GTTSThread(threading.Thread):
    """Thread-safe TTS worker using a deque and a lock.

    This avoids race conditions when multiple threads call `speak()`.
    """
    def __init__(self):
        super().__init__()
        self.text_queue = deque()
        self.lock = threading.Lock()
        self.is_running = True
        try:
            mixer.init()
        except Exception:
            # If mixer.init fails (e.g., no audio device), continue but log later
            print("⚠️  Warning: pygame.mixer init failed")

    def run(self) -> None:
        while self.is_running:
            text = None
            with self.lock:
                if self.text_queue:
                    text = self.text_queue.popleft()

            if text:
                self._speak_text(text)
            else:
                time.sleep(0.05)

    def _speak_text(self, text: str):
        filename = f"temp_{uuid.uuid4()}.mp3"
        try:
            # Use US English for faster generation (tld='com' is faster than 'co.in')
            tts = gTTS(text=text, lang='en', tld='com', slow=False)
            tts.save(filename)

            mixer.music.load(filename)
            mixer.music.play()
            while mixer.music.get_busy():
                time.sleep(0.05)

            try:
                mixer.music.unload()
            except Exception:
                pass

            time.sleep(0.05)
            if os.path.exists(filename):
                os.remove(filename)
        except Exception as e:
            print(f"⚠️  TTS Error: {e}")
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    pass

    def speak(self, text: str):
        with self.lock:
            self.text_queue.append(text)

    def stop(self):
        self.is_running = False


if __name__ == '__main__':
    pass


# Module-level singleton speaker helpers
_global_speaker = None
_global_lock = threading.Lock()


def _get_speaker():
    global _global_speaker
    with _global_lock:
        if _global_speaker is None:
            _global_speaker = GTTSThread()
            _global_speaker.daemon = True
            try:
                _global_speaker.start()
            except RuntimeError:
                # If the thread was already started or failed, ignore
                pass
        return _global_speaker


def speak(text_or_list):
    """Public speak API: accepts a string or list of strings.

    This lazily starts the background speaker thread and queues text.
    """
    sp = _get_speaker()
    if isinstance(text_or_list, str):
        sp.speak(text_or_list)
    else:
        for t in text_or_list:
            sp.speak(t)


def stop_speaker():
    sp = _global_speaker
    if sp:
        sp.stop()


def is_speaking() -> bool:
    """Return True if something is queued or mixer is currently playing."""
    sp = _global_speaker
    if not sp:
        return False
    
    try:
        busy = mixer.music.get_busy()
    except Exception:
        busy = False
    
    try:
        with sp.lock:
            has_queue = len(sp.text_queue) > 0
            return busy or has_queue
    except Exception:
        return busy