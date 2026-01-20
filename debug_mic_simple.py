import pyaudio
import speech_recognition as sr
import time
import audioop
import sys

def check_mic_energy():
    r = sr.Recognizer()
    try:
        # Try default mic first
        m = sr.Microphone()
        print(f"Using default microphone: {m.device_index}")
        
        with m as source:
            print("Adjusting for ambient noise... (hold quiet)")
            r.adjust_for_ambient_noise(source, duration=2)
            print(f"Energy Threshold: {r.energy_threshold}")
            
            print("Listening for 5 seconds... Speak now!")
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
                print(f"Audio captured. Size: {len(audio.get_raw_data())} bytes")
                
                print("Attempting recognition...")
                try:
                    text = r.recognize_google(audio)
                    print(f"SUCCESS! Heard: {text}")
                except sr.UnknownValueError:
                    print("RecognizeGoogle: UnknownValueError (Audio intelligible or silence)")
                    # Analyze audio energy
                    raw_data = audio.get_raw_data()
                    rms = audioop.rms(raw_data, 2)
                    print(f"Audio RMS (Energy): {rms}")
                    
                except sr.RequestError as e:
                    print(f"RecognizeGoogle Error: {e}")
                    
            except sr.WaitTimeoutError:
                print("WaitTimeoutError: No speech detected.")
                
    except Exception as e:
        print(f"General Error: {e}")

def list_devices():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    print("\n--- Available Audio Devices ---")
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print(f"Input Device id {i} - {p.get_device_info_by_host_api_device_index(0, i).get('name')}")
            # Try to see supported rates
            dev_info = p.get_device_info_by_host_api_device_index(0, i)
            print(f"  Default Rate: {dev_info.get('defaultSampleRate')}")

    p.terminate()

if __name__ == "__main__":
    list_devices()
    check_mic_energy()
