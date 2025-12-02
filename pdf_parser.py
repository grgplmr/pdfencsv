"""Utilitaires d'extraction du texte des PDF."""

from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: str) -> str:
    """Lit toutes les pages d'un PDF et renvoie le texte concaténé."""
    reader = PdfReader(pdf_path)
    texts = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    return "\n".join(texts)
