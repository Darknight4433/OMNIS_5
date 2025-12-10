import asyncio
import speech_recognition as sr
# import snowboydecoder


# Hotword detection callback function
def hotword_callback():
    print("Hotword detected. Listening...")

    # Perform speech recognition
    loop.create_task(speech_recognition_task(10))


# Speech recognition task
async def speech_recognition_task(timeout=10):
    r = sr.Recognizer()

    # Listen to microphone
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        audio_data = r.listen(source)

    # Speech recognition
    try:
        text = r.recognize_google(audio_data, timeout=timeout)
        print("Recognized speech:", text)
    except sr.UnknownValueError:
        print("Sorry, Unable to recognize speech")
    except sr.RequestError as e:
        print("Error occurred: {0}".format(e))
    except sr.WaitTimeoutError:
        print("Sorry, speech recognition timed out.")
        return ""

# Configure Snowboy for hotword detection
models = "path/to/model.pmdl"  # Replace with your Snowboy model file
sensitivity = 0.5  # Adjust sensitivity threshold as needed
detector = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity)

# Create an event loop
loop = asyncio.get_event_loop()

# Run the hotword detection as a background task
loop.run_in_executor(None, detector.start, hotword_callback)

# Run the event loop
loop.run_forever()

# Cleanup tasks
# detector.terminate()
