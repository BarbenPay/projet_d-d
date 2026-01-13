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

try:
    from llama_cpp import Llama
    print("Librairie llama-cpp-python chargée avec succès.")
except ImportError:
    print("Erreur: llama-cpp-python n'est pas installé.")
    Llama = None
    
MODEL_PATH = "./models/Meta-Llama-3.1-8B-Instruct-Q3_K_M.gguf"

llm = None
if Llama:
    try:
        llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=2048,
            n_threads=4,
            verbose=False
        )
        print(f"Modèle chargé depuis {MODEL_PATH}")
    except Exception as e:
        print(f"Impossible de charger le modèle : {e}")

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

        subraces_list = dictSubraceDependingRace.get(player_race.lower(), [])
        
        print(f"DEBUG: Liste trouvée pour '{player_race}' = {subraces_list}")


        message_text = f"As a {player_race}, choose your legacy:\n\n"
        
        
        for subrace_key in subraces_list:

            description = dictNaturalAbilityFromSubrace.get(subrace_key, "Unknown ability")
            display_title = subrace_key.capitalize()

            message_text += f"🔹 **{display_title}**: {description}\n"

        return []
    
class ActionAskClassWithAbility(Action):
    def name(self) -> Text:
        return "action_ask_race_with_ability"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


        message_text = f"Choose a class (paladin, rogue, wizard, druid, monk, barbarian, bard, ranger, sorcerer).\n\n"
        
        buttons_list = []
        
        for class_key, class_data in dictClassAbilities.items():

            description = class_data.get("desc", "Unknown description")
            display_title = class_data.get("name", "Unknown name").capitalize()

            message_text += f"🔹 **{display_title}**: {description}\n\n"


            buttons_list.append({
                "title": f"Select {display_title}", 
                "payload": f'/race{{"race": "{class_key}"}}'
            })


        dispatcher.utter_message(
            text=message_text, 
            buttons=buttons_list
            )

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
        
    
class askLLM(Action):
    def name(self) -> Text:
        return "action_ask_LLM"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        player_race = tracker.get_slot("race")
        player_subrace = tracker.get_slot("subrace")
        player_class = tracker.get_slot("class")
        player_weapon = tracker.get_slot("weapon")
        player_attributes = tracker.get_slot("attributes")
        player_abilities = tracker.get_slot("abilities")
        
        current_message = tracker.latest_message.get('text')
        
        
        if not llm:
            dispatcher.utter_message(text="Désolé, le modèle d'IA n'est pas disponible pour le moment.")
        
        character_context = ""
        if player_race and player_subrace:
            character_context += f"Le joueur incarne un {player_race}, sa sous-race est {player_subrace}. Cela lui apporte la capacité {dictNaturalAbilityFromSubrace.get(player_subrace)}"
        if player_class and player_weapon:
            character_context += f"Le joueur a choisis la classe {player_class}. Il a également choisis comme arme principal un(e) {player_weapon}. Cela lui apporte la capacité de base {player_abilities}."
        
        system_prompt = (
            "Tu es un Maître de donjon expert en Dongeon & Dragon. "
            "Répond de manière immersive, brève et direct."
            f"{character_context}"
        )
        
        conversation_history = ""
        
        relevant_events = [e for e in tracker.events if e['event'] in ['user', 'bot']]
        recent_events = relevant_events[-10:]
        
        if relevant_events and relevant_events[-1].get('text') == current_message:
            events_to_process = relevant_events[:-1][-10:]
        else:
            events_to_process = relevant_events[-10:]
        
        for event in events_to_process:
            if event['event'] == 'user' and event.get('text'):
                conversation_history += f"<|start_header_id|>user<|end_header_id|>\n\n{event.get('text')}<|eot_id|>"
            
            elif event['event'] == 'bot' and event.get('text'):
                conversation_history += f"<|start_header_id|>assistant<|end_header_id|>\n\n{event.get('text')}<|eot_id|>"
                
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
                    {system_prompt}
                    <|eot_id|>
                    
                    {conversation_history}
                    
                    <|start_header_id|>user<|end_header_id|>
                    {current_message}
                    <|start_header_id|>assistant<|end_header_id|>
                    """
                    
        if 'llm' not in globals() or llm is None:
             dispatcher.utter_message(text="Le LLM est indisponible.")
             return []
         
        
        output = llm(
            prompt,
            max_tokens=350,
            stop=["<|eot_id|>", "user:"],
            echo=False,
            temperature=0.7 
        )
        
        response_text = output['choices'][0]['text'].strip()
        dispatcher.utter_message(text=response_text)

        return []