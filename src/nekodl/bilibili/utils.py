import os

class Utils:
    def get_ydl_opts(output_path=None, quality="bv*+ba/b", cookies_path=None, logger=None):
        opts = {
            "format": quality,
            "ignoreerrors": True,
            "quiet": True,
            "merge_output_format": "mp4",
        }

        if output_path:
            opts["outtmpl"] = os.path.join(output_path, "%(title)s.%(ext)s")

        # Cookies dans le cas ou l'utilisateur serait un premium pour télécharger la video en 1080p par exemple
        if cookies_path:
            opts["cookies"] = cookies_path

        if logger:
            opts["logger"] = logger
            opts["progress_hooks"] = [logger.hook]

        return opts
