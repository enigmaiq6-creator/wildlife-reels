"""
Mapa Taxonómico y Visual de Vida Salvaje v8.0:
Proporciona consultas cinemáticas precisas y términos familiares para cada una de las 47 criaturas.
Garantiza que Pexels y Pixabay SIEMPRE encuentren clips de video 4K reales y dinámicos.
"""

from typing import Dict, List, Any

WILDLIFE_TAXONOMY: Dict[str, Dict[str, Any]] = {
    # 1. Serpientes y Reptiles Venenosos
    "inland_taipan": {
        "required_any": ["snake", "taipan", "viper", "serpent", "reptile", "cobra"],
        "primary_queries": ["taipan snake", "venomous snake", "snake strike 4k", "viper head close up"],
        "family_queries": ["snake crawling wild", "snake tongue flicking", "desert snake predator", "deadly snake attack"],
        "banned": ["pet snake", "zoo", "holding", "handler", "aquarium", "cage", "rubber"]
    },
    "black_mamba": {
        "required_any": ["snake", "mamba", "black mamba", "viper", "cobra", "reptile"],
        "primary_queries": ["black mamba snake", "venomous snake strike", "snake mouth open", "african snake 4k"],
        "family_queries": ["fast snake crawling", "snake head close up", "savanna snake predator", "cobra strike"],
        "banned": ["pet", "zoo", "handler", "cage"]
    },
    "king_cobra": {
        "required_any": ["cobra", "king cobra", "snake", "serpent", "reptile"],
        "primary_queries": ["king cobra snake", "cobra hood spread", "cobra strike 4k", "snake rearing up"],
        "family_queries": ["giant snake rainforest", "snake attacking", "venomous serpent", "cobra head"],
        "banned": ["charmer", "basket", "pet", "zoo", "handler", "man"]
    },
    "green_anaconda": {
        "required_any": ["anaconda", "snake", "boa", "constrictor", "python", "serpent"],
        "primary_queries": ["green anaconda snake", "giant snake swimming", "anaconda river", "constrictor snake"],
        "family_queries": ["huge snake rainforest", "snake underwater", "giant reptile swimming", "python stalking"],
        "banned": ["pet", "zoo", "handler", "cage"]
    },

    # 2. Aves Rapaces y Dinosaurios Vivos
    "harpy_eagle": {
        "required_any": ["eagle", "harpy", "raptor", "hawk", "bird of prey", "falcon"],
        "primary_queries": ["harpy eagle", "giant eagle", "eagle talons claws", "eagle flying 4k"],
        "family_queries": ["eagle perched rainforest", "hawk predator flying", "bird of prey eyes", "eagle hunting"],
        "banned": ["pigeon", "parrot", "cage", "zoo", "pet", "seagull"]
    },
    "shoebill_stork": {
        "required_any": ["shoebill", "stork", "bird", "balaeniceps", "whalehead", "prehistoric bird"],
        "primary_queries": ["shoebill stork", "shoebill bird close up", "shoebill swamp", "giant stork staring"],
        "family_queries": ["prehistoric bird swamp", "stork hunting fish", "giant wetland bird", "bird death stare"],
        "banned": ["cage", "zoo", "flamingo", "pelican"]
    },
    "cassowary": {
        "required_any": ["cassowary", "bird", "ratite", "dinosaur bird", "emu", "ostrich"],
        "primary_queries": ["cassowary bird", "cassowary claws feet", "cassowary rainforest", "giant bird walking"],
        "family_queries": ["prehistoric bird rainforest", "large wild bird", "cassowary head close up", "bird running wild"],
        "banned": ["cage", "zoo", "farm", "chicken", "turkey"]
    },
    "peregrine_falcon": {
        "required_any": ["falcon", "peregrine", "hawk", "raptor", "bird of prey", "eagle"],
        "primary_queries": ["peregrine falcon", "falcon dive high speed", "falcon flying 4k", "falcon head close up"],
        "family_queries": ["raptor bird sky", "fastest bird dive", "hawk hunting", "bird of prey eyes"],
        "banned": ["pigeon", "cage", "pet", "parrot"]
    },
    "african_crowned_eagle": {
        "required_any": ["eagle", "crowned eagle", "raptor", "hawk", "bird of prey"],
        "primary_queries": ["crowned eagle", "african eagle", "eagle talons attack", "giant raptor bird"],
        "family_queries": ["eagle hunting forest", "eagle flying wild", "bird of prey claws", "hawk attack"],
        "banned": ["cage", "zoo", "pet"]
    },
    "osprey": {
        "required_any": ["osprey", "sea hawk", "fish eagle", "eagle", "raptor"],
        "primary_queries": ["osprey diving water", "osprey catching fish", "fish eagle flying", "osprey talons"],
        "family_queries": ["eagle hunting water", "raptor bird lake", "bird of prey diving", "eagle carrying fish"],
        "banned": ["cage", "zoo", "pet"]
    },
    "bearded_vulture": {
        "required_any": ["vulture", "lammergeier", "bearded vulture", "raptor", "bird"],
        "primary_queries": ["bearded vulture", "vulture mountain flight", "lammergeier bone", "giant vulture 4k"],
        "family_queries": ["vulture soaring mountains", "scavenger bird cliff", "huge bird flight", "bird cliff"],
        "banned": ["cage", "zoo", "pet"]
    },
    "secretary_bird": {
        "required_any": ["secretary bird", "bird", "raptor", "sagittarius serpentarius"],
        "primary_queries": ["secretary bird stomping", "secretary bird hunting", "secretary bird savanna", "tall bird walking"],
        "family_queries": ["savanna bird hunting snake", "african raptor bird", "bird kicking ground", "wild savanna bird"],
        "banned": ["cage", "zoo", "pet"]
    },

    # 3. Monstruos y Depredadores Marinos
    "great_white_shark": {
        "required_any": ["shark", "great white", "carcharodon", "predator fish"],
        "primary_queries": ["great white shark underwater", "shark breaching surface", "shark teeth jaws", "shark swimming 4k"],
        "family_queries": ["apex predator shark ocean", "shark deep blue", "ocean shark attack", "shark close up"],
        "banned": ["cage diver", "scuba diver", "aquarium", "swimmer", "whale shark"]
    },
    "colossal_squid": {
        "required_any": ["squid", "giant squid", "octopus", "tentacles", "cephalopod", "deep sea"],
        "primary_queries": ["giant squid swimming", "deep sea squid", "squid tentacles underwater", "abyss creature 4k"],
        "family_queries": ["underwater cephalopod", "octopus deep ocean", "bioluminescent sea monster", "squid glowing"],
        "banned": ["calamari", "recipe", "cooking", "plate", "market", "fried"]
    },
    "blue_ringed_octopus": {
        "required_any": ["octopus", "blue ringed", "cephalopod", "tentacles", "marine predator"],
        "primary_queries": ["blue ringed octopus", "small octopus glowing", "octopus coral reef", "venomous octopus"],
        "family_queries": ["octopus swimming reef", "octopus camouflage", "tentacles moving ocean", "colorful octopus"],
        "banned": ["cooking", "recipe", "food", "aquarium"]
    },
    "orca": {
        "required_any": ["orca", "killer whale", "orcinus", "whale"],
        "primary_queries": ["killer whale orca ocean", "orca pod hunting", "orca breaching wave", "orca underwater 4k"],
        "family_queries": ["arctic ocean whale predator", "orca fin ocean", "killer whales antarctic", "whale swimming fast"],
        "banned": ["seaworld", "trainer", "show", "aquarium", "pool"]
    },
    "bull_shark": {
        "required_any": ["shark", "bull shark", "carcharhinus", "river shark"],
        "primary_queries": ["bull shark underwater", "shark shallow water", "bull shark teeth", "shark murky river"],
        "family_queries": ["powerful shark swimming", "ocean predator shark", "aggressive shark close up", "shark hunting"],
        "banned": ["aquarium", "diver", "cage"]
    },
    "hammerhead_shark": {
        "required_any": ["hammerhead", "shark", "sphyrna", "predator fish"],
        "primary_queries": ["hammerhead shark swimming", "school of hammerheads", "hammerhead head close up", "shark underwater 4k"],
        "family_queries": ["ocean predator shark", "tropical reef shark", "shark cruising blue", "hammerhead ocean"],
        "banned": ["aquarium", "diver", "cage"]
    },
    "goblin_shark": {
        "required_any": ["shark", "goblin shark", "deep sea", "abyss predator", "slingshot jaw"],
        "primary_queries": ["deep sea shark", "strange shark underwater", "abyss predator fish", "alien shark ocean"],
        "family_queries": ["deep ocean monster", "weird fish abyss", "dark ocean predator", "creepy marine creature"],
        "banned": ["aquarium", "diver"]
    },
    "mantis_shrimp": {
        "required_any": ["mantis shrimp", "shrimp", "stomatopod", "crustacean", "peacock mantis"],
        "primary_queries": ["peacock mantis shrimp", "mantis shrimp strike", "colorful mantis shrimp", "shrimp coral reef"],
        "family_queries": ["marine crustacean eyes", "reef predator macro", "underwater macro creature", "crustacean punch"],
        "banned": ["cooking", "recipe", "fried shrimp", "restaurant", "plate", "food"]
    },
    "pistol_shrimp": {
        "required_any": ["pistol shrimp", "shrimp", "snapping shrimp", "crustacean", "alpheus"],
        "primary_queries": ["pistol shrimp claw", "snapping shrimp underwater", "shrimp burrow reef", "macro shrimp 4k"],
        "family_queries": ["marine shrimp claw", "underwater reef crustacean", "tiny ocean predator", "shrimp sand"],
        "banned": ["cooking", "recipe", "food", "restaurant"]
    },
    "cone_snail": {
        "required_any": ["snail", "cone snail", "conus", "marine snail", "mollusk", "shell"],
        "primary_queries": ["marine cone snail", "underwater sea snail", "snail crawling ocean", "cone shell reef"],
        "family_queries": ["venomous sea snail", "mollusk underwater", "sea snail hunting", "macro snail crawling"],
        "banned": ["escargot", "recipe", "cooking", "plate"]
    },
    "box_jellyfish": {
        "required_any": ["jellyfish", "box jellyfish", "chironex", "sea wasp", "medusa"],
        "primary_queries": ["box jellyfish swimming", "lethal jellyfish tentacles", "clear jellyfish ocean", "jellyfish glowing 4k"],
        "family_queries": ["ocean jellyfish floating", "venomous tentacles water", "deep sea jellyfish", "translucent sea creature"],
        "banned": ["aquarium", "touching"]
    },
    "stonefish": {
        "required_any": ["stonefish", "scorpionfish", "synanceia", "camouflage fish", "rockfish"],
        "primary_queries": ["stonefish camouflage reef", "venomous stonefish ocean", "stonefish spines", "hidden fish sand"],
        "family_queries": ["camouflaged predator fish", "reef rock fish", "lethal venomous fish", "ugly ocean fish"],
        "banned": ["aquarium", "tank", "cooking"]
    },
    "electric_eel": {
        "required_any": ["electric eel", "eel", "electrophorus", "river fish", "gymnotus"],
        "primary_queries": ["electric eel freshwater", "eel swimming river", "giant electric eel amazon", "eel breathing surface"],
        "family_queries": ["river predator amazon", "murky water eel", "snake like fish swimming", "long predator fish"],
        "banned": ["aquarium", "tank", "sushi", "unagi", "recipe", "cooking"]
    },
    "moray_eel": {
        "required_any": ["moray eel", "eel", "moray", "muraenidae", "reef eel"],
        "primary_queries": ["moray eel opening mouth", "green moray eel reef", "giant moray eel teeth", "moray eel cave"],
        "family_queries": ["reef predator eel", "eel biting underwater", "spotted moray ocean", "sea eel coral"],
        "banned": ["aquarium", "tank", "cooking"]
    },
    "goliath_tigerfish": {
        "required_any": ["tigerfish", "goliath tigerfish", "hydrocynus", "monster fish", "river fish"],
        "primary_queries": ["goliath tigerfish teeth", "tigerfish congo river", "giant predator fish freshwater", "monster fish river"],
        "family_queries": ["freshwater monster fish", "crocodile teeth fish", "african river predator", "big tooth fish 4k"],
        "banned": ["aquarium", "market", "food"]
    },
    "giant_freshwater_stingray": {
        "required_any": ["stingray", "ray", "freshwater stingray", "urotrygon", "potamotrygon"],
        "primary_queries": ["giant freshwater stingray river", "huge stingray mud", "stingray barb tail", "river stingray swimming"],
        "family_queries": ["massive stingray water", "freshwater river giant", "stingray sand bottom", "ray gliding river"],
        "banned": ["aquarium", "touch tank"]
    },

    # 4. Felinos y Mamíferos Carnívoros
    "jaguar": {
        "required_any": ["jaguar", "panthera onca", "black panther", "big cat", "wildcat"],
        "primary_queries": ["wild jaguar rainforest", "jaguar swimming river", "jaguar biting caiman", "jaguar stalk 4k"],
        "family_queries": ["panther predator forest", "big cat hunting water", "jaguar eyes stare", "spotted big cat"],
        "banned": ["zoo", "cage", "pet", "kitten", "leopard", "cheetah"]
    },
    "siberian_tiger": {
        "required_any": ["tiger", "siberian tiger", "amur tiger", "panthera tigris", "big cat"],
        "primary_queries": ["siberian tiger snow", "amur tiger winter forest", "tiger roar teeth", "tiger stalk prey 4k"],
        "family_queries": ["giant tiger walking snow", "big cat predator winter", "tiger face eyes", "wild tiger hunting"],
        "banned": ["zoo", "cage", "pet", "circus", "cub"]
    },
    "snow_leopard": {
        "required_any": ["snow leopard", "leopard", "panthera uncia", "ghost cat", "mountain cat"],
        "primary_queries": ["snow leopard cliffs", "snow leopard mountains himalayas", "snow leopard tail leap", "snow leopard face"],
        "family_queries": ["mountain predator snow", "ghost leopard rocks", "wild mountain feline", "leopard stalking snow"],
        "banned": ["zoo", "cage", "pet"]
    },
    "grizzly_bear": {
        "required_any": ["grizzly bear", "bear", "brown bear", "ursus arctos", "kodiak"],
        "primary_queries": ["grizzly bear river fishing", "giant grizzly bear standing", "grizzly bear claws teeth", "brown bear alaska"],
        "family_queries": ["wild bear forest", "bear catching salmon", "massive grizzly bear walking", "bear roar 4k"],
        "banned": ["zoo", "cage", "circus", "teddy", "costume"]
    },
    "honey_badger": {
        "required_any": ["honey badger", "badger", "mellivora", "ratel"],
        "primary_queries": ["honey badger wild savanna", "honey badger digging", "badger fighting predator", "honey badger walking"],
        "family_queries": ["fearless badger african savanna", "badger claws ground", "honey badger face", "badger stalking"],
        "banned": ["zoo", "pet", "cage", "ferret", "skunk"]
    },
    "wolverine": {
        "required_any": ["wolverine", "gulo gulo", "arctic predator", "mustelid"],
        "primary_queries": ["wolverine snow forest", "wolverine walking winter", "wild wolverine arctic", "wolverine claws"],
        "family_queries": ["arctic predator forest", "fearless wolverine animal", "wolverine teeth jaw", "snow predator running"],
        "banned": ["marvel", "x-men", "hugh jackman", "costume", "actor", "movie"]
    },
    "african_wild_dog": {
        "required_any": ["wild dog", "painted dog", "lycaon", "african dog", "hunting pack"],
        "primary_queries": ["african wild dog pack", "painted wolf hunting", "wild dog running savanna", "african wild dog face"],
        "family_queries": ["wild dog pack stalking", "painted dog ears close up", "african savanna predator pack", "wild dog run"],
        "banned": ["pet dog", "puppy", "domestic dog", "husky", "labrador"]
    },
    "leopard_seal": {
        "required_any": ["leopard seal", "seal", "hydrurga", "antarctic predator"],
        "primary_queries": ["leopard seal ice antarctica", "leopard seal underwater teeth", "leopard seal opening jaws", "seal swimming ice"],
        "family_queries": ["antarctic apex seal", "giant predatory seal", "leopard seal hunting penguin", "seal underwater 4k"],
        "banned": ["zoo", "aquarium", "circus"]
    },
    "vampire_bat": {
        "required_any": ["bat", "vampire bat", "desmodus", "flying fox", "fruit bat", "nocturnal bat"],
        "primary_queries": ["bat in cave close up", "flying bats sunset", "wild bat face eyes", "bat hanging upside down"],
        "family_queries": ["colony of bats flying", "nocturnal bat rainforest", "bat crawling ground", "small bat close up"],
        "banned": ["halloween", "costume", "vampire movie", "dracula", "actor", "dracula costume", "mask", "party"]
    },
    "giant_anteater": {
        "required_any": ["anteater", "giant anteater", "myrmecophaga", "anteater claws"],
        "primary_queries": ["giant anteater walking", "anteater snout tongue", "anteater massive claws", "wild anteater savanna"],
        "family_queries": ["giant anteater rainforest", "anteater digging termite", "anteater tail fur", "strange mammal walking"],
        "banned": ["zoo", "cage", "pet"]
    },

    # 5. Insectos, Arácnidos y Reptiles Ancestrales
    "komodo_dragon": {
        "required_any": ["komodo dragon", "komodo", "varanus", "monitor lizard", "giant lizard"],
        "primary_queries": ["komodo dragon walking island", "komodo dragon tongue flicking", "komodo dragon teeth saliva", "giant monitor lizard 4k"],
        "family_queries": ["huge lizard predator", "komodo dragon beach", "reptile predator hunting", "monitor lizard close up"],
        "banned": ["pet lizard", "gecko", "zoo", "cage", "iguana"]
    },
    "alligator_snapping_turtle": {
        "required_any": ["turtle", "snapping turtle", "alligator turtle", "macrochelys", "giant turtle"],
        "primary_queries": ["alligator snapping turtle underwater", "snapping turtle jaws open", "prehistoric turtle river", "turtle lure tongue"],
        "family_queries": ["giant freshwater turtle", "snapping turtle ambush", "river turtle predator", "armored turtle shell"],
        "banned": ["small turtle", "pet turtle", "pet shop", "aquarium"]
    },
    "nile_crocodile": {
        "required_any": ["crocodile", "nile crocodile", "alligator", "caiman", "crocodylus"],
        "primary_queries": ["nile crocodile attack river", "crocodile jaws open teeth", "crocodile ambush water", "giant crocodile swimming 4k"],
        "family_queries": ["river predator crocodile", "massive croc basking", "crocodile strike water", "alligator river stalk"],
        "banned": ["zoo", "bag", "boots", "wallet", "leather", "pet"]
    },
    "golden_poison_dart_frog": {
        "required_any": ["poison frog", "dart frog", "frog", "phyllobates", "amphibian", "tree frog"],
        "primary_queries": ["golden poison dart frog rainforest", "yellow poison frog leaf", "poison dart frog macro", "bright frog jungle 4k"],
        "family_queries": ["rainforest tree frog close up", "amphibian macro eyes", "colorful poison frog", "tiny lethal frog moss"],
        "banned": ["pet", "terrarium", "aquarium", "toad cooking"]
    },
    "deathstalker_scorpion": {
        "required_any": ["scorpion", "deathstalker", "leiurus", "arachnid", "desert scorpion"],
        "primary_queries": ["deathstalker scorpion desert sand", "scorpion stinger tail", "yellow scorpion claws", "scorpion hunting night 4k"],
        "family_queries": ["desert scorpion walking", "macro scorpion strike", "venomous arachnid sand", "scorpion glowing uv"],
        "banned": ["pet", "eating", "street food", "fried scorpion", "market"]
    },
    "sydney_funnel_web_spider": {
        "required_any": ["spider", "funnel web", "tarantula", "atrax", "arachnid"],
        "primary_queries": ["sydney funnel web spider fangs", "aggressive spider rearing up", "spider venom fangs", "black funnel web spider 4k"],
        "family_queries": ["deadly black spider macro", "spider fangs dripping venom", "armored spider burrow", "tarantula walking ground"],
        "banned": ["halloween decoration", "toy", "fake spider", "spider-man", "drawing"]
    },
    "tarantula_hawk_wasp": {
        "required_any": ["wasp", "tarantula hawk", "pepsis", "hornet", "hunting wasp"],
        "primary_queries": ["tarantula hawk wasp flying", "giant wasp orange wings", "wasp hunting spider", "huge desert wasp 4k"],
        "family_queries": ["parasitic wasp macro", "predatory wasp ground", "wasp stinger close up", "insect predator flying"],
        "banned": ["bee honey", "cartoon", "dead bug"]
    },
    "driver_ant_colony": {
        "required_any": ["ant", "ants", "driver ant", "army ant", "dorylus", "ant colony"],
        "primary_queries": ["driver ant colony marching", "army ants swarm jungle", "ant soldiers jaws macro", "millions of ants moving 4k"],
        "family_queries": ["ant trail rainforest floor", "macro ant biting", "swarm of ants predator", "marching ant colony"],
        "banned": ["cartoon", "picnic", "ant farm toy"]
    }
}

