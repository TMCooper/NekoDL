import re
import cloudscraper
from bs4 import BeautifulSoup

def get_seasons(anime_url):
    """
    Scrapes the anime page and returns a list of available seasons and their corresponding URLs.
    """
    scraper = cloudscraper.create_scraper()
    reponse = scraper.get(anime_url)
    if reponse.status_code != 200:
        return []

    soup = BeautifulSoup(reponse.text, 'html.parser')
    scripts = soup.find_all("script")
    pattern = re.compile(r'panneau(?:Anime|Film|Scan|Visual)\s*\(\s*(["\'])(.*?)\1\s*,\s*(["\'])(.*?)\3\s*\)')

    seasons = []
    for script in scripts:
        if script.text:
            text = re.sub(r'/\*.*?\*/', '', script.text, flags=re.DOTALL)
            matches = pattern.findall(text)
            for quote1, name, quote2, link in matches:
                if name.lower() != "nom" and link.lower() != "url":
                    season_url = anime_url.rstrip("/") + "/" + link.lstrip("/")
                    seasons.append({
                        "season": name,
                        "url": season_url
                    })

    return seasons

def get_episode_links(season_url):
    """
    Scrapes the JavaScript file of the season and returns a dictionary of players
    (e.g., 'eps1', 'eps2') mapping to a list of episode URLs.
    """
    scraper = cloudscraper.create_scraper()
    reponse = scraper.get(season_url)
    if reponse.status_code != 200:
        return {}

    soup = BeautifulSoup(reponse.text, 'html.parser')
    script_tag = soup.find("script", src=lambda s: s and "episodes.js" in s)
    
    if not script_tag:
        return {}

    js_str = str(script_tag)
    try:
        js_link = js_str.split('src="')[1].split('"')[0]
    except IndexError:
        return {}

    jsfile = f"{season_url.rstrip('/')}/{js_link.lstrip('/')}"
    js_reponse = scraper.get(jsfile)
    if js_reponse.status_code != 200:
        return {}

    js_text = js_reponse.text
    matches = re.findall(r"var\s+(eps\d+)\s*=\s*\[(.*?)\];", js_text, re.DOTALL)

    all_eps = {
        name: re.findall(r"'(https?://[^']+)'", content)
        for name, content in matches
    }

    return all_eps
