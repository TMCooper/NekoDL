import shutil, sys

class YuiCleanLogger:
    def __init__(self):
        self.path_printed = False

    def debug(self, msg):
        # print(msg) # A décommentez pour le débug
        pass # Ignore les messages de type '[info]', '[generic]', etc.

    def warning(self, msg):
        # print(msg) # A  décommentez pour voir les avertissements
        pass # Ignore les avertissements

    def error(self, msg):
        print(msg)

    def hook(self, d):
        if d['status'] == 'downloading':
            if not self.path_printed:
                print(f"Destination: {d['filename']}")
                self.path_printed = True

            # La ligne de progression qui se met à jour
            progress_line = (
                f"[download] {d['_percent_str']} of {d.get('total_bytes_str', 'N/A')}"
                f" at {d['_speed_str']} ETA {d['_eta_str']}"
            )
            
            try:
                # Récupère la largeur actuelle du terminal
                terminal_width = shutil.get_terminal_size().columns
            except OSError:
                 # Largeur par défaut pour éviter les crashes    
                terminal_width = 80
            
            line_to_write = f"\r{progress_line:<{terminal_width - 1}}"
            sys.stdout.write(line_to_write) 
            sys.stdout.flush()

        if d['status'] == 'finished':
            # print(self.languages[self.langue]["ytDlpFinish"])
            # Réinitialise la variable pour le prochain fichier à télécharger
            self.path_printed = False

class Kit:
    cleanLogger = YuiCleanLogger()

    # OPTS utiliser uniquement pour le fetch des info youtube et tiktok
    OPTS = {
        'format': "best",                                               # Format plus flexible
        'ignoreerrors': True,                                           # Ignorer certaines erreurs non critiques
        "logger": cleanLogger,                                          # Logger spécifique pour retirer tous se qui est de trop
        "progress_hooks": [cleanLogger.hook],                           # Pour un affichage personnalisé de la progression
        'verbose': False                                                # Afficher plus d'informations
    }