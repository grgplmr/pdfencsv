"""Écriture des questions de quiz dans un fichier CSV."""

import csv
from typing import List, Dict


def write_quiz_csv(title: str, description: str, questions: List[Dict[str, str]], output_path: str) -> None:
    header = [
        "title",
        "description",
        "question",
        "choix1",
        "choix2",
        "choix3",
        "choix4",
        "bonne_reponse(1-4)",
        "explication",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(header)

        for idx, q in enumerate(questions):
            writer.writerow(
                [
                    title if idx == 0 else "",
                    description if idx == 0 else "",
                    q.get("question", ""),
                    q.get("choix1", ""),
                    q.get("choix2", ""),
                    q.get("choix3", ""),
                    q.get("choix4", ""),
                    q.get("bonne_reponse", ""),
                    q.get("explication", ""),
                ]
            )
