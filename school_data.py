from datetime import datetime

# ============================================
# SCHOOL CONFIGURATION & RULES
# ============================================
# Easy to update! Just modify values here and OMNIS will use them

SCHOOL_INFO = {
    "name": "MGM Model School",
    "location": "Varkala, Kerala, India",
    "founded": 1983,
    "principal": "Dr Pooja S",
    "founder": "Dr P K Sukumaran",
    "tagline": "Satyameya Jayate",
    "vision": "To Develop Global Citizens, with indian values, capable of transforming every indian to lead a generous, empathetic and fulfilled life",
    "total_students": 2900,
    "total_staff": 250,
    "sister_school": "KPM Model School",
    "starting_students": 5,
}

# School Rules - UK Style + MGM Rules
SCHOOL_RULES = {
    "attendance": {
        "requirement": "95% minimum attendance required",
        "uniform": "Compulsory Monday to Friday",
        "assembly": "Daily morning assembly at 8:15 AM",
        "late_policy": "Students arriving after 8:30 AM marked as late",
        "absent_protocol": "Parent notification within 2 hours",
    },
    "uniform": {
        "weekdays": "Full uniform compulsory",
        "pe_days": "PE uniform on designated sports days",
        "formal_events": "Formal attire for assemblies and events",
        "shoes": "Black leather shoes only",
    },
    "conduct": {
        "bullying": "Zero tolerance - immediate disciplinary action",
        "mobile_phones": "Not permitted during school hours",
        "behavior": "Respectful conduct towards staff and peers",
        "language": "English/Malayalam only in class",
    },
}

# Custom Q&A for Specific Rules - Easy to Ask!
CUSTOM_QA = {
    # ATTENDANCE & TIME RULES
    "What is the assembly time?": "Daily morning assembly is at 8:15 AM sharp.",
    "When am I marked late?": "Students arriving after 8:30 AM are marked as late.",
    "What is the attendance requirement?": "You need minimum 95% attendance to continue in school.",
    "What happens if I'm absent?": "Your parents will be notified within 2 hours of your absence.",
    
    # UNIFORM RULES
    "What is the dress code?": "Full school uniform is compulsory Monday to Friday. Uniform includes shirt/blouse, tie, trousers/skirt, and black leather shoes.",
    "When can I wear PE uniform?": "PE uniform is only worn on designated sports days as per the timetable.",
    "What about formal events?": "Formal attire must be worn for assemblies, ceremonies, and special events.",
    "What shoes should I wear?": "Only black leather shoes are permitted. No colored or casual shoes.",
    
    # MOBILE PHONE & CONDUCT RULES
    "Can I bring my mobile phone to school?": "No, mobile phones are not permitted during school hours. Any phones found will be confiscated and returned to parents.",
    "What is the bullying policy?": "MGM has a zero-tolerance policy on bullying. Any bullying will result in immediate disciplinary action.",
    "What language should I speak in class?": "Only English or Malayalam is permitted in class. No other languages.",
    "How should I behave?": "Always show respectful conduct towards all staff and peers. Use polite language and follow instructions.",
    
    # LATE & LEAVE PROCEDURES
    "What should I do if I'm late for school?": "Report to the main office with a note from your parent. You will be marked as late in your record.",
    "How do I request leave?": "Submit a leave form to your class teacher at least 3 days in advance. Medical certificates are required for sick leave longer than 2 days.",
    "What is the emergency leave process?": "For emergency situations, call the school office immediately. Parent notification is compulsory within the same day.",
    
    # FEE PAYMENT RULES
    "When are fees due?": "School fees must be paid by the 5th of each month.",
    "What if I pay late?": "Late payment will incur a 5% late charge. Please pay on time to avoid penalties.",
    "How do I pay fees?": "Fees can be paid via online bank transfer or cheque. Always request a receipt for your records.",
    
    # SAFETY & LABORATORY RULES
    "What are the laboratory safety rules?": "Lab access is only permitted with teacher supervision. Always wear safety goggles and follow all instructions exactly.",
    "What if I don't follow lab rules?": "Non-compliance with lab safety rules will result in suspension from lab access and disciplinary action.",
    "What medical facilities are available?": "A qualified school nurse is available 8 AM to 4 PM daily. Report any injuries or health issues immediately.",
    
    # BULLYING & DISCIPLINE
    "What should I do if I'm being bullied?": "Report immediately to any teacher, counselor, or the principal. All complaints will be investigated and appropriate action taken.",
    "What is the grievance procedure?": "First speak to your class teacher. If unresolved, contact the administrator. For formal complaints, submit a written request to the principal.",
    "How long does grievance resolution take?": "The Grievance Redressal Committee reviews all complaints and aims to resolve within 30 days.",
    
    # LIBRARY & STUDY FACILITIES
    "What are the library hours?": "The library is open from 8:00 AM to 4:00 PM on all school days.",
    "How long can I keep books?": "Books can be issued for 2 weeks. You can renew if no one else has requested the book.",
    "Are there digital resources?": "Yes, we have three digital libraries with e-books and online resources available to all students.",
    
    # SPORTS & ACTIVITIES
    "Do I have to participate in sports?": "Yes, all students must participate in at least one sport or physical activity per week.",
    "What sports facilities are available?": "We have a basketball court, volleyball court, badminton facilities, and sports equipment for various activities.",
    "Are there extracurricular activities?": "Yes, students can join various clubs including debate, music, arts, STEM, and community service.",
    
    # CANTEEN & FOOD
    "What is the canteen policy?": "Only healthy food is served in the canteen. Junk food is strictly prohibited.",
    "Are there special meals for allergies?": "Yes, please inform the canteen manager and principal of any food allergies for special arrangements.",
    
    # CONTACT & ADMINISTRATION
    "Who is the principal?": "Dr Pooja S is our principal. Office hours are 8:30 AM to 4:00 PM.",
    "How do I contact the school?": "Call the main office or visit the school during office hours. Email queries can be sent to the school website.",
    "Is there a school counselor?": "Yes, a qualified counselor is available for student support, academic guidance, and personal counseling.",
}

