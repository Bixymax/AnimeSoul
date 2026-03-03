import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from urllib.parse import urlparse

from config import THEMES
from utils.system_utils import apply_dark_title_bar
from utils.string_utils import normalize_text

class AnimeFormWindow(tk.Toplevel):
    def __init__(self, parent, app_instance, original_title=None):
        super().__init__(parent)
        self.app = app_instance
        self.original_title = original_title
        self.is_edit_mode = original_title is not None
        
        self.current_theme_name = self.app.current_theme_name
        self.colors = THEMES.get(self.current_theme_name, THEMES["dark"])
        self.normal_text_color = self.colors["text"]
        self.placeholder_color = "#A0A0A0" if self.current_theme_name == "dark" else "#808080"

        self.withdraw()
        titre_fenetre = f"Modifier : {self.original_title}" if self.is_edit_mode else "Ajouter un Anime"
        self.title(titre_fenetre)
        self.resizable(False, False)
        self.configure(bg=self.colors["bg_main"])
        
        self.transient(parent)
        self.grab_set()
        self.focus_set()

        parent.update_idletasks()
        width, height = 600, 600
        pos_x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
        pos_y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

        self.entries = {}
        self.placeholders_text = {
            "Titre": "Ex: Frieren",
            "Contenu": "Ex: 5 Saisons + 1 Film",
            "Note": "Ex: 9",
            "Site_URL": "Ex: https://www.swordart-online.net/",
            "NAUT_MAL_URL": "Ex: https://myanimelist.net/..."
        }
        
        self.columns = ["Titre", "Contenu", "Info_Suite", "Note", "Premiere_Fois", "Nb_Vu", "Derniere_Verif", "Site_URL", "NAUT_MAL_URL"]
        self.anime_data = self.app.db.get_anime_details(self.original_title, self.columns) if self.is_edit_mode else None

        self.create_widgets()
        
        self.deiconify()
        self.after(10, lambda: apply_dark_title_bar(self, dark_mode=(self.current_theme_name == "dark")))

    def on_focus_in(self, entry, placeholder_text):
        if entry.cget('fg') == self.placeholder_color:
            entry.delete(0, tk.END)
            entry.config(fg=self.normal_text_color)

    def on_focus_out(self, entry, placeholder_text):
        if not entry.get().strip():
            entry.insert(0, placeholder_text)
            entry.config(fg=self.placeholder_color)

    def create_widgets(self):
        main_frame = tk.Frame(self, bg=self.colors["bg_main"], padx=30, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)

        fields = {
            "Titre": "Titre *",
            "Contenu": "Format / Saisons *",
            "Info_Suite": "Infos Suite *",
            "Note": "Note (/10) *",
            "Premiere_Fois": "Premier visionnage *",
            "Nb_Vu": "Nombre de vues *",
            "Derniere_Verif": "Dernière vérification *",
            "Site_URL": "Lien Site",
            "NAUT_MAL_URL": "Lien Nautiljon/MyAnimeList"
        }

        today_str = datetime.today().strftime("%d/%m/%Y")

        row_idx = 0
        for i, (db_col, label_text) in enumerate(fields.items()):
            tk.Label(main_frame, text=label_text, bg=self.colors["bg_main"], fg=self.colors["text"], 
                     font=("Segoe UI", 10, "bold" if "*" in label_text else "normal")).grid(row=row_idx, column=0, sticky="w", pady=10)
            
            current_value = ""
            if self.is_edit_mode and self.anime_data and self.anime_data[i] is not None:
                current_value = str(self.anime_data[i])
            elif not self.is_edit_mode:
                if db_col in ["Premiere_Fois", "Derniere_Verif"]:
                    current_value = today_str
                elif db_col == "Nb_Vu":
                    current_value = "1"

            if db_col == "Info_Suite":
                entry = ttk.Combobox(main_frame, values=["Suite annoncée", "Pas de suite / En attente", "Terminé"], 
                                     font=("Segoe UI", 10), state="readonly", width=30)
                entry.grid(row=row_idx, column=1, sticky="w", padx=(15, 0), pady=10)
                entry.set(current_value if current_value else "Pas de suite / En attente")
            else:
                entry = tk.Entry(main_frame, font=("Segoe UI", 10), width=32, relief="flat",
                                 bg=self.colors["bg_dark"], fg=self.normal_text_color, insertbackground=self.colors["text"])
                entry.grid(row=row_idx, column=1, sticky="w", padx=(15, 0), pady=10, ipady=4)
                
                if current_value:
                    entry.insert(0, current_value)
                elif db_col in self.placeholders_text:
                    text_placeholder = self.placeholders_text[db_col]
                    entry.insert(0, text_placeholder)
                    entry.config(fg=self.placeholder_color)
                    
                    entry.bind("<FocusIn>", lambda event, e=entry, t=text_placeholder: self.on_focus_in(e, t))
                    entry.bind("<FocusOut>", lambda event, e=entry, t=text_placeholder: self.on_focus_out(e, t))

            self.entries[db_col] = entry
            row_idx += 1

        bottom_frame = tk.Frame(self, bg=self.colors["bg_main"], pady=15)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        if self.is_edit_mode:
            tk.Button(bottom_frame, text="🗑 Supprimer", command=self.delete_anime, width=12, 
                      bg=self.colors.get("danger", "#DC3545"), fg=self.colors["white"], font=("Segoe UI", 10, "bold"), 
                      relief="flat", bd=0, cursor="hand2", pady=5).pack(side=tk.LEFT, padx=20)

        tk.Button(bottom_frame, text="Annuler", command=self.destroy, width=12, 
                  bg=self.colors["secondary"], fg=self.colors["text"], relief="flat", bd=0, cursor="hand2", pady=5).pack(side=tk.RIGHT, padx=20)
                  
        texte_bouton_save = "Sauvegarder" if self.is_edit_mode else "Ajouter"
        tk.Button(bottom_frame, text=texte_bouton_save, command=self.save_anime, width=12, 
                  bg=self.colors["primary"], fg=self.colors["white"], font=("Segoe UI", 10, "bold"), relief="flat", bd=0, cursor="hand2", pady=5).pack(side=tk.RIGHT)

    def get_clean_value(self, db_col) -> str:
        entry = self.entries[db_col]
        val = entry.get().strip()
        if isinstance(entry, tk.Entry) and entry.cget('fg') == self.placeholder_color:
            return ""
        return val

    def save_anime(self) -> None:
        titre_clean = self.get_clean_value("Titre")
        if not titre_clean:
            messagebox.showwarning("Erreur", "Le champ 'Titre' est obligatoire.", parent=self)
            self.entries["Titre"].focus_set()
            return
            
        titre_nouveau_normalise = normalize_text(titre_clean)
        tous_les_animes = self.app.db.get_all_animes()
        
        for anime in tous_les_animes:
            titre_existant = anime[0]
            if self.is_edit_mode and titre_existant == self.original_title:
                continue
            if normalize_text(titre_existant) == titre_nouveau_normalise:
                messagebox.showwarning("Erreur", f"Un anime similaire existe déjà : '{titre_existant}'", parent=self)
                self.entries["Titre"].focus_set()
                return

        contenu = self.get_clean_value("Contenu")
        if not contenu:
            messagebox.showwarning("Erreur", "Le champ 'Format / Saisons' est obligatoire.", parent=self)
            self.entries["Contenu"].focus_set()
            return
            
        mots_cles = ["saison", "film", "episode", "épisode", "one shot", "saisons", "films", "episodes", "épisodes"]
        if not any(mot in contenu.lower() for mot in mots_cles):
            messagebox.showwarning("Erreur", "Le champ 'Format / Saisons' doit contenir au moins un de ces mots :\nSaison, Film, Episode ou One shot.", parent=self)
            self.entries["Contenu"].focus_set()
            return

        info_suite = self.entries["Info_Suite"].get().strip()
        if not info_suite:
            messagebox.showwarning("Erreur", "Le champ 'Infos Suite' est obligatoire.", parent=self)
            self.entries["Info_Suite"].focus_set()
            return

        note_str = self.get_clean_value("Note")
        try:
            note = int(note_str)
            if not (0 <= note <= 10):
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Erreur", "La 'Note' doit être un nombre entier compris entre 0 et 10.", parent=self)
            self.entries["Note"].focus_set()
            return

        prem_fois = self.get_clean_value("Premiere_Fois")
        date_to_check = prem_fois.lower().replace("avant ", "").replace("avant", "").strip()
        try:
            datetime.strptime(date_to_check, "%d/%m/%Y")
        except ValueError:
            messagebox.showwarning("Erreur", "Le 'Premier visionnage' doit être une date au format JJ/MM/AAAA.", parent=self)
            self.entries["Premiere_Fois"].focus_set()
            return

        nb_vu_str = self.get_clean_value("Nb_Vu")
        try:
            int(nb_vu_str)
        except ValueError:
            messagebox.showwarning("Erreur", "Le 'Nombre de vues' doit être un nombre entier.", parent=self)
            self.entries["Nb_Vu"].focus_set()
            return

        dern_verif = self.get_clean_value("Derniere_Verif")
        try:
            datetime.strptime(dern_verif, "%d/%m/%Y")
        except ValueError:
            messagebox.showwarning("Erreur", "La 'Dernière vérification' doit être une date valide au format JJ/MM/AAAA.", parent=self)
            self.entries["Derniere_Verif"].focus_set()
            return

        site_url = self.get_clean_value("Site_URL")
        if site_url:
            parsed = urlparse(site_url)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                messagebox.showwarning("Erreur", "Le 'Lien Site' doit être une URL valide (http ou https).", parent=self)
                self.entries["Site_URL"].focus_set()
                return

        url_mal = self.get_clean_value("NAUT_MAL_URL")
        if url_mal:
            parsed_mal = urlparse(url_mal)
            if parsed_mal.scheme not in ("http", "https") or not parsed_mal.netloc:
                messagebox.showwarning("Erreur", "Le lien Nautiljon/MyAnimeList doit être une URL valide.", parent=self)
                self.entries["NAUT_MAL_URL"].focus_set()
                return
                
            domaine = parsed_mal.netloc.lower()
            if "myanimelist.net" not in domaine and "nautiljon.com" not in domaine:
                messagebox.showwarning("Erreur", "Le lien doit pointer vers 'myanimelist.net' ou 'nautiljon.com'.", parent=self)
                self.entries["NAUT_MAL_URL"].focus_set()
                return

        data = (
            titre_clean, contenu, info_suite, note_str, prem_fois,
            nb_vu_str, dern_verif, site_url, url_mal
        )

        if self.is_edit_mode:
            success = self.app.db.update_anime(self.original_title, data)
        else:
            success = self.app.db.add_anime(data)

        if success:
            self.app.refresh_list()
            self.master.event_generate("<<AnimeDataChanged>>")
            self.destroy()
    
    def delete_anime(self) -> None:
        confirmation = messagebox.askyesno(
            "Confirmation de suppression", 
            f"Êtes-vous sûr de vouloir supprimer '{self.original_title}' ?\nCette action est irréversible.",
            parent=self
        )
        if confirmation:
            if self.app.db.delete_anime(self.original_title):
                self.master.event_generate("<<AnimeDataChanged>>")
                self.destroy()
            else:
                messagebox.showerror("Erreur", "Un problème est survenu lors de la suppression.", parent=self)