from typing import Dict, Any, List

WILDLIFE_CATALOG: Dict[str, Dict[str, Any]] = {
    "jaguar_cazador": {
        "topic_id": "JAGUAR-CAZADOR-SELVA",
        "title": "5 Secretos Letales del Jaguar de la Selva",
        "hook": "¡El jaguar posee la mordida más devastadora de todos los felinos del planeta!",
        "curiosities": [
            "Número uno: Su mandíbula es capaz de perforar el caparazón blindado de una tortuga marina y el cráneo de un caimán de un solo bocado.",
            "Número dos: A diferencia de otros felinos que evitan el agua, los jaguares son nadadores olímpicos y cazan bajo el agua en ríos caudalosos.",
            "Número tres: Cazan acechando en silencio absoluto gracias a almohadillas especiales en sus patas que absorben cualquier vibración.",
            "Número cuatro: El patrón de rosetas en su pelaje es tan único e irrepetible como la huella dactilar de un ser humano.",
            "Número cinco: En la mitología maya, eran considerados deidades guardianas de la noche y señores del inframundo."
        ],
        "cta": "¿Crees que un jaguar podría vencer a un león en la selva? ¡Deja tu opinión en los comentarios y síguenos!",
        "pexels_keywords": [
            "jaguar in jungle 4k vertical",
            "jaguar hunting water 4k",
            "jaguar swimming river vertical",
            "jaguar walking rainforest vertical",
            "jaguar eyes close up 4k",
            "wild jaguar resting branch 4k",
            "amazon rainforest wildlife vertical"
        ],
        "hashtags": ["#jaguar", "#vidasalvaje", "#depredadores", "#naturaleza", "#animales", "#selva"]
    },
    "orca_depredador_supremo": {
        "topic_id": "ORCA-DEPREDADOR-SUPREMO",
        "title": "5 Razones por las que la Orca es el Rey del Océano",
        "hook": "¡Ni siquiera el gran tiburón blanco se atreve a enfrentarse a una orca en el océano!",
        "curiosities": [
            "Número uno: Las orcas no son ballenas, sino los miembros más grandes y poderosos de la familia de los delfines.",
            "Número dos: Tienen dialectos acústicos únicos que se transmiten de generación en generación como un lenguaje familiar.",
            "Número tres: Para cazar al tiburón blanco, las orcas lo voltean de espaldas para inducirle una parálisis tónica involuntaria.",
            "Número cuatro: Trabajan en equipo coordinado creando olas gigantescas para derribar focas de los témpanos de hielo.",
            "Número cinco: Tienen una esperanza de vida que en hembras salvajes puede superar los 90 años de edad."
        ],
        "cta": "¿Sabías que las orcas nunca han atacado a un humano en libertad? ¡Comenta y suscríbete para más fauna!",
        "pexels_keywords": [
            "killer whale orca ocean 4k vertical",
            "orca breaching waves vertical",
            "orca pod swimming underwater 4k",
            "great white shark swimming 4k",
            "orca iceberg arctic vertical",
            "ocean predator wildlife 4k",
            "killer whale close up underwater vertical"
        ],
        "hashtags": ["#orcas", "#oceanos", "#vidasalvaje", "#naturaleza", "#depredadores", "#faunamarina"]
    },
    "aguila_arpia": {
        "topic_id": "AGUILA-ARPIA-REINA-DEL-AIRE",
        "title": "5 Datos Asombrosos del Águila Arpía",
        "hook": "¡Esta gigantesca ave rapaz tiene garras más grandes que las de un oso pardo!",
        "curiosities": [
            "Número uno: Sus garras traseras pueden medir hasta 13 centímetros y ejercer una presión de más de 40 kilos por centímetro cuadrado.",
            "Número dos: Es capaz de levantar presas que igualan su propio peso corporal en pleno vuelo vertical entre la densa selva.",
            "Número tres: Su visión es ocho veces más potente que la del ojo humano, detectando presas a más de doscientos metros de distancia.",
            "Número cuatro: Sus alas son redondeadas para maniobrar a gran velocidad entre las ramas de árboles gigantes sin colisionar.",
            "Número cinco: Las parejas de águila arpía son monógamas de por vida y construyen nidos de más de un metro y medio de ancho."
        ],
        "cta": "¿Te imaginas ver de cerca a esta reina de los cielos? ¡Cuéntanos en comentarios y síguenos para más!",
        "pexels_keywords": [
            "harpy eagle flight 4k vertical",
            "giant eagle talons close up 4k",
            "eagle perched tree rainforest vertical",
            "eagle hunting jungle canopy 4k",
            "bird of prey eyes 4k vertical",
            "rainforest canopy flight 4k",
            "wild eagle wings spread vertical"
        ],
        "hashtags": ["#aguilaarpia", "#avesrapaces", "#vidasalvaje", "#naturaleza", "#fauna", "#selvaamazonica"]
    },
    "calamar_colosal": {
        "topic_id": "CALAMAR-COLOSAL-ABISMO",
        "title": "5 Misterios del Monstruoso Calamar Colosal",
        "hook": "¡En las profundidades heladas de la Antártida habita un monstruo con garras giratorias!",
        "curiosities": [
            "Número uno: El calamar colosal es el invertebrado más masivo del planeta, alcanzando pesos de casi media tonelada.",
            "Número dos: Posee los ojos más grandes del reino animal, con el diámetro exacto de un plato de comida o un balón de fútbol.",
            "Número tres: Sus tentáculos no tienen ventosas comunes, sino garfios giratorios afilados que destrozan a sus presas.",
            "Número cuatro: Su único depredador conocido en el abismo es el colosal cachalote, librando batallas titánicas a 2000 metros de profundidad.",
            "Número cinco: Su sangre es de color azul porque utiliza hemocianina a base de cobre para transportar oxígeno en aguas heladas."
        ],
        "cta": "¿Te atreverías a explorar las profundidades marinas? ¡Déjanos tu comentario y comparte este video!",
        "pexels_keywords": [
            "giant squid deep ocean underwater 4k vertical",
            "deep sea creature glowing underwater 4k",
            "sperm whale deep diving vertical",
            "dark abyss underwater ocean 4k",
            "squid tentacles moving underwater 4k",
            "antarctic ocean underwater ice vertical",
            "mysterious ocean depths 4k vertical"
        ],
        "hashtags": ["#calamarcolosal", "#abismo", "#monstruosmarinos", "#vidasalvaje", "#oceanos", "#misterio"]
    }
}

def get_wildlife_topic(topic_name: str) -> Dict[str, Any]:
    """Obtiene un tema del catálogo predefinido."""
    key = topic_name.lower().replace("-", "_")
    return WILDLIFE_CATALOG.get(key, list(WILDLIFE_CATALOG.values())[0])

def get_all_wildlife_topics() -> List[str]:
    """Retorna todas las claves del catálogo de Vida Salvaje."""
    return list(WILDLIFE_CATALOG.keys())