# ============================================
# LEGACY METADATA - Original School Q&A
# ============================================
METADATA = [
    {'answer': "Our school is forty years old", 'question_data': ["old", 'mgm']},
    {'answer': "Welcome to MGM Model School Robot", 'question_data': ["my", 'name', 'is']},
    {'answer': "I am MGM Robot. How are you?", 'question_data': ["your", 'name']},
    {'answer': f'{datetime.now().strftime("%M minutes past %I%p")}', 'question_data': ["what", 'time']},
    {'answer': f'{datetime.now().strftime("Today is %B %d %Y")}', 'question_data': ["what", 'date', 'today']},
    {'answer': "You are welcome!", 'question_data': ["thank", 'you']},
    {'answer': "Dr P K Sukumaran", 'question_data': ['who', 'founder', 'mgm']},
    {'answer': "Dr P K Sukumaran", 'question_data': ['who', 'founded', 'mgm']},
    {'answer': "Nitya Haritha Nayakan Mister Prem Nasir", 'question_data': ['foundation', 'stone', 'laid']},
    {'answer': 'Dr Pooja S', 'question_data': ['our', 'principal']},
    {'answer': 'Ms Lalitha', 'question_data': ['who', 'first', 'principal', 'of', 'mgm']},
    {'answer': 'We have three digital libraries', 'question_data': ['many', 'digital', 'library', 'libraries']},
    {'answer': "Dr A P J Abdul Kalam", 'question_data': ['Name', 'President', 'visit', 'mgm']},
    {'answer': "To develop global citizens, with Indian values, capable of transforming every Indian to lead a generous, empathetic and fulfilled life", 
        'question_data': ['what', 'vision', 'our', 'school']},
    {'answer': 'Two thousand nine hundred', 'question_data': ['many', 'students', 'do', 'have']},
    {'answer': "Nineteen eighty three", 'question_data': ['mgm', 'mgm model school', 'start', 'started', 'year', 'which']},
    {'answer': "KPM model school, Mayyanad", 'question_data': ['which', 'sister', 'sister concern', 'school', 'mgm']},
    {'answer': "We started with five students", 'question_data': ['how', 'many', 'students', 'there', 'mgm', 'begining']},
    {'answer': "Twenty twenty", 'question_data': ['which', 'novel', 'method', 'teaching', 'introduced', 'mgm']},
    {'answer': 'Ruby Jubilee', 'question_data': ['what', 'going', 'celebrated', 'celebration', 'year', '20', '23', '24']},
    {'answer': "Honourable Governer Shri Arif Mohammed Khan", 'question_data': ['who', 'inagurated', 'innovation', 'center']},
    {'answer': "Shri Oommen Chandy", 'question_data': ['which', 'chief', 'minister', 'visit', 'mgm']},
    {'answer': "Satyameya Jayate", 'question_data': ['tagline', 'mgm', 'tag', 'line', 'what']},
    {'answer': "We have two hundred and fifty employees", 'question_data': ['how', 'many', 'employees', 'have']},
    {'answer': "Digital library, Maths 3d corner, Maths innovation center, Globe, Basket ball court, Butterfly garden, and one yoga period for class one to eighth", 
     'question_data': ['what', 'facilities', 'infrastructure', 'provided', 'mgm']}
]

