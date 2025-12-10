# OMNIS - Raspberry Pi Quick Start

## Setup (First Time Only)

1. Copy this folder to your Raspberry Pi
2. Run setup:
   ```bash
   cd ~/OMNIS_ROBOT-main
   chmod +x setup_pi.sh
   ./setup_pi.sh
   ```
3. Wait 5-10 minutes for installation to complete

## Run OMNIS

```bash
cd ~/OMNIS_ROBOT-main
python3 main.py
```

## Test Voice

Say: **"Hello, how are you?"**

Or: **"OMNIS, what is AI?"**

## Change API Key (Optional)

Edit `secrets_local.py`:
```python
GEMINI_KEY = 'your-api-key-here'
```

That's it! 🚀
