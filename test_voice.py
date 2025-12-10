"""
Test script for microphone and speech recognition
Run this to verify your microphone and voice recognition work
"""
import speech_recognition as sr

print("=" * 50)
print("OMNIS Voice Recognition Test")
print("=" * 50)
print()

# List available microphones
print("Available microphones:")
for index, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"  {index}: {name}")
print()

# Create recognizer
r = sr.Recognizer()

print("Testing microphone...")
print("Please speak after the beep...")
print()

try:
    with sr.Microphone() as source:
        print("🎤 Adjusting for ambient noise... (please be quiet)")
        r.adjust_for_ambient_noise(source, duration=2)
        print("✓ Ready! Speak now...")
        
        audio = r.listen(source, timeout=10, phrase_time_limit=5)
        print("✓ Audio captured! Processing...")
        
        try:
            text = r.recognize_google(audio)
            print()
            print("=" * 50)
            print(f"✅ SUCCESS! You said: '{text}'")
            print("=" * 50)
            print()
            print("Your microphone and speech recognition are working!")
            
            # Test wake word detection
            if "omnis" in text.lower():
                print("🎉 Wake word 'OMNIS' detected!")
            else:
                print("💡 Try saying 'OMNIS' to test wake word detection")
                
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            print("   Try speaking louder and clearer")
        except sr.RequestError as e:
            print(f"❌ Could not request results: {e}")
            print("   Check your internet connection")
            
except sr.WaitTimeoutError:
    print("❌ Timeout - no speech detected")
    print("   Make sure your microphone is working and not muted")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("Test complete!")
input("Press Enter to exit...")
