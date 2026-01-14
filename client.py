import requests
import json

# L'URL du webhook REST de Rasa (grâce au port 5005 qu'on vient d'ouvrir)
url = "http://localhost:5005/webhooks/rest/webhook"

# On définit un ID utilisateur fixe pour retrouver la conversation dans Rasa X
sender_id = "cf9146ffa1b74699950abc2af754df46"

print("--- Client Multimodal ---")
print("Appuyez sur 'Entrée' pour envoyer 'Hello' à Rasa.")
print("Tapez 'q' puis Entrée pour quitter.")

while True:
    user_input = input(">> ") # Attend que tu appuies sur Entrée

    if user_input.lower() == 'q':
        break

    # Le message qu'on veut envoyer automatiquement
    message = "Hello"

    payload = {
        "sender": sender_id,  # Identifiant unique de l'utilisateur
        "message": message    # Le texte à envoyer
    }

    try:
        # Envoi de la requête POST à Rasa
        response = requests.post(url, json=payload)
        
        # Vérification de la réponse du bot
        if response.status_code == 200:
            print(f"✅ Message '{message}' envoyé avec succès !")
            bot_responses = response.json()
            for bot_msg in bot_responses:
                print(f"🤖 Bot répond : {bot_msg.get('text')}")
        else:
            print(f"❌ Erreur : {response.status_code}")
            
    except Exception as e:
        print(f"Erreur de connexion : {e}")