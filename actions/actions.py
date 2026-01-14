# This files contains your custom actions which can be used to run
# custom Python code.

import os
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
    
    try:
        from llama_cpp import Llama
    except ImportError:
        print("❌ Erreur : llama-cpp-python n'est pas installé.")
        return None

    # --- CHANGEMENT ICI ---
    # On pointe maintenant vers le dossier monté "/app/models"
    model_path = "/app/models/Llama-3.2-3B-Instruct-Q4_K_M.gguf"

    if not os.path.exists(model_path):
        print(f"❌ Erreur : Modèle introuvable à l'emplacement : {model_path}")
        # Petit debug pour t'aider si ça plante
        print(f"Contenu de /app/models : {os.listdir('/app/models') if os.path.exists('/app/models') else 'Dossier inexistant'}")
        return None

    try:
        _llm_instance = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=4,
            verbose=False
        )
        print(f"✅ Modèle chargé avec succès depuis {model_path}")
        return _llm_instance
    except Exception as e:
        print(f"❌ Impossible de charger le modèle : {e}")
        return None

dictWeaponPossibilityDependingClass = {
            "paladin": ["longsword", "hammer", "shield", "mace", "sword"],
            "barbarian": ["axe", "longsword", "hammer", "mace"],
            
            "rogue": ["dagger", "bow", "sword"],
            "ranger": ["bow", "dagger", "axe", "longsword"],
            "monk": ["staff", "dagger"],

            "wizard": ["staff", "orb"],
            "sorcerer": ["orb", "staff", "dagger"],
            "druid": ["staff", "mace"],

            "bard": ["luth", "dagger", "sword", "bow"]
                           }

dictClassAbilities = {
    "paladin": {
        "name": "Divine Guardian",
        "desc": "Grants +1 AC to adjacent allies when holding a Shield."
    },
    "barbarian": {
        "name": "Feral Instinct",
        "desc": "Deals +2 damage when HP is below 50%."
    },
    "rogue": {
        "name": "Cheap Shot",
        "desc": "First attack of combat deals bonus damage."
    },
    "ranger": {
        "name": "Hunter's Mark",
        "desc": "Consecutive attacks on the same target deal +2 damage."
    },
    "monk": {
        "name": "Flow of Ki",
        "desc": "Successful attacks increase Dodge chance by 10%."
    },
    "wizard": {
        "name": "Arcane Study",
        "desc": "Identifies enemy weaknesses using an Orb."
    },
    "sorcerer": {
        "name": "Unstable Power",
        "desc": "Re-roll damage results of 1 on spells."
    },
    "druid": {
        "name": "Nature's Touch",
        "desc": "Passive health regeneration of 2 HP per turn."
    },
    "bard": {
        "name": "Inspiring Tune",
        "desc": "Allies gain +1 Attack when the Bard holds a Luth."
    }
}

dictSubraceDependingRace = {
    "elf" : ["high", "wood"],
    "dwarf" : ["hill", "mountain"],
    "gnome" : ["rock", "forest", "cave"],
    "dragonborn" : ["metallic", "gem", "dragonblood"],
    "drow" : ["deep", "surface"]
}

dictNaturalAbilityFromSubrace = {
    "high": "Keen Mind: You know a handy little magic trick (light or small spark).",
    "wood": "Fleet of Foot: You can move through the forest without making a sound.",
    
    "hill": "Dwarven Toughness: You are hardier and can take more hits than others.",
    "mountain": "Brute Strength: You are accustomed to wearing heavy armor without fatigue.",

    "rock": "Tinker: You know how to repair small mechanical objects or locks.",
    "forest": "Speak with Small Beasts: Small animals (squirrels, birds) naturally trust you.",
    "cave": "Superior Darkvision: Your eyes see in total darkness as if it were day.",

    "deep": "Spider Master: Living in deep caves, spiders are your allies.",
    "surface": "Light Magic: Living above ground, you create magical lights to guide you.",

    "metallic": "Dragon Breath: You can exhale fire or ice once a day.",
    "gem": "Telepathy: You can send simple thoughts into the minds of others.",
    "draconblood": "Royal Presence: People listen to you more attentively thanks to your charisma."
}

# --- Actions ---

