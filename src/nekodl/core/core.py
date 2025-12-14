import os, yt_dlp
from .utils import YuiCleanLogger, Kit

def _download_generic(url, folder_name, *, quality="best", PATH=None):
    """Fonction centrale pour tout téléchargement."""
    try : 
        if not PATH:
            AP = os.getcwd()
            PATH = os.path.join(AP, f"{folder_name}")

        cleanLogger = YuiCleanLogger()

        ydl_opts = {
            'outtmpl': os.path.join(PATH, '%(title)s.%(ext)s'),         # Ouput directement envoie avec le titre de la video dans le bon dossier
            'format': quality,                                          # Format flexible
            'ignoreerrors': True,                                       # Ignorer certaines erreurs non critiques
            "logger": cleanLogger,                                      # Logger spécifique pour retirer tous se qui est de trop
            "progress_hooks": [cleanLogger.hook],                       # Pour un affichage personnalisé de la progression
            'verbose': False                                            # Afficher moins d'informationsyt-dl
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.download([url])
        
    except KeyboardInterrupt:
        return None
    
    
class Info:
    def _fetch_info(*, url):
        with yt_dlp.YoutubeDL(Kit.OPTS) as yt:
            return yt.extract_info(url, download=False)
        
    def _get_title(info):
        """
        Returns the title of the YouTube video.

        Can be None if the information is missing or extraction failed.
        """
        return info.get("title")

    def _get_creator(info):
        """
        Returns the name of the creator or uploader of the video.

        yt-dlp may provide this information via different fields depending on the video.
        """
        return info.get("creator")

    def _get_like_count(info):
        """
        Returns the number of likes for the video.

        Can be None if the data is unavailable.
        """
        return info.get("like_count")

    def _get_age_limit(info):
        """
        Returns the age restriction for the video (e.g., 18).

        None if no restriction is set.
        """
        return info.get("age_limit")

    def _get_availability(info):
        """
        Returns the availability status of the video.

        Examples: "public", "private", "unlisted", etc.
        """
        return info.get("availability")

    def _get_available_at(info):
        """
        Returns the Unix timestamp (in seconds) when the video becomes available.

        None if not defined.
        """
        return info.get("available_at")

    def _get_comment_count(info):
        """
        Returns the number of comments on the video.

        Can be None if comments are disabled or unavailable.
        """
        return info.get("comment_count")

    def _get_duration(info):
        """
        Returns the duration of the video in seconds.

        Can be None if the duration is unknown.
        """
        return info.get("duration")

    def _get_formats(info):
        """
        Returns the list of available formats for the video.

        Each format is a dictionary provided by yt-dlp.
        """
        return info.get("formats")

    def _get_id(info):
        """
        Returns the unique ID of the YouTube video.
        """
        return info.get("id")

    def _get_tags(info):
        """
        Returns the tags associated with the video.

        Can be an empty list or None if no tags are defined.
        """
        return info.get("tags")

    def _get_thumbnail(info):
        """
        Returns the URL of the main thumbnail of the video.
        """
        return info.get("thumbnail")

    def _get_timestamp(info):
        """
        Returns the Unix timestamp of the video publication.

        None if unknown.
        """
        return info.get("timestamp")

    def _get_url(info):
        """
        Returns the URL of the YouTube video.
        """
        return info.get("url")