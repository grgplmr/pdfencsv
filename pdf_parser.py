"""Utilitaires d'extraction et de parsing des quiz PDF."""

import re
from typing import List, Dict

# Nécessite : pip install pypdf
from pypdf import PdfReader

QuestionDict = Dict[str, str]


def extract_text_from_pdf(pdf_path: str) -> str:
    """Lit toutes les pages d'un PDF et renvoie le texte concaténé."""
    reader = PdfReader(pdf_path)
    texts = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    return "\n".join(texts)


def _clean_line(line: str) -> str:
    return line.strip().replace("\uf0b7", "").strip()


def parse_quiz_from_text(text: str) -> List[QuestionDict]:
    """Parse le texte complet d'un quiz et renvoie la liste des questions."""
    # Séparation des blocs par question en gardant l'indicateur "Qn -".
    blocks = re.split(r"(?=Q\d+\s*-)", text)
    questions: List[QuestionDict] = []

    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = [_clean_line(line) for line in block.splitlines() if _clean_line(line)]
        if not lines:
            continue

        # La première ligne contient la question après "Qn - ".
        question_match = re.match(r"Q\d+\s*-\s*(.+)", lines[0])
        if not question_match:
            continue
        question_text = question_match.group(1).strip()

        # Chercher les 4 choix sur des lignes séparées commençant par 1) 2) 3) 4)
        choix = {}
        for line in lines[1:]:
            option_match = re.match(r"([1-4])\)\s*(.+)", line)
            if option_match:
                choix[option_match.group(1)] = option_match.group(2).strip()

        if len(choix) < 4:
            raise ValueError("Moins de 4 choix trouvés pour une question.")

        # Réponse : X
        answer_line = next((l for l in lines if l.lower().startswith("réponse")), None)
        if not answer_line:
            raise ValueError("Ligne de réponse manquante.")
        answer_match = re.search(r"[1-4]", answer_line)
        if not answer_match:
            raise ValueError("Réponse invalide (attendu 1-4).")
        bonne_reponse = int(answer_match.group(0))

        # Explication : texte après le préfixe
        explanation_line = next((l for l in lines if l.lower().startswith("explication")), "")
        explication = re.sub(r"^explication\s*:\s*", "", explanation_line, flags=re.IGNORECASE).strip()

        questions.append(
            {
                "question": question_text,
                "choix1": choix.get("1", ""),
                "choix2": choix.get("2", ""),
                "choix3": choix.get("3", ""),
                "choix4": choix.get("4", ""),
                "bonne_reponse": bonne_reponse,
                "explication": explication,
            }
        )

    return questions
