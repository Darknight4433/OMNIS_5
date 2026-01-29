#!/usr/bin/env python3
"""
Test the updated speaker.py to verify audio playback works
Run this on the Raspberry Pi after updating speaker.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("  Testing OMNIS Speaker with Card 1")
print("="*60)

# Import the speaker module
try:
    import speaker
    print("\n✓ speaker.py imported successfully")
except Exception as e:
    print(f"\n✗ Failed to import speaker.py: {e}")
    sys.exit(1)

# Check audio config
try:
    import audio_config
    card = audio_config.SPEAKER_CARD_INDEX
    print(f"✓ Audio configured for Card {card}")
except:
    print("⚠ Could not read audio_config.py")
    card = 1

# Initialize speaker thread
print(f"\n[1] Initializing speaker thread...")
try:
    speaker.init_speaker_thread()
    print("✓ Speaker thread initialized")
except Exception as e:
    print(f"✗ Failed to initialize: {e}")
    sys.exit(1)

# Test speech
print(f"\n[2] Testing audio playback...")
print("    You should hear: 'Testing OMNIS audio on card one'")
print("    (This may take a few seconds to generate and play)")

try:
    speaker.speak("Testing OMNIS audio on card one")
    
    # Wait for speech to complete
    import time
    timeout = 15
    start = time.time()
    
    while speaker.is_speaking() and (time.time() - start) < timeout:
        time.sleep(0.5)
    
    # Give it a moment to finish
    time.sleep(1)
    
    if time.time() - start >= timeout:
        print("\n⚠ Timeout waiting for speech to complete")
    else:
        print("\n✅ Audio playback completed!")
        print("\n" + "="*60)
        print("  SUCCESS! OMNIS audio is working!")
        print("="*60)
        print("\nYou can now run: python3 main.py")
        sys.exit(0)
        
except Exception as e:
    print(f"\n✗ Error during playback: {e}")
    sys.exit(1)
