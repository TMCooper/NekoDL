import re
import unicodedata
import cloudscraper
from bs4 import BeautifulSoup
from .utils import get_base_url

try:
    from rapidfuzz import process, fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False


def normalize_title(title: str) -> str:
    """
    Normalizes accents, special quotes, and forbidden characters in title strings.
    """
    if not title:
        return ""

    title = unicodedata.normalize("NFKD", title)
    title = "".join([c for c in title if not unicodedata.combining(c)])

    title = title.replace("“", "\"").replace("”", "\"")
    title = title.replace("‘", "'").replace("’", "'")

    forbidden = r'[\/\\\:\*\?\"\<\>\|]'
    title = re.sub(forbidden, " ", title)

    title = re.sub(r"[^a-zA-Z0-9\-\_\&\.\'\#\s]", " ", title)
    title = re.sub(r"\s+", " ", title).strip()

    return title


def clean_string(text: str) -> str:
    """
    Cleans and normalizes text for string comparisons (lowercase, alphanumeric + spaces).
    """
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fetch_catalog(max_pages: int = None) -> list[dict]:
    """
    Scrapes the Anime-Sama catalog to retrieve title, link, and cover image for available anime.
    
    :param max_pages: Optional maximum number of catalog pages to scrape.
    :return: List of dicts with keys 'title', 'link', and 'cover'.
    """
    base_url = get_base_url()
    scraper = cloudscraper.create_scraper()
    
    first_response = scraper.get(f"{base_url}/catalogue")
    if first_response.status_code != 200:
        return []

    soup_init = BeautifulSoup(first_response.content, 'lxml')
    pagination_links = soup_init.find_all('a', class_=["p-3", "pagination-link", "rounded-md"])

    page_numbers = []
    for link in pagination_links:
        text = link.get_text(strip=True)
        if text.isdigit():
            page_numbers.append(int(text))

    detected_max = max(page_numbers) if page_numbers else 1
    total_pages = min(detected_max, max_pages) if max_pages else detected_max

    catalog = []
    for page in range(1, total_pages + 1):
        resp = scraper.get(f"{base_url}/catalogue/?page={page}")
        if resp.status_code != 200:
            continue

        soup = BeautifulSoup(resp.content, 'lxml')
        titles = soup.find_all('h2', class_="card-title")

        for title_tag in titles:
            card_link = title_tag.find_parent('a')
            if not card_link:
                continue

            titre = title_tag.get_text(strip=True)
            link = card_link.get('href', '')
            if link and not link.startswith('http'):
                link = base_url.rstrip('/') + '/' + link.lstrip('/')

            img_tag = card_link.find('img', class_="card-image")
            img_src = img_tag.get('src', '') if img_tag else ""
            if img_src and not img_src.startswith('http'):
                img_src = base_url.rstrip('/') + '/' + img_src.lstrip('/')

            catalog.append({
                "title": normalize_title(titre),
                "link": link,
                "cover": img_src
            })

    return catalog


def search_anime(query: str, catalog: list[dict] = None, limit: int = 10) -> list[dict]:
    """
    Searches for an anime in the Anime-Sama catalog using fuzzy matching.
    
    :param query: Search query (e.g. "Frieren", "Solo Leveling").
    :param catalog: Optional pre-loaded catalog. If None, scrapes first 5 pages of catalog.
    :param limit: Maximum number of search results to return.
    :return: List of result dicts with 'title', 'link', 'cover', and 'score'.
    """
    cleaned_search = clean_string(query)
    if not cleaned_search:
        return []

    if catalog is None:
        # Load sample/catalog pages for responsive search
        catalog = fetch_catalog(max_pages=5)

    if not catalog:
        return []

    cleaned_to_anime_map = {}
    for item in catalog:
        ct = clean_string(item.get("title", ""))
        if ct and ct not in cleaned_to_anime_map:
            cleaned_to_anime_map[ct] = item

    cleaned_titles = list(cleaned_to_anime_map.keys())

    if HAS_RAPIDFUZZ:
        matches = process.extract(cleaned_search, cleaned_titles, scorer=fuzz.token_set_ratio, limit=limit * 2)
        temp_results = []
        for cleaned_title, score, _ in matches:
            if score < 60:
                continue

            length_ratio = len(cleaned_title) / len(cleaned_search) if len(cleaned_search) > 0 else 0
            specificity_bonus = 0
            if 0.9 <= length_ratio <= 1.1:
                specificity_bonus = 10
            elif length_ratio < 0.5:
                specificity_bonus = -15

            final_score = score + specificity_bonus
            anime_item = cleaned_to_anime_map[cleaned_title]
            temp_results.append({
                "title": anime_item["title"],
                "link": anime_item["link"],
                "cover": anime_item.get("cover", ""),
                "score": final_score
            })

        temp_results.sort(key=lambda x: x["score"], reverse=True)
        
        seen_links = set()
        final_results = []
        for res in temp_results:
            if len(final_results) >= limit:
                break
            if res["link"] not in seen_links:
                final_results.append(res)
                seen_links.add(res["link"])
        return final_results
    else:
        # Fallback simple containment / keyword matching
        results = []
        for ct, item in cleaned_to_anime_map.items():
            if cleaned_search in ct:
                results.append({
                    "title": item["title"],
                    "link": item["link"],
                    "cover": item.get("cover", ""),
                    "score": 100
                })
                if len(results) >= limit:
                    break
        return results
