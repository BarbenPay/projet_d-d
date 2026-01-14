# This files contains your custom actions which can be used to run
# custom Python code.

import os
import time
import psutil
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, ActiveLoop
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction

_llm_instance = None

def get_llm():
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    print("⏳ Initialisation du chargement du LLM...")

    mem_before = print_memory_usage("Avant chargement du modèle")
    
    try:
        from llama_cpp import Llama
    except ImportError:
        print("DEBUG: llama-cpp-python n'est pas installé.")
        return None

    # --- CHANGEMENT ICI ---
    # On pointe maintenant vers le dossier monté "/app/models"
    model_path = "/app/models/qwen2.5-3b-instruct-q4_k_m.gguf"

    if not os.path.exists(model_path):
        print(f"DEBUG: Modèle introuvable à l'emplacement : {model_path}")
        # Petit debug pour t'aider si ça plante
        print(f"Contenu de /app/models : {os.listdir('/app/models') if os.path.exists('/app/models') else 'Dossier inexistant'}")
        return None

    try:
        _llm_instance = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=6,
            verbose=False
        )

        mem_after = print_memory_usage("Après chargement du modèle")

        diff = mem_after - mem_before

        print(f"DEBUG: Poids estimé du modèle en RAM : {diff:.2f} MB")

        print(f"DEBUG: Modèle chargé avec succès depuis {model_path}")
        return _llm_instance
    except Exception as e:
        print(f"DEBUG: Impossible de charger le modèle : {e}")
        return None
    

def print_memory_usage(step_name=""):
    process = psutil.Process(os.getpid())
    ram_mb = process.memory_info().rss / 1024 / 1024 
    print(f"DEBUG: Mémoire consommée par le LLM {step_name} : {ram_mb:.2f} MB utilisés")
    return ram_mb

dictWeaponPossibilityDependingClass = {
            "paladin": ["épée longue", "marteau", "bouclier", "masse", "épée"],
            "barbare": ["hache", "épée longue", "marteau", "masse"],
            
            "roublard": ["dague", "arc", "épée"],
            "rôdeur": ["arc", "dague", "hache", "épée longue"],
            "moine": ["bâton", "dague"],

            "magicien": ["bâton", "orbe"],
            "sorcier": ["orbe", "bâton", "dague"],
            "druide": ["bâton", "masse"],

            "barde": ["luth", "dague", "épée", "arc"]
                           }

dictClassAbilities = {
    "paladin": {
        "name": "Gardien Divin",
        "desc": "Confère +1 CA aux alliés adjacents lorsqu'il tient un bouclier."
    },
    "barbare": {
        "name": "Instinct Feral",
        "desc": "Inflige +2 dégâts quand les PV sont sous 50%."
    },
    "roublard": {
        "name": "Coup Bas",
        "desc": "La première attaque du combat inflige des dégâts bonus."
    },
    "rôdeur": {
        "name": "Marque du Chasseur",
        "desc": "Les attaques consécutives sur la même cible infligent +2 dégâts."
    },
    "moine": {
        "name": "Flux de Ki",
        "desc": "Les attaques réussies augmentent les chances d'esquive de 10%."
    },
    "magicien": {
        "name": "Étude Arcanique",
        "desc": "Identifie les faiblesses ennemies en utilisant un orbe."
    },
    "sorcier": {
        "name": "Puissance Instable",
        "desc": "Relance les dés de dégâts affichant 1 pour les sorts."
    },
    "druide": {
        "name": "Toucher de la Nature",
        "desc": "Régénération passive de 2 PV par tour."
    },
    "barde": {
        "name": "Mélodie Inspirante",
        "desc": "Les alliés gagnent +1 en Attaque quand le Barde tient un luth."
    }
}

dictSubraceDependingRace = {
    "elfe" : ["haut", "bois"],
    "nain" : ["collines", "montagnes"],
    "gnome" : ["roches", "forêts", "cavernes"],
    "drakéide" : ["métallique", "gemme", "sang-dragon"],
    "drow" : ["profondeurs", "surface"]
}

dictNaturalAbilityFromSubrace = {
    "haut": "Esprit Vif : Vous connaissez un petit tour de magie pratique (lumière ou étincelle).",
    "bois": "Pied Léger : Vous pouvez vous déplacer en forêt sans faire de bruit.",
    
    "collines": "Ténacité Naine : Vous êtes plus robuste et encaissez mieux les coups.",
    "montagnes": "Force Brute : Vous êtes habitué au port d'armures lourdes sans fatigue.",

    "roches": "Bricoleur : Vous savez réparer de petits objets mécaniques ou serrures.",
    "forêts": "Langage des Bêtes : Les petits animaux (écureuils, oiseaux) vous font naturellement confiance.",
    "cavernes": "Vision des Ténèbres Supérieure : Vos yeux voient dans le noir total comme en plein jour.",

    "profondeurs": "Maître des Araignées : Vivant dans les grottes profondes, les araignées sont vos alliées.",
    "surface": "Magie Lumineuse : Vivant à la surface, vous créez des lumières magiques pour vous guider.",

    "métallique": "Souffle de Dragon : Vous pouvez cracher du feu ou de la glace une fois par jour.",
    "gemme": "Télépathie : Vous pouvez envoyer des pensées simples dans l'esprit des autres.",
    "sang-dragon": "Présence Royale : Les gens vous écoutent plus attentivement grâce à votre charisme."
}

