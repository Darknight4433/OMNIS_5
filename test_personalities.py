import shared_state
from ai_response import get_chat_response
import time

def test_personality(name, settings, query):
    print(f"\n--- TESTING PERSONA: {name} ---")
    shared_state.current_personality = name
    shared_state.current_voice_settings = settings
    
    print(f"Voice Settings: {settings}")
    print(f"User Query: {query}")
    
    response = get_chat_response(query)
    text = response['choices'][0]['message']['content']
    print(f"AI Response: {text}")
    return text

if __name__ == "__main__":
    # 1. Default
    test_personality("default", {"pitch": 50, "speed": 175, "accent": "com"}, "How are you?")
    
    # 2. Shakespeare
    test_personality("William Shakespeare", {"pitch": 45, "speed": 150, "accent": "co.uk"}, "How are you?")
    
    # 3. Giant (Deep Voice)
    test_personality("a friendly Giant", {"pitch": 25, "speed": 130, "accent": "com.au"}, "Tell me a joke.")
    
    # 4. Scientist
    test_personality("NASA Scientist", {"pitch": 55, "speed": 180, "accent": "com"}, "What is the moon?")
    
    print("\n[VERIFICATION COMPLETE] Check the response tone for each persona.")
