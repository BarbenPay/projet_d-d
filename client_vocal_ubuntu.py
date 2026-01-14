import os
import sys
import time
import requests
import speech_recognition as sr
from ctypes import *

# --- 1. SUPPRESSION DES ERREURS ALSA (Pour nettoyer le terminal) ---
try:
    ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
    def py_error_handler(filename, line, function, err, fmt):
        pass
    c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
    asound = cdll.LoadLibrary('libasound.so.2')
    asound.snd_lib_error_set_handler(c_error_handler)
except:
    pass # Si ça rate, ce n'est pas grave, on aura juste des logs en plus

# --- 2. CONFIGURATION ---
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"
# Remplace par TON ID de conversation (celui qui marche dans le navigateur)
SENDER_ID = "452d439a1d974137b672302bed19264e" 

def send_to_rasa(text):
    if not text: return
    print(f"📤 Envoi de : '{text}'")
    try:
        response = requests.post(RASA_URL, json={"sender": SENDER_ID, "message": text})
        print("\n--- Réponse du Bot ---")
        for bot_msg in response.json():
            print(f"🤖 {bot_msg.get('text')}")
        print("----------------------\n")
    except Exception as e:
        print(f"❌ Erreur Rasa : {e}")

def record_audio():
    recognizer = sr.Recognizer()
    
    # On utilise le micro par défaut
    with sr.Microphone() as source:
        print("\n🤫  Ajustement du bruit ambiant (0.5s)...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        print("🎤  PARLEZ MAINTENANT ! (J'écoute...)")
        try:
            # On écoute pendant 5 secondes max
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("⏳  Analyse en cours...")
            
            # Transcription via Google
            # Change "en-US" en "fr-FR" si tu parles français
            text = recognizer.recognize_google(audio, language="en-US") 
            print(f"✅  J'ai entendu : \"{text}\"")
            return text
            
        except sr.WaitTimeoutError:
            print("⚠️  Temps écoulé (Silence)")
        except sr.UnknownValueError:
            print("⚠️  Je n'ai pas compris les mots")
        except sr.RequestError:
            print("❌  Problème de connexion internet")
        return None

# --- MAIN ---
if __name__ == "__main__":
    print("--- CLIENT VOCAL UBUNTU (SANS SUDO) ---")
    print(f"Session ID : {SENDER_ID}")
    
    while True:
        # On remplace keyboard.is_pressed par input()
        user_choice = input("👉 Appuyez sur [Entrée] pour parler (ou 'q' pour quitter) : ")
        
        if user_choice.lower() == 'q':
            break
            
        text = record_audio()
        if text:
            send_to_rasa(text)