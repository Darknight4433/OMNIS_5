import os
import re
import threading
import time
import requests
import warnings
import datetime
import shared_state

# Suppress annoying deprecated warning from old SDK
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*google.generativeai.*")

# Fix for gRPC fork/poll error on Raspberry Pi
os.environ["GRPC_POLL_STRATEGY"] = "poll"

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from memory_manager import MemoryManager

# --- CONFIGURATION ---
MAX_TOKENS = 400  # Increased for fuller responses (was 300)
TEMPERATURE = 0.7 
SYSTEM_PROMPT = (
    "You are OMNIS, a friendly and lifelike school robot from MGM Model School. "
    "Give detailed but concise answers (typically 3-5 sentences). "
    "Be helpful, empathetic, and professional. "
    "Never start your response with 'AI:' or 'OMNIS:'. "
    "Be direct and natural."
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
    # 1. Check for Key List (New Method)
    if hasattr(secrets_local, 'GEMINI_KEYS'):
        for k in secrets_local.GEMINI_KEYS:
            if k and k not in API_KEYS: API_KEYS.append(k)
            
    # 2. Check for Single Key (Legacy Method)
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

    # HARD FALLBACK: Use offline school knowledge
    print("\n⚠️ All Gemini keys exhausted. Switching to OFFLINE mode.")
    try:
        from school_data import get_school_response
        offline_response = get_school_response(payload)
        if offline_response and offline_response != "I don't have that information.":
            return {'choices': [{'message': {'content': offline_response}}]}
    except Exception as e:
        print(f"Offline fallback error: {e}")
    
    return {'choices': [{'message': {'content': "I'm currently in offline mode, but I'm still here to help with school information. Try asking about MGM Model School!"}}]}

def get_chat_response_stream(payload: str, user_id: str = "Unknown"):
    """Yields AI response parts (sentences) using Gemini Streaming."""
    global current_key_index
    
    if not API_KEYS:
        yield "I'm in offline mode. Ask me about MGM Model School!"
        return

    # Reuse context logic (Memory context is needed here too)
    history = memory.get_recent_history(user_id)
    facts = memory.get_user_facts(user_id)
    
    history_context = ""
    if history:
        history_context = "\nRecent Conversation:\n"
        for u, a in history: history_context += f"User: {u}\nAI: {a}\n"
    
    facts_context = ""
    if facts:
        facts_context = "\nKnown facts about this user:\n"
        for k, v in facts.items(): facts_context += f"- {k}: {v}\n"
    
    personality = getattr(shared_state, 'current_personality', 'default')
    persona_prompt = f" Current Personality/Role: {personality}. Adopt this persona's tone, vocabulary, and style." if personality != "default" else ""
    
    now = datetime.datetime.now()
    time_context = f" Time: {now.strftime('%I:%M %p')}. Date: {now.strftime('%A, %B %d, %Y')}. User Mood: {getattr(shared_state, 'active_user_mood', 'Neutral')}."

    enhanced_system_prompt = f"{SYSTEM_PROMPT}{persona_prompt}{time_context}\n{facts_context}\nYou are talking to {user_id}."
    full_prompt = f"{enhanced_system_prompt}\n{history_context}\nUser: {payload}"

    models_to_try_base = [
        'models/gemini-1.5-flash',
        'models/gemini-1.5-flash-8b',
        'models/gemini-2.0-flash',
        'models/gemini-1.5-pro',
        'models/gemini-1.0-pro-latest',
        'models/gemini-pro'
    ]
    
    max_retries = min(2, len(API_KEYS))  # Try max 2 keys, then fail fast
    retries = 0
    full_text = ""
    
    while retries < max_retries:
        key = API_KEYS[current_key_index]
        success = False

        # 1. Automatic model discovery for this specific key
        discovered_raw = []
        try:
            genai.configure(api_key=key)
            discovered_raw = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        except Exception:
            pass

        # 2. Build the trial list
        candidates = list(models_to_try_base)
        for d in discovered_raw:
            # Add full name and short name
            if d not in candidates: candidates.append(d)
            short = d.split('/')[-1]
            if short not in candidates: candidates.append(short)

        # 3. Filter and Prioritize
        # Flash is the king of free tier quota
        flash_models = [m for m in candidates if 'flash' in m.lower() and 'research' not in m.lower()]
        pro_models = [m for m in candidates if 'pro' in m.lower() and m not in flash_models and 'research' not in m.lower()]
        others = [m for m in candidates if m not in flash_models and m not in pro_models]
        
        final_models = flash_models + pro_models + others
        
        # Final cleanup: No duplicates, no research/thinking/exp unless necessary
        ready_to_try = []
        seen = set()
        for m in final_models:
            m_low = m.lower()
            if m in seen: continue
            # Avoid experimental/research models on first pass as they are often 429-0-limit
            if ('research' in m_low or 'thinking' in m_low or 'exp' in m_low) and retries < max_retries - 1:
                continue
            ready_to_try.append(m)
            seen.add(m)

        if retries == 0:
            print(f"   [Debug] Models to try: {ready_to_try[:5]}...")

        for model_name in ready_to_try:
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel(model_name)
                
                print(f"   [Model {model_name}] Trying...")
                
                # Try Streaming First
                response = model.generate_content(
                    full_prompt,
                    stream=True,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=MAX_TOKENS,
                        temperature=TEMPERATURE,
                    )
                )
                
                chunk_received = False
                sentence_buffer = ""
                for chunk in response:
                    chunk_received = True
                    try:
                        if not chunk.text: continue
                        text = chunk.text
                    except ValueError: continue
                        
                    full_text += text
                    sentence_buffer += text
                    
                    if any(term in sentence_buffer for term in [". ", "! ", "? ", "\n"]):
                        parts = re.split(r'(?<=[.!?\n]) ', sentence_buffer)
                        if len(parts) > 1:
                            for p in parts[:-1]:
                                p_clean = re.sub(r'^(\s*AI\s*:?|\s*OMNIS\s*:?)+', '', p, flags=re.IGNORECASE).strip()
                                if p_clean: yield p_clean
                            sentence_buffer = parts[-1]
                
                # If streaming worked, we are done
                if chunk_received:
                    if sentence_buffer.strip():
                        p_clean = re.sub(r'^(\s*AI\s*:?|\s*OMNIS\s*:?)+', '', sentence_buffer, flags=re.IGNORECASE).strip()
                        if p_clean: yield p_clean
                    success = True
                    break

                # --- FALLBACK: Try Non-Streaming if Stream gave nothing ---
                print(f"   [Model {model_name}] Stream empty, trying non-streaming...")
                response = model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=MAX_TOKENS,
                        temperature=TEMPERATURE,
                    )
                )
                if response.text:
                    full_text = response.text
                    clean_res = re.sub(r'^(\s*AI\s*:?|\s*OMNIS\s*:?)+', '', full_text, flags=re.IGNORECASE).strip()
                    # Yield sentences from the full block
                    for s in re.split(r'(?<=[.!?\n]) ', clean_res):
                        if s.strip(): yield s.strip()
                    success = True
                    break

            except Exception as e:
                err_str = str(e).lower()
                print(f"   [Model {model_name}] Error: {err_str}")

                
                if "quota" in err_str or "429" in err_str:
                    # Key quota reached - stop trying models with this key
                    break 
                elif "not found" in err_str or "not_found" in err_str or "invalid" in err_str:
                    # Specific model not available for this key, try next model
                    continue 
                else: 
                    # Unexpected error (permissions, network, etc)
                    break
        
        if success:
            # --- SAVE TO MEMORY ---
            clean_full = full_text.replace('*', '').replace('#', '').strip()
            clean_full = re.sub(r'^(\s*AI\s*:?|\s*OMNIS\s*:?)+', '', clean_full, flags=re.IGNORECASE).strip()
            memory.add_conversation(user_id, payload, clean_full)
            return

        # Advance key
        print(f"⚠️ Key #{current_key_index + 1} exhausted or failed. Rotating...")
        current_key_index = (current_key_index + 1) % len(API_KEYS)
        retries += 1


    
    
    # HARD FALLBACK for Streaming: Try offline school knowledge
    print("\n⚠️ All Gemini keys exhausted in stream. Trying OFFLINE mode.")
    try:
        from school_data import get_school_response
        offline_response = get_school_response(payload)
        if offline_response and offline_response != "I don't have that information.":
            yield offline_response
            return
    except Exception as e:
        print(f"Offline fallback error: {e}")
    
    yield "I'm currently in offline mode, but I'm still here to help with school information. Try asking about MGM Model School!"

if __name__ == '__main__':
    # Test Streaming
    print("--- TESTING STREAMING AI RESPONSE ---")
    for chunk in get_chat_response_stream("Tell me a 1-sentence joke."):
        print(f"STREAM: {chunk}")
    print("--- DONE ---")
