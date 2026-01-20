import os
import google.generativeai as genai
import shared_state
import time
import datetime

# Fix for gRPC fork/poll error on Raspberry Pi
os.environ["GRPC_POLL_STRATEGY"] = "poll"

# --- CONFIGURATION ---
MAX_TOKENS = 300  # Increased for fuller responses (was 150)
TEMPERATURE = 0.7 
SYSTEM_PROMPT = (
    "You are OMNIS, a friendly and lifelike school robot from MGM Model School. "
    "Keep answers conversational, short (2-3 sentences), and helpful. "
    "Never start your response with 'AI:' or 'OMNIS:'. "
    "Avoid starting sentences with 'Um' or 'Well' unless necessary. "
    "Be natural."
)

# --- API KEY ROTATION MANAGER ---
try:
    from api_keys import API_KEYS
except ImportError:
    API_KEYS = []

# Fallback: Check env var or legacy secrets
env_key = os.environ.get('GEMINI_KEY')
if env_key and env_key not in API_KEYS:
    API_KEYS.insert(0, env_key)

try:
    import secrets_local
    legacy_key = getattr(secrets_local, 'GEMINI_KEY', None)
    if legacy_key and legacy_key not in API_KEYS:
        API_KEYS.append(legacy_key)
except: pass

current_key_index = 0

def configure_next_key() -> bool:
    """Rotates to the next available API key. Returns True if successful."""
    global current_key_index
    
    if not API_KEYS:
        print("ERROR: No API Keys available!")
        return False
        
    attempts = 0
    while attempts < len(API_KEYS):
        key = API_KEYS[current_key_index]
        try:
            print(f"KEY: Switching to API Key #{current_key_index + 1}...")
            genai.configure(api_key=key)
            return True
        except Exception as e:
            print(f"   Key #{current_key_index + 1} failed setup: {e}")
            
        # Rotate index
        current_key_index = (current_key_index + 1) % len(API_KEYS)
        attempts += 1
            
    return False

# Initial configuration
if API_KEYS:
    configure_next_key()
    print(f"SUCCESS: Gemini Configured with {len(API_KEYS)} keys available.")
else:
    print("ERROR: No Gemini Keys found. AI response will fail.")


from memory_manager import MemoryManager

# Initialize Memory Manager
memory = MemoryManager()

def get_chat_response(payload: str, user_id: str = "Unknown"):
    """Get AI response using Google Gemini with Key Rotation and Memory"""
    global current_key_index
    
    if not API_KEYS:
        return {"choices": [{"message": {"content": "I need an API key to think."}}]}

    # --- MEMORY INTEGRATION ---
    history = memory.get_recent_history(user_id)
    facts = memory.get_user_facts(user_id)
    
    # Format history for prompt
    history_context = ""
    if history:
        history_context = "\nRecent Conversation:\n"
        for u, a in history:
            history_context += f"User: {u}\nAI: {a}\n"
    
    # Format facts for prompt
    facts_context = ""
    if facts:
        facts_context = "\nKnown facts about this user:\n"
        for k, v in facts.items():
            facts_context += f"- {k}: {v}\n"
    
    # Enhanced System Prompt with memory, personality, and TIME awareness
    personality = getattr(shared_state, 'current_personality', 'default')
    persona_prompt = ""
    if personality != "default":
        persona_prompt = f" Current Personality/Role: {personality}. Adopt this persona's tone, vocabulary, and style in your response."

    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    day_str = now.strftime("%A, %B %d, %Y")
    mood = getattr(shared_state, 'active_user_mood', 'Neutral')
    time_context = f" Current Time: {time_str}. Current Date: {day_str}. User Mood: {mood}."

    enhanced_system_prompt = (
        f"{SYSTEM_PROMPT}{persona_prompt}{time_context}\n"
        f"{facts_context}\n"
        f"You are talking to {user_id}."
    )

    # 1. Preferred models (from your diagnostic)
    models_to_try = [
        'gemini-2.0-flash',
        'gemini-2.5-flash',
        'gemini-2.0-flash-001',
        'gemini-1.5-flash',
    ]
    
    # 2. Add automatic discovery (In case names change)
    try:
        available = [m.name.split('/')[-1] for m in genai.list_models() 
                    if 'generateContent' in m.supported_generation_methods]
        for m in available:
            if m not in models_to_try:
                models_to_try.append(m)
    except: pass

    max_retries = len(API_KEYS) 
    retries = 0
    
    while retries < max_retries:
        content = None
        should_rotate_key = False
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                # Include history in the prompt
                full_prompt = f"{enhanced_system_prompt}\n{history_context}\nUser: {payload}"

                response = model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=MAX_TOKENS,
                        temperature=TEMPERATURE,
                    )
                )
                
                if hasattr(response, 'text') and response.text:
                    content = response.text.strip()
                elif hasattr(response, 'parts'):
                    content = response.parts[0].text.strip()
                elif response.candidates:
                    content = response.candidates[0].content.parts[0].text.strip()

                # Clean up any "AI:" or "OMNIS:" prefixes
                import re
                if content:
                    # Aggressively remove any combination of "AI:" "AI" "OMNIS:" at the start
                    content = re.sub(r'^(\s*AI\s*:?|\s*OMNIS\s*:?)+', '', content, flags=re.IGNORECASE).strip()
                
                if content: break 

            except Exception as e:
                err_str = str(e).lower()
                if "429" in err_str or "quota" in err_str:
                    if "limit: 0" in err_str:
                        continue 
                    print(f"WARNING: Key #{current_key_index + 1} quota reached. Rotating...")
                    should_rotate_key = True
                    break 
                continue

        if content:
            clean_text = content.replace('*', '').replace('#', '').replace('**', '')
            
            # --- SAVE TO MEMORY ---
            
            # Check for explicit memory triggers
            payload_lower = payload.lower()
            permanent_memory = False
            memory_triggers = ["remember this", "keep in mind", "remember forever", "remember for ever", "don't forget this"]
            
            if any(trigger in payload_lower for trigger in memory_triggers):
                permanent_memory = True
                print("🧠 Long-term memory triggered for this interaction.")

            memory.add_conversation(user_id, payload, clean_text, permanent=permanent_memory)
            
            # Simple heuristic to extract facts (Heuristic: "My favorite X is Y")
            if "my favorite" in payload.lower() and "is" in payload.lower():
                try:
                    parts = payload.lower().split("my favorite")[1].split("is")
                    key = parts[0].strip()
                    val = parts[1].strip().rstrip(".!?")
                    memory.store_fact(user_id, key, val)
                    print(f"INFO: Learned a fact: {key} = {val}")
                except: pass

            return {'choices': [{'message': {'content': clean_text}}]}
            
        if should_rotate_key:
            current_key_index = (current_key_index + 1) % len(API_KEYS)
            configure_next_key()
            retries += 1
            continue
        else:
            print(f"WARNING: Key #{current_key_index + 1} failed all models. Rotating...")
            current_key_index = (current_key_index + 1) % len(API_KEYS)
            configure_next_key()
            retries += 1
            continue

    return {'choices': [{'message': {'content': "My daily brain power is exhausted. Please check my API keys in a few minutes."}}]}


    return {'choices': [{'message': {'content': "My daily brain power is exhausted. Please check my API keys in a few minutes."}}]}

if __name__ == '__main__':
    # Test
    print(get_chat_response("What is the capital of India?"))
