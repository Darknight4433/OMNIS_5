#!/usr/bin/env python
import os
import google.generativeai as genai

api_key = os.environ.get('GEMINI_KEY')
if not api_key:
	print('GEMINI_KEY not set. Set GEMINI_KEY in the environment to run this tool.')
	raise SystemExit(1)
genai.configure(api_key=api_key)

print("Available HarmCategory values:")
print(dir(genai.types.HarmCategory))
print("\nAvailable HarmBlockThreshold values:")
print(dir(genai.types.HarmBlockThreshold))