class ActionHelloWorld(Action):

     def name(self) -> Text:
         return "action_hello_world"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

         dispatcher.utter_message(text="Hello World!")
         return []
     
class ActionCheckWeapon(Action):
    
    def name(self) -> Text:
        return "action_check_weapon"
    
    def run(self,dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        player_class = tracker.get_slot("class")
        player_weapon = tracker.get_slot("weapon")
        
        if not player_class or not player_weapon:
            dispatcher.utter_message(text="It misses some informations to verify the equipments.")
            return []
        
        if player_weapon not in dictWeaponPossibilityDependingClass.get(player_class):
            dispatcher.utter_message(text=f"A {player_class} can not pick a {player_weapon} !")
            return [SlotSet("weapon", None)]
        else:
            dispatcher.utter_message(text=f"Alright ! Your {player_class} is stuffed with a {player_weapon}.")
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
            text=f"As a {player_class}, choose your weapon ({options_display}):"
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
            dispatcher.utter_message(text="Cannot determine your current race.")
            return []

        subraces_list = dictSubraceDependingRace.get(player_race.lower(), [])
        
        message_text = f"As a {player_race}, choose your legacy:\n\n"
        
        for subrace_key in subraces_list:
            description = dictNaturalAbilityFromSubrace.get(subrace_key, "Unknown ability")
            display_title = subrace_key.capitalize()
            message_text += f"🔹 **{display_title}**: {description}\n"
        
        # CORRECTION BUG: L'envoi du message manquait ici !
        dispatcher.utter_message(text=message_text)

        return []
    
class ActionAskClassWithAbility(Action):
    def name(self) -> Text:
        # Renommé pour correspondre au slot 'class'
        return "action_ask_class"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message_text = f"Choose a class from the list below:\n\n"
        
        for class_key, class_data in dictClassAbilities.items():
            description = class_data.get("desc", "Unknown description")
            display_title = class_data.get("name", "Unknown name").capitalize()
            # On affiche tout en texte
            message_text += f"🔹 **{class_key.capitalize()}** ({display_title}): {description}\n"

        dispatcher.utter_message(text=message_text)

        return []
    
    
class ActionFillAllTheSlot(Action):
    def name(self) -> Text:
        return "action_fill_all_the_slot"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        player_class = tracker.get_slot("class")
        player_subrace = tracker.get_slot("subrace")
        
        abilities_found = []

        if player_class:
            class_key = player_class.lower()
            class_data = dictClassAbilities.get(class_key)
            if class_data:
                ability_str = f"Class Ability ({class_data['name']}): {class_data['desc']}"
                abilities_found.append(ability_str)

        if player_subrace:
            subrace_key = player_subrace.lower()
            subrace_data = dictNaturalAbilityFromSubrace.get(subrace_key)
            if subrace_data:
                ability_str = f"Racial Ability: {subrace_data}"
                abilities_found.append(ability_str)

        if not abilities_found:
             dispatcher.utter_message(text="I couldn't determine your abilities yet. Please select a class and subrace first.")
        else:
             msg = "Abilities updated:\n" + "\n".join([f"- {a}" for a in abilities_found])
             dispatcher.utter_message(text=msg)

        return [SlotSet("abilities", abilities_found)]
    

class ActionAskRace(Action):
    def name(self) -> Text:
        return "action_ask_race"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        available_races = list(dictSubraceDependingRace.keys())
        if "human" not in available_races:
             available_races.append("human")

        # Affichage texte simple
        races_str = ", ".join([r.capitalize() for r in available_races])
        
        dispatcher.utter_message(
            text=f"Choose a race for your character ({races_str}):"
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
        
        print("DEBUG: Je force l'ordre des slots via Python !") 
        return ["race", "subrace", "class", "weapon", "attribute"]
    
    def validate_race(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        available = list(dictSubraceDependingRace.keys()) + ["human"]
        if slot_value.lower() not in available:
            dispatcher.utter_message(text=f"Race inconnue. Choix: {', '.join(available)}")
            return {"race": None}
        return {"race": slot_value}

    def validate_subrace(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        race = tracker.get_slot("race")
        # Gestion des humains ou races sans sous-race
        if race == "human":
             return {"subrace": "None", "ability_subrace": "Versatile: +1 to all stats."}
             
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
        # Validation simple (accepte tout tant que ce n'est pas vide)
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

        # 1. Récupération du LLM via la fonction (qui le charge si besoin)
        llm = get_llm()

        if llm is None:
            dispatcher.utter_message(text="[Système] Le Narrateur n'est pas connecté (Erreur chargement modèle).")
            # Astuce : On laisse adventure_text à None pour rester dans la boucle même en cas d'erreur
            return {"adventure_text": None}
        

        theme = tracker.get_slot("theme") or "Médiéval Fantastique"
        difficulty = tracker.get_slot("difficulty") or "Normale"
        nb_players = tracker.get_slot("nb_players") or "1"
        language = tracker.get_slot("language") or "Français"
        
        # Fiche personnage
        p_race = tracker.get_slot("race") or "Inconnu"
        p_subrace = tracker.get_slot("subrace") or ""
        p_class = tracker.get_slot("class") or "Aventurier"
        p_weapon = tracker.get_slot("weapon") or "Mains nues"
        p_attribute = tracker.get_slot("attribute") or "Aucun"
        # On essaie de récupérer les capacités si le slot existe, sinon chaîne vide
        p_abilities = tracker.get_slot("abilities") 
        if isinstance(p_abilities, list):
            p_abilities = ", ".join(p_abilities)
        
        # 3. Construction du Prompt Système (Le "Cerveau" du DM)
        # On lui donne toutes les billes pour qu'il soit cohérent.
        system_prompt = (
            f"Tu es un Maître du Donjon (MJ) expert pour un jeu de rôle textuel. \n"
            f"LANGUE DE RÉPONSE: {language}. \n\n"
            f"--- PARAMÈTRES DE LA PARTIE ---\n"
            f"Thème: {theme}\n"
            f"Difficulté: {difficulty}\n"
            f"Nombre de joueurs: {nb_players}\n\n"
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

        # 4. Fenêtre Glissante (Sliding Window) de l'historique
        # On récupère les événements, on filtre pour n'avoir que User et Bot
        events = [e for e in tracker.events if e['event'] in ['user', 'bot']]
        
        # On garde les 10 derniers échanges (donc 20 messages max : 10 users + 10 bots)
        # On exclut le tout dernier message utilisateur car il sera ajouté juste après dans le prompt
        past_events = events[:-1][-20:] 

        history_text = ""
        for event in past_events:
            if event['event'] == 'user' and event.get('text'):
                history_text += f"<|start_header_id|>user<|end_header_id|>\n\n{event.get('text')}<|eot_id|>"
            elif event['event'] == 'bot' and event.get('text'):
                # On évite de remettre les messages techniques de Rasa s'il y en a
                history_text += f"<|start_header_id|>assistant<|end_header_id|>\n\n{event.get('text')}<|eot_id|>"

        # 5. Message actuel de l'utilisateur
        current_message = slot_value

        # 6. Assemblage du Prompt Final (Format Llama 3)
        full_prompt = (
            f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            f"{system_prompt}<|eot_id|>\n"
            f"{history_text}"
            f"<|start_header_id|>user<|end_header_id|>\n\n"
            f"{current_message}<|eot_id|>\n"
            f"<|start_header_id|>assistant<|end_header_id|>\n\n"
        )

        print("DEBUG: Envoi au LLM...") # Utile pour voir si ça bloque
        
        try:
            output = llm(
                full_prompt,
                max_tokens=400,       # Un peu plus de place pour la narration
                stop=["<|eot_id|>", "<|start_header_id|>"], # Stop tokens stricts pour Llama 3
                echo=False,
                temperature=0.7,      # Créatif mais pas délirant
                top_p=0.9
            )
            response_text = output['choices'][0]['text'].strip()
            
            # Envoi de la réponse au joueur
            dispatcher.utter_message(text=response_text)
            
        except Exception as e:
            print(f"ERREUR LLM : {e}")
            dispatcher.utter_message(text="Une perturbation magique brouille les sens du Maître du Donjon... (Erreur technique)")

        # 7. IMPORTANT : Reset du slot pour la boucle infinie
        return {"adventure_text": None}