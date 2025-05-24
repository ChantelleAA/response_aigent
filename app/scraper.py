import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

SITE_URL = "https://www.nileedgeinnovations.org"

def extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    def extract(selector):
        return [el.get_text(strip=True) for el in soup.select(selector)]

    text = []
    text += extract("#hero h2, #hero p")
    text += extract(".section-blog .blog_text")
    text += extract("#services .service-item p")
    text += extract(".accordion-header h3")
    text += extract(".accordion-body p")
    text += extract(".testimonial-item span")
    text += extract(".info-item p")
    text += extract("h1, h2, h3, li")
    text += [img["alt"] for img in soup.find_all("img", alt=True)]
    return list(set(filter(None, text)))


def get_site_content(url):
    print(f"Scraping {url} ...")
    try:
        html = requests.get(url, timeout=10).text
        return extract_text_from_html(html)
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return []


def collect_internal_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("#"):
            continue
        full_url = urljoin(base_url, href)
        if full_url.endswith((".jpg", ".jpeg", ".png", ".svg", ".pdf", ".zip")):
            continue
        if full_url.startswith(base_url):
            links.add(full_url)
    return sorted(list(links))


def get_all_site_content(base_url):
    try:
        html = requests.get(base_url, timeout=10).text
        subpages = collect_internal_links(html, base_url)
        print("Found subpages:", subpages)
    except Exception as e:
        print(f"Failed to get links from {base_url}: {e}")
        subpages = []

    all_text = get_site_content(base_url)
    for page in subpages:
        all_text += get_site_content(page)
    return list(set(all_text)), subpages
