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
