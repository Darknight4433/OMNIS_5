"""
Lightweight in-memory shared state for coordination between
the face-detection loop (`main.py`) and the speech thread (`sr_class.py`).

This avoids complex IPC and is fine while the process runs in one interpreter.
"""
from typing import Optional
import numpy as np

# When True, the speech thread should treat the next recognized phrase as a name
awaiting_name: bool = False
# The face encoding (128-d float array) captured for the unknown primary face
awaiting_encoding: Optional[object] = None
# Small RGB image (numpy array) cropped around the unknown face (ready to write)
awaiting_face_image: Optional[object] = None
detected_people = [] # Live list of people currently in frame
active_user: str = "Unknown" # The primary person being interacted with
current_personality: str = "default" # Current persona (e.g., 'Shakespeare', 'NASA Scientist')
active_user_mood: str = "Neutral" # Predicted mood (Happy, Neutral, etc.)
current_voice_settings: dict = {"pitch": 50, "speed": 175, "accent": "com"} # Added for voice modulation

# Interaction State
last_interaction_time: float = 0 # Unix timestamp of last user input or AI speech
last_user_text: str = "" # Final transcribed user sentence
last_ai_text: str = "" # Final AI sentence
is_listening: bool = False # UI hook
is_thinking: bool = False # UI hook
is_speaking: bool = False # UI hook
is_generating: bool = False # Internal generation block
