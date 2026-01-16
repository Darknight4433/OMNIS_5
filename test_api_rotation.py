import sys
sys.path.insert(0, '.')

from ai_response import get_chat_response

print("Testing API Rotation System...")
print("=" * 50)

# Test 1: Simple question
print("\n1. Testing basic AI response:")
response = get_chat_response("What is 2 plus 2?")
print(f"   Answer: {response['choices'][0]['message']['content']}")

# Test 2: Another question
print("\n2. Testing second question:")
response = get_chat_response("What is the capital of India?")
print(f"   Answer: {response['choices'][0]['message']['content']}")

print("\n✅ API rotation test complete!")