def get_school_answer(question: str, accuracy: float = 0.6):
    """
    Checks if the question matches any local school metadata.
    Returns the answer string if found, else None.
    """
    best_match = None
    max_score = 0
    
    question_lower = question.lower()
    
    for item in METADATA:
        count = 0
        valid = 0
        total_keywords = len(item["question_data"])
        
        for word in item["question_data"]:
            if word.lower() in question_lower:
                valid += 1
        
        if total_keywords > 0:
            score = valid / total_keywords
            if score >= accuracy and score > max_score:
                max_score = score
                # Handle answers that are lists (from user provided code) or strings
                ans = item['answer']
                if isinstance(ans, list):
                    best_match = ans[0]
                else:
                    best_match = ans
                    
    return best_match


def get_rule_based_answer(question: str) -> str:
    """
    Check CUSTOM_QA for exact or close rule-based matches
    Returns answer if found, else None
    
    Uses 2-tier matching:
    1. Exact substring match (strict)
    2. Keyword matching with higher threshold (requires 50%+ keyword match)
    """
    question_lower = question.lower().strip()
    
    # First try exact substring match (one string fully contains the other)
    for qa_question, qa_answer in CUSTOM_QA.items():
        qa_lower = qa_question.lower()
        # Check if question contains the Q&A question or vice versa
        if qa_lower in question_lower:
            return qa_answer
    
    # Try keyword matching with higher threshold
    for qa_question, qa_answer in CUSTOM_QA.items():
        qa_lower = qa_question.lower()
        keywords = [kw for kw in qa_lower.split() if len(kw) > 3]  # Only keywords > 3 chars
        if not keywords:
            continue
            
        match_count = sum(1 for kw in keywords if kw in question_lower)
        match_ratio = match_count / len(keywords)
        
        # Require 50%+ keyword match (not just 2 keywords)
        if match_ratio >= 0.5 and match_count >= 2:
            return qa_answer
    
    return None


def get_school_answer_enhanced(question: str, accuracy: float = 0.6) -> str:
    """
    Enhanced version that tries:
    1. Rule-based custom Q&A first
    2. Then legacy METADATA matching
    """
    # First try custom rules
    rule_answer = get_rule_based_answer(question)
    if rule_answer:
        return rule_answer
    
    # Fall back to METADATA
    return get_school_answer(question, accuracy)