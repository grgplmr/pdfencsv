"""Génération de quiz BIA à partir d'un cours texte via l'API OpenAI."""

from openai import OpenAI
import os
import json
import textwrap
from typing import List, Dict


client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def _truncate_text(text: str, max_chars: int = 15000) -> str:
    """Limite la longueur du texte pour l'envoyer au modèle."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars]


def _extract_response_text(response) -> str:
    """Récupère le texte renvoyé par l'API en gérant plusieurs structures possibles."""
    if hasattr(response, "output_text") and response.output_text:
        return response.output_text

    output = getattr(response, "output", None)
    if output:
        for item in output:
            contents = getattr(item, "content", [])
            for content in contents:
                if getattr(content, "type", None) in {"text", "output_text"}:
                    text_value = getattr(content, "text", None)
                    if text_value:
                        return text_value
    raise ValueError("Réponse du modèle sans texte exploitable.")


def generate_quiz_from_text(text: str, category: str, nb_questions: int = 20) -> List[Dict]:
    """Génère une liste de questions de quiz à partir d'un texte de cours."""

    truncated_text = _truncate_text(text)
    prompt = textwrap.dedent(
        f"""
        Vous êtes un formateur expert du BIA.
        À partir du cours suivant sur la catégorie : {category}, générez EXACTEMENT {nb_questions} questions de quiz de type QCM niveau BIA.
        Pour chaque question :
        - 4 propositions de réponse,
        - 1 seule bonne réponse,
        - une explication courte.
        Répondez STRICTEMENT au format JSON suivant (et rien d'autre) :
        [
          {{
            \"question\": \"...\",
            \"choix1\": \"...\",
            \"choix2\": \"...\",
            \"choix3\": \"...\",
            \"choix4\": \"...\",
            \"bonne_reponse\": 1,
            \"explication\": \"...\"
          }},
          ...
        ]
        Voici le cours :
        """{truncated_text}"""
        """
    ).strip()

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    response_text = _extract_response_text(response)

    try:
        questions = json.loads(response_text)
    except json.JSONDecodeError as exc:  # noqa: B904
        raise ValueError("Réponse du modèle au format JSON invalide.") from exc

    if not isinstance(questions, list):
        raise ValueError("Le format JSON renvoyé n'est pas une liste de questions.")

    if len(questions) != nb_questions:
        raise ValueError(f"Le modèle doit retourner exactement {nb_questions} questions (reçu {len(questions)}).")

    return questions
