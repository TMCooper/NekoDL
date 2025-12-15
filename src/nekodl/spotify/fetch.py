import subprocess
import json
import tempfile
import os
from .utils import clean_spotify_url

def fetch_info(*, URL):
    url = clean_spotify_url(URL)
    
    # Crée un fichier temporaire
    with tempfile.NamedTemporaryFile(mode='w', suffix='.spotdl', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Sauvegarde les métadonnées
        result = subprocess.run(
            ["spotdl", "save", url, "--save-file", tmp_path], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0 and os.path.exists(tmp_path):
            # Lit le fichier JSON
            with open(tmp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data # Renvoie des donnée qui nous interesse
        else:
            print("Erreur:", result.stderr)
            return None
    finally:
        # Nettoie immédiatement le fichier tmp
        if os.path.exists(tmp_path):
            os.remove(tmp_path)