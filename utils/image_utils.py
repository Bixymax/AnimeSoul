import io
import requests
from urllib.parse import urlparse
from typing import Tuple, Optional
from PIL import Image, ImageTk, ImageOps, ImageDraw

# Limite de taille pour les images téléchargées (5 Mo)
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024 

def load_icon(image_path: str, size: Tuple[int, int]) -> ImageTk.PhotoImage:
    """
    Charge et redimensionne une image locale pour l'utiliser comme icône Tkinter.
    
    :param image_path: Le chemin complet vers le fichier image.
    :param size: Un tuple (largeur, hauteur) pour le redimensionnement.
    :return: Un objet ImageTk.PhotoImage prêt à être utilisé dans un widget Tkinter.
    """
    im = Image.open(image_path).convert("RGBA")
    im = im.resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(im)

def fetch_api_image(title: str, size: Tuple[int, int]) -> Optional[ImageTk.PhotoImage]:
    """
    Récupère l'image de couverture d'un anime via l'API publique Jikan (MyAnimeList).
    
    :param title: Le titre exact de l'anime à rechercher.
    :param size: Un tuple (largeur, hauteur) pour redimensionner l'affiche récupérée.
    :return: Un objet ImageTk.PhotoImage si l'image est trouvée et valide, sinon None.
    """
    try:
        api_url = "https://api.jikan.moe/v4/anime"
        response = requests.get(api_url, params={"q": title, "limit": 1}, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if not data.get("data"):
            return None
            
        img_url = data["data"][0]["images"]["jpg"]["large_image_url"]
        
        parsed_url = urlparse(img_url)
        if parsed_url.scheme not in ("http", "https"):
            print(f"Protocole non sécurisé rejeté : {img_url}")
            return None
        
        img_response = requests.get(img_url, timeout=10, stream=True)
        img_response.raise_for_status()
        
        content_length = img_response.headers.get('Content-Length')
        if content_length and int(content_length) > MAX_IMAGE_SIZE_BYTES:
            print("Image trop volumineuse rejetée.")
            return None

        img_data = bytearray()
        for chunk in img_response.iter_content(chunk_size=8192):
            img_data.extend(chunk)
            if len(img_data) > MAX_IMAGE_SIZE_BYTES:
                print("Image dépassant la limite de sécurité.")
                return None
                
        im = Image.open(io.BytesIO(img_data)).convert("RGBA")
        im = im.resize(size, Image.Resampling.LANCZOS)
        
        return ImageTk.PhotoImage(im)
        
    except Exception as e:
        print(f"Erreur pour l'anime '{title}' : {e}")
        return None

def round_image(image_path: str, size: Tuple[int, int], radius: int) -> ImageTk.PhotoImage:
    """
    Charge une image locale, la redimensionne et arrondit ses angles.
    
    :param image_path: Chemin vers le fichier image.
    :param size: Tuple (largeur, hauteur) pour le redimensionnement.
    :param radius: Rayon de l'arrondi en pixels.
    :return: Un objet ImageTk.PhotoImage aux bords arrondis.
    """
    im = Image.open(image_path)
    im = im.resize(size, Image.Resampling.LANCZOS)
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0) + size, radius=radius, fill=255)
    output = ImageOps.fit(im, size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return ImageTk.PhotoImage(output)