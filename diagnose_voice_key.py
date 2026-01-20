
import os
import sys

print("--- OMNIS ElevenLabs Diagnostic ---")

# 1. Check Import
try:
    import elevenlabs
    from elevenlabs.client import ElevenLabs
    print(f"✅ Library 'elevenlabs' imported successfully.")
except ImportError as e:
    print(f"❌ Failed to import 'elevenlabs'. Error: {e}")
    print("   Please run: pip3 install elevenlabs --upgrade")
    sys.exit(1)
except Exception as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

# 2. Check Secrets
keys = []
try:
    import secrets_local
    print("✅ secrets_local.py found.")
    
    # Check List
    if hasattr(secrets_local, 'ELEVENLABS_KEYS'):
        count = len(secrets_local.ELEVENLABS_KEYS)
        print(f"   Found 'ELEVENLABS_KEYS' list with {count} keys.")
        keys.extend(secrets_local.ELEVENLABS_KEYS)
    
    # Check Single
    if hasattr(secrets_local, 'ELEVENLABS_API_KEY'):
        print(f"   Found 'ELEVENLABS_API_KEY' variable.")
        if secrets_local.ELEVENLABS_API_KEY and secrets_local.ELEVENLABS_API_KEY not in keys:
            keys.append(secrets_local.ELEVENLABS_API_KEY)
            
except ImportError:
    print("❌ secrets_local.py NOT found. (Did you copy secrets_template_new.py?)")
    
if not keys:
    print("❌ No API Keys found! Please edit secrets_local.py")
    sys.exit(1)

print(f"ℹ️  Testing with {len(keys)} available keys...")

# 3. Test Generation
voice_id = "9BWtsMINqrJLrRacOk9x" # Aria

for i, key in enumerate(keys):
    masked = key[:4] + "..." + key[-4:] if len(key) > 8 else "INVALID"
    print(f"\n🔑 Testing Key #{i+1} ({masked})...")
    
    try:
        client = ElevenLabs(api_key=key)
        
        # Try a tiny generation
        audio = client.text_to_speech.convert(
            text="Testing voice.",
            voice_id=voice_id,
            model_id="eleven_turbo_v2",
            output_format="mp3_44100_128",
        )
        
        # Iterate generator to force request
        chunk = next(audio) 
        
        print("   ✅ SUCCESS! Audio stream received.")
        print("   (This key works correctly)")
        break # We found a working one
        
    except Exception as e:
        err = str(e)
        if "401" in err or "unauthorized" in err:
             print("   ❌ Auth Error (401). Invalid Key?")
        elif "quota" in err or "429" in err:
             print("   ⚠️ Quota Exceeded (429/Quota). Needed Rotation.")
        else:
             print(f"   ❌ Unknown Error: {e}")

print("\n--- Diagnostic Complete ---")
