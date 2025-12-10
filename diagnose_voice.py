"""
Quick Voice Diagnostic
======================
This will help us figure out why voice isn't working.
"""

import speech_recognition as sr
import time

print("="*50)
print("OMNIS VOICE DIAGNOSTIC")
print("="*50)

# Test 1: Microphone Access
print("\n[1/4] Testing microphone access...")
try:
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("✅ Microphone found and accessible")
except Exception as e:
    print(f"❌ FAILED: {e}")
    exit(1)

# Test 2: Ambient Noise
print("\n[2/4] Measuring ambient noise...")
try:
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=2)
        threshold = r.energy_threshold
        print(f"✅ Energy threshold: {threshold}")
        if threshold > 1000:
            print("⚠️  WARNING: Very noisy! Try quieter room.")
        elif threshold < 100:
            print("⚠️  WARNING: Very quiet! Speak louder.")
except Exception as e:
    print(f"❌ FAILED: {e}")

# Test 3: Recording
print("\n[3/4] Testing recording...")
print(">>> Say 'HELLO' now...")
try:
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source, timeout=5, phrase_time_limit=3)
        print("✅ Audio captured")
except sr.WaitTimeoutError:
    print("❌ TIMEOUT: No speech detected")
    print("   - Check if mic is muted")
    print("   - Speak louder")
    exit(1)
except Exception as e:
    print(f"❌ FAILED: {e}")
    exit(1)

# Test 4: Recognition
print("\n[4/4] Testing Google Speech Recognition...")
try:
    text = r.recognize_google(audio)
    print(f"✅ SUCCESS! Heard: '{text}'")
    
    if "omnis" in text.lower() or "omni" in text.lower():
        print("\n🎉 PERFECT! OMNIS wake word detected!")
    else:
        print(f"\n⚠️  You said '{text}', not 'OMNIS'")
        print("   Try saying 'OMNIS' more clearly")
        
except sr.UnknownValueError:
    print("❌ Could not understand audio")
    print("   - Speak more clearly")
    print("   - Reduce background noise")
except sr.RequestError as e:
    print(f"❌ API Error: {e}")
    print("   - Check internet connection")
except Exception as e:
    print(f"❌ FAILED: {e}")

print("\n" + "="*50)
print("Diagnostic complete!")
print("="*50)
