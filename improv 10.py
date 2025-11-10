import os
import json
import uuid
import smtplib
from time import ctime, sleep
from gtts import gTTS
import playsound
import speech_recognition as sr
import webbrowser
import requests
import wikipedia
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox, scrolledtext
from itertools import cycle
load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
CONTACTS_FILE = "contacts.json"
def load_contacts():
    if os.path.exists(CONTACTS_FILE):
        with open(CONTACTS_FILE, "r") as f:
            return json.load(f)
    return {}
def save_contacts():
    with open(CONTACTS_FILE, "w") as f:
        json.dump(contacts, f, indent=4)
contacts = load_contacts()
root = tk.Tk()
root.title("🤖 Aravind's Smart Assistant")
root.geometry("750x580")
root.configure(bg="#0f111a")
header = tk.Canvas(root, width=750, height=100, highlightthickness=0)
header.pack()
for i, color in enumerate(["#0078D7", "#0063B1", "#004E8C", "#003B6F"]):
    header.create_rectangle(0, i * 25, 750, (i + 1) * 25, outline="", fill=color)
header.create_text(375, 50, text="🎙️ Aravind's Smart Assistant", fill="white", font=("Segoe UI", 22, "bold"))
chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20,
                                     bg="#1e1f29", fg="#ffffff", font=("Consolas", 11), bd=0)
chat_box.pack(padx=15, pady=10)
chat_box.config(state=tk.DISABLED)
def log_message(sender, message, color="#00FFFF"):
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, f"{sender}: ", "sender")
    chat_box.insert(tk.END, f"{message}\n\n", "message")
    chat_box.tag_config("sender", foreground=color, font=("Segoe UI", 10, "bold"))
    chat_box.tag_config("message", foreground="white")
    chat_box.config(state=tk.DISABLED)
    chat_box.see(tk.END)
def respond(text):
    log_message("🤖 Assistant", text)
    tts = gTTS(text=text, lang='en')
    filename = f"voice_{uuid.uuid4()}.mp3"
    tts.save(filename)
    sleep(0.3)
    try:
        playsound.playsound(filename)
    except Exception as e:
        log_message("⚠️ Error", f"Sound issue: {e}", color="#FF5555")
    finally:
        if os.path.exists(filename):
            os.remove(filename)
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        log_message("🎤", "Listening...")
        animate_listen(True)
        audio = r.listen(source, phrase_time_limit=5)
        animate_listen(False)
    try:
        text = r.recognize_google(audio, language='en-US')
        log_message("🗣 You", text, color="#FFD700")
        return text.lower()
    except sr.UnknownValueError:
        respond("I couldn’t understand that.")
        return ""
    except sr.RequestError:
        respond("Network error while recognizing speech.")
        return ""
def get_weather(city="Melbourne"):
    api_key = "your_openweathermap_api_key_here"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url).json()
        if response.get("main"):
            temp = response["main"]["temp"]
            desc = response["weather"][0]["description"]
            return f"The weather in {city} is {desc} with {temp}°C."
        else:
            return "Sorry, I couldn't fetch the weather right now."
    except Exception:
        return "Failed to fetch weather due to network error."
def send_email():
    global contacts
    respond("Who should I send the email to?")
    to_name = listen()
    if not to_name:
        return
    if to_name not in contacts:
        respond(f"I don't have an email for {to_name}. Please provide their email.")
        to_email = listen()
        if not to_email:
            return
        contacts[to_name] = to_email
        save_contacts()
        respond(f"Added {to_name} to contacts.")
    else:
        to_email = contacts[to_name]
    respond("What is the subject?")
    subject = listen()
    respond("What should I say?")
    body = listen()
    content = f"Subject: {subject}\n\n{body}"
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as mail:
            mail.starttls()
            mail.login(EMAIL_USER, EMAIL_PASS)
            mail.sendmail(EMAIL_USER, to_email, content)
        respond(f"Email sent to {to_name} successfully!")
    except Exception as e:
        respond(f"Failed to send email: {e}")
def virtual_assistant(command):
    if not command:
        return
    if "how are you" in command:
        respond("I'm doing great, thanks for asking!")
    elif "time" in command:
        respond(f"The current time is {ctime()}")
    elif "open google" in command:
        respond("Opening Google...")
        webbrowser.open("https://www.google.com")
    elif "weather" in command:
        respond("Which city?")
        city = listen()
        respond(get_weather(city))
    elif "wikipedia" in command:
        topic = command.replace("wikipedia", "").strip()
        if not topic:
            respond("What should I search on Wikipedia?")
            topic = listen()
        try:
            summary = wikipedia.summary(topic, sentences=2)
            respond(summary)
        except Exception:
            respond("I couldn't find anything about that.")
    elif "email" in command:
        send_email()
    elif "youtube" in command or "video" in command:
        respond("Which video would you like to watch?")
        video = listen()
        if video:
            respond(f"Opening {video} on YouTube.")
            webbrowser.open(f"https://www.youtube.com/results?search_query={video}")
    elif "song" in command or "music" in command:
        respond("Which song should I play?")
        song = listen()
        if song:
            respond(f"Playing {song} on YouTube Music.")
            webbrowser.open(f"https://music.youtube.com/search?q={song}")
    elif "locate" in command:
        place = command.replace("locate", "").strip()
        if place:
            respond(f"Locating {place} on Google Maps...")
            webbrowser.open(f"https://www.google.com/maps/search/{place}")
        else:
            respond("Please tell me the location.")
    elif any(word in command for word in ["exit", "quit", "bye", "stop"]):
        respond("Goodbye Aravind! Have a great day!")
        root.destroy()
    else:
        respond("I'm not sure about that, could you repeat?")
button_frame = tk.Frame(root, bg="#0f111a")
button_frame.pack(pady=15)
def hover_effect(widget, enter_color, leave_color):
    widget.bind("<Enter>", lambda e: widget.config(bg=enter_color))
    widget.bind("<Leave>", lambda e: widget.config(bg=leave_color))
def start_listening():
    command = listen()
    virtual_assistant(command)
def show_weather():
    respond(get_weather("Melbourne"))
def exit_app():
    respond("Goodbye Aravind! Take care!")
    root.destroy()
buttons = [
    ("🎤 Listen", start_listening),
    ("🌤️ Weather", show_weather),
    ("📧 Email", send_email),
    ("❌ Exit", exit_app),
]
for text, cmd in buttons:
    btn = tk.Button(button_frame, text=text, command=cmd, bg="#0078D7", fg="white",
                    font=("Segoe UI", 12, "bold"), relief="raised", width=14, height=2, bd=0)
    hover_effect(btn, "#005A9E", "#0078D7")
    btn.pack(side=tk.LEFT, padx=10)
listen_label = tk.Label(root, text="", font=("Segoe UI", 16), bg="#0f111a", fg="#00FFFF")
listen_label.pack()
wave_frames = cycle(["•     ", "••    ", "•••   ", "••••  ", "••••• ", "••••••", "••••• ", "••••  ", "•••   ", "••    "])
animating = False
def animate_listen(start=False):
    global animating
    animating = start
    if not start:
        listen_label.config(text="")
        return
    def animate():
        if animating:
            listen_label.config(text=next(wave_frames))
            root.after(150, animate)
    animate()
respond("Hey Aravind, I'm ready to help you!")
root.mainloop()