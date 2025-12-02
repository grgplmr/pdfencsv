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
    return "BIA - Quiz général"


def build_title_description_from_filename(pdf_path: str) -> Tuple[str, str, str]:
    """Construit le titre, la description et la catégorie à partir du chemin du PDF."""

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    category = _detect_category(base_name)
    title = f"Quiz BIA - {category} - {base_name}"
    description = (
        f"Quiz de 20 questions niveau BIA basé sur le cours {base_name} (catégorie : {category})."
    )
    return title, description, category
