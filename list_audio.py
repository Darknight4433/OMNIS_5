import subprocess
import os

def list_audio_info():
    print("========================================")
    print("      OMNIS Audio Device Auditor")
    print("========================================")
    
    print("\n[1] --- Playback Devices (aplay -l) ---")
    try:
        result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
        print(result.stdout if result.stdout else "No playback devices found.")
    except Exception as e:
        print(f"Error running aplay: {e}")

    print("\n[2] --- Record/Mic Devices (arecord -l) ---")
    try:
        result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
        print(result.stdout if result.stdout else "No recording devices found.")
    except Exception as e:
        print(f"Error running arecord: {e}")

    print("\n[3] --- Card Details (cat /proc/asound/cards) ---")
    try:
        with open('/proc/asound/cards', 'r') as f:
            print(f.read())
    except Exception as e:
        print(f"Error reading /proc/asound/cards: {e}")

    print("\n[4] --- PulseAudio Status (pactl info) ---")
    try:
        result = subprocess.run(['pactl', 'info'], capture_output=True, text=True)
        if result.returncode == 0:
            print("PulseAudio is running.")
            # Get default sink/source
            for line in result.stdout.split('\n'):
                if "Default Sink" in line or "Default Source" in line:
                    print(f"  {line}")
        else:
            print("PulseAudio is not running or not responding.")
    except:
        print("pactl command not available.")

    print("\n========================================")
    print("Copy and paste the output above to me.")
    print("========================================")

if __name__ == "__main__":
    list_audio_info()
