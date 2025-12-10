import os
import pickle
import cv2
import numpy as np

ENCODE_FILE = 'encoded_file.p'
FACES_DIR = 'images/faces'

def _safe_name(name: str) -> str:
    # Create a filesystem-friendly uppercase name
    s = name.strip()
    s = s.replace('\n',' ').replace('\r',' ')
    s = '_'.join(s.split())
    return s.upper()

def register_name(name: str, encoding, face_image=None):
    """Register `name` for the provided face encoding and optional image.

    - Appends the encoding and name to `encoded_file.p`.
    - Saves `face_image` to `images/faces/<NAME>.jpg` if provided.
    Returns True on success.
    """
    if encoding is None:
        print("[register_face] No encoding provided; aborting registration")
        return False

    os.makedirs(FACES_DIR, exist_ok=True)
    person = _safe_name(name)

    # Persist the face image if available
    if face_image is not None:
        img_path = os.path.join(FACES_DIR, f"{person}.jpg")
        try:
            cv2.imwrite(img_path, face_image)
        except Exception as e:
            print(f"[register_face] Failed to write face image: {e}")

    # Load existing encodings (if any), append and write back atomically
    try:
        if os.path.exists(ENCODE_FILE):
            with open(ENCODE_FILE, 'rb') as f:
                data = pickle.load(f)
            encode_list_known, studentIds = data
        else:
            encode_list_known, studentIds = [], []

        # Append
        encode_list_known.append(encoding)
        studentIds.append(person)

        # Write to temp file and replace
        tmp = ENCODE_FILE + '.tmp'
        with open(tmp, 'wb') as f:
            pickle.dump((encode_list_known, studentIds), f)
        os.replace(tmp, ENCODE_FILE)
        print(f"[register_face] Registered {person} (encodings={len(studentIds)})")
        return True
    except Exception as e:
        print(f"[register_face] Error saving encoding: {e}")
        return False
