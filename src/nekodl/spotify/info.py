def get_title(info):
    """
    Return the titles of all music tracks.
    
    :param info: List of song dictionaries
    :return: List of titles
    """
    return [song['name'] for song in info]


def get_artists(info):
    """
    Return the unique creators of all music
    
    :param info: List of song dictionaries
    :return: List of unique artists
    """
    artists = set()
    for song in info:
        artists.update(song['artists'])
    return list(artists)


def get_genre(info):
    """
    Return unique genres of all tracks
    """
    genres = set()
    for song in info:
        genres.update(song['genres'])
    return list(genres)


def get_disc_number(info):
    """
    Return unique disc numbers in the album
    """
    return list({song['disc_number'] for song in info})


def get_album_name(info):
    """
    Return unique album names
    """
    return list({song['album_name'] for song in info})


def get_album_artist(info):
    """
    Return unique album artists
    """
    return list({song['album_artist'] for song in info})


def get_duration(info):
    """
    Return total duration of all tracks in minutes
    """
    total_seconds = sum(song['duration'] for song in info)
    return total_seconds / 60


def get_year(info):
    """
    Return unique years of all tracks
    """
    return list({song['year'] for song in info})


def get_date(info):
    """
    Return unique release dates of all tracks
    """
    return list({song['date'] for song in info})


def get_track_number(info):
    """
    Return all track numbers
    """
    return [song['track_number'] for song in info]


def get_song_id(info):
    """
    Return all song IDs
    """
    return [song['song_id'] for song in info]


def get_explicit(info):
    """
    Return explicit status of all tracks
    """
    return [song['explicit'] for song in info]


def get_publisher(info):
    """
    Return unique publishers
    """
    return list({song['publisher'] for song in info})


def get_url(info):
    """
    Return URLs of all tracks
    """
    return [song['url'] for song in info]


def get_isrc(info):
    """
    Return unique ISRC codes
    """
    return list({song['isrc'] for song in info})


def get_cover_url(info):
    """
    Return cover URLs of all tracks
    """
    return [song['cover_url'] for song in info]


def get_copyright_text(info):
    """
    Return unique copyright texts
    """
    return list({song['copyright_text'] for song in info})


def get_popularity(info):
    """
    Return popularity of all tracks
    """
    return [song['popularity'] for song in info]


def get_album_id(info):
    """
    Return unique album IDs
    """
    return list({song['album_id'] for song in info})


def get_artist_id(info):
    """
    Return unique artist IDs
    """
    return list({song['artist_id'] for song in info})


def get_album_type(info):
    """
    Return unique album types
    """
    return list({song['album_type'] for song in info})
