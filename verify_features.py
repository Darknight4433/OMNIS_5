import os
import time
from ai_response import get_chat_response
from memory_manager import MemoryManager
from speaker import speak, stop_speech, is_speaking

def test_memory():
    print("\n--- Testing Memory ---")
    user_id = "Tester"
    msg = "My favorite color is blue" 
    print(f"Sending: '{msg}'")
    resp = get_chat_response(msg, user_id=user_id)
    print(f"AI: {resp['choices'][0]['message']['content']}")
    
    time.sleep(1)
    
    msg2 = "What is my favorite color?"
    print(f"Sending: '{msg2}'")
    resp2 = get_chat_response(msg2, user_id=user_id)
    answer = resp2['choices'][0]['message']['content']
    print(f"AI: {answer}")
    
    if "blue" in answer.lower():
        print("[PASS] Memory Test Passed!")
    else:
        print("[FAIL] Memory Test Failed (or AI used different wording).")

def test_gestures_logic():
    print("\n--- Testing Gesture Stop Logic ---")
    print("Beginning speech...")
    speak("This is a long sentence that I will try to stop halfway through using the stop command simulation.")
    time.sleep(1)
    print("Simulating gesture stop...")
    stop_speech()
    time.sleep(1)
    if not is_speaking():
        print("[PASS] Gesture Stop Logic Passed!")
    else:
        print("[FAIL] Gesture Stop Logic Failed!")

if __name__ == "__main__":
    test_memory()
    test_gestures_logic()
    print("\nNext: Try running 'python main.py' to test with actual camera and voice!")
