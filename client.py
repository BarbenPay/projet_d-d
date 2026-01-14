import requests
import speech_recognition as sr
from ctypes import *

# Suppression des erreurs ALSA
try:
    ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
    def py_error_handler(filename, line, function, err, fmt): pass
    c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
    asound = cdll.LoadLibrary('libasound.so.2')
    asound.snd_lib_error_set_handler(c_error_handler)
except: pass

RASA_URL = "http://localhost:5005/webhooks/rest/webhook"
SENDER_ID = "client_user"
current_mode = "text"

def listen_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Parlez maintenant...")
        try:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=5)
            # Change "fr-FR" en "en-US" si tu parles anglais
            return r.recognize_google(audio, language="en-US")
        except:
            return None

print(f"Client lance. Mode : {current_mode}")

while True:
    if current_mode == "text":
        user_message = input("Votre message : ")
    else:
        input("Appuyez sur Entree pour activer le micro...")
        user_message = listen_audio()

    if not user_message: continue
    if user_message.lower() == "quit": break

    try:
        payload = {"sender": SENDER_ID, "message": user_message}
        resp = requests.post(RASA_URL, json=payload).json()

        for msg in resp:
            if "text" in msg:
                print(f"Bot: {msg['text']}")
            
            # Detection du changement de mode envoye par actions.py
            if "custom" in msg and "set_mode" in msg["custom"]:
                current_mode = msg["custom"]["set_mode"]
                print(f"--- Mode change : {current_mode} ---")

    except Exception as e:
        print(f"Erreur connexion: {e}")