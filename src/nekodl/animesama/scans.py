import os
import re
import sys
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
import cloudscraper
from bs4 import BeautifulSoup

from .utils import get_base_url

print_lock = threading.Lock()

def resolve_manga_title(anime_url_or_title: str) -> str:
    """
    Resolves the exact manga title as used on Anime-Sama's server.
    Accepts either an Anime-Sama URL or a title string.
    """
    scraper = cloudscraper.create_scraper()
    base_url = get_base_url()
    
    if anime_url_or_title.startswith("http://") or anime_url_or_title.startswith("https://"):
        url = anime_url_or_title
        # First, attempt to scrape page for main heading (h1)
        resp = scraper.get(url)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            h1 = soup.find('h1')
            if h1 and h1.get_text(strip=True):
                return h1.get_text(strip=True)
        
        # If h1 not found on page (e.g. /scan/vf/), extract catalog slug from URL
        match = re.search(r'/catalogue/([^/]+)', url)
        if match:
            slug = match.group(1)
            cat_url = f"{base_url}/catalogue/{slug}/"
            cat_resp = scraper.get(cat_url)
            if cat_resp.status_code == 200:
                soup = BeautifulSoup(cat_resp.text, 'html.parser')
                h1 = soup.find('h1')
                if h1 and h1.get_text(strip=True):
                    return h1.get_text(strip=True)
            return slug
        return anime_url_or_title.rstrip('/').split('/')[-1]
    else:
        # Check if the title directly yields scan info from AnimeSama API endpoint
        title = anime_url_or_title.strip()
        chk_url = f"{base_url}/s2/scans/get_nb_chap_et_img.php?oeuvre={quote(title)}"
        resp = scraper.get(chk_url)
        if resp.status_code == 200 and resp.text.startswith('{'):
            return title
        
        # Fallback to catalogue slug lookup
        cat_url = f"{base_url}/catalogue/{title.lower().replace(' ', '-')}/"
        cat_resp = scraper.get(cat_url)
        if cat_resp.status_code == 200:
            soup = BeautifulSoup(cat_resp.text, 'html.parser')
            h1 = soup.find('h1')
            if h1 and h1.get_text(strip=True):
                return h1.get_text(strip=True)

        return title


def get_scan_info(anime_url_or_title: str) -> dict:
    """
    Retrieves scan details for a given manga (title and number of pages per chapter).
    Returns a dictionary containing title, max_chapter, and chapters dict.
    """
    title = resolve_manga_title(anime_url_or_title)
    scraper = cloudscraper.create_scraper()
    base_url = get_base_url()
    
    endpoint = f"{base_url}/s2/scans/get_nb_chap_et_img.php?oeuvre={quote(title)}"
    resp = scraper.get(endpoint)
    
    if resp.status_code != 200:
        raise ValueError(f"Could not fetch scan information for '{anime_url_or_title}' (HTTP {resp.status_code}).")

    try:
        raw_chapters = resp.json()
    except Exception as e:
        raise ValueError(f"Failed to parse scan data for '{title}': {e}")

    # Ensure chapters are sorted numerically
    sorted_chapters = {}
    for k in sorted(raw_chapters.keys(), key=lambda x: int(x) if x.isdigit() else x):
        sorted_chapters[str(k)] = int(raw_chapters[k])

    return {
        "title": title,
        "max_chapter": len(sorted_chapters),
        "chapters": sorted_chapters
    }


def get_scan_links(anime_url_or_title: str, chapter=None) -> dict:
    """
    Generates direct image URLs for specified chapters of a manga scan.
    
    :param anime_url_or_title: Anime-Sama URL or manga title.
    :param chapter: Chapter number (int), list of chapter numbers (list[int]), "all", or None for all.
    :return: Dictionary mapping chapter names (e.g., "Chapitre 1") to lists of image URLs.
    """
    scan_info = get_scan_info(anime_url_or_title)
    title = scan_info["title"]
    chapters_dict = scan_info["chapters"]
    base_url = get_base_url()

    if chapter is None or chapter == "all":
        target_chaps = list(chapters_dict.keys())
    elif isinstance(chapter, int):
        target_chaps = [str(chapter)]
    elif isinstance(chapter, list):
        target_chaps = [str(c) for c in chapter]
    elif isinstance(chapter, str) and chapter.isdigit():
        target_chaps = [chapter]
    else:
        target_chaps = list(chapters_dict.keys())

    encoded_title = quote(title).replace(" ", "%20")

    links_dict = {}
    for chap in target_chaps:
        if chap in chapters_dict:
            nb_pages = chapters_dict[chap]
            chap_key = f"Chapitre {chap}"
            img_urls = []
            for page in range(1, nb_pages + 1):
                url = f"{base_url}/s2/scans/{encoded_title}/{chap}/{page}.jpg"
                img_urls.append(url)
            links_dict[chap_key] = img_urls

    return links_dict


