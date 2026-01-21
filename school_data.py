"""
School data and offline fallback responses for OMNIS.
Used when API keys are exhausted or internet is unavailable.
"""

# School information database
SCHOOL_METADATA = [
    {'answer': ["our school is forty years old"], 'question_data': ["old", 'mgm']},
    {'answer': [None], 'question_data': ["weather"]},
    {'answer': [None], 'question_data': ["temperature"]},
    {'answer': ["Welcome to MGM School Robot"], 'question_data': ['my', 'name']},
    {'answer': ["I am MGM Robot. How are you?"], 'question_data': ["your", 'name']},
    {'answer': ["I'm sorry, I can't tell the current time in offline mode."], 'question_data': ['time']},
    {'answer': ["I'm sorry, I can't tell today's date in offline mode."], 'question_data': ['date', 'today']},
    {'answer': ["you are welcome!"], 'question_data': ["thank", 'you']},
    {'answer': ["Dr P K Sukumaran"], 'question_data': ['founder', 'mgm', 'founded']},
    {'answer': ["Dr P K Sukumaran"], 'question_data': ['founded', 'mgm']},
    {'answer': ["Nitya haritha nayakan mister Prem nasir"], 'question_data': ['foundation', 'stone', 'laid']},
    {'answer': ['Dr Pooja S'], 'question_data': ['our', 'principal', 'present', 'current', 'pooja', 'name']},
    {'answer': ["Mr Unnikrishnan Vishakam"], 'question_data': ['pta', 'president', 'mgm']},
    {'answer': ['Ms Lalitha'], 'question_data': ['first', 'principal', 'mgm']},
    {'answer': ['we have three digital libraries'], 'question_data': ['many', 'digital', 'library', 'libraries']},
    {'answer': ["Dr A P J Abdul Kalam"], 'question_data': ['Name', 'President', 'visit', 'mgm']},
    {'answer': ["To Develop Global Citizens, with indian values, capable of transforming every indian to lead a generous, empathetic and fulfilled life"], 
        'question_data': ['vision', 'our', 'school', 'mgm']},
    {'answer': ['two thousand nine hundred'], 'question_data': ['many', 'students', 'have']},
    {'answer': ["Nineteen eighty three"], 'question_data': ['mgm', 'mgm model school', 'start', 'started', 'year']},
    {'answer': ["KPM model school", "mayyanad"], 'question_data': ['sister', 'sister concern', 'school' 'mgm']},
    {'answer': ["we started with five students"], 'question_data': ['how', 'many', 'students', 'there', 'mgm', 'begining']},
    {'answer': ["twenty twenty"], 'question_data': ['which', 'novel', 'method', 'teaching', 'introduced', 'mgm']},
    {'answer': ['ruby jubilee'], 'question_data': ['going', 'celebrated', 'celebration', 'year', '20', '23', '24']},
    {'answer': ["Honourable governer Shri arif mohammed khan"], 'question_data': ['inagurated', 'innovation', 'center', 'innovation center']},
    {'answer': ["Shri Oommen Chandy"], 'question_data': ['oommen', 'chandy', 'visit', 'visited', 'chief', 'minister']},
    {'answer': ["satyameya jayate"], 'question_data': ['tagline', 'mgm', 'tag', 'line']},
    {'answer': ["we have two hundred and fifty employees"], 'question_data': ['how', 'many', 'employees', 'have']},
    {'answer': ["Digital library",
                "Maths 3d corner",
                "Maths innovation center",
                "Globe",
                "Basket ball court",
                "Butterfly garden",
                "one yoga period for class one to eighth"], 'question_data': ['facilities', 'infrastructure', 'provided', 'mgm']}
]


def get_school_response(question: str) -> str:
    """
    Get a school-related response from offline database.
    
    Args:
        question: The question asked by the user
        
    Returns:
        str: The answer if found, else a default message
    """
    if not question:
        return "I don't have that information."
    
    # Convert question to lowercase and remove punctuation for better matching
    question_lower = question.lower().replace('?', '').replace('.', '').replace(',', '').replace('!', '')
    question_words = set(question_lower.split())
    
    # Find matching metadata entry
    best_match = None
    best_score = 0
    
    for entry in SCHOOL_METADATA:
        question_data = entry.get('question_data', [])
        # Count how many keywords match
        match_score = len([word for word in question_data if word.lower() in question_words])
        
        if match_score > best_score:
            best_score = match_score
            best_match = entry
    
    # Return answer if we found a good match
    if best_match and best_score > 0:
        answers = best_match.get('answer', [])
        # Return first non-None answer
        for ans in answers:
            if ans is not None:
                return ans
    
    return "I don't have that information."


def get_school_answer_enhanced(question: str) -> str:
    """
    Enhanced version of get_school_response for sr_class.py compatibility.
    Returns answer only if there's a confident match (score > 1).
    
    Args:
        question: The question asked by the user
        
    Returns:
        str: The answer if confident match found, else empty string (triggers AI fallback)
    """
    if not question:
        return ""
    
    # Convert question to lowercase and remove punctuation for better matching
    question_lower = question.lower().replace('?', '').replace('.', '').replace(',', '').replace('!', '')
    question_words = set(question_lower.split())
    
    # Find matching metadata entry
    best_match = None
    best_score = 0
    
    for entry in SCHOOL_METADATA:
        question_data = entry.get('question_data', [])
        # Count how many keywords match
        match_score = len([word for word in question_data if word.lower() in question_words])
        
        if match_score > best_score:
            best_score = match_score
            best_match = entry
    
    # Return answer only if we have a confident match (at least 2 keywords)
    if best_match and best_score > 1:
        answers = best_match.get('answer', [])
        # Return first non-None answer
        for ans in answers:
            if ans is not None:
                return ans
    
    # Return empty string to trigger AI fallback
    return ""
