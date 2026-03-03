"""
Point d'entrée principal de l'application AnimeSoul.
Il initialise la boucle Tkinter et lance la fenêtre principale.
"""
import tkinter as tk
from ui.main_window import AnimeListApp
from utils.system_utils import set_windows_dpi_awareness

if __name__ == "__main__":
    # Ajuste le rendu sous Windows pour éviter que les polices soient floues
    set_windows_dpi_awareness()
    
    root = tk.Tk()
    app = AnimeListApp(root)
    root.mainloop()