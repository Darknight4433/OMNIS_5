#!/bin/bash
# OMNIS Robot - Raspberry Pi Run Script
# This script starts OMNIS with proper environment settings

echo "========================================"
echo "Starting OMNIS Robot Assistant"
echo "========================================"
echo ""

# Optional: Set environment variables here if not using secrets_local.py
# export GEMINI_KEY="your-api-key-here"

# Optional: Enable debug mode
# export OMNIS_DEBUG=1

# Optional: Adjust Gemini response settings
# export GEMINI_MAX_TOKENS=200
# export GEMINI_TEMPERATURE=0.6

# Optional: Set face recognition tolerance (lower = stricter)
# export FACE_MATCH_TOLERANCE=0.55

# Optional: Limit max faces to process (helps performance on Pi)
# export FACE_MAX_FACES=2

echo "Starting main program..."
python3 main.py

echo ""
echo "OMNIS has stopped."
