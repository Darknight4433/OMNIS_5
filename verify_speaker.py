from speaker import GTTSThread
try:
    s = GTTSThread()
    s.speak("test")
    print("SUCCESS: speak method exists")
except AttributeError:
    print("FAIL: speak method missing")
except Exception as e:
    print(f"ERROR: {e}")
