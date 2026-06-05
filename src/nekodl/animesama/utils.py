import re
import cloudscraper
import requests

def get_base_url(status_url="https://anime-sama.pw"):
    """
    Dynamically finds and returns the active base URL for AnimeSama
    by parsing their status page (default: anime-sama.pw).
    """
    scraper = cloudscraper.create_scraper()
    try:
        reponse = scraper.get(status_url)
        html = reponse.text

        # Extract domains list from JavaScript
        pattern = r"const domains = \[(.*?)\];"
        match = re.search(pattern, html, re.DOTALL)

        if match:
            domains_js = match.group(1)
            
            # Extract each domain with regex
            domain_pattern = r"name:\s*'([^']+)'"
            domains = re.findall(domain_pattern, domains_js)
            
            for domain in domains:
                try:
                    url = f"https://{domain}"
                    # First request WITHOUT following redirects
                    response_no_redirect = scraper.get(url, timeout=5, allow_redirects=False)
                    
                    # If status code is 200, it's the main active domain
                    if response_no_redirect.status_code == 200:
                        return url
                except requests.exceptions.RequestException:
                    pass
    except requests.exceptions.RequestException:
        pass
    
    # Fallback to a known domain if resolution fails
    return "https://anime-sama.me"
