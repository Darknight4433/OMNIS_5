import shared_state
from ai_response import get_chat_response
import time

def test_advanced_interaction(persona, query):
    print(f"\n--- TESTING PERSONA: {persona} ---")
    shared_state.current_personality = persona
    
    print(f"User Query: {query}")
    
    # Verify the AI response includes human-like fillers/tone if possible
    # (Requires API key, otherwise just checking for errors)
    try:
        response = get_chat_response(query)
        text = response['choices'][0]['message']['content']
        print(f"AI Response with Prosody: {text}")
        return text
    except Exception as e:
        print(f"AI Error: {e}")
        return None

if __name__ == "__main__":
    # Test 1: Default with fillers
    test_advanced_interaction("default", "Tell me about your day.")
    
    # Test 2: Shakespeare with elegant tone
    test_advanced_interaction("William Shakespeare", "What is the meaning of life?")
    
    # Test 3: Giant with deep voice mapping
    test_advanced_interaction("a friendly Giant", "Can you help me climb this hill?")
    
    print("\n[VERIFICATION COMPLETE] Check if responses contain 'um', 'well', or self-corrections.")
