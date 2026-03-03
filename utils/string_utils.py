import unicodedata

def normalize_text(text: str) -> str:
    """
    Normalise une chaîne de caractères en retirant les accents et en la passant en minuscules.
    Idéal pour rendre les comparaisons de recherche insensibles à la casse et aux accents.
    
    :param text: La chaîne de caractères d'origine à normaliser.
    :return: La chaîne nettoyée, sans accents et en minuscules.
    """
    if not text:
        return ""
    text = text.lower()
    text_normalized = unicodedata.normalize('NFKD', text)
    return "".join(c for c in text_normalized if not unicodedata.combining(c))