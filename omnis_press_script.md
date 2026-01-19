# OMNIS: The Future of Educational Robotics
**Press Presentation Script & Functional Deep-Dive**
*Version 1.0 - MGM Model School*

---

## 🎙️ Presentation Script

### 1. The Opening (Warm-up)
"Good morning, members of the press, staff, and students. Today, we are proud to introduce **OMNIS**, not just a robot, but a pioneer in educational technology right here at MGM Model School. OMNIS was born from a vision to blend AI with the warmth of human interaction to assist our school community."

### 2. The Reveal (Live Interaction)
*(Walk towards OMNIS and let it see you or a known reporter)*
- **OMNIS greets you:** "Good morning Vaishnavi! Welcome back to MGM Model School."
- **Presenter:** "OMNIS, meet the press. Can you tell them about yourself?"
- **OMNIS:** "Hello everyone. I am OMNIS, the AI-powered assistant for MGM Model School. I recognize faces, answer school-related questions, and even use Google Gemini for general knowledge. How can I help you today?"

### 3. Feature Showcase (Demo)
"OMNIS is packed with cutting-edge technology. Let's look at what it can do:"

- **Voice Intelligence:** "OMNIS, who is our principal?" -> *(OMNIS answers 'Dr Pooja S')*
- **Visual Awareness:** "OMNIS can track my movement. Watch how its head follows me as I move across the stage."
- **Deep Knowledge:** "It knows our history, our rules, and our sister schools by heart—no internet required for these local queries."
- **Weather Updates:** "OMNIS can tell us the current weather. 'OMNIS, what's the weather like today?'" -> *(OMNIS responds with current weather conditions)*
- **Dynamic Memory:** "It remembers our conversations. If I ask about a topic, it can follow up later, showing a truly personalized interaction."
- **Modern AI:** "When we need more, it connects to Google Gemini to explain complex topics like quantum physics or to write a poem for us."

### 4. The Closing
"OMNIS represents the Ruby Jubilee spirit of MGM—valuing our foundations while embracing the future. It’s more than a machine; it's a student’s companion and a school's digital memory. Thank you."

---

## 🛠️ OMNIS: Functional Deep-Dive
*(Handout for the Press)*

### 👁️ Core Intelligence (Vision & Interaction)
| Feature | Description |
| :--- | :--- |
| **Face Recognition** | Recognizes 16+ registered students and staff with 0.5s response time. |
| **VIP Press Greeting** | Pre-programmed to recognize and welcome specific reporters from Malayala Manorama, Mathrubhumi, Asianet, and more by name. |
| **Emotion Detection** | Uses vision to detect if the user is happy, neutral, or surprised, adjusting its tone accordingly. |
| **Gesture Control** | Recognizes "STOP" (Hand Palm) to interrupt speech and "THUMBS_UP" for confirmation. |

### 🗣️ Communication & Knowledge
| Feature | Description |
| :--- | :--- |
| **Always-On Assistant** | Wake word activation ("OMNIS") with a conversation mode that allows follow-up questions without repeating the name. |
| **MGM Knowledge Base** | A dedicated database of 25+ school-specific topics (Founding 1983, Principal Dr Pooja S, Digital Libraries, etc.). |
| **Hybrid AI Engine** | Uses local rule-matching for speed and **Google Gemini 1.5** for complex, general reasoning. |
| **Dynamic Memory** | Remembers the user's last conversation topic to provide personalized follow-ups later ("I hope that thing about [topic] went well!"). |

### 🤖 Hardware & Execution
- **Architecture**: Powered by a **Raspberry Pi** and **Python 3.10**.
- **Robotic Control**: Servo-controlled head for active face tracking and expressive nodding.
- **Audio System**: Advanced ALSA-based audio processing with Edge-TTS for human-like voice synthesis.

---

## ❓ Frequently Asked Questions (For Journalists)

**Q: Does OMNIS need internet to work?**
A: For school-specific questions and face recognition, it works completely offline. Internet is only required for general knowledge queries via Gemini.

**Q: Is student data safe?**
A: Yes. All face encodings are stored locally on the robot in a secure, binary format. No images are uploaded to the cloud.

**Q: Can anyone add their face?**
A: OMNIS has an admin-only registration script to ensure only authorized individuals are added to its memory.
