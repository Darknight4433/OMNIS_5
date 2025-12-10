#!/usr/bin/env python3

from datetime import datetime
import queue
from time import sleep
import threading
from gtts import gTTS
import os
import requests
from bs4 import BeautifulSoup
from ai_response import get_chat_response as ai_get_chat_response
import speech_recognition as sr
import pygame
# from robot.openai import get_response


pygame.mixer.init(frequency=53000)

# Setup Mic and recognizer
r = sr.Recognizer()
mic = sr.Microphone()

ACCURACY = 0.7
is_speaking = False
listen_tag = False


def get_weather_data(city: str='varkala'):
    url = 'https://www.google.com/search?q='+'weather'+city

    res = requests.get(url).content

    soup = BeautifulSoup(res, 'html.parser')

    temperature = soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'}).text
    str = soup.find('div', attrs={'class': 'BNeawe tAd8D AP7Wnd'}).text
 
    # formatting data
    data = str.split('\n')
    time = data[0]
    sky = data[1]

    # getting all div tag
    listdiv = soup.findAll('div', attrs={'class': 'BNeawe s3v9rd AP7Wnd'})
    strd = listdiv[5].text
    
    # getting other required data
    pos = strd.find('Wind')
    other_data = strd[pos:]
    out = f'The temperature is {temperature}. with a {sky} sky'
    print(out)
    return out


METADATA = [
    {'answer': ["our school is forty years old"], 'question_data': ["old", 'mgm']},
    {'answer': [None], 'question_data': ["weather"]},
    {'answer': [None], 'question_data': ["temperature"]},
    {'answer': ["Welcome to MGM School Robot"], 'question_data': ["my", 'name', 'is']},
    {'answer': ["I am MGM Robot. How are you?"], 'question_data': ["your", 'name']},
    {'answer': [f'{datetime.now().strftime("%M minutes past %I%p")}'], 'question_data': ["what", 'time']},
    {'answer': [f'{datetime.now().strftime("Todays date is %B %d %Y")}'], 'question_data': ["what", 'date', 'today']},
    {'answer': ["you are welcome!"], 'question_data': ["thank", 'you']},
    {'answer': ["Dr p k sukumaran"], 'question_data': ['who', 'founder', 'mgm']},
    {'answer': ["Dr p k sukumaran"], 'question_data': ['who', 'founded', 'mgm']},
    {'answer': ["Nitya haritha nayakan mister Prem nasir"], 'question_data': ['foundation', 'stone', 'foundation stone', 'laid']},
    {'answer': ['Dr Pooja S'], 'question_data': ['our', 'principal']},
    {'answer': ['Ms Lalitha'], 'question_data': ['who', 'first', 'principal', 'of', 'mgm']},
    {'answer': ['we have three digital libraries'], 'question_data': ['many', 'digital', 'library', 'libraries']},
    {'answer': ["Dr A P J Abdul Kalam"], 'question_data': ['Name', 'President', 'visit', 'mgm']},
    {'answer': ["To Develop Global Citizens, with indian values, capable of transforming every indian to lead a generous, empathetic and fulfilled life"], 
        'question_data': ['what', 'vision', 'our', 'school']},
    {'answer': ['two thousand nine hundred'], 'question_data': ['many', 'students', 'do', 'have']},
    {'answer': ["Nineteen eighty three"], 'question_data': ['mgm', 'mgm model school', 'start', 'started', 'year', 'which']},
    {'answer': ["KPM model school", "mayyanad"], 'question_data': ['which', 'sister', 'sister concern', 'school' 'mgm']},
    {'answer': ["we started with five students"], 'question_data': ['how', 'many', 'students', 'there', 'mgm', 'begining']},
    {'answer': ["twenty twenty"], 'question_data': ['which', 'novel', 'method', 'teaching', 'introduced', 'mgm']},
    {'answer': ['ruby jubilee'], 'question_data': ['what', 'going', 'celebrated', 'celebration', 'year', '20', '23', '24']},
    {'answer': ["Honourable governer Shri arif mohammed khan"], 'question_data': ['who', 'inagurated', 'innovation', 'center', 'innovation center']},
    {'answer': ["Shri Oommen Chandy"], 'question_data': ['which', 'chief', 'chief minister', 'minister', 'visit', 'mgm']},
    {'answer': ["satyameya jayate"], 'question_data': ['tagline', 'mgm', 'tag', 'line', 'what']},
    {'answer': ["we have two hundred and fifty employees"], 'question_data': ['how', 'many', 'employees', 'have']},
    {'answer': ["Digital library",
                "Maths 3d corner",
                "Maths innovation center",
                "Globe",
                "Basket ball court",
                "Butterfly garden",
                "one yoga period for class one to eighth"], 'question_data': ['what', 'facilities', 'infrastructure', 'provided', 'mgm']}
]


