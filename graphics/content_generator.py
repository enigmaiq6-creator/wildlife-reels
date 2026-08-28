import os
import json
import random
from typing import Dict, Any, List, Optional, Tuple
import urllib.request
import urllib.error

class ContentGenerator:
    """
    Curated and Dynamic AI Content Generator for Wild Vault Multi-Format Graphics.
    - 100% in English
    - Extreme animal curiosities, bizarre evolutionary adaptations, prehistoric beasts, and deep sea mysteries.
    - Strict anti-repetition mechanism.
    - Dynamic Groq / Gemini AI fallback for infinite fresh wildlife topics.
    """

    FORMAT_TYPES = [
        "format_1_taxonomic_catalog",
        "format_2_real_vs_illustrated",
        "format_3_curiosity_pip",
        "format_5_creature_profile",
        "format_6_vintage_guide",
        "format_7_breaking_news",
        "format_8_quad_collage"
    ]

    CURATED_TOPICS = {
        "format_1_taxonomic_catalog": [
            {
                "topic_id": "CATALOG-OWLS",
                "title": "8 Types of Owls Around the World",
                "species": [
                    {"name": "Eurasian Eagle Owl", "scientific": "Bubo bubo", "prompt": "Eurasian eagle owl isolated studio portrait black background"},
                    {"name": "Barn Owl", "scientific": "Tyto alba", "prompt": "barn owl isolated studio portrait black background"},
                    {"name": "Snowy Owl", "scientific": "Bubo scandiacus", "prompt": "snowy owl pure white isolated studio portrait black background"},
                    {"name": "Stygian Owl", "scientific": "Asio stygius", "prompt": "stygian owl red eyes isolated studio portrait black background"},
                    {"name": "Little Owl", "scientific": "Athene noctua", "prompt": "little owl isolated studio portrait black background"},
                    {"name": "Great Horned Owl", "scientific": "Bubo virginianus", "prompt": "great horned owl isolated studio portrait black background"},
                    {"name": "African Scops Owl", "scientific": "Otus senegalensis", "prompt": "african scops owl isolated studio portrait black background"},
                    {"name": "Blakiston's Fish Owl", "scientific": "Ketupa blakistoni", "prompt": "blakiston fish owl isolated studio portrait black background"}
                ],
                "caption": "🦉 Owls possess specialized comb-like serrations on their flight feathers that break up air turbulence into micro-currents, muffling sound and rendering their silent flight undetectable to prey.\n\nWhich of these species looks the most magnificent? Drop a comment and follow Wild Vault for daily wildlife discoveries!"
            },
            {
                "topic_id": "CATALOG-BIG-CATS",
                "title": "8 Apex Big Cats of Planet Earth",
                "species": [
                    {"name": "Amazon Jaguar", "scientific": "Panthera onca", "prompt": "amazon jaguar isolated studio portrait black background"},
                    {"name": "Bengal Tiger", "scientific": "Panthera tigris", "prompt": "bengal tiger isolated studio portrait black background"},
                    {"name": "Snow Leopard", "scientific": "Panthera uncia", "prompt": "snow leopard isolated studio portrait black background"},
                    {"name": "African Lion", "scientific": "Panthera leo", "prompt": "african male lion mane isolated studio portrait black background"},
                    {"name": "Cheetah", "scientific": "Acinonyx jubatus", "prompt": "cheetah isolated studio portrait black background"},
                    {"name": "Black Panther", "scientific": "Panthera pardus", "prompt": "black panther melanistic leopard isolated studio portrait black background"},
                    {"name": "Cougar", "scientific": "Puma concolor", "prompt": "mountain lion cougar isolated studio portrait black background"},
                    {"name": "Clouded Leopard", "scientific": "Neofelis nebulosa", "prompt": "clouded leopard isolated studio portrait black background"}
                ],
                "caption": "🐆 Big cats have evolved some of the highest relative bite forces in the animal kingdom. The jaguar, for example, delivers over 1,500 psi—enough to puncture armored turtle shells and caiman skulls directly.\n\nWhich big cat is your favorite? Follow Wild Vault for daily predator facts!"
            },
            {
                "topic_id": "CATALOG-CHAMELEONS",
                "title": "8 Bizarre Species of Chameleons",
                "species": [
                    {"name": "Parson's Chameleon", "scientific": "Calumma parsonii", "prompt": "giant parson chameleon isolated studio portrait black background"},
                    {"name": "Panther Chameleon", "scientific": "Furcifer pardalis", "prompt": "vibrant rainbow panther chameleon isolated studio portrait black background"},
                    {"name": "Veiled Chameleon", "scientific": "Chamaeleo calyptratus", "prompt": "veiled chameleon casqued head isolated studio portrait black background"},
                    {"name": "Jackson's Chameleon", "scientific": "Trioceros jacksonii", "prompt": "three horned jackson chameleon isolated studio portrait black background"},
                    {"name": "Labord's Chameleon", "scientific": "Furcifer labordi", "prompt": "labord chameleon isolated studio portrait black background"},
                    {"name": "Carpet Chameleon", "scientific": "Furcifer lateralis", "prompt": "colorful carpet chameleon isolated studio portrait black background"},
                    {"name": "Nose-Horned Chameleon", "scientific": "Calumma nasutum", "prompt": "pinocchio nose horned chameleon isolated studio portrait black background"},
                    {"name": "Pygmy Leaf Chameleon", "scientific": "Brookesia micra", "prompt": "tiny miniature leaf chameleon on matchstick isolated studio portrait black background"}
                ],
                "caption": "🦎 Chameleons don't just change color for camouflage—they use rapid structural photonics in their iridophore cells to signal mood, territorial dominance, and body temperature. Their ballistic tongues accelerate faster than a fighter jet!\n\nFollow Wild Vault to explore nature's most bizarre adaptations!"
            }
        ],
        "format_2_real_vs_illustrated": [
            {
                "topic_id": "SPLIT-SHARK-DIVER",
                "prompt_real": "scuba diver carefully examining open mouth of wild shark underwater turquoise clear ocean sand bottom high resolution photography",
                "prompt_illustrated": "anime comic style ghibli illustration of friendly shark with wide open mouth getting teeth inspected by anime scuba diver cute funny dialogue bubble underwater reef",
                "dialogue": "A bit lower, right there!",
                "caption": "🦈 In ocean cleaning stations, apex sharks will slow down and open their jaws wide to allow cleaner fish (and brave researchers) to remove parasites and hooks.\n\nWould you ever dare to inspect a shark's teeth? Follow Wild Vault!"
            },
            {
                "topic_id": "SPLIT-CAPYBARA-CROCODILE",
                "prompt_real": "wild capybara calmly sitting right next to giant caiman crocodile in river bank sunbathing high detail nature photography",
                "prompt_illustrated": "funny anime style illustration of chill capybara sitting on top of confused crocodile friendly cute anime expressions pastel colors",
                "dialogue": "Can we be friends?",
                "caption": "🐾 Capybaras emit exceptionally low threat cues, putting even aggressive reptiles at ease. Their calm social demeanor has earned them the title of the world's most diplomatic animal.\n\nFollow Wild Vault for daily wildlife curiosities!"
            },
            {
                "topic_id": "SPLIT-HONEY-BADGER-LIONS",
                "prompt_real": "fierce fearless honey badger confronting a pride of adult lions in african savanna high detail action wildlife photography",
                "prompt_illustrated": "funny comic illustration of tiny furious honey badger yelling at three shocked nervous lions cute anime style",
                "dialogue": "You picked the wrong neighborhood!",
                "caption": "🦡 The honey badger's rubbery, thick skin is nearly impervious to bee stings, porcupine quills, and predator fangs. Their loose skin allows them to twist around and bite back even when clamped in a lion's jaws.\n\nFollow Wild Vault to meet nature's bravest brawler!"
            }
        ],
        "format_3_curiosity_pip": [
            {
                "topic_id": "PIP-ECLYSE-ZEBROID",
                "prompt_main": "rare real zorse eclyse animal hybrid zebra and white horse walking in green meadow full body ultra realistic photography",
                "prompt_pip": "close up face stripes of zebra horse hybrid grazing grass detailed macro photography",
                "badge": "RARE HYBRID",
                "headline": [
                    "ECLYSE IS A RARE HYBRID",
                    "BORN FROM A ZEBRA",
                    "AND A WHITE HORSE"
                ],
                "caption": "🦓 Eclyse is a famous 'zorse' born from an Italian safari park mating. Unlike typical zedonks, her genetics caused melanin expression only in distinct patches, leaving her center torso completely white.\n\nHave you ever seen a hybrid like this? Follow Wild Vault for rare animal discoveries!"
            },
            {
                "topic_id": "PIP-STYGIAN-OWL",
                "prompt_main": "stygian owl with eerie glowing red eyes perched on dark jungle tree branch nighttime atmospheric wildlife photography",
                "prompt_pip": "night vision thermal view of demonic looking stygian owl in pitch black forest close up glowing eyes",
                "badge": "NIGHT STALKER",
                "headline": [
                    "THE STYGIAN OWL HAS",
                    "A GLOWING RED GAZE",
                    "THAT LOOKS SUPERNATURAL"
                ],
                "caption": "👁️ The Stygian Owl (*Asio stygius*) reflects ambient light through rich blood vessels behind its retina, resulting in glowing crimson eyes that gave rise to ancient vampire folklore in Central and South America.\n\nFollow Wild Vault for dark wildlife mysteries!"
            },
            {
                "topic_id": "PIP-GLASS-FROG",
                "prompt_main": "translucent glass frog clinging to green jungle leaf macro shot showing beating heart and internal organs photography",
                "prompt_pip": "ultra close up macro shot of crystal clear translucent belly of glass frog with visible beating red heart",
                "badge": "LIVING CRYSTAL",
                "headline": [
                    "THE GLASS FROG HAS",
                    "TRANSPARENT SKIN THAT",
                    "REVEALS ITS BEATING HEART"
                ],
                "caption": "🐸 Glass frogs possess completely translucent abdominal skin. When resting on leaves, light passes directly through their bodies, making their silhouettes virtually invisible to predatory birds below.\n\nNature's camouflage is unmatched! Follow Wild Vault!"
            },
            {
                "topic_id": "PIP-BARRELEYE-FISH",
                "prompt_main": "macropinna microstoma barreleye fish with transparent fluid filled dome head glowing green tubular eyes deep sea dark ocean",
                "prompt_pip": "macro detail of barreleye fish glowing green tubular lenses inside transparent head",
                "badge": "DEEP SEA ALIEN",
                "headline": [
                    "THE BARRELEYE FISH",
                    "HAS A TRANSPARENT HEAD",
                    "AND EYES THAT ROTATE INSIDE"
                ],
                "caption": "🐟 Macropinna microstoma lives in pitch-black depths between 2,000 to 2,600 feet. Its glowing emerald-green eyes can rotate upwards through its clear forehead dome to track siphonophore silhouettes in the water column above.\n\nFollow Wild Vault to explore Earth's deep ocean aliens!"
            }
        ],
        "format_5_creature_profile": [
            {
                "topic_id": "PROFILE-NAUTILUS",
                "prompt": "nautilus living fossil swimming deep blue coral ocean macro shot high detail 8k photography",
                "title": "The Nautilus",
                "paragraphs": [
                    {"text": "A living fossil that has survived"},
                    {"text": "over 500 million years unchanged."},
                    {"text": "Its spiral shell contains internal chambers"},
                    {"text": "filled with gas to regulate buoyancy"},
                    {"text": "just like a submarine."}
                ],
                "caption": "🐚 The Nautilus predates the first dinosaurs by over 250 million years. Its buoyant gas chambers are connected by a living tube called a siphuncle that pumps water out to adjust diving depth.\n\nFollow Wild Vault for ancient living legends!"
            },
            {
                "topic_id": "PROFILE-COELACANTH",
                "prompt": "ancient coelacanth prehistoric fish swimming dark deep underwater abyss rare wildlife macro photography",
                "title": "The Coelacanth",
                "paragraphs": [
                    {"text": "Believed to have gone extinct"},
                    {"text": "66 million years ago with dinosaurs,"},
                    {"text": "until a live specimen was discovered in 1938"},
                    {"text": "off the coast of South Africa."}
                ],
                "caption": "🐟 Coelacanths possess electrosensory rostral organs and fleshy lobed fins containing bone structures identical to early land tetrapods, offering a direct window into evolutionary history.\n\nFollow Wild Vault for more living fossils!"
            },
            {
                "topic_id": "PROFILE-SHOEBILL",
                "prompt": "shoebill stork giant grey bird intense prehistoric look staring forward swamp background 8k photography",
                "title": "The Shoebill",
                "paragraphs": [
                    {"text": "Stands up to 5 feet tall and hunts lungfish"},
                    {"text": "with a colossal razor-sharp shoe beak."},
                    {"text": "It can stand completely motionless for hours,"},
                    {"text": "striking prey with the speed of an alligator."}
                ],
                "caption": "🦅 The Shoebill Stork (*Balaeniceps rex*) sounds like a machine gun when clattering its beak to communicate. It routinely decapitates baby crocodiles and 3-foot lungfish in Ugandan papyrus swamps.\n\nFollow Wild Vault for Earth's most formidable birds!"
            }
        ],
        "format_6_vintage_guide": [
            {
                "topic_id": "VINTAGE-DANGEROUS-FISH",
                "title": "The 9 Most Dangerous Fish on Earth",
                "species": [
                    {"name": "Pufferfish", "sci": "Takifugu rubripes", "desc": "Contains lethal tetrodotoxin", "prompt": "pufferfish isolated studio portrait white background"},
                    {"name": "Stonefish", "sci": "Synanceia verrucosa", "desc": "Master of venomous camouflage", "prompt": "stonefish camouflaged isolated studio portrait white background"},
                    {"name": "Lionfish", "sci": "Pterois volitans", "desc": "Painful neurotoxic dorsal spines", "prompt": "lionfish fins spread isolated studio portrait white background"},
                    {"name": "River Stingray", "sci": "Potamotrygon motoro", "desc": "Venomous barbed tail stinger", "prompt": "freshwater stingray spotted isolated studio portrait white background"},
                    {"name": "Great Barracuda", "sci": "Sphyraena barracuda", "desc": "Razor-sharp predatory strike", "prompt": "great barracuda fish isolated studio portrait white background"},
                    {"name": "Great White Shark", "sci": "Carcharodon carcharias", "desc": "Apex ocean predator with 300 teeth", "prompt": "great white shark head isolated studio portrait white background"},
                    {"name": "Electric Eel", "sci": "Electrophorus electricus", "desc": "Discharges up to 860 volts", "prompt": "electric eel fish isolated studio portrait white background"},
                    {"name": "Candiru Catfish", "sci": "Vandellia cirrhosa", "desc": "Parasitic blood feeder of Amazon", "prompt": "candiru vampire fish isolated studio portrait white background"},
                    {"name": "Waspfish", "sci": "Ablabys taenianotus", "desc": "Potent paralytic toxins", "prompt": "cockatoo waspfish isolated studio portrait white background"}
                ],
                "caption": "🌊 Aquatic life has engineered remarkable chemical defenses and mechanical weapons. The stonefish alone delivers verrucotoxin powerful enough to cause cardiac arrest within hours if left untreated.\n\nWhich of these 9 fish intimidates you the most? Follow Wild Vault!"
            },
            {
                "topic_id": "VINTAGE-DEADLIEST-SNAKES",
                "title": "The 9 Deadliest Venomous Snakes",
                "species": [
                    {"name": "Inland Taipan", "sci": "Oxyuranus microlepidotus", "desc": "Most toxic venom of any reptile", "prompt": "inland taipan snake head isolated studio portrait white background"},
                    {"name": "Black Mamba", "sci": "Dendroaspis polylepis", "desc": "Lightning fast with deadly neurotoxins", "prompt": "black mamba open mouth isolated studio portrait white background"},
                    {"name": "King Cobra", "sci": "Ophiophagus hannah", "desc": "World's longest venomous serpent", "prompt": "king cobra hood spread isolated studio portrait white background"},
                    {"name": "Saw-scaled Viper", "sci": "Echis carinatus", "desc": "Causes more bites than any other viper", "prompt": "saw scaled viper coiled isolated studio portrait white background"},
                    {"name": "Coastal Taipan", "sci": "Oxyuranus scutellatus", "desc": "Highly aggressive with long fangs", "prompt": "coastal taipan snake isolated studio portrait white background"},
                    {"name": "Boomslang", "sci": "Dispholidus typus", "desc": "Rear-fanged hemotoxic predator", "prompt": "green boomslang snake isolated studio portrait white background"},
                    {"name": "Russell's Viper", "sci": "Daboia russelii", "desc": "Potent cytotoxins causing necrosis", "prompt": "russell viper isolated studio portrait white background"},
                    {"name": "Dubois Sea Snake", "sci": "Aipysurus duboisii", "desc": "Most venomous marine snake", "prompt": "dubois sea snake swimming isolated studio portrait white background"},
                    {"name": "Fer-de-Lance", "sci": "Bothrops asper", "desc": "Terrifying pit viper of rainforests", "prompt": "fer de lance snake head isolated studio portrait white background"}
                ],
                "caption": "🐍 A single bite from the Inland Taipan packs enough specialized neurotoxins to neutralize 100 adult humans in 45 minutes. Fortunately, it rarely encounters people in its remote Australian desert home.\n\nFollow Wild Vault for daily wildlife breakdowns!"
            }
        ],
        "format_7_breaking_news": [
            {
                "topic_id": "NEWS-PURUSSAURUS",
                "prompt": "giant prehistoric purussaurus crocodile 12 meters long attacking huge rodent in ancient amazon swamp cinematic prehistoric scene",
                "headline": "Fossils reveal a giant 40-foot prehistoric caiman hunted 4,000-pound mammals in the ancient Amazon 12 million years ago",
                "caption": "🦖 Purussaurus was the uncontested ruler of Miocene South America. Its robust skull and serrated teeth were built to crush thick carapace armor of giant prehistoric turtles and massive astrapotheres.\n\nFollow Wild Vault to explore Earth's ancient apex predators!"
            },
            {
                "topic_id": "NEWS-TITANOBOA",
                "prompt": "massive prehistoric titanoboa snake 14 meters long coiled around giant ancient turtle in tropical swamp photorealistic cinematic",
                "headline": "Scientists confirm Titanoboa measured over 45 feet long and ruled ancient tropical jungles swallowing giant crocodilians whole",
                "caption": "🐍 Titanoboa thrived in the ultra-warm greenhouse climate 60 million years ago. Its immense girth measured over 3 feet in diameter, allowing it to constrict with 400 psi of pressure.\n\nFollow Wild Vault for deep prehistoric history!"
            },
            {
                "topic_id": "NEWS-MEGALODON-BLUBBER",
                "prompt": "colossal megalodon shark 65 feet long hunting giant ancient whale in open ocean cinematic dramatic lighting underwater",
                "headline": "New biomechanical study reveals Megalodon could swim faster than modern sharks and consume entire killer whales in a single bite",
                "caption": "🦈 3D modeling of Megalodon's stomach volume indicates it could consume a 26-foot killer whale in just a few bites, giving it enough caloric reserves to traverse thousands of miles across prehistoric oceans without eating for months.\n\nFollow Wild Vault for more ocean giant discoveries!"
            }
        ],
        "format_8_quad_collage": [
            {
                "topic_id": "QUAD-TITANS",
                "title": "4 Titans with a Deadly Gaze",
                "prompts": [
                    "andean condor giant head close up menacing stare 8k wildlife photography",
                    "shoebill stork terrifying prehistoric stare looking directly at camera 8k",
                    "harpy eagle giant raptor intense predator eyes close up 8k photography",
                    "southern cassowary dinosaur bird blue neck glowing eyes staring forward 8k"
                ],
                "caption": "🦅 These 4 avian apex creatures have preserved the intense predatory gaze of their theropod ancestors. Their talon force, wingspan, and razor vision dominate the skies and wetlands.\n\nWhich of these 4 looks the most intimidating? Vote in the comments and follow Wild Vault!"
            },
            {
                "topic_id": "QUAD-PREHISTORIC-SURVIVORS",
                "title": "4 Prehistoric Survivors Alive Today",
                "prompts": [
                    "horseshoe crab blue blood ancient armor walking on wet sand 8k macro photography",
                    "tuatara reptile with third parietal eye new zealand ancient rock 8k photography",
                    "komodo dragon giant lizard venomous saliva flicking tongue 8k photography",
                    "alligator gar prehistoric armored fish sharp teeth swimming clear river 8k photography"
                ],
                "caption": "🦕 These 4 extraordinary animals have walked and swam the Earth unchanged for hundreds of millions of years, surviving multiple mass extinctions that wiped out the dinosaurs.\n\nWhich living fossil fascinates you most? Follow Wild Vault!"
            }
        ]
    }

    @classmethod
    def get_random_topic(cls, format_type: Optional[str] = None, seen_topic_ids: Optional[List[str]] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Selects a unique format and topic, strictly preventing any repetition of seen_topic_ids.
        If all curated topics for a format are exhausted, it automatically falls back to an unused format.
        """
        seen_set = set(seen_topic_ids or [])

        # 1. Collect all unused topics across all formats
        all_unused = []
        for f_type, topic_list in cls.CURATED_TOPICS.items():
            if format_type and f_type != format_type:
                continue
            for t in topic_list:
                if t.get("topic_id") not in seen_set:
                    all_unused.append((f_type, t))

        # 2. Pick an unused topic
        if all_unused:
            chosen_format, chosen_topic = random.choice(all_unused)
            return chosen_format, chosen_topic

        # 3. If all curated are exhausted, pick topics that are NOT in the recent 30 publications
        recent_30 = set(list(seen_topic_ids or [])[-30:])
        not_recent = []
        for f_type, topic_list in cls.CURATED_TOPICS.items():
            if format_type and f_type != format_type:
                continue
            for t in topic_list:
                if t.get("topic_id") not in recent_30:
                    not_recent.append((f_type, t))
        if not_recent:
            chosen_format, chosen_topic = random.choice(not_recent)
            return chosen_format, chosen_topic

        # Fallback total: pick any random topic
        chosen_format = format_type or random.choice(cls.FORMAT_TYPES)
        topic_list = cls.CURATED_TOPICS.get(chosen_format, cls.CURATED_TOPICS["format_3_curiosity_pip"])
        chosen_topic = random.choice(topic_list)
        return chosen_format, chosen_topic
