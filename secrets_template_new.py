
# OMNIS API Configuration
# -----------------------------------------------------------------------------
# INSTRUCTIONS FOR RASPBERRY PI:
# 1. Run: cp secrets_template_new.py secrets_local.py
# 2. Edit: nano secrets_local.py
# 3. Paste your REAL keys into the lists below.
# -----------------------------------------------------------------------------

# 1. Gemini API Keys (BRAIN)
# Add multiple keys in the list to enable auto-rotation if quota is exceeded.
GEMINI_KEYS = [
    'PASTE_YOUR_REAL_GEMINI_KEY_1_HERE',
    'PASTE_YOUR_REAL_GEMINI_KEY_2_HERE',
    # Add more lines if you have more keys...
]

# Legacy single key support (Optional - leave empty if using list above)
GEMINI_KEY = '' 

# 2. ElevenLabs API Keys (VOICE)
ELEVENLABS_KEYS = [
    'sk_1671a85ae149df5c19809c2df4d439f747d9fe181617e82a',
    'sk_d508cc204cfca17e6877698aff7a8908959cd50a91523da1',
    'sk_cf261d99ce4ddd58372efd9da1e2ac358b8ae755d8eb18d6'
]
