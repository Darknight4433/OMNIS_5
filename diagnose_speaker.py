import os
import time
from gtts import gTTS

print("="*50)
print("🔊 HARDWARE SPEAKER DIAGNOSTIC")
print("="*50)

def test_device(device_name, description):
    print(f"\nTesting {description} ({device_name})...")
    filename = f"test_{device_name.replace(':', '_').replace(',', '_')}.mp3"
    try:
        tts = gTTS(text=f"Testing {description}", lang='en')
        tts.save(filename)
        
        # Try several common playback commands
        # 1. mpg321 (common on Pi)
        exit_code = os.system(f"mpg321 -a {device_name} -q {filename}")
        if exit_code == 0:
            print(f"✅ Success with mpg321 on {device_name}")
            return True
            
        # 2. aplay (standard ALSA)
        # Note: aplay usually needs WAV, but let's try just listing devices first
        print(f"❌ Failed {device_name} with mpg321")
    except Exception as e:
        print(f"⚠️ Error testing {device_name}: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)
    return False

print("\n--- Listing Audio Devices (aplay -l) ---")
os.system("aplay -l")

print("\n--- Diagnostic Tests ---")
# Test common Pi audio targets
test_device("hw:0,0", "Default/HDMI Audio")
test_device("plughw:1,0", "USB Audio (Card 1)")
test_device("pulse", "PulseAudio System")
test_device("default", "System Default")

print("\n" + "="*50)
print("If you heard NO sound above:")
print("1. Check if speakers are plugged in and powered on.")
print("2. Run 'alsamixer' and ensure volume is not muted (press F6 to select card).")
print("3. Try running: 'aplay /usr/share/sounds/alsa/Front_Center.wav'")
print("="*50)