# Removed direct OpenAI calls in favor of centralized `ai_response.get_chat_response`


def speak_task(data: list):
    # Bridge to centralized speaker implementation in `speaker.py`
    try:
        from speaker import speak as speaker_speak
    except Exception as e:
        print(f"[speak_task] Cannot import centralized speaker: {e}")
        return

    try:
        # `data` may be a list of strings
        speaker_speak(data)
    except Exception as e:
        print(f"[speak_task] Error while speaking: {e}")


def generate_ai_question(question:str, level: int=3, words_limit=30):
    """Execute openai API if question doesnot belong to LUT

    Args:
        question (str): The question to be asked to openai
        level (int): level of the question. 
                        level 1 = lower primary 1 - 4
                        level 2 = upper primary 4 - 8
                        level 3 = higher - above 8th
    """
    if level == 1:
        return f"reply to 4th grader : {question} \n in max {words_limit} words."
    if level == 2:
        return f"reply to 8th grader : {question} \nin max {words_limit} words."
    if level == 3:
        return f"reply to 10th grader : {question}\nin max {words_limit} words."
    
    return f"{question}\n in max {words_limit} words."


def validate_questions(question: str, accuracy: float):
    global METADATA
    
    for item in METADATA:
        count = 0
        valid = 0
        for word in item["question_data"]:
            if word.lower() in question.lower():
                valid += 1
            count += 1

        # print(f'{item} -> {valid/count}')
        if valid / count > accuracy:
            # If the stored answer is None (placeholder), compute it dynamically
            ans = item['answer']
            if ans and ans[0] is None:
                # Known dynamic entries: weather/temperature
                if 'weather' in item['question_data'] or 'temperature' in item['question_data']:
                    try:
                        return [get_weather_data()]
                    except Exception as e:
                        print(f"[Weather] Error getting weather data: {e}")
                        return ["Sorry, weather service unavailable."]
            return item['answer']
    
    print(f"Sending to AI backend")
    try:
        resp = ai_get_chat_response(generate_ai_question(question))
        response = None
        try:
            response = resp['choices'][0]['message']['content']
        except Exception:
            # ai_response already returns friendly fallbacks; print raw for debugging
            print(f"[AI] Raw response: {resp}")
            response = None
        negetive_responses = ['I\'m sorry', 'i\'m sorry', 'I do not have', 'i do not have', 'mein', 'mera']
    
        if response and not any(item.lower() in response for item in negetive_responses):
            return [response]
        else:
            return ["Sorry Didn't recognise the question."]
    except Exception as e:
        print(f'[OPENAI_ERROR] -> {e}')
    # print(f"Response from OpenAI -> {response}")


def speech_to_text_task(listen_queue: queue.Queue):
    global listener_flag
    global stored_data, ACCURACY

    listening = True
    while listening:
        
        if not listen_queue.empty():
            try:    
                listening = listen_queue.get()
            except queue.Empty:
                print(f'[Speech Recognition] Queue is empty')

        with mic as source:
            print("Listening...")
            r.adjust_for_ambient_noise(source)
            r.dynamic_energy_threshold = 3000
            try:
                listen_tag = True
                audio = r.listen(source, timeout=2, phrase_time_limit=3)
                response = r.recognize_google(audio)                
                print(response)
                print('listener off')
                listen_tag = False

                answer = validate_questions(response, accuracy=ACCURACY)

                print(f'[Speech Recognition]  -->  Answer is {answer}')
                speak_task(answer)
                # speakerThread = threading.Thread(target=speak_task, args=(response))
                # speakerThread.start()

            except sr.UnknownValueError:
                print("[Speech Recogniton] Didn't recognise that.")
                sleep(0.5)
            except sr.WaitTimeoutError:
                print("[Speech Recognition] Timed out...")
                sleep(1)
    print(f"[Speech Recognition] Task has stopped. Listen_flag -> {listening}")
    

if __name__ == '__main__':
    payload = ["Hello", "Welcome to MGM Model School"]

    # Listener thread initialised and started once
    listener_flag = queue.Queue()
    listening_task = threading.Thread(target=speech_to_text_task, args=(listener_flag, ), daemon=True)
    try:
        listening_task.start()
        # Keep main thread alive while listener runs
        while listening_task.is_alive():
            sleep(0.5)
    except KeyboardInterrupt:
        print('[Application]: Interrupted by user, shutting down')
    except Exception as e:
        print(f'[Application]: Fatal error: {e}')
