from school_data import get_school_response, get_school_answer_enhanced

questions = [
    ("Who is the principal?", "Dr Pooja S"),
    ("Who is the present principal", "Dr Pooja S"),
    ("Principal name", "Dr Pooja S"),
    ("Who is the first principal?", "Ms Lalitha"),
    ("Who is the founder?", "Dr P K Sukumaran"),
    ("Who is the Prime Minister of India?", "I don't have that information."),
    ("Who is the Chief Minister of Kerala?", "I don't have that information.")
]

print("--- Testing School Data Fix (With False Positives Check) ---")
for q, expected in questions:
    ans = get_school_response(q)
    enhanced_ans = get_school_answer_enhanced(q)
    print(f"Q: '{q}'")
    print(f"   -> Basic Answer: '{ans}'")
    print(f"   -> Enhanced Answer (for Voice): '{enhanced_ans}'")
    
    match_status = "✅ PASS" if ans == expected else f"❌ FAIL (Expected: {expected})"
    if "I don't have that information" in expected and "I don't have that information" in ans:
         match_status = "✅ PASS"
    
    print(f"   -> Status: {match_status}\n")
