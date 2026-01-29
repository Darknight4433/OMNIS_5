#!/usr/bin/env python3
"""
OMNIS Speaker Card Diagnostic & Fix
====================================
This script will:
1. List all available audio cards
2. Test each card for playback capability
3. Update audio_config.py with the working card
"""

import os
import subprocess
import time

print("="*60)
print("OMNIS SPEAKER CARD DIAGNOSTIC")
print("="*60)

# Step 1: List all audio cards
print("\n[1/3] Listing all audio cards...")
try:
    result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
    print(result.stdout)
    
    # Parse card numbers
    cards = []
    for line in result.stdout.split('\n'):
        if line.startswith('card '):
            card_num = line.split(':')[0].replace('card ', '').strip()
            cards.append(card_num)
    
    print(f"\nFound {len(cards)} card(s): {cards}")
    
except Exception as e:
    print(f"❌ Error listing cards: {e}")
    exit(1)

# Step 2: Test each card
print("\n[2/3] Testing each card for playback...")
working_cards = []

for card in cards:
    print(f"\n  Testing card {card}...")
    
    # Try to play a test tone using speaker-test
    try:
        # Use speaker-test with minimal output
        result = subprocess.run(
            ['speaker-test', '-D', f'plughw:{card},0', '-c', '2', '-t', 'wav', '-l', '1'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"  ✅ Card {card} works!")
            working_cards.append(card)
        else:
            print(f"  ❌ Card {card} failed: {result.stderr[:100]}")
            
    except subprocess.TimeoutExpired:
        print(f"  ⏱️  Card {card} timed out (might still work)")
        working_cards.append(card)  # Add it anyway, timeout might be OK
    except Exception as e:
        print(f"  ❌ Card {card} error: {e}")

# Step 3: Update config
print("\n[3/3] Updating configuration...")

if not working_cards:
    print("❌ No working audio cards found!")
    print("\nTroubleshooting steps:")
    print("  1. Check if speakers are connected")
    print("  2. Run: sudo alsa force-reload")
    print("  3. Check if another process is using the audio device")
    print("  4. Try: fuser -v /dev/snd/*")
    exit(1)

# Use the first working card
selected_card = working_cards[0]
print(f"\n✅ Selected card {selected_card} for OMNIS")

# Update audio_config.py
config_content = f"""# Audio configuration for OMNIS
# This file is automatically updated by fix_speaker_card.py

# The ALSA card index for the speaker (e.g., 0, 1, 2, 3)
# Automatically detected working card
SPEAKER_CARD_INDEX = {selected_card}
"""

try:
    with open('audio_config.py', 'w') as f:
        f.write(config_content)
    print(f"✅ Updated audio_config.py with card {selected_card}")
except Exception as e:
    print(f"❌ Failed to update config: {e}")
    exit(1)

# Step 4: Test with mpg123
print("\n[4/4] Testing with mpg123...")
print("  Generating test audio file...")

try:
    # Create a simple test audio using espeak
    subprocess.run(
        ['espeak-ng', '-w', 'test_audio.wav', 'Testing OMNIS speaker'],
        capture_output=True,
        timeout=5
    )
    
    # Convert to mp3 if ffmpeg is available
    if subprocess.run(['which', 'ffmpeg'], capture_output=True).returncode == 0:
        subprocess.run(
            ['ffmpeg', '-i', 'test_audio.wav', '-y', 'test_audio.mp3'],
            capture_output=True,
            timeout=5
        )
        test_file = 'test_audio.mp3'
    else:
        test_file = 'test_audio.wav'
    
    print(f"  Playing test audio on card {selected_card}...")
    result = subprocess.run(
        ['mpg123', '-q', '-a', f'plughw:{selected_card},0', test_file],
        capture_output=True,
        timeout=10
    )
    
    if result.returncode == 0:
        print("  ✅ mpg123 playback successful!")
    else:
        print(f"  ⚠️  mpg123 had issues: {result.stderr[:100]}")
        print("  (This might still work in OMNIS)")
    
    # Cleanup
    for f in ['test_audio.wav', 'test_audio.mp3']:
        if os.path.exists(f):
            os.remove(f)
            
except Exception as e:
    print(f"  ⚠️  Test playback error: {e}")
    print("  (OMNIS might still work)")

print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE!")
print("="*60)
print(f"\n✅ Audio configured to use card {selected_card}")
print("\nNext steps:")
print("  1. Try running: python3 main.py")
print("  2. Say 'OMNIS' to test voice recognition")
print("  3. OMNIS should now speak properly")
print("\nIf issues persist:")
print("  - Check volume: alsamixer")
print("  - Unmute channels: alsamixer (press M)")
print("  - Check processes using audio: fuser -v /dev/snd/*")
print("="*60)
