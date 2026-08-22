import random
from typing import Dict, Any, List, Optional, Tuple

class ContentGenerator:
    """
    Curated Content and AI Generator for Wild Vault Multi-Format Graphics.
    100% in English, scientific tone, high curiosity and viral engagement.
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

    # Curated High-Engagement Encyclopedia
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
                "caption": "🦉 Owls are widely considered the most silent and efficient nocturnal apex hunters on Earth. Their specialized serrated wing feathers eliminate air turbulence, allowing them to swoop down in total silence.\n\nWhich of these species looks the most magnificent to you? Drop a comment below and follow Wild Vault for daily wildlife discoveries!"
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
                "caption": "🐆 Big cats possess extraordinary bite force and agility. From the elusive ghost of the mountains (Snow Leopard) to the bone-crushing jaws of the Amazon Jaguar.\n\nWhich one is your ultimate favorite? Follow Wild Vault for breathtaking nature content every day!"
            }
        ],
        "format_2_real_vs_illustrated": [
            {
                "topic_id": "SPLIT-SHARK-DIVER",
                "prompt_real": "scuba diver carefully examining open mouth of wild shark underwater turquoise clear ocean sand bottom high resolution photography",
                "prompt_illustrated": "anime comic style ghibli illustration of friendly shark with wide open mouth getting teeth inspected by anime scuba diver cute funny dialogue bubble underwater reef",
                "dialogue": "A bit lower, right there!",
                "caption": "🦈 In the wild, sharks frequently visit underwater cleaning stations where cleaner fish (and occasionally marine researchers) inspect their teeth to remove parasites and hooked debris.\n\nDespite their fearsome reputation, they exhibit remarkable cooperative behaviors. Would you ever dare to dive with them? Follow Wild Vault!"
            },
            {
                "topic_id": "SPLIT-CAPYBARA-CROCODILE",
                "prompt_real": "wild capybara calmly sitting right next to giant caiman crocodile in river bank sunbathing high detail nature photography",
                "prompt_illustrated": "funny anime style illustration of chill capybara sitting on top of confused crocodile friendly cute anime expressions pastel colors",
                "dialogue": "Can we be friends?",
                "caption": "🐾 The capybara is universally crowned the chillest animal in the world. Their zen demeanor and minimal threat signals often confuse apex predators, allowing them to lounge side-by-side with wild caimans without any aggression.\n\nFollow Wild Vault to discover the strangest phenomena in the animal kingdom!"
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
                "caption": "🦓 Meet Eclyse, one of the world's most unique zorses. Born from the cross between a female zebra and a white horse, she inherited zebra stripes exclusively across her head and rear quarters, leaving her torso pure white.\n\nHave you ever seen a hybrid like this? Share your thoughts and follow Wild Vault!"
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
                "caption": "👁️ The Stygian Owl (*Asio stygius*) roams deep tropical rainforests. When flashlight beams reflect off its large retinas at night, they produce an intense fiery-red glow that fueled centuries of ghost folklore.\n\nFollow Wild Vault to explore the most mysterious creatures of the wild!"
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
                "caption": "🐚 The Nautilus is a cephalopod that outlived all 5 major mass extinctions on Earth, including the dinosaurs. Its logarithmic spiral shell is one of nature's greatest feats of biological engineering.\n\nDid you know this ancient creature is still roaming our oceans? Follow Wild Vault for more living legends!"
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
                "caption": "🐟 The discovery of the living Coelacanth is hailed as the greatest zoological find of the 20th century. Its lobed, limb-like fins represent the evolutionary transition from sea creatures to the first land vertebrates.\n\nFollow Wild Vault for more expeditions into our planet's deep past!"
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
                "caption": "🌊 Oceans and freshwater rivers harbor creatures with astonishing offensive and defensive weapons. From the camouflaged stonefish to the electric charges of the Amazonian eel.\n\nWhich of these 9 fish intimidates you the most? Comment below and follow Wild Vault!"
            }
        ],
        "format_7_breaking_news": [
            {
                "topic_id": "NEWS-PURUSSAURUS",
                "prompt": "giant prehistoric purussaurus crocodile 12 meters long attacking huge rodent in ancient amazon swamp cinematic prehistoric scene",
                "headline": "Fossils reveal a giant 40-foot prehistoric caiman hunted 4,000-pound mammals in the ancient Amazon 12 million years ago",
                "caption": "🦖 Purussaurus brasiliensis was one of the largest apex crocodilians to ever walk the Earth after the dinosaurs. Fossil bite marks show it delivered over 7 tons of bite pressure—surpassing even the Tyrannosaurus Rex.\n\nCan you imagine swimming in those prehistoric rivers? Follow Wild Vault for mind-blowing prehistoric discoveries!"
            },
            {
                "topic_id": "NEWS-TITANOBOA",
                "prompt": "massive prehistoric titanoboa snake 14 meters long coiled around giant ancient turtle in tropical swamp photorealistic cinematic",
                "headline": "Scientists confirm Titanoboa measured over 45 feet long and ruled ancient tropical jungles swallowing giant crocodilians whole",
                "caption": "🐍 Titanoboa cerrejonensis slithered through South America 60 million years ago. Weighing over 2,500 pounds, this colossus could easily constrict and swallow prey the size of a family car.\n\nFollow Wild Vault to discover the prehistoric monsters that once ruled Earth!"
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
                "caption": "🦅 These 4 avian titans have preserved the terrifying gaze of their theropod dinosaur ancestors. Their sheer scale and piercing stare command respect across their ecosystems.\n\nWhich of these 4 looks the most intimidating to you? Cast your vote in the comments and follow Wild Vault!"
            }
        ]
    }

    @classmethod
    def get_random_topic(cls, format_type: Optional[str] = None, seen_topic_ids: Optional[List[str]] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Selects a format and topic at random, strictly avoiding repeated topic_ids.
        """
        chosen_format = format_type or random.choice(cls.FORMAT_TYPES)
        available = cls.CURATED_TOPICS.get(chosen_format, cls.CURATED_TOPICS["format_3_curiosity_pip"])
        
        seen_set = set(seen_topic_ids or [])
        unseen = [t for t in available if t.get("topic_id") not in seen_set]

        if unseen:
            chosen_topic = random.choice(unseen)
        else:
            chosen_topic = random.choice(available)

        return chosen_format, chosen_topic
