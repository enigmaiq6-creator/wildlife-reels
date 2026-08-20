from typing import Dict, Any, List

WILDLIFE_CATALOG: Dict[str, Dict[str, Any]] = {
    "jaguar_hunter": {
        "topic_id": "JAGUAR-JUNGLE-HUNTER",
        "title": "5 Insane Facts About the World's Strongest Cat Bite!",
        "hook": "The jaguar has the most powerful bite of any big cat on Earth!",
        "curiosities": [
            "Number one: Its jaws can easily crush a turtle shell and pierce thick skull bones in a single bite.",
            "Number two: Unlike other big cats who dislike water, jaguares are champion swimmers and hunt underwater.",
            "Number three: They stalk their prey in total silence using special soft pads on their massive paws.",
            "Number four: The unique spots on their fur are like human fingerprints, with no two jaguars ever looking identical.",
            "Number five: Ancient civilizations worshipped them as sacred guardians of the night and kings of the jungle."
        ],
        "cta": "Who would win: a Jaguar or an African Lion? Drop your vote in the comments and follow for more!",
        "pexels_keywords": [
            "jaguar in jungle 4k vertical",
            "jaguar hunting water 4k",
            "jaguar swimming river vertical",
            "jaguar walking rainforest vertical",
            "jaguar eyes close up 4k",
            "wild jaguar resting branch 4k",
            "amazon rainforest wildlife vertical"
        ],
        "hashtags": ["#jaguar", "#wildlife", "#predators", "#animals", "#nature", "#bigcats"]
    },
    "killer_whale_orca": {
        "topic_id": "ORCA-APEX-OCEAN-KING",
        "title": "5 Reasons Why Orcas Rule the Entire Ocean!",
        "hook": "Not even the Great White Shark dares to challenge an Orca in the open ocean!",
        "curiosities": [
            "Number one: Orcas are actually the largest and smartest members of the oceanic dolphin family.",
            "Number two: Each family pod has its own unique vocal dialect passed down across generations.",
            "Number three: To hunt Great White Sharks, orcas flip them upside down to paralyze them instantly.",
            "Number four: They work as a team to create giant waves that wash seals off floating ice sheets.",
            "Number five: In the wild, female killer whales can live for over 90 years."
        ],
        "cta": "Did you know wild orcas have never harmed a human? Comment your thoughts below and subscribe!",
        "pexels_keywords": [
            "killer whale orca ocean 4k vertical",
            "orca breaching waves vertical",
            "orca pod swimming underwater 4k",
            "great white shark swimming 4k",
            "orca iceberg arctic vertical",
            "ocean predator wildlife 4k",
            "killer whale close up underwater vertical"
        ],
        "hashtags": ["#orcas", "#killerwhales", "#ocean", "#wildlife", "#marinelife", "#predators"]
    },
    "harpy_eagle": {
        "topic_id": "HARPY-EAGLE-MONSTER-TALONS",
        "title": "5 Mind-Blowing Facts About the Harpy Eagle!",
        "hook": "This gigantic bird of prey has talons larger than a grizzly bear's claws!",
        "curiosities": [
            "Number one: Its rear talons can grow up to five inches long and exert devastating crushing force.",
            "Number two: It can lift monkeys and sloths that match its own body weight straight up into the trees.",
            "Number three: Its eyesight is eight times sharper than a human, spotting small prey from over 600 feet away.",
            "Number four: It has rounded wings designed to dodge thick tree branches at extreme flight speeds.",
            "Number five: Harpy eagles mate for life and build massive nests over five feet wide."
        ],
        "cta": "Could you imagine seeing this apex raptor in person? Tell us in the comments and follow for more!",
        "pexels_keywords": [
            "harpy eagle flight 4k vertical",
            "giant eagle talons close up 4k",
            "eagle perched tree rainforest vertical",
            "eagle hunting jungle canopy 4k",
            "bird of prey eyes 4k vertical",
            "rainforest canopy flight 4k",
            "wild eagle wings spread vertical"
        ],
        "hashtags": ["#harpyeagle", "#eagles", "#birdsofprey", "#wildlife", "#nature", "#animals"]
    },
    "colossal_squid": {
        "topic_id": "COLOSSAL-SQUID-DEEP-ABYSS",
        "title": "5 Terrifying Secrets of the Colossal Squid!",
        "hook": "In the pitch-black waters of Antarctica lives a deep sea monster with rotating swiveling claws!",
        "curiosities": [
            "Number one: The colossal squid is the heaviest invertebrate on Earth, weighing up to 1,100 pounds.",
            "Number two: It possesses the largest eyes in the animal kingdom, measuring the size of a dinner plate.",
            "Number three: Its tentacles feature razor-sharp rotating hooks that rip through thick prey.",
            "Number four: Its only natural rival is the Sperm Whale, clashing in epic battles over a mile deep.",
            "Number five: Its blood is blue because it uses copper-based molecules to carry oxygen in icy waters."
        ],
        "cta": "Would you ever dare to explore the deep ocean? Let us know in the comments and share this video!",
        "pexels_keywords": [
            "giant squid deep ocean underwater 4k vertical",
            "deep sea creature glowing underwater 4k",
            "sperm whale deep diving vertical",
            "dark abyss underwater ocean 4k",
            "squid tentacles moving underwater 4k",
            "antarctic ocean underwater ice vertical",
            "mysterious ocean depths 4k vertical"
        ],
        "hashtags": ["#colossalsquid", "#deepsea", "#oceanmonsters", "#wildlife", "#nature", "#abyss"]
    }
}

def get_wildlife_topic(topic_name: str) -> Dict[str, Any]:
    """Retrieves a wildlife topic from the predefined catalog."""
    key = topic_name.lower().replace("-", "_")
    return WILDLIFE_CATALOG.get(key, list(WILDLIFE_CATALOG.values())[0])

def get_all_wildlife_topics() -> List[str]:
    """Returns all keys from the Wildlife catalog."""
    return list(WILDLIFE_CATALOG.keys())