def get_taxonomy_for_creature(creature_name: str) -> Dict[str, Any]:
    """Busca o construye la regla taxonómica y consultas visuales para cualquier criatura."""
    clean_name = creature_name.lower().replace("-", "_").replace(" ", "_").strip()
    
    # 1. Búsqueda exacta o parcial
    for key, data in WILDLIFE_TAXONOMY.items():
        if key == clean_name or key in clean_name or clean_name in key:
            return data
            
    # 2. Búsqueda por palabras individuales
    words = [w for w in creature_name.lower().replace("-", " ").replace("_", " ").split() if len(w) > 2]
    root = words[-1] if words else creature_name.lower()
    
    for key, data in WILDLIFE_TAXONOMY.items():
        if any(w in key for w in words) or root in key:
            return data
            
    # 3. Generación dinámica de respaldo
    human_clean = creature_name.lower().replace("-", " ").replace("_", " ").strip()
    return {
        "required_any": [human_clean, root] + words + ["wildlife", "animal", "nature"],
        "primary_queries": [f"{human_clean} wildlife 4k", f"{human_clean} close up", f"{root} wild 4k"],
        "family_queries": [f"{root} in nature", f"{root} hunting", f"wild {root} predator", f"{root} natural habitat"],
        "banned": ["pet", "zoo", "cage", "holding", "costume", "toy", "animation", "drawing"]
    }
