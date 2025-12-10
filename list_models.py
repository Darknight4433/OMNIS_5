#!/usr/bin/env python
import os
import google.generativeai as genai

api_key = os.environ.get('GEMINI_KEY')
if not api_key:
    print('GEMINI_KEY not set. Set GEMINI_KEY in the environment to list models.')
    raise SystemExit(1)
genai.configure(api_key=api_key)

print("Available Models:")
print("="*50)
for model in genai.list_models():
    print(f"- {model.name}")
