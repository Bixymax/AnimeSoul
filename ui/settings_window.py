import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Any

from config import THEMES
from core.settings_manager import SettingsManager
from utils.system_utils import apply_dark_title_bar

class SettingsWindow(tk.Toplevel):
    """
    Fenêtre modale permettant à l'utilisateur de configurer les paramètres 
    de l'application (thème, téléchargement API, colonnes visibles, export CSV).
    """

    def __init__(self, parent: tk.Misc, app_instance: Any) -> None:
        """
        Initialise la fenêtre de paramètres.
        
        :param parent: Le widget parent (généralement la fenêtre principale).
        :param app_instance: La référence à l'instance principale de l'application (AnimeListApp).
        """
        super().__init__(parent)
        self.app = app_instance
        
        self.current_settings = SettingsManager.load()

        self.current_theme_name = self.current_settings.get("theme", "dark")
        self.colors = THEMES.get(self.current_theme_name, THEMES["dark"])
        
        self.withdraw()
        self.title("Paramètres")
        self.resizable(False, False)
        self.configure(bg=self.colors["bg_main"])
        
        self.transient(parent)
        self.grab_set()
        self.focus_set()

        parent.update_idletasks()
        width, height = 450, 625
        
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        
        pos_x = parent_x + (parent_w // 2) - (width // 2)
        pos_y = parent_y + (parent_h // 2) - (height // 2)
        
        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

        self.all_columns = {
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
        
        self.create_widgets()
        
        self.deiconify()
        self.after(10, lambda: apply_dark_title_bar(self, dark_mode=(self.current_theme_name == "dark")))

    def reset_to_defaults(self) -> None:
        """Réinitialise les sélections de la fenêtre aux paramètres par défaut."""
        self.theme_var.set("dark")
        self.dl_img_var.set(True)
        self.update_toggle_visual()
        
        default_cols = SettingsManager.DEFAULT_SETTINGS["visible_columns"]
        for col_id, var in self.col_vars.items():
            var.set(col_id in default_cols)

    def save_settings(self) -> None:
        """Récupère les données du formulaire, sauvegarde via le manager, et met à jour l'app principale."""
        self.current_settings["theme"] = self.theme_var.get()
        self.current_settings["download_images"] = self.dl_img_var.get()
        
        selected_cols = [col for col, var in self.col_vars.items() if var.get()]
        if not selected_cols:
            messagebox.showwarning("Attention", "Vous devez sélectionner au moins une colonne.", parent=self)
            return
            
        self.current_settings["visible_columns"] = selected_cols

        SettingsManager.save(self.current_settings)
        self.app.apply_settings(self.current_settings)
        self.destroy()

    def export_csv(self) -> None:
        """Ouvre une boîte de dialogue pour sauvegarder toute la base de données dans un fichier CSV."""
        filepath = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv")],
            title="Exporter la base de données",
            initialfile="animes_export.csv"
        )
        if not filepath:
            return 
            
        try:
            self.app.db.export_to_csv(filepath)
            messagebox.showinfo("Succès", "L'exportation CSV a réussi !", parent=self)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export :\n{e}", parent=self)

    def update_toggle_visual(self) -> None:
        """Met à jour l'apparence visuelle du bouton de bascule de téléchargement API."""
        if self.dl_img_var.get():
            self.toggle_btn.config(text="ON", bg=self.colors["primary"], fg=self.colors["bg_main"])
        else:
            self.toggle_btn.config(text="OFF", bg=self.colors["danger"], fg=self.colors["bg_main"])

    def toggle_api(self) -> None:
        """Inverse l'état du téléchargement d'images via l'API lors du clic sur le bouton."""
        self.dl_img_var.set(not self.dl_img_var.get())
        self.update_toggle_visual()

    def create_widgets(self) -> None:
        """Construit et place tous les éléments d'interface utilisateur de la fenêtre."""
        bottom_frame = tk.Frame(self, bg=self.colors["bg_main"], pady=15)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        tk.Button(bottom_frame, text="Par défaut", command=self.reset_to_defaults, width=12, 
                  bg=self.colors["secondary"], fg=self.colors["text"], relief="flat", bd=0, cursor="hand2", pady=5).pack(side=tk.LEFT, padx=20)
        
        tk.Button(bottom_frame, text="OK", command=self.save_settings, width=12, 
                  bg=self.colors["primary"], fg=self.colors["bg_main"], font=("Segoe UI", 10, "bold"), relief="flat", bd=0, cursor="hand2", pady=5).pack(side=tk.RIGHT, padx=(0, 20))
        
        tk.Button(bottom_frame, text="Annuler", command=self.destroy, width=12, 
                  bg=self.colors["secondary"], fg=self.colors["text"], relief="flat", bd=0, cursor="hand2", pady=5).pack(side=tk.RIGHT, padx=10)

        main_frame = tk.Frame(self, bg=self.colors["bg_main"], padx=25, pady=25)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        title_font = ("Segoe UI", 12, "bold")
        text_color = self.colors["text"]
        
        widget_style = {
            "bg": self.colors["bg_main"], 
            "fg": text_color, 
            "activebackground": self.colors["bg_main"], 
            "activeforeground": self.colors["primary"],
            "selectcolor": self.colors["secondary"], 
            "highlightthickness": 0,
            "font": ("Segoe UI", 10)
        }

        tk.Label(main_frame, text="🎨 Apparence (Nécessite un redém.)", font=title_font, bg=self.colors["bg_main"], fg=self.colors["primary"]).pack(anchor="w", pady=(0, 5))
        self.theme_var = tk.StringVar(value=self.current_theme_name)
        tk.Radiobutton(main_frame, text="Thème Clair", variable=self.theme_var, value="light", **widget_style).pack(anchor="w", pady=2)
        tk.Radiobutton(main_frame, text="Thème Sombre", variable=self.theme_var, value="dark", **widget_style).pack(anchor="w", pady=2)

        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=15)

        tk.Label(main_frame, text="🌐 Réseau", font=title_font, bg=self.colors["bg_main"], fg=self.colors["primary"]).pack(anchor="w", pady=(0, 5))
        api_frame = tk.Frame(main_frame, bg=self.colors["bg_main"])
        api_frame.pack(anchor="w", fill="x")
        
        tk.Label(api_frame, text="Télécharger les affiches via l'API : ", bg=self.colors["bg_main"], fg=text_color, font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.dl_img_var = tk.BooleanVar(value=self.current_settings.get("download_images", True))
        
        self.toggle_btn = tk.Button(api_frame, font=("Segoe UI", 9, "bold"), width=6, relief="flat", bd=0, cursor="hand2", command=self.toggle_api)
        self.toggle_btn.pack(side=tk.LEFT, padx=10)
        self.update_toggle_visual()

        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=15)

        tk.Label(main_frame, text="📊 Colonnes affichées", font=title_font, bg=self.colors["bg_main"], fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
        self.col_vars = {}
        cols_frame = tk.Frame(main_frame, bg=self.colors["bg_main"])
        cols_frame.pack(anchor="w", fill="x")
        
        row_idx, col_idx = 0, 0
        visible_cols = self.current_settings.get("visible_columns", [])
        for col_id, col_name in self.all_columns.items():
            var = tk.BooleanVar(value=(col_id in visible_cols))
            self.col_vars[col_id] = var
            
            cb = tk.Checkbutton(cols_frame, text=col_name, variable=var, **widget_style)
            cb.grid(row=row_idx, column=col_idx, sticky="w", padx=(0, 20), pady=4)
            
            col_idx += 1
            if col_idx > 1:
                col_idx = 0
                row_idx += 1

        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=15)

        tk.Label(main_frame, text="💾 Données", font=title_font, bg=self.colors["bg_main"], fg=self.colors["primary"]).pack(anchor="w", pady=(0, 5))
        tk.Button(main_frame, text="Exporter la base en CSV", command=self.export_csv, width=25, 
                  bg=self.colors["secondary"], fg=self.colors["text"], relief="flat", bd=0, cursor="hand2", pady=6, font=("Segoe UI", 10)).pack(anchor="w", pady=5)