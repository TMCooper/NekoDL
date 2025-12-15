import re

def clean_spotify_url(url: str) -> str:
    url = url.strip()

    # spotify:track:ID
    m = re.match(r"spotify:(track|playlist|album):([A-Za-z0-9]+)", url)
    if m:
        kind, sid = m.groups()
        return f"https://open.spotify.com/{kind}/{sid}"

    # https://open.spotify.com/.../type/ID?... 
    m = re.search(
        r"open\.spotify\.com/(?:intl-[a-z]{2}/)?(track|playlist|album)/([A-Za-z0-9]+)",
        url
    )
    if m:
        kind, sid = m.groups()
        return f"https://open.spotify.com/{kind}/{sid}"

    raise ValueError(f"URL Spotify invalide: {url}")