class ActionCheckWeapon(Action):
    
    def name(self) -> Text:
        return "action_check_weapon"
    
    def run(self,dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        player_class = tracker.get_slot("class")
        player_weapon = tracker.get_slot("weapon")
        
        if not player_class or not player_weapon:
            dispatcher.utter_message(text="Il manque des informations pour vérifier l'équipement.")
            return []
        
        if player_weapon not in dictWeaponPossibilityDependingClass.get(player_class):
            dispatcher.utter_message(text=f"Un {player_class} ne peut pas choisir : {player_weapon} !")
            return [SlotSet("weapon", None)]
        else:
            dispatcher.utter_message(text=f"Parfait ! Votre {player_class} est équipé avec : {player_weapon}.")
            return []
        
class ActionAskWeapon(Action):
    
    def name(self) -> Text:
        return "action_ask_weapon"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        player_class = tracker.get_slot("class")
        weapons = dictWeaponPossibilityDependingClass.get(player_class, ["sword", "shield"])
        
        # Affichage texte simple des options
        options_display = ", ".join([w.capitalize() for w in weapons])

        dispatcher.utter_message(
            text=f"En tant que {player_class}, choisissez votre arme ({options_display}) :"
        )

        return []
    
class ActionAskSubrace(Action):
    def name(self) -> Text:
        return "action_ask_subrace"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        player_race = tracker.get_slot("race")
        print(f"DEBUG: Race reçue = '{player_race}'")
        
        if not player_race:
            dispatcher.utter_message(text="Impossible de déterminer votre race actuelle.")
            return []

        subraces_list = dictSubraceDependingRace.get(player_race.lower(), [])
        
        message_text = f"En tant que {player_race}, choisissez votre héritage :\n\n"
        dispatcher.utter_message(text=message_text)
        
        for subrace_key in subraces_list:
            message_text = ""
            description = dictNaturalAbilityFromSubrace.get(subrace_key, "Capacité inconnue")
            display_title = subrace_key.capitalize()
            message_text += f"🔹 **{display_title}**: {description}\n"
            dispatcher.utter_message(text=message_text)

        return []
    
class ActionAskClassWithAbility(Action):
    def name(self) -> Text:
        # Renommé pour correspondre au slot 'class'
        return "action_ask_class"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message_text = f"Choisissez une classe dans la liste ci-dessous :\n\n"
        dispatcher.utter_message(text=message_text)
        
        for class_key, class_data in dictClassAbilities.items():
            message_text = ""
            description = class_data.get("desc", "Description inconnue")
            display_title = class_data.get("name", "Nom inconnu").capitalize()
            message_text += f"🔹 **{class_key.capitalize()}** ({display_title}): {description}\n"
            dispatcher.utter_message(text=message_text)
        return []

class ActionAskRace(Action):
    def name(self) -> Text:
        return "action_ask_race"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        available_races = list(dictSubraceDependingRace.keys())
        if "humain" not in available_races:
             available_races.append("humain")

        races_str = ", ".join([r.capitalize() for r in available_races])
        
        dispatcher.utter_message(
            text=f"Choisissez une race pour votre personnage ({races_str}) :"
        )

        return []
    
class ValidateCaracterCreationForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_caracter_creation_form"

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Text]:
        
        print("DEBUG: Ordre forcé pour le form sinon ça demande par ordre alphabétique") 
        return ["race", "subrace", "class", "weapon", "attribute"]
    
    def validate_race(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        available = list(dictSubraceDependingRace.keys()) + ["humain"]
        if slot_value.lower() not in available:
            dispatcher.utter_message(text=f"Race inconnue. Choix: {', '.join(available)}")
            return {"race": None}
        return {"race": slot_value}

    def validate_subrace(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        race = tracker.get_slot("race")
        if race == "humain":
             return {"subrace": "None", "ability_subrace": "Polyvalent : +1 à toutes les statistiques."}
             
        valid = dictSubraceDependingRace.get(race, [])
        if slot_value.lower() not in valid and valid:
            dispatcher.utter_message(text=f"Choix impossibles pour {race}. Essayez: {', '.join(valid)}")
            return {"subrace": None}
            
        # AUTOMATISATION : On récupère la capacité ici
        ability = dictNaturalAbilityFromSubrace.get(slot_value.lower(), "Aucune")
        
        return {"subrace": slot_value, "ability_subrace": ability}

    def validate_class(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        if slot_value.lower() not in dictClassAbilities:
            dispatcher.utter_message(text="Classe inconnue.")
            return {"class": None}
        
        # AUTOMATISATION : On récupère la capacité de classe ici
        info = dictClassAbilities.get(slot_value.lower())
        ability = f"{info['name']}: {info['desc']}"
        
        return {"class": slot_value, "ability_class": ability}
    
    def validate_weapon(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        p_class = tracker.get_slot("class")
        allowed = dictWeaponPossibilityDependingClass.get(p_class, [])
        if slot_value.lower() not in allowed and allowed:
            dispatcher.utter_message(text=f"Un {p_class} ne peut pas utiliser {slot_value}. Choix: {', '.join(allowed)}")
            return {"weapon": None}
        return {"weapon": slot_value}

    def validate_attribute(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        if len(slot_value) < 2:
            dispatcher.utter_message(text="Attribut invalide.")
            return {"attribute": None}
        return {"attribute": slot_value}
        
    
class ValidateAdventureForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_adventure_form"

    async def validate_adventure_text(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        llm = get_llm()

        if llm is None:
            dispatcher.utter_message(text="[Système] Le Narrateur n'est pas connecté (Erreur chargement modèle).")
            return {"adventure_text": None}
        
        print("DEBUG: Lancement du llm")



        theme = tracker.get_slot("theme") or "Médiéval Fantastique"
        difficulty = tracker.get_slot("difficulty") or "Normale"
        
        p_race = tracker.get_slot("race") or "Inconnu"
        p_subrace = tracker.get_slot("subrace") or ""
        p_class = tracker.get_slot("class") or "Aventurier"
        p_weapon = tracker.get_slot("weapon") or "Mains nues"
        p_attribute = tracker.get_slot("attribute") or "Aucun"
        p_abilities = tracker.get_slot("ability_class") + tracker.get_slot("ability_subrace")
        if isinstance(p_abilities, list):
            p_abilities = ", ".join(p_abilities)
        
        system_prompt = (
            f"Tu es un Maître du Donjon (MJ) expert pour un jeu de rôle textuel. \n"
            f"LANGUE DE RÉPONSE: Français. \n\n"
            f"--- PARAMÈTRES DE LA PARTIE ---\n"
            f"Thème: {theme}\n"
            f"Difficulté: {difficulty}\n"
            f"Nombre de joueurs: 1\n\n"
            f"--- FICHE PERSONNAGE ---\n"
            f"Race: {p_race} ({p_subrace})\n"
            f"Classe: {p_class}\n"
            f"Arme principale: {p_weapon}\n"
            f"Attribut majeur: {p_attribute}\n"
            f"Capacités spéciales: {p_abilities}\n\n"
            f"--- INSTRUCTIONS ---\n"
            f"1. Tu dois décrire l'action, l'environnement et les réactions des PNJ de manière immersive.\n"
            f"2. Prends en compte la difficulté ({difficulty}) pour décider si les actions du joueur réussissent ou échouent.\n"
            f"3. Sois concis : Ne fais pas de monologues trop longs (max 3-4 phrases).\n"
            f"4. Ne joue jamais à la place du joueur. Demande-lui ce qu'il fait ensuite."
        )

        events = [e for e in tracker.events if e['event'] in ['user', 'bot']]
        
        past_events = events[:-1][-20:] 

        history_text = ""
        for event in past_events:
            if event['event'] == 'user' and event.get('text'):
                history_text += f"<|start_header_id|>user<|end_header_id|>\n\n{event.get('text')}<|eot_id|>"
            elif event['event'] == 'bot' and event.get('text'):
                history_text += f"<|start_header_id|>assistant<|end_header_id|>\n\n{event.get('text')}<|eot_id|>"

        print(f"DEBUG: HISTORIQUE DE LA CONVERSATION : \n" + history_text)

        current_message = slot_value

        full_prompt = (
            f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            f"{system_prompt}<|eot_id|>\n"
            f"{history_text}"
            f"<|start_header_id|>user<|end_header_id|>\n\n"
            f"{current_message}<|eot_id|>\n"
            f"<|start_header_id|>assistant<|end_header_id|>\n\n"
        )

        print("DEBUG: Envoi au LLM...")
        
        try:
            start_time = time.time()
            output = llm(
                full_prompt,
                max_tokens=450,
                stop=["<|eot_id|>", "<|start_header_id|>"],
                echo=False,
                temperature=0.8,
                top_p=0.9
            )

            end_time = time.time()

            duration = end_time - start_time

            print(f"DEBUG: Génération terminée en {duration:.2f} secondes.")

            response_text = output['choices'][0]['text'].strip()
            
            dispatcher.utter_message(text=response_text)
            
        except Exception as e:
            print(f"ERREUR LLM : {e}")
            dispatcher.utter_message(text="Une perturbation magique brouille les sens du Maître du Donjon... (Erreur technique)")

        return {"adventure_text": None}