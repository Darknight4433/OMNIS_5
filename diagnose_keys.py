
import os
import google.generativeai as genai
from api_keys import API_KEYS

def diagnose():
    if not API_KEYS:
        print("❌ No keys found in api_keys.py")
        return

    print(f"🔍 Testing {len(API_KEYS)} keys...\n")
    
    # Very safe model
    model_name = 'gemini-1.5-flash'
    
    for i, key in enumerate(API_KEYS):
        print(f"--- Key #{i+1} ---")
        try:
            genai.configure(api_key=key)
            
            # 1. List valid models for this key
            print("📋 Available Models:")
            count = 0
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    print(f"  - {m.name}")
                    count += 1
                if count > 5: break # Only show first 5
            
            # 2. Try a test generation
            model = genai.GenerativeModel('gemini-2.0-flash') 
            response = model.generate_content("Say 'OK'")
            print(f"✅ Status: SUCCESS")
        except Exception as e:
            print(f"❌ Status: FAILED")
            print(f"⚠️ Error: {e}")
        print("")

if __name__ == "__main__":
    diagnose()
