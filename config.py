"""
Configuration globale de l'application AnimeSoul.
Contient les constantes de chemins, les thèmes de couleurs et les paramètres globaux.
"""
from pathlib import Path
from typing import Dict

BASE_DIR: Path = Path(__file__).resolve().parent

THEMES: Dict[str, Dict[str, str]] = {
    "dark": {
        "bg_main": "#1E1E2E",       # Fond principal (Gris/Bleu très sombre)
        "bg_dark": "#181825",       # Fond secondaire (Pour la liste et les champs)
        "primary": "#10B981",       # Vert émeraude (Couleur d'accent moderne)
        "primary_hover": "#059669", # Vert foncé pour le survol
        "secondary": "#313244",     # Gris moyen pour les séparateurs/titres
        "text": "#CDD6F4",          # Texte principal (Blanc cassé doux)
        "text_muted": "#A6ADC8",    # Texte secondaire (Gris clair)
        "white": "#FFFFFF",
        "alert": "#F9E2AF",         # Jaune doux
        "danger": "#F38BA8",        # Rouge doux
        "link": "#89B4FA"           # Bleu moderne pour les liens
    },
    "light": {
        "bg_main": "#F8F9FA",       # Fond principal très clair
        "bg_dark": "#FFFFFF",       # Fond secondaire (liste/champs) en blanc pur
        "primary": "#10B981",       # Vert émeraude conservé
        "primary_hover": "#059669", 
        "secondary": "#E9ECEF",     # Gris clair pour les séparateurs/titres
        "text": "#212529",          # Texte principal (gris très foncé, presque noir)
        "text_muted": "#6C757D",    # Texte secondaire (gris moyen)
        "white": "#FFFFFF",
        "alert": "#FFC107",
        "danger": "#DC3545",
        "link": "#0D6EFD"           # Bleu classique pour les liens
    }
}

DB_DIR: Path = BASE_DIR / "database"
DB_PATH: Path = DB_DIR / "animes.db"

ASSETS_DIR: Path = BASE_DIR / "assets"
SETTINGS_PATH: Path = BASE_DIR / "settings.json"