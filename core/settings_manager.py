import json
from typing import Dict, Any
from config import SETTINGS_PATH

class SettingsManager:
    """
    Gestionnaire des paramètres utilisateur.
    Permet de charger et de sauvegarder la configuration locale (thème, colonnes, etc.) au format JSON.
    """
    DEFAULT_SETTINGS: Dict[str, Any] = {
        "theme": "dark",
        "download_images": True,
        "visible_columns": ["titre", "contenu", "nb_vu", "note"]
    }

    @staticmethod
    def load() -> Dict[str, Any]:
        """
        Charge les paramètres depuis le fichier JSON.
        Si le fichier est absent ou corrompu, retourne les paramètres par défaut.
        
        :return: Un dictionnaire contenant les paramètres de l'application.
        """
        if SETTINGS_PATH.exists():
            try:
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    user_settings = json.load(f)
                    # Fusionne les paramètres par défaut avec ceux de l'utilisateur pour éviter les clés manquantes
                    return {**SettingsManager.DEFAULT_SETTINGS, **user_settings}
            except json.JSONDecodeError as e:
                print(f"Erreur: Fichier settings.json corrompu ({e}). Paramètres par défaut chargés.")
            except OSError as e:
                print(f"Erreur: Impossible de lire settings.json ({e}). Paramètres par défaut chargés.")
                
        return dict(SettingsManager.DEFAULT_SETTINGS)

    @staticmethod
    def save(settings: Dict[str, Any]) -> None:
        """
        Sauvegarde les paramètres actuels dans le fichier JSON.
        
        :param settings: Dictionnaire contenant les paramètres à sauvegarder.
        """
        try:
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4)
        except OSError as e:
            print(f"Erreur grave: Impossible de sauvegarder les paramètres ({e})")