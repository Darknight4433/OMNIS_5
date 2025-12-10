import speech_recognition as sr

print("Testing microphone...")
r = sr.Recognizer()

try:
    with sr.Microphone() as source:
        print("✅ Microphone found!")
        print("Adjusting for noise...")
        r.adjust_for_ambient_noise(source, duration=1)
        print(f"Energy threshold: {r.energy_threshold}")
        print("\nSay something...")
        audio = r.listen(source, timeout=5, phrase_time_limit=5)
        print("Processing...")
        text = r.recognize_google(audio)
        print(f"You said: {text}")
except sr.WaitTimeoutError:
    print("❌ Timeout - no speech detected")
except Exception as e:
    print(f"❌ Error: {e}")
