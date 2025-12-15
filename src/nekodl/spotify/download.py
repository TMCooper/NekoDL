import os, subprocess

def downloader(URL, *, PATH=None):
    """Téléchargement Spotify"""
    try:
        if not PATH:
            AP = os.getcwd()
            PATH = os.path.join(AP, "Spotify_Download")
    
        subprocess.run(["spotdl", URL, "--output", PATH], capture_output=True, text=True)

    except KeyboardInterrupt:
        return None