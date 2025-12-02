"""Configuration et utilitaires pour les métadonnées de quiz."""

import os
from typing import Tuple

CATEGORY_PREFIXES = {
    "HISTOIRE": "Histoire de l'aéronautique et de l'espace",
    "METEO": "Météorologie et aérologie",
    "AERO": "Aérodynamique et mécanique du vol",
    "NAV": "Navigation, sécurité et réglementation",
    "AERONEF": "Connaissance des aéronefs",
    "ANGLAIS": "Anglais aéronautique",
}


def _detect_category(filename: str) -> str:
    upper_name = filename.upper()
    for prefix, category in CATEGORY_PREFIXES.items():
        if upper_name.startswith(prefix):
            return category
    return "BIA - Quiz"


def build_title_description_from_filename(pdf_filename: str) -> Tuple[str, str]:
    base_name = os.path.splitext(os.path.basename(pdf_filename))[0]
    category = _detect_category(base_name)
    title = f"Quiz {category.split(' ')[0]} - {base_name}"
    description = f"Quiz BIA - {category} à partir du fichier {base_name}"
    return title, description
