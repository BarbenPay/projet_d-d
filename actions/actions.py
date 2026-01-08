# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
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
    "gnome" : ["rock", "forest", "deep"],
    "drakeide" : ["steel", "gem", "dragonblood"],
    "drow" : ["deep", "surface"]
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

        player_class = tracker.get_slot("classe")

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

        armes_disponibles = dictWeaponPossibilityDependingClass.get(classe_actuelle, ["sword", "shield"])

        buttons = []
        for arme in armes_disponibles:
            buttons.append({
                "title": arme.capitalize(),
                "payload": f'/weapon{{"arme": "{arme}"}}'
            })

        dispatcher.utter_message(
            text=f"As a {classe_actuelle}, what weapon do you pick ?",
            buttons=buttons
        )

        return []
