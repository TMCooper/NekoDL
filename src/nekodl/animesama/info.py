from ..core.core import Info

def get_title(info):
    """
    Returns the title of the YouTube video.

    Can be None if the information is missing or extraction failed.
    """
    return Info._get_title(info)

def get_creator(info):
    """
    Returns the name of the creator or uploader of the video.

    yt-dlp may provide this information via different fields depending on the video.
    """
    return Info._get_creator(info)

def get_like_count(info):
    """
    Returns the number of likes for the video.

    Can be None if the data is unavailable.
    """
    return Info._get_like_count(info)

def get_age_limit(info):
    """
    Returns the age restriction for the video (e.g., 18).

    None if no restriction is set.
    """
    return Info._get_age_limit(info)

def get_availability(info):
    """
    Returns the availability status of the video.

    Examples: "public", "private", "unlisted", etc.
    """
    return Info._get_availability(info)

def get_available_at(info):
    """
    Returns the Unix timestamp (in seconds) when the video becomes available.

    None if not defined.
    """
    return Info._get_available_at(info)

def get_comment_count(info):
    """
    Returns the number of comments on the video.

    Can be None if comments are disabled or unavailable.
    """
    return Info._get_comment_count(info)

def get_duration(info):
    """
    Returns the duration of the video in seconds.

    Can be None if the duration is unknown.
    """
    return Info._get_duration(info)

def get_formats(info):
    """
    Returns the list of available formats for the video.

    Each format is a dictionary provided by yt-dlp.
    """
    return Info._get_formats(info)

def get_id(info):
    """
    Returns the unique ID of the YouTube video.
    """
    return Info._get_id(info)

def get_tags(info):
    """
    Returns the tags associated with the video.

    Can be an empty list or None if no tags are defined.
    """
    return Info._get_tags(info)

def get_thumbnail(info):
    """
    Returns the URL of the main thumbnail of the video.
    """
    return Info._get_thumbnail(info)

def get_timestamp(info):
    """
    Returns the Unix timestamp of the video publication.

    None if unknown.
    """
    return Info._get_timestamp(info)

def get_url(info):
    """
    Returns the URL of the AnimeSama video.
    """
    return Info._get_url(info)

def get_anime_metadata(anime_url):
    """
    Scrapes the Anime-Sama anime page to extract basic metadata.
    Returns a dictionary with 'title', 'synopsis', and 'cover_url'.
    """
    import cloudscraper
    from bs4 import BeautifulSoup
    
    scraper = cloudscraper.create_scraper()
    response = scraper.get(anime_url)
    if response.status_code != 200:
        return {"title": None, "synopsis": None, "cover_url": None}

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Title extraction (from the main heading or title tag)
    title_tag = soup.find('h1') or soup.find('h2')
    title = title_tag.get_text(strip=True) if title_tag else None
    if not title and soup.title:
        title = soup.title.get_text(strip=True).replace(" - Anime-Sama", "")

    # Synopsis extraction (Anime-Sama usually uses paragraphs or specific divs)
    synopsis = None
    synopsis_elem = soup.find(lambda tag: tag.name in ['p', 'div'] and tag.get('class') and any('synopsis' in c.lower() for c in tag.get('class')))
    if synopsis_elem:
        synopsis = synopsis_elem.get_text(strip=True)
    
    # Cover image extraction
    cover_url = None
    cover_elem = soup.find('img', class_=lambda c: c and 'cover' in c.lower())
    if not cover_elem:
        # Fallback to the largest or first prominent image
        img_tags = soup.find_all('img')
        for img in img_tags:
            src = img.get('src', '')
            if 'cover' in src.lower() or 'affiche' in src.lower():
                cover_url = src
                break
    else:
        cover_url = cover_elem.get('src')
        
    if cover_url and not cover_url.startswith('http'):
        from urllib.parse import urlparse
        parsed = urlparse(anime_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        cover_url = base_url.rstrip("/") + "/" + cover_url.lstrip("/")

    return {
        "title": title,
        "synopsis": synopsis,
        "cover_url": cover_url
    }