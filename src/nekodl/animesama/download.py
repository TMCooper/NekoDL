from ..core.core import _download_generic

def download(url, *, PATH=None):
    # PATH = os.path.join(AP, "Anime") # Instorer un system pour reconnaitre l'animer télécharger de manière a pouvoir faire le path sous cette forme : USER_PATH / Anime / Anime_Name / vf / vostfr / episodes
    return _download_generic(url, folder_name="AnimeSama_Download", quality="best", PATH=PATH)