def _download_image(scraper, url: str, path: str, headers: dict = None) -> bool:
    """
    Downloads a single image to the target path.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    try:
        resp = scraper.get(url, headers=headers or {}, stream=True)
        if resp.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        else:
            return False
    except Exception:
        return False


def _prepare_scan_tasks(anime_url_or_title: str, chapter=None, path=None) -> tuple[str, list[dict]]:
    """
    Prepares download tasks (URL and local file path) for requested chapters/pages.
    """
    scan_links = get_scan_links(anime_url_or_title, chapter=chapter)
    scan_info = get_scan_info(anime_url_or_title)
    manga_title = scan_info["title"]

    safe_title = "".join([c for c in manga_title if c.isalnum() or c in (' ', '-', '_')]).strip()
    base_path = path or os.path.join(os.getcwd(), "scans", safe_title)

    tasks = []
    for chap_name, urls in scan_links.items():
        chap_dir = os.path.join(base_path, chap_name)
        total_pages = len(urls)
        # Calculate zero-padding length based on total pages (minimum 3 digits)
        pad_len = max(3, len(str(total_pages)))
        
        for idx, url in enumerate(urls, start=1):
            filename = f"{idx:0{pad_len}d}.jpg"
            img_path = os.path.join(chap_dir, filename)
            tasks.append({
                "url": url,
                "path": img_path,
                "chapter": chap_name,
                "page": idx,
                "total_pages": total_pages
            })

    return manga_title, tasks


def download_scans(anime_url_or_title: str, chapter=None, path=None, headers=None):
    """
    Downloads scans sequentially (one image by one image).
    
    :param anime_url_or_title: Anime-Sama URL or manga title.
    :param chapter: Chapter number (int), list of ints, or None for all.
    :param path: Destination directory. Defaults to [CWD]/scans/[Manga_Name]/
    :param headers: Optional HTTP headers.
    """
    manga_title, tasks = _prepare_scan_tasks(anime_url_or_title, chapter, path)
    if not tasks:
        print(f"No scan tasks found for '{anime_url_or_title}'.")
        return

    print(f"Starting sequential download of {len(tasks)} scan images for '{manga_title}'...")
    scraper = cloudscraper.create_scraper()
    
    total = len(tasks)
    for idx, task in enumerate(tasks, start=1):
        filename = os.path.basename(task["path"])
        sys.stdout.write(f"\r[{idx}/{total}] Downloading {task['chapter']} - Page {task['page']}/{task['total_pages']} ({filename})...")
        sys.stdout.flush()
        
        success = _download_image(scraper, task["url"], task["path"], headers=headers)
        if not success:
            sys.stdout.write(f"\n[Warning] Failed to download {task['url']}\n")

    print(f"\nCompleted download of {total} scan images to '{os.path.dirname(tasks[0]['path'])}'.")


def download_scans_many(anime_url_or_title: str, chapter=None, path=None, headers=None, max_workers: int = 4):
    """
    Downloads scans concurrently using multiple worker threads (several images at a time).
    
    :param anime_url_or_title: Anime-Sama URL or manga title.
    :param chapter: Chapter number (int), list of ints, or None for all.
    :param path: Destination directory. Defaults to [CWD]/scans/[Manga_Name]/
    :param headers: Optional HTTP headers.
    :param max_workers: Number of concurrent threads (default 4).
    """
    manga_title, tasks = _prepare_scan_tasks(anime_url_or_title, chapter, path)
    if not tasks:
        print(f"No scan tasks found for '{anime_url_or_title}'.")
        return

    print(f"Starting concurrent download of {len(tasks)} scan images for '{manga_title}' ({max_workers} threads)...")

    completed_count = 0
    total = len(tasks)
    
    def _worker(task):
        nonlocal completed_count
        thread_scraper = cloudscraper.create_scraper()
        success = _download_image(thread_scraper, task["url"], task["path"], headers=headers)
        
        with print_lock:
            completed_count += 1
            sys.stdout.write(f"\rProgress: [{completed_count}/{total}] images downloaded. Current: {task['chapter']} Page {task['page']}")
            sys.stdout.flush()
            if not success:
                sys.stdout.write(f"\n[Warning] Failed to download {task['url']}\n")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_worker, task) for task in tasks]
        for future in futures:
            future.result()

    print(f"\nCompleted concurrent download of {total} scan images to '{os.path.dirname(tasks[0]['path'])}'.")
