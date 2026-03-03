import sqlite3
import csv
from contextlib import closing
from typing import List, Tuple, Optional, Any
from config import DB_PATH, DB_DIR

class AnimeDatabase:
    """
    Gestionnaire de la base de données SQLite pour l'application AnimeSoul.
    Fournit des méthodes sécurisées pour interagir avec les données des animes.
    """

    ALLOWED_COLUMNS = {
        "Titre", "Contenu", "Info_Suite", "Note", "Premiere_Fois", 
        "Nb_Vu", "Derniere_Verif", "Site_URL", "NAUT_MAL_URL"
    }

    def __init__(self) -> None:
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """
        Crée et retourne une nouvelle connexion à la base de données SQLite.
        """
        return sqlite3.connect(DB_PATH)

    def _init_db(self) -> None:
        """Crée le dossier et la table 'animes' avec ses index s'ils sont manquants."""
        if not DB_DIR.exists():
            DB_DIR.mkdir(parents=True, exist_ok=True)

        with closing(self._get_connection()) as conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS animes (
                        Titre TEXT,
                        Contenu TEXT,
                        Info_Suite TEXT,
                        Note INTEGER,
                        Premiere_Fois TEXT,
                        Nb_Vu INTEGER,
                        Derniere_Verif TEXT,
                        Site_URL TEXT,
                        NAUT_MAL_URL TEXT
                    )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_titre ON animes (Titre)")

    def get_all_animes(self) -> List[Tuple[Any, ...]]:
        """
        Récupère tous les animes de la base de données, triés par note et par titre.
        """
        if not DB_PATH.exists():
            return []
            
        with closing(self._get_connection()) as conn:
            cursor = conn.cursor()
            query = """
                SELECT Titre, Contenu, Info_Suite, Note, Premiere_Fois, 
                       Nb_Vu, Derniere_Verif, Site_URL, NAUT_MAL_URL 
                FROM animes 
                ORDER BY Note DESC, Titre ASC
            """
            cursor.execute(query)
            return cursor.fetchall()

    def get_anime_details(self, titre: str, colonnes: List[str]) -> Optional[Tuple[Any, ...]]:
        """
        Récupère les détails spécifiques d'un anime en fonction de son titre.
        """
        invalid_cols = [col for col in colonnes if col not in self.ALLOWED_COLUMNS]
        if invalid_cols:
            raise ValueError(f"Colonnes non autorisées : {invalid_cols}")

        cols_str = ", ".join(colonnes)
        query = f"SELECT {cols_str} FROM animes WHERE Titre = ?"
        with closing(self._get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (titre,))
            return cursor.fetchone()

    def _sanitize_for_csv(self, value: Any) -> str:
        """
        Prévient l'exécution de formules dans Excel/Calc (DDE Injection).
        """
        val_str = str(value) if value is not None else ""
        if val_str.startswith(("=", "+", "-", "@", "\t", "\r")):
            return f"'{val_str}"
        return val_str

    def export_to_csv(self, filepath: str) -> None:
        """
        Exporte la totalité de la table dans un fichier CSV de manière sécurisée.
        """
        with closing(self._get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM animes")
            rows = cursor.fetchall()
            col_names = [description[0] for description in cursor.description]
            
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(col_names)
            safe_rows = [tuple(self._sanitize_for_csv(cell) for cell in row) for row in rows]
            writer.writerows(safe_rows)

    def add_anime(self, data: Tuple[Any, ...]) -> bool:
        """
        Ajoute un nouvel anime dans la base de données en utilisant des requêtes paramétrées.
        """
        query = """
            INSERT INTO animes (Titre, Contenu, Info_Suite, Note, Premiere_Fois, Nb_Vu, Derniere_Verif, Site_URL, NAUT_MAL_URL)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with closing(self._get_connection()) as conn:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute(query, data)
            return True
        except sqlite3.Error as e:
            print(f"Erreur DB (Ajout) : {e}")
            return False
    
    def update_anime(self, old_title: str, data: Tuple[Any, ...]) -> bool:
        """Met à jour un anime existant."""
        query = """
            UPDATE animes 
            SET Titre=?, Contenu=?, Info_Suite=?, Note=?, Premiere_Fois=?, 
                Nb_Vu=?, Derniere_Verif=?, Site_URL=?, NAUT_MAL_URL=?
            WHERE Titre=?
        """
        try:
            with closing(self._get_connection()) as conn:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute(query, (*data, old_title))
            return True
        except sqlite3.Error as e:
            print(f"Erreur DB (Mise à jour) : {e}")
            return False
    
    def delete_anime(self, titre: str) -> bool:
        """Supprime un anime de la base de données."""
        query = "DELETE FROM animes WHERE Titre = ?"
        try:
            with closing(self._get_connection()) as conn:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute(query, (titre,))
            return True
        except sqlite3.Error as e:
            print(f"Erreur DB (Suppression) : {e}")
            return False