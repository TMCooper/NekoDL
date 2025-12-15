def get_title(info):
    """
    Return the titles of all music tracks.
    
    :param info: List of song dictionaries
    :return: List of titles
    """
    title = []
    for song in info:
        title.append({song['name']})
    return title

def get_creator(info):
    """
    Return the unique creators of all music
    
    :param info: List of song dictionaries
    :return: List of unique artists
    """
    artists = set()
    for song in info:
        artists.update(song['artists'])
    return list(artists)
