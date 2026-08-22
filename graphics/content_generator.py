import random
from typing import Dict, Any, List, Optional, Tuple

class ContentGenerator:
    """
    Generador de Contenido Curado e IA para los 8 Formatos de Imagen de Wild Vault.
    100% en español, tono científico, asombroso y de alta retención viral.
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

    # Banco de Contenidos Curados de Máxima Calidad
    CURATED_TOPICS = {
        "format_1_taxonomic_catalog": [
            {
                "topic_id": "CATALOG-OWLS",
                "title": "8 Tipos de Búhos del Mundo",
                "species": [
                    {"name": "Búho Real", "scientific": "Bubo bubo", "prompt": "Eurasian eagle owl isolated studio portrait black background"},
                    {"name": "Lechuza Común", "scientific": "Tyto alba", "prompt": "barn owl isolated studio portrait black background"},
                    {"name": "Búho Nival", "scientific": "Bubo scandiacus", "prompt": "snowy owl pure white isolated studio portrait black background"},
                    {"name": "Búho Estigio", "scientific": "Asio stygius", "prompt": "stygian owl red eyes isolated studio portrait black background"},
                    {"name": "Mochuelo Europeo", "scientific": "Athene noctua", "prompt": "little owl isolated studio portrait black background"},
                    {"name": "Búho Cornudo", "scientific": "Bubo virginianus", "prompt": "great horned owl isolated studio portrait black background"},
                    {"name": "Autillo Africano", "scientific": "Otus senegalensis", "prompt": "african scops owl isolated studio portrait black background"},
                    {"name": "Búho Pescador", "scientific": "Ketupa blakistoni", "prompt": "blakiston fish owl isolated studio portrait black background"}
                ],
                "caption": "🦉 Los búhos son considerados las aves rapaces nocturnas más letales y silenciosas del planeta. Sus plumas serradas eliminan la fricción del aire permitiéndoles volar en absoluto silencio.\n\n¿Cuál de estas especies te parece la más imponente? ¡Déjanos tu comentario y sigue a Wild Vault para más maravillas de la naturaleza!"
            },
            {
                "topic_id": "CATALOG-BIG-CATS",
                "title": "8 Grandes Felinos del Planeta",
                "species": [
                    {"name": "Jaguar", "scientific": "Panthera onca", "prompt": "amazon jaguar isolated studio portrait black background"},
                    {"name": "Tigre de Bengala", "scientific": "Panthera tigris", "prompt": "bengal tiger isolated studio portrait black background"},
                    {"name": "Leopardo de las Nieves", "scientific": "Panthera uncia", "prompt": "snow leopard isolated studio portrait black background"},
                    {"name": "León Africano", "scientific": "Panthera leo", "prompt": "african male lion mane isolated studio portrait black background"},
                    {"name": "Guepardo", "scientific": "Acinonyx jubatus", "prompt": "cheetah isolated studio portrait black background"},
                    {"name": "Pantera Negra", "scientific": "Panthera pardus", "prompt": "black panther melanistic leopard isolated studio portrait black background"},
                    {"name": "Puma", "scientific": "Puma concolor", "prompt": "mountain lion cougar isolated studio portrait black background"},
                    {"name": "Leopardo Nublado", "scientific": "Neofelis nebulosa", "prompt": "clouded leopard isolated studio portrait black background"}
                ],
                "caption": "🐆 Los felinos poseen la mayor fuerza de mordida relativa y agilidad entre los depredadores terrestres. Desde el sigiloso leopardo de las nieves hasta la mandíbula demoledora del jaguar.\n\n¿Cuál es tu favorito? ¡Síguenos en Wild Vault para contenido diario de vida salvaje!"
            }
        ],
        "format_2_real_vs_illustrated": [
            {
                "topic_id": "SPLIT-SHARK-DIVER",
                "prompt_real": "scuba diver carefully examining open mouth of wild shark underwater turquoise clear ocean sand bottom high resolution photography",
                "prompt_illustrated": "anime comic style ghibli illustration of friendly shark with wide open mouth getting teeth inspected by anime scuba diver cute funny dialogue bubble underwater reef",
                "dialogue": "Más abajo, ahí, ahí",
                "caption": "🦈 Los tiburones a menudo permiten que peces limpiadores (y a veces buzos de investigación) inspeccionen sus dientes para remover parásitos y anzuelos atorados.\n\nAunque imponen respeto, demuestran comportamientos de cooperación fascinantes en su hábitat natural. ¿Te atreverías a bucear con ellos? ¡Sigue a Wild Vault!"
            },
            {
                "topic_id": "SPLIT-CAPYBARA-CROCODILE",
                "prompt_real": "wild capybara calmly sitting right next to giant caiman crocodile in river bank sunbathing high detail nature photography",
                "prompt_illustrated": "funny anime style illustration of chill capybara sitting on top of confused crocodile friendly cute anime expressions pastel colors",
                "dialogue": "¿Podemos ser amigos?",
                "caption": "🐾 El carpincho o capibara es conocido como el animal más pacífico y sociable del reino animal. Su naturaleza calmada y baja emisión de señales de amenaza confunde a los depredadores, permitiéndoles convivir pacíficamente junto a caimanes y otros animales.\n\n¡Sigue a Wild Vault para descubrir los secretos más insólitos de la fauna!"
            }
        ],
        "format_3_curiosity_pip": [
            {
                "topic_id": "PIP-ECLYSE-ZEBROID",
                "prompt_main": "rare real zorse eclyse animal hybrid zebra and white horse walking in green meadow full body ultra realistic photography",
                "prompt_pip": "close up face stripes of zebra horse hybrid grazing grass detailed macro photography",
                "badge": "HÍBRIDO INSÓLITO",
                "headline": [
                    "ECLYSE ES UN ANIMAL",
                    "HÍBRIDO QUE NACIÓ DE UNA",
                    "CEBRA Y UN CABALLO"
                ],
                "caption": "🦓 Conoce a Eclyse, uno de los híbridos más famosos del mundo (Zorse). Nació del cruce entre una cebra y un caballo en un parque safari, heredando el patrón de rayas solo en la cabeza y cuartos traseros, dejando el resto de su cuerpo blanco.\n\n¿Habías visto un animal así antes? ¡Comparte tu reacción y sigue a Wild Vault!"
            },
            {
                "topic_id": "PIP-STYGIAN-OWL",
                "prompt_main": "stygian owl with eerie glowing red eyes perched on dark jungle tree branch nighttime atmospheric wildlife photography",
                "prompt_pip": "night vision thermal view of demonic looking stygian owl in pitch black forest close up glowing eyes",
                "badge": "DEPREDADOR DE LA NOCHE",
                "headline": [
                    "EL BÚHO ESTIGIO POSEE",
                    "UNA MIRADA TAN INQUIETANTE",
                    "QUE PARECE SOBRENATURAL"
                ],
                "caption": "👁️ El Búho Estigio (*Asio stygius*) habita en las selvas de América. Cuando la luz de una linterna refleja sus ojos en la oscuridad, emiten un brillo rojo intenso que durante siglos dio origen a leyendas de criaturas místicas.\n\n¡Sigue a Wild Vault para explorar los misterios más oscuros de la naturaleza!"
            }
        ],
        "format_5_creature_profile": [
            {
                "topic_id": "PROFILE-NAUTILUS",
                "prompt": "nautilus living fossil swimming deep blue coral ocean macro shot high detail 8k photography",
                "title": "El Nautilo",
                "paragraphs": [
                    {"text": "Es un fósil viviente que lleva"},
                    {"text": "500 millones de años sin cambiar nada,"},
                    {"text": "y su concha está dividida en cámaras"},
                    {"text": "que llena de gas para flotar"},
                    {"text": "exactamente como un submarino."}
                ],
                "caption": "🐚 El Nautilo es un molusco cefalópodo que sobrevivió a las 5 grandes extinciones masivas de la Tierra, incluidos los dinosaurios. Su concha sigue la proporción áurea matemática y es una obra maestra de ingeniería biológica.\n\n¿Sabías que aún existía? ¡Sigue a Wild Vault para descubrir criaturas ancestrales!"
            },
            {
                "topic_id": "PROFILE-COELACANTH",
                "prompt": "ancient coelacanth prehistoric fish swimming dark deep underwater abyss rare wildlife macro photography",
                "title": "El Celacanto",
                "paragraphs": [
                    {"text": "Se creía extinto hace 66 millones de años"},
                    {"text": "junto con los dinosaurios,"},
                    {"text": "hasta que fue hallado vivo en 1938"},
                    {"text": "en las profundidades de Sudáfrica."}
                ],
                "caption": "🐟 El Celacanto es uno de los descubrimientos zoológicos más impactantes del siglo XX. Posee aletas lobuladas articuladas que representan la transición evolutiva de los peces hacia los primeros vertebrados terrestres.\n\n¡Sigue a Wild Vault para más expediciones al pasado de nuestro planeta!"
            }
        ],
        "format_6_vintage_guide": [
            {
                "topic_id": "VINTAGE-DANGEROUS-FISH",
                "title": "Los 9 Peces Más Peligrosos del Mundo",
                "species": [
                    {"name": "Pez globo", "sci": "Takifugu rubripes", "desc": "Contiene tetrodotoxina letal", "prompt": "pufferfish isolated studio portrait white background"},
                    {"name": "Pez piedra", "sci": "Synanceia verrucosa", "desc": "Espinas dorsales venenosas", "prompt": "stonefish camouflaged isolated studio portrait white background"},
                    {"name": "Pez león", "sci": "Pterois volitans", "desc": "Espinas con toxinas dolorosas", "prompt": "lionfish fins spread isolated studio portrait white background"},
                    {"name": "Raya de río", "sci": "Potamotrygon motoro", "desc": "Aguijón con potente veneno", "prompt": "freshwater stingray spotted isolated studio portrait white background"},
                    {"name": "Barracuda", "sci": "Sphyraena barracuda", "desc": "Mordida veloz como navaja", "prompt": "great barracuda fish isolated studio portrait white background"},
                    {"name": "Tiburón blanco", "sci": "Carcharodon carcharias", "desc": "Superdepredador con 300 dientes", "prompt": "great white shark head isolated studio portrait white background"},
                    {"name": "Anguila eléctrica", "sci": "Electrophorus electricus", "desc": "Descargas de hasta 860 voltios", "prompt": "electric eel fish isolated studio portrait white background"},
                    {"name": "Pez vampiro", "sci": "Vandellia cirrhosa", "desc": "Parásito hematófago del Amazonas", "prompt": "candiru vampire fish isolated studio portrait white background"},
                    {"name": "Pez avispa", "sci": "Ablabys taenianotus", "desc": "Veneno neurotóxico agudo", "prompt": "cockatoo waspfish isolated studio portrait white background"}
                ],
                "caption": "🌊 El océano y los ríos esconden criaturas con adaptaciones defensivas y ofensivas letales. Desde el veneno del pez piedra hasta las descargas eléctricas de la anguila amazónica.\n\n¿Cuál de estos peces te parece el más temible? ¡Comenta abajo y sigue a Wild Vault!"
            }
        ],
        "format_7_breaking_news": [
            {
                "topic_id": "NEWS-PURUSSAURUS",
                "prompt": "giant prehistoric purussaurus crocodile 12 meters long attacking huge rodent in ancient amazon swamp cinematic prehistoric scene",
                "headline": "Descubren que un cocodrilo gigante de 12 metros cazaba mamíferos de 2,000 kilos en el Amazonas hace 12 millones de años",
                "caption": "🦖 El Purussaurus brasiliensis fue uno de los mayores reptiles depredadores tras la extinción de los dinosaurios. Nuevas evidencias fósiles demuestran que su mordida generaba más de 7 toneladas de fuerza, superando al propio Tiranosaurio Rex.\n\n¿Te imaginas nadar en aquellos ríos? ¡Sigue a Wild Vault para más descubrimientos prehistóricos!"
            },
            {
                "topic_id": "NEWS-TITANOBOA",
                "prompt": "massive prehistoric titanoboa snake 14 meters long coiled around giant ancient turtle in tropical swamp photorealistic cinematic",
                "headline": "Fósiles revelan que la Titanoboa medía más de 14 metros y dominaba la selva tropical devorando cocodrilos enteros",
                "caption": "🐍 La Titanoboa cerrejonensis vivió hace 60 millones de años en lo que hoy es Colombia. Con un peso de más de 1,100 kg, era capaz de asfixiar y tragar presas del tamaño de un coche.\n\n¡Sigue a Wild Vault para descubrir los monstruos que dominaron nuestro planeta!"
            }
        ],
        "format_8_quad_collage": [
            {
                "topic_id": "QUAD-TITANS",
                "title": "4 Titanes con Mirada Letal",
                "prompts": [
                    "andean condor giant head close up menacing stare 8k wildlife photography",
                    "shoebill stork terrifying prehistoric stare looking directly at camera 8k",
                    "harpy eagle giant raptor intense predator eyes close up 8k photography",
                    "southern cassowary dinosaur bird blue neck glowing eyes staring forward 8k"
                ],
                "caption": "🦅 Estas 4 aves gigantes conservan rasgos y miradas que recuerdan directamente a sus ancestros los dinosaurios terópodos. Su tamaño y presencia dominan sus ecosistemas.\n\n¿Cuál de estas 4 miradas te intimida más? ¡Vota en los comentarios y sigue a Wild Vault!"
            }
        ]
    }

    @classmethod
    def get_random_topic(cls, format_type: Optional[str] = None, seen_topic_ids: Optional[List[str]] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Selecciona un formato y tema al azar garantizando CERO REPETICIÓN de topic_id.
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
