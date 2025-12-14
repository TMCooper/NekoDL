import yt_dlp
from .utils import Utils

def fetch_info(*, url):
    with yt_dlp.YoutubeDL(Utils.get_ydl_opts()) as yt:
        return yt.extract_info(url, download=False)