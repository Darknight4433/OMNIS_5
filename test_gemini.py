#!/usr/bin/env python
import os
from ai_response import get_chat_response

print("\nTesting Gemini API Integration...")
print("="*50)

# Require GEMINI_KEY to be set in the environment to avoid embedding secrets in code
if not os.environ.get('GEMINI_KEY'):
    print("GEMINI_KEY not found in environment. Set GEMINI_KEY before running this test.")
    raise SystemExit(1)

# Test with different prompts
prompts = [
    "What is the weather?",
    "Tell me a joke",
    "What time is it?",
    "What is 2+2?"
]

for prompt in prompts:
    print(f"\nPrompt: {prompt}")
    result = get_chat_response(prompt)
    if isinstance(result, dict) and 'error' not in result:
        # ai_response.get_chat_response returns either text or dict depending on implementation
        try:
            response = result['choices'][0]['message']['content']
            print(f"Response: {response[:80]}...")
        except Exception:
            print(f"Response (raw): {result}")
    else:
        print(f"Error: {result.get('error') if isinstance(result, dict) else result}")
