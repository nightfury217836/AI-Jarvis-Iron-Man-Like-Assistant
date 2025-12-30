import os
import random
import webbrowser
import datetime
import json
import pickle
import pyautogui
import pyttsx3
import speech_recognition as sr
import numpy as np
import wikipedia
import requests
import subprocess
import pyaudio
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import warnings
import time

warnings.filterwarnings("ignore")

# ========== INITIAL SETUP ==========
with open("intents.json") as file:
    intents = json.load(file)

model = load_model("chat_model.h5")
with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)
with open("label_encoder.pkl", "rb") as encoder_file:
    label_encoder = pickle.load(encoder_file)

max_len = 20


# ========== SPEAK FUNCTION ==========
def speak(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)  # you can switch between [0] male / [1] female

        print(f"JASMINE: {text}")
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        del engine
        time.sleep(0.1)
    except Exception as e:
        print(f"[ERROR in speak()]: {e}")

# ========== LISTEN FUNCTION (UPGRADED) ==========
def listen_command():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source: 
        print("🎧  LISTENING... Please speak")
        recognizer.pause_threshold = 3
        audio = recognizer.listen(source, phrase_time_limit=6)

    try:
        print("\n🌀 Processing your voice...")
        print("🎤 Recognizing speech...")

        query = recognizer.recognize_google(audio, language='en-IN')
        print(f"🗣️ You said: ⭐ {query} ⭐")
        return query.lower()

    except sr.UnknownValueError:
        print("\n⚠️  Could not understand. Please try again.")
        speak("Sorry, I didn't catch that. Please say again.")
        return ""

    except Exception as e:
        print("\n💥 Error:", e)
        speak("Sorry, I’m having trouble understanding you right now.")
        return ""


# ========== INTENT PREDICTION ==========
def predict_intent(text):
    sequence = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(sequence, truncating='post', maxlen=max_len)
    predictions = model.predict(padded, verbose=0)[0]
    tag_index = np.argmax(predictions)
    confidence = predictions[tag_index]

    if confidence < 0.6:
        return "noanswer", "Sorry, I didn't get that."

    tag = label_encoder.inverse_transform([tag_index])[0]
    for intent in intents["intents"]:
        if intent["tag"] == tag:
            response = random.choice(intent["responses"])
            return tag, response

    return "noanswer", "Sorry, I didn't understand that."


# ========== COMMAND EXECUTION ==========
def execute_command(tag, query):
    if tag == "datetime":
        now = datetime.datetime.now()
        speak(f"The time is {now.strftime('%I:%M %p')} and today is {now.strftime('%A, %d %B %Y')}.")

    elif tag == "open_browser":
        speak("Opening browser...")
        os.system("start chrome")

    elif tag == "search_web":
        search_term = query.replace("search for", "").replace("google", "").strip()
        if search_term:
            speak(f"Searching for {search_term}")
            webbrowser.open(f"https://www.google.com/search?q={search_term}")
        else:
            speak("What should I search for?")

    elif tag == "youtube_search":
        speak("Opening YouTube...")
        search_term = query.replace("play", "").replace("on youtube", "").strip()
        webbrowser.open(f"https://www.youtube.com/results?search_query={search_term}")

    elif tag == "open_app":
        speak("Opening the requested application...")
        if "notepad" in query:
            os.system("notepad")
        elif "calculator" in query:
            os.system("calc")
        elif "command prompt" in query:
            os.system("start cmd")
        elif "word" in query:
            os.system("start winword")
        elif "excel" in query:
            os.system("start excel")
        elif "vs code" in query or "visual studio" in query:
            os.system("code")
        elif "spotify" in query:
            os.system("start spotify")
        else:
            speak("App not recognized, Boss.")

    elif tag == "close_tab":
        speak("Closing current tab.")
        pyautogui.hotkey('ctrl', 'w')

    elif tag == "volume_up":
        speak("Increasing volume.")
        for _ in range(5):
            pyautogui.press("volumeup")

    elif tag == "volume_down":
        speak("Decreasing volume.")
        for _ in range(5):
            pyautogui.press("volumedown")

    elif tag == "mute_volume":
        pyautogui.press("volumemute")
        speak("Muted volume.")

    elif tag == "unmute_volume":
        pyautogui.press("volumemute")
        speak("Unmuted volume.")

    elif tag == "system_control":
        if "shutdown" in query:
            speak("Shutting down your PC.")
            os.system("shutdown /s /t 1")
        elif "restart" in query:
            speak("Restarting your PC.")
            os.system("shutdown /r /t 1")
        elif "lock" in query:
            speak("Locking your PC.")
            os.system("rundll32.exe user32.dll,LockWorkStation")
        elif "sleep" in query:
            speak("Putting PC to sleep.")
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])

    elif tag == "weather":
        speak("Fetching the weather...")
        try:
            res = requests.get("https://wttr.in/?format=3")
            speak(res.text)
        except:
            speak("Unable to fetch weather at the moment.")

    elif tag == "wikipedia":
        speak("Searching Wikipedia...")
        query = query.replace("who is", "").replace("what is", "").replace("tell me about", "").strip()
        try:
            result = wikipedia.summary(query, sentences=2)
            speak(result)
        except:
            speak("Sorry, I couldn't find details on that topic.")

    elif tag == "news":
        speak("Opening latest news headlines.")
        webbrowser.open("https://news.google.com/")

    elif tag == "reminder":
        speak("Okay, what should I remind you about?")
        reminder = listen_command()
        speak(f"Reminder noted: {reminder}")

    elif tag == "take_note":
        speak("What should I write down?")
        note = listen_command()
        with open("jarvis_notes.txt", "a") as f:
            f.write(f"{datetime.datetime.now()} - {note}\n")
        speak("Note saved successfully.")

    elif tag == "goodbye":
        speak("Goodbye Boss. Powering off now.")
        exit()

    else:
        pass


# ========== MAIN LOOP  ==========
def main():
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🤖 JASMINE AI ASSISTANT ONLINE")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    speak("Hello Boss, Jasmine is online and fully operational.")

    while True:
        query = listen_command()

        if query == "":
            print("🔁 Waiting for next command...\n")
            continue

        print("\n🧠 Processing your request...")
        tag, response = predict_intent(query)

        print(f"💬 Jasmine: {response}")
        speak(response)

        print("⚙️ Executing command...\n")
        execute_command(tag, query)

        print("💡 Ready for your next command!\n")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")



if __name__ == "__main__":
    main()
