# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

dictWeaponPossibilityDependingClass = {
            "paladin": ["longsword", "hammer", "shield", "mace", "sword"],
            "barbarian": ["axe", "longsword", "hammer", "mace"],
            
            "rogue": ["dagger", "bow", "sword"],
            "ranger": ["bow", "dagger", "axe", "longsword"],
            "monk": ["staff", "dagger"],

            "wizard": ["staff", "orb", "dagger"],
            "sorcerer": ["orb", "staff", "dagger"],
            "druid": ["staff", "mace"],

            "bard": ["luth", "dagger", "sword", "bow"]
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

        buttons = []
        for weapon in weapons:
            buttons.append({
                "title": weapon.capitalize(),
                "payload": f'/weapon{{"weapon": "{weapon}"}}'
            })

        dispatcher.utter_message(
            text=f"As a {player_class}, what weapon do you pick ?",
            buttons=buttons
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

        # Récupération de la liste
        subraces_list = dictSubraceDependingRace.get(player_race.lower(), [])
        
        print(f"DEBUG: Liste trouvée pour '{player_race}' = {subraces_list}")

        # --- CHANGEMENT ICI : On prépare du TEXTE et des BOUTONS (plus de carousel) ---
        
        # 1. On prépare le message d'intro
        message_text = f"As a {player_race}, choose your legacy:\n\n"
        
        buttons_list = []
        
        for subrace_key in subraces_list:
            # On récupère la description
            description = dictNaturalAbilityFromSubrace.get(subrace_key, "Unknown ability")
            display_title = subrace_key.replace("_gnome", "").replace("_drow", "").capitalize()

            # 2. On ajoute la description dans le TEXTE principal (pour que le joueur la lise)
            message_text += f"🔹 **{display_title}**: {description}\n"

            # 3. On crée un bouton simple
            buttons_list.append({
                "title": f"Select {display_title}", 
                "payload": f'/subrace{{"subrace": "{subrace_key}"}}'
            })

        if not buttons_list:
            dispatcher.utter_message(text=f"No subrace available for {player_race}.")
            return []

        # 4. On envoie le tout : Texte détaillé + Boutons en bas
        dispatcher.utter_message(text=message_text, buttons=buttons_list)

        return []