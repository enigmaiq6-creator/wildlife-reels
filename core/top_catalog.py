from typing import Dict, Any, List

TOP_CATALOG: Dict[str, Dict[str, Any]] = {
    "top_camera_moments": {
        "topic_id": "TOP-3-SHOCKING-ANIMAL-MOMENTS",
        "title": "Top 3 Most Terrifying Animal Encounters Caught on Camera! 🐺📹",
        "hook": "Here are the top three most terrifying animal encounters ever caught on camera!",
        "items": [
            {
                "rank": 3,
                "badge": "#3: THE DINOSAUR STARE",
                "creature_name": "shoebill stork",
                "text": "Number three: The Shoebill Stork. Standing over five feet tall, this prehistoric bird remains completely motionless for hours before locking its cold dinosaur death stare directly into your soul.",
                "action_type": "death_stare_eyes"
            },
            {
                "rank": 2,
                "badge": "#2: THE OCEAN BREACH",
                "creature_name": "shark",
                "text": "Number two: The Great White Shark. Lurking in the dark depths below, it accelerates at twenty-five miles per hour into an explosive breach that launches thousands of pounds completely out of the water.",
                "action_type": "explosive_strike"
            },
            {
                "rank": 1,
                "badge": "#1: THE JUNGLE AMBUSH",
                "creature_name": "jaguar",
                "text": "Number one: The Amazon Jaguar. Armed with jaws strong enough to pierce alligator skulls, it stalks silently beneath river currents to drag massive caimans straight out of the water.",
                "action_type": "explosive_strike"
            }
        ],
        "climax_cta": "Which of these three encounters shocked you the most? Drop your vote in the comments and follow for daily wild moments!",
        "hashtags": ["#wildlife", "#animals", "#caughtoncamera", "#predators", "#nature", "#top3", "#shorts"]
    },
    "top_ocean_monsters": {
        "topic_id": "TOP-3-OCEAN-MONSTERS",
        "title": "Top 3 Deadliest Monsters of the Deep Ocean! 🌊🦈",
        "hook": "These are the top three most terrifying apex predators ruling the deep ocean!",
        "items": [
            {
                "rank": 3,
                "badge": "#3: THE BULLET STRIKE",
                "creature_name": "mantis shrimp",
                "text": "Number three: The Mantis Shrimp. Packing a punch with the same acceleration as a gunshot bullet, it boils the surrounding water and shatters thick crab shells in a fraction of a second.",
                "action_type": "explosive_strike"
            },
            {
                "rank": 2,
                "badge": "#2: THE GREAT WHITE",
                "creature_name": "shark",
                "text": "Number two: The Great White Shark. With over three hundred razor-sharp serrated teeth arranged in rotating rows, it detects the single heartbeat of a fish from miles away.",
                "action_type": "teeth_jaws"
            },
            {
                "rank": 1,
                "badge": "#1: THE KILLER ORCA",
                "creature_name": "orca",
                "text": "Number one: The Killer Orca. Weighing over ten tons with extreme intelligence, it hunts in calculated pods and delivers devastating tail slaps that even great whites flee from.",
                "action_type": "explosive_strike"
            }
        ],
        "climax_cta": "Who do you think is the true king of the sea? Drop your thought below and follow for more ocean beasts!",
        "hashtags": ["#ocean", "#shark", "#orca", "#deepsea", "#wildlife", "#top3", "#marinelife"]
    },
    "top_rainforest_predators": {
        "topic_id": "TOP-3-RAINFOREST-KILLERS",
        "title": "Top 3 Deadliest Hunters in the Amazon Rainforest! 🌴🐆",
        "hook": "Deep in the Amazon rainforest, these three apex predators rule without mercy!",
        "items": [
            {
                "rank": 3,
                "badge": "#3: THE SKY MISSILE",
                "creature_name": "harpy eagle",
                "text": "Number three: The Harpy Eagle. Armed with talons larger than a grizzly bear's claws, it glides silently through the dense canopy to snatch monkeys straight from the treetops.",
                "action_type": "explosive_strike"
            },
            {
                "rank": 2,
                "badge": "#2: THE DINOSAUR BIRD",
                "creature_name": "shoebill stork",
                "text": "Number two: The Shoebill Stork. Waiting in absolute silence in African swamps, its massive razor-sharp bill crushes lungfish and baby crocodiles in seconds.",
                "action_type": "death_stare_eyes"
            },
            {
                "rank": 1,
                "badge": "#1: THE RIVER PHANTOM",
                "creature_name": "jaguar",
                "text": "Number one: The Amazon Jaguar. Unlike other big cats who avoid water, it swims silently underwater to execute an armor-crushing bite directly into the skull of caimans.",
                "action_type": "explosive_strike"
            }
        ],
        "climax_cta": "Which rainforest hunter would you fear most in the dark? Tell us in the comments and subscribe for more!",
        "hashtags": ["#rainforest", "#amazon", "#jaguar", "#harpyeagle", "#wildlife", "#top3", "#nature"]
    }
}

def get_top_topic(topic_name: str) -> Dict[str, Any]:
    key = topic_name.lower().replace("-", "_")
    return TOP_CATALOG.get(key, list(TOP_CATALOG.values())[0])

def get_all_top_topics() -> List[str]:
    return list(TOP_CATALOG.keys())
