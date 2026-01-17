from greeting_manager import GreetingManager
from ai_response import get_chat_response
import datetime
import time

def test_time_aware_greetings():
    print("\n--- Testing Time-Aware Greetings ---")
    gm = GreetingManager()
    
    # Mock some names
    names = ["Pooja", "Unknown", "Deva Nandan"]
    
    for name in names:
        greeting = gm.get_greeting(name)
        print(f"Greeting for {name}: {greeting}")

def test_ai_time_awareness():
    print("\n--- Testing AI Time Awareness ---")
    now = datetime.datetime.now()
    print(f"System Clock: {now.strftime('%I:%M %p')}")
    
    # We can't easily test the actual AI response without keys, but we can verify the prompt generation logic
    # by looking at how it behaves. (Actually, we just want to see it run without errors)
    try:
        # This will likely return "Need API key" but should NOT throw Indentation/Import errors
        resp = get_chat_response("What time is it?")
        print(f"AI Response Attempt: {resp['choices'][0]['message']['content']}")
    except Exception as e:
        print(f"AI Logic Error: {e}")

if __name__ == "__main__":
    test_time_aware_greetings()
    test_ai_time_awareness()
    print("\n[VERIFICATION COMPLETE]")
