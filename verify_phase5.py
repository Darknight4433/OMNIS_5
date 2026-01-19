import shared_state
from greeting_manager import GreetingManager
from emotion_manager import EmotionManager
from memory_manager import MemoryManager
import time


def test_mood_logic():
    print("\n--- Testing Mood Integration ---")
    shared_state.active_user_mood = "Happy"
    # We can't easily test ai_response without keys here, but we check shared_state
    print(f"Current Mood in State: {shared_state.active_user_mood}")

def test_proactive_greeting():
    print("\n--- Testing Proactive Greeting ---")
    # 1. Add a dummy conversation for a user
    mem = MemoryManager("omnis_memory.db")
    user = "Deva Nandan"
    mem.add_conversation(user, "I am working on a very difficult science project for the exhibition.", "That sounds fascinating! I wish you luck with it.")
    
    # 2. Trigger greeting
    gm = GreetingManager()
    # Mock last greeted to be very old
    gm.last_greeted[user] = 0
    
    greeting = gm.get_greeting(user)
    print(f"OMNIS Proactive Greeting: {greeting}")
    
    if "science project" in greeting.lower():
        print("✅ SUCCESS: OMNIS recalled the conversation topic!")

if __name__ == "__main__":
    test_mood_logic()
    test_proactive_greeting()
    print("\n[VERIFICATION COMPLETE] Test face tracking and mood manually on the Pi hardware.")
