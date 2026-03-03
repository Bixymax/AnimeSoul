import tkinter as tk
from tkinter import font, ttk, messagebox
import time
import threading
import webbrowser
from typing import Any, Dict
from PIL import Image, ImageTk

from config import THEMES, ASSETS_DIR
from core.database import AnimeDatabase
from core.settings_manager import SettingsManager
from utils.image_utils import load_icon, fetch_api_image
from utils.system_utils import apply_dark_title_bar
from utils.string_utils import normalize_text
from ui.settings_window import SettingsWindow

class AnimeListApp:
    """
    Classe principale contrôlant la fenêtre de liste des animes.
    Gère l'interface principale, le tableau de données (Treeview), et les interactions API.
    """

    def __init__(self, root: tk.Tk) -> None:
        """
        Initialise la fenêtre principale de l'application.
        
        :param root: L'instance principale Tkinter (Tk).
        """
        self.root = root
        self.root.title("AnimeSoul")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        app_width = min(1400, int(screen_width * 0.8))
        app_height = min(1000, int(screen_height * 0.8))
        
        pos_x = (screen_width // 2) - (app_width // 2)
        pos_y = (screen_height // 2) - (app_height // 2)
        
        self.root.geometry(f"{app_width}x{app_height}+{pos_x}+{pos_y}")
        self.root.minsize(1050, 750) 
        
        self.db = AnimeDatabase()
        self.settings = SettingsManager.load()
        
        self.search_timer: Any = None

        self.current_theme_name = self.settings.get("theme", "dark")
        self.colors = THEMES.get(self.current_theme_name, THEMES["dark"])
        
        self.root.configure(bg=self.colors["bg_main"])
        
        self.last_request_time: float = 0.0
        self.current_fetch_title: Any = None

        self.custom_font = font.Font(family="Segoe UI", size=11)
        self.title_font = font.Font(family="Segoe UI", size=28, weight="bold")
        self.label_font = font.Font(family="Segoe UI", size=10, weight="bold")

        self.setup_icon()
        apply_dark_title_bar(self.root, dark_mode=(self.current_theme_name == "dark"))

        self.display_fields: Dict[str, str] = {
            "Titre": "Titre",
            "Contenu": "Format / Saisons",
            "Note": "Note (/10)",
            "Premiere_Fois": "Premier visionnage",
            "Nb_Vu": "Nombre de vues",
            "NAUT_MAL_URL": "Lien Nautiljon/MyAnimeList" 
        }

        self.tree_headers: Dict[str, str] = {
            "titre": "Titre",
            "contenu": "Format / Saisons",
            "info_suite": "Infos Suite",
            "note": "Note",
            "premiere_fois": "Premier visionnage",
            "nb_vu": "Nombre de vues",
            "derniere_verif": "Dernière vérification",
            "site_url": "Lien Site",
            "nautiljon_url": "Lien Nautiljon/MyAnimeList"
        }

        self.create_header()
        self.create_main_content()
        self.create_footer_list()
        
        self.refresh_list()
        self.apply_settings(self.settings)
        self.root.bind("<<AnimeDataChanged>>", self._on_data_changed)

    def _on_data_changed(self, event: tk.Event = None) -> None:
        """Méthode appelée automatiquement quand un anime est ajouté, modifié ou supprimé."""
        self.refresh_list()
        self.reset_poster()
        for col in self.display_fields.keys():
            entry = self.entries[col]
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, "---")
            entry.config(state="readonly")

    def setup_icon(self) -> None:
        """Configure l'icône de l'application en fonction du thème actif."""
        icon_file = "anime_soul_logo_small_dark.png" if self.current_theme_name == "dark" else "anime_soul_logo_small.png"
        icon_path = ASSETS_DIR / icon_file
        if icon_path.exists():
            img = tk.PhotoImage(file=str(icon_path))
            self.root.iconphoto(True, img)

    def create_header(self) -> None:
        """Construit l'en-tête de l'interface principale (Logo, Titre, Bouton Paramètres)."""
        header_frame = tk.Frame(self.root, bg=self.colors["bg_main"], pady=15, padx=30)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        logo_file = "anime_soul_logo_dark.png" if self.current_theme_name == "dark" else "anime_soul_logo.png"
        logo_path = ASSETS_DIR / logo_file
        
        if logo_path.exists():
            self.logo_img = load_icon(str(logo_path), (100, 100))
            tk.Label(header_frame, image=self.logo_img, bg=self.colors["bg_main"]).pack(side=tk.LEFT)
        
        tk.Label(header_frame, text="Anime Soul", font=self.title_font, 
                 bg=self.colors["bg_main"], fg=self.colors["text"]).pack(side=tk.LEFT, padx=15)

        param_path = ASSETS_DIR / "parametres.png"
        if param_path.exists():
            self.param_img = load_icon(str(param_path), (30, 30))
            tk.Button(header_frame, image=self.param_img, bg=self.colors["bg_main"],
                      relief="flat", activebackground=self.colors["bg_main"], bd=0, cursor="hand2",
                      command=self.open_settings).pack(side=tk.RIGHT)

    def create_main_content(self) -> None:
        """Construit la zone d'affichage des détails et de l'affiche de l'anime (au centre)."""
        content_frame = tk.Frame(self.root, bg=self.colors["bg_main"], pady=20, padx=30)
        content_frame.pack(side=tk.TOP, fill=tk.X)
        
        content_frame.grid_columnconfigure(1, weight=1)

        self.reset_poster()
        
        self.poster_label = tk.Label(content_frame, image=self.poster_img, bg=self.colors["bg_main"])
        self.poster_label.grid(row=0, column=0, padx=(0, 40), sticky="nw")

        details_box = tk.Frame(content_frame, bg=self.colors["bg_main"])
        details_box.grid(row=0, column=1, sticky="nw") 

        self.entries = {}
        row_idx, col_idx = 0, 0
        
        for col, label_text in self.display_fields.items():
            field_frame = tk.Frame(details_box, bg=self.colors["bg_main"])
            field_frame.grid(row=row_idx, column=col_idx, sticky="nw", padx=(0, 40), pady=(0, 15))
            
            tk.Label(field_frame, text=label_text.upper(), bg=self.colors["bg_main"], fg=self.colors["text_muted"], 
                     font=self.label_font).pack(anchor="w", pady=(0, 4))
            
            entry = tk.Entry(field_frame, font=self.custom_font, width=32, relief="flat", 
                             bg=self.colors["bg_dark"], fg=self.colors["text"], insertbackground=self.colors["text"],
                             readonlybackground=self.colors["bg_dark"], highlightthickness=0)
            entry.pack(anchor="w", ipady=5)
            entry.insert(0, "---")
            entry.config(state="readonly")
            
            if "URL" in col:
                entry.config(fg=self.colors["link"], cursor="hand2")
                entry.bind("<Button-1>", lambda event, c=col: self.open_link(c))

            self.entries[col] = entry
            
            col_idx += 1
            if col_idx > 1:
                col_idx = 0
                row_idx += 1

    def create_footer_list(self) -> None:
        """Construit le tableau (Treeview) et la barre de recherche dans la partie inférieure."""
        list_container = tk.Frame(self.root, bg=self.colors["bg_main"], padx=30, pady=20)
        list_container.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        action_frame = tk.Frame(list_container, bg=self.colors["bg_main"])
        action_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        search_frame = tk.Frame(action_frame, bg=self.colors["bg_main"])
        search_frame.pack(side=tk.LEFT, fill=tk.X)

        tk.Label(search_frame, text="🔍 Rechercher :", bg=self.colors["bg_main"], fg=self.colors["text"], 
                 font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=(0, 10))
                 
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search_change)
        
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=self.custom_font, width=35,
                                relief="flat", bg=self.colors["bg_dark"], fg=self.colors["text"], insertbackground=self.colors["text"],
                                highlightthickness=0)
        search_entry.pack(side=tk.LEFT, ipady=6)

        tk.Button(action_frame, text="✚ Ajouter", command=self.open_add_window, 
                  font=("Segoe UI", 10, "bold"), bg=self.colors["primary"], fg=self.colors["white"], 
                  width=15, pady=6, relief="flat", bd=0, activebackground=self.colors["primary_hover"], activeforeground=self.colors["white"],
                  cursor="hand2").pack(side=tk.RIGHT, padx=(10, 0))
                 
        tk.Button(action_frame, text="✎ Modifier", command=self.open_edit_window, 
                  font=("Segoe UI", 10, "bold"), bg=self.colors["secondary"], fg=self.colors["text"], 
                  width=15, pady=6, relief="flat", bd=0, activebackground=self.colors["bg_dark"], activeforeground=self.colors["white"],
                  cursor="hand2").pack(side=tk.RIGHT)

        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview", 
                        background=self.colors["bg_dark"], 
                        fieldbackground=self.colors["bg_dark"], 
                        foreground=self.colors["text"], 
                        font=self.custom_font, 
                        rowheight=35,
                        borderwidth=0)
        
        style.configure("Treeview.Heading", 
                        font=("Segoe UI", 11, "bold"), 
                        background=self.colors["secondary"], 
                        foreground=self.colors["text"],
                        relief="flat",
                        padding=5)
                        
        style.map("Treeview", background=[('selected', self.colors["primary"])])
        style.map("Treeview.Heading", background=[('active', self.colors["primary_hover"])])
        
        tree_frame = tk.Frame(list_container)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        
        self.tree = ttk.Treeview(tree_frame, columns=tuple(self.tree_headers.keys()), 
                                 show="tree headings", yscrollcommand=scrollbar.set, selectmode="browse")

        def prevent_resize(event: tk.Event) -> str | None:
            if self.tree.identify_region(event.x, event.y) == "separator":
                return "break"
                
        self.tree.bind('<Button-1>', prevent_resize)
        
        scrollbar.config(command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree.heading("#0", text="🔄", command=lambda: self.refresh_list())
        self.tree.column("#0", width=40, stretch=tk.NO, anchor="center")

        for col, text in self.tree_headers.items():
            self.tree.heading(col, text=text, command=lambda c=col: self.sort_column(c, False))

        self.tree.column("titre", width=300, minwidth=200, anchor="w", stretch=True)
        self.tree.column("contenu", width=150, minwidth=100, anchor="center", stretch=True)
        self.tree.column("info_suite", width=120, minwidth=100, anchor="center", stretch=True)
        self.tree.column("note", width=80, minwidth=50, anchor="center", stretch=True)
        self.tree.column("premiere_fois", width=130, minwidth=100, anchor="center", stretch=True)
        self.tree.column("nb_vu", width=80, minwidth=60, anchor="center", stretch=True)
        self.tree.column("derniere_verif", width=130, minwidth=100, anchor="center", stretch=True)
        self.tree.column("site_url", width=120, minwidth=80, anchor="w", stretch=True)
        self.tree.column("nautiljon_url", width=120, minwidth=80, anchor="w", stretch=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_anime_select)
        self.tree.bind("<Double-1>", self.copy_cell_to_clipboard)

    def copy_cell_to_clipboard(self, event: tk.Event) -> None:
        """Copie le contenu de la cellule cliquée dans le presse-papier et affiche une bulle informative."""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            row_id = self.tree.identify_row(event.y)
            column_id = self.tree.identify_column(event.x) 
            
            if row_id and column_id:
                logical_col_id = self.tree.column(column_id, "id")
                cell_value = str(self.tree.set(row_id, logical_col_id))
                
                if cell_value and cell_value not in ("None", "N/A", ""):
                    self.root.clipboard_clear()
                    self.root.clipboard_append(cell_value)
                    self.root.update()
                    
                    tooltip = tk.Toplevel(self.root)
                    tooltip.wm_overrideredirect(True) 
                    tooltip.configure(bg=self.colors["primary"])
                    
                    x = event.x_root + 15
                    y = event.y_root + 15
                    tooltip.geometry(f"+{x}+{y}")
                    
                    label = tk.Label(tooltip, text=f"Copié : {cell_value}", 
                                     bg=self.colors["primary"], fg=self.colors["bg_main"], 
                                     font=("Segoe UI", 9, "bold"), padx=10, pady=4)
                    label.pack()
                    
                    tooltip.after(1500, tooltip.destroy)

    def refresh_list(self, search_query: str = "") -> None:
        """Vite le tableau et le reremplit avec les données de la base. Filtre si une recherche est active."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for col, text in self.tree_headers.items():
            self.tree.heading(col, text=text, command=lambda c=col: self.sort_column(c, False))
            
        animes = self.db.get_all_animes()
        
        if not animes:
            self.tree.insert("", tk.END, values=("Aucune donnée ou base introuvable.", "", "", "", "", "", "", "", ""))
            return
            
        query_clean = normalize_text(search_query)
        
        for anime in animes:
            titre_anime = str(anime[0])
            titre_clean = normalize_text(titre_anime)
            
            if not query_clean or query_clean in titre_clean:
                self.tree.insert("", tk.END, values=anime)

    def on_search_change(self, *args: Any) -> None:
        """Callback déclenché à chaque frappe dans le champ de recherche, utilise un minuteur (debounce)."""
        if self.search_timer is not None:
            self.root.after_cancel(self.search_timer)
            
        self.search_timer = self.root.after(300, self.execute_search)

    def execute_search(self) -> None:
        """Exécute la recherche visuelle une fois le minuteur terminé."""
        terme_recherche = self.search_var.get()
        self.refresh_list(terme_recherche)

    def open_link(self, col: str) -> None:
        """Ouvre l'URL présente dans le champ de détail dans le navigateur web par défaut."""
        url = self.entries[col].get()
        if url and url.startswith("http"):
            webbrowser.open(url)

    def on_anime_select(self, event: tk.Event) -> None:
        """Gère l'événement lors du clic sur un anime dans le Treeview (remplit les détails et lance l'API)."""
        selected_item = self.tree.selection()
        if not selected_item: return
        
        titre = self.tree.item(selected_item[0], "values")[0]
        row = self.db.get_anime_details(titre, list(self.display_fields.keys())) 
        
        if row:
            for i, col in enumerate(self.display_fields.keys()):
                entry = self.entries[col]
                val = row[i] if row[i] is not None else "N/A"
                
                entry.config(state="normal")
                entry.delete(0, tk.END)
                entry.insert(0, str(val))
                entry.config(state="readonly")
                
            current_time = time.time()
            temps_ecoule = current_time - self.last_request_time
            
            if temps_ecoule < 0.5:
                self.reset_poster()
                if temps_ecoule < 0.2:
                    messagebox.showwarning("Doucement !", "Vous naviguez trop vite.\nPour respecter l'API, veuillez patienter un instant.")
                return
                
            self.last_request_time = current_time
            self.current_fetch_title = titre
            threading.Thread(target=self.load_poster_thread, args=(titre,), daemon=True).start()

    def load_poster_thread(self, titre: str) -> None:
        """Méthode exécutée dans un thread séparé pour ne pas geler l'interface pendant la requête API."""
        if not self.settings.get("download_images", True):
            self.root.after(0, self.reset_poster)
            return
            
        new_poster = fetch_api_image(titre, (225, 320))
        
        if self.current_fetch_title == titre:
            if new_poster:
                self.root.after(0, self.update_poster, new_poster)
            else:
                self.root.after(0, self.reset_poster)

    def update_poster(self, photo_image: ImageTk.PhotoImage) -> None:
        """Met à jour l'image de couverture dans le thread principal (Tkinter)."""
        self.poster_img = photo_image
        self.poster_label.config(image=self.poster_img)

    def reset_poster(self) -> None:
        """Remet l'image de couverture à une zone vide (placeholder) de la bonne couleur."""
        placeholder = Image.new("RGBA", (225, 320), self.colors["bg_dark"])
        self.poster_img = ImageTk.PhotoImage(placeholder)
        if hasattr(self, 'poster_label'):
            self.poster_label.config(image=self.poster_img)

    def sort_column(self, col: str, reverse: bool) -> None:
        """Trie visuellement le Treeview selon la colonne sélectionnée (numérique, chronologique ou alphabétique)."""
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        
        if col in ("nb_vu", "note"):
            def sort_key(x: Any) -> float:
                try: 
                    return float(x[0])
                except ValueError: 
                    return -1.0
            items.sort(key=sort_key, reverse=reverse)
            
        elif col in ("premiere_fois", "derniere_verif"):
            from datetime import datetime
            def sort_key(x: Any) -> datetime:
                valeur_texte = str(x[0]).lower().replace("avant ", "").replace("avant", "").strip()
                try:
                    return datetime.strptime(valeur_texte, "%d/%m/%Y")
                except ValueError:
                    return datetime.min
            items.sort(key=sort_key, reverse=reverse)
            
        else:
            items.sort(key=lambda x: str(x[0]).lower(), reverse=reverse)
            
        for index, (_, k) in enumerate(items):
            self.tree.move(k, "", index)
            
        for c, text in self.tree_headers.items():
            if c == col:
                arrow = " ▼" if reverse else " ▲"
                self.tree.heading(c, text=text + arrow, 
                                  command=lambda c_=c, rev_=not reverse: self.sort_column(c_, rev_))
            else:
                self.tree.heading(c, text=text, 
                                  command=lambda current=c: self.sort_column(current, False))
                
    def open_settings(self) -> None:
        """Ouvre la fenêtre modale des paramètres de l'application."""
        SettingsWindow(self.root, self)

    def apply_settings(self, settings: Dict[str, Any]) -> None:
        """Applique les nouveaux paramètres (comme les colonnes visibles) à l'interface."""
        self.settings = settings
        visible_cols = settings.get("visible_columns", list(self.tree_headers.keys()))
        self.tree["displaycolumns"] = tuple(visible_cols)
        
        default_widths = {
            "titre": 300, "contenu": 150, "info_suite": 120,
            "note": 80, "premiere_fois": 130, "nb_vu": 80,
            "derniere_verif": 130, "site_url": 120, "nautiljon_url": 120
        }
        for col in visible_cols:
            self.tree.column(col, width=default_widths.get(col, 100))

    def open_add_window(self) -> None:
        """Ouvre la fenêtre permettant l'ajout d'un nouvel anime."""
        from ui.anime_form import AnimeFormWindow
        AnimeFormWindow(self.root, self)
    
    def open_edit_window(self) -> None:
        """Ouvre la fenêtre d'édition pour l'anime actuellement sélectionné."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Attention", "Veuillez sélectionner un anime à modifier.")
            return
            
        titre = self.tree.item(selected_item[0], "values")[0]
        from ui.anime_form import AnimeFormWindow
        AnimeFormWindow(self.root, self, original_title=titre)