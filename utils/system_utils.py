import ctypes
from typing import Any

def set_windows_dpi_awareness() -> None:
    """
    Active la prise en charge du DPI sous Windows pour éviter que l'interface 
    soit floue sur les écrans haute résolution (ex: écrans 4K).
    Ignore silencieusement l'opération sur les autres systèmes d'exploitation.
    """
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
        windll.shell32.SetCurrentProcessExplicitAppUserModelID('mycompany.animesoul')
    except (ImportError, AttributeError):
        # Normal si l'OS n'est pas Windows, on ignore silencieusement
        pass

def apply_dark_title_bar(window: Any, dark_mode: bool = True) -> None:
    """
    Applique un thème sombre ou clair à la barre de titre native de la fenêtre sous Windows 10/11.
    
    :param window: L'instance de la fenêtre Tkinter (Tk ou Toplevel).
    :param dark_mode: True pour appliquer le thème sombre, False pour le thème clair.
    """
    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    try:
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        value = ctypes.c_int(1 if dark_mode else 0) 
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 
            DWMWA_USE_IMMERSIVE_DARK_MODE, 
            ctypes.byref(value), 
            ctypes.sizeof(value)
        )
    except Exception as e:
        # On ne bloque pas l'application pour un souci cosmétique, mais on l'affiche
        print(f"Info: Impossible d'appliquer le thème de la barre de titre ({e})")