from ..core.core import YuiCleanLogger
import os, yt_dlp, cloudscraper

def download(url, folder_name="AnimeSama_Download", *, quality="best", PATH=None):
    # PATH = os.path.join(AP, "Anime") # Instorer un system pour reconnaitre l'animer télécharger de manière a pouvoir faire le path sous cette forme : USER_PATH / Anime / Anime_Name / vf / vostfr / episodes
    """Fonction centrale pour tout téléchargement."""
    custom_headers = {
        'Referer': url, # Le Referer est la page d'embed
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
        'Accept': '*/*'
    }
    try : 
        if not PATH:
            AP = os.getcwd()
            PATH = os.path.join(AP, f"{folder_name}")

        scraper = cloudscraper.create_scraper()  # équivaut à un navigateur
        reponse = scraper.get(url, headers=custom_headers)
        if reponse.status_code == 200:
            source = reponse.text
            file = source.split("episodes.js?")[1].split("'")[0] # Isole le filever=ID affin de recontruire le lien après
            server_file_url = url + "episodes.js?" + file # Reconstitue le lien vers le fichier contenant tous les lien

            content_file = scraper.get(server_file_url)
            print(content_file.text) 
            # TODO continuer la mise en place de la fonction en fesant un system qui analyse ou est chaque épisode de manière a que si un ne fonctionne pas on le remplace par 
            # uniquement les lien avec les id corespondant a celui qui manque dans le cas ou il remplisse les condition que nous avons déjà fixé au préalable
        
        else:
            return f"Error durring the request status code : {reponse.status_code}"

        cleanLogger = YuiCleanLogger()

        ydl_opts = {
            'outtmpl': os.path.join(PATH, '%(title)s.%(ext)s'),         # Ouput directement envoie avec le titre de la video dans le bon dossier
            'format': quality,                                          # Format flexible
            'ignoreerrors': True,                                       # Ignorer certaines erreurs non critiques
            "logger": cleanLogger,                                      # Logger spécifique pour retirer tous se qui est de trop
            "progress_hooks": [cleanLogger.hook],                       # Pour un affichage personnalisé de la progression
            'verbose': False,                                           # Afficher moins d'informationsyt-dl
            'http_headers': {
                'Referer': url, # Toujours envoyer le Referer !
                'User-Agent': custom_headers['User-Agent'],
                }
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.download([url])
        
    except KeyboardInterrupt:
        return None

