import os
import yt_dlp
from ..core.utils import YuiCleanLogger
from .utils import Utils

def download(url, *, quality="bv*+ba/b", PATH=None, cookies_path=None):
    """Téléchargement Bilibili"""

    try:
        if not PATH:
            AP = os.getcwd()
            PATH = os.path.join(AP, "Bilibili_Download")

        os.makedirs(PATH, exist_ok=True)

        cleanLogger = YuiCleanLogger()

        # ydl_opts = {
        #     "outtmpl": os.path.join(PATH, "%(title)s.%(ext)s"),             # Dossier et nom fichier            
        #     "format": quality,                                              # bv* = meilleure vidéo / ba = meilleur audio
        #     "merge_output_format": "mp4",                                   # Passe la video en mp4 automatiquement
        #     "ignoreerrors": True,                                           # Evite les erreur non critique pour continuer malgré tous
        #     "quiet": True,                                                  # Evite la saturation du terminal
        #     "verbose": False,                                               # Evite les log inutile
        #     "logger": cleanLogger,                                          # Logger sépcifique
        #     "progress_hooks": [cleanLogger.hook],                           # Progresse bar spécifique
        # }

        ydl_opts = Utils.get_ydl_opts(
            output_path=PATH,
            quality=quality,
            cookies_path=cookies_path,
            logger=cleanLogger
        )


        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.download([url])

    except KeyboardInterrupt:
        return None
