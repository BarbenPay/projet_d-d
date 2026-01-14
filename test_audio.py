import pyttsx3

print("Initialisation...")
engine = pyttsx3.init()

# On force le volume au max
engine.setProperty('volume', 1.0) 

print("Tentative de parole...")
engine.say("Ceci est un test audio sur Ubuntu.")
engine.runAndWait()

print("Fin du script.")