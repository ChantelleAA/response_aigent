import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

SITE_URL = "https://www.nileedgeinnovations.org"

def extract_sections_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    def collect_text(selector):
        return [el.get_text(strip=True) for el in soup.select(selector) if el.get_text(strip=True)]

    page_data = {
        "title": soup.title.string.strip() if soup.title else "",
        "sections": []
    }

    # Collect structured content
    sections = []
    sections += collect_text("#hero h2, #hero p")
    sections += collect_text(".section-blog .blog_text")
    sections += collect_text("#services .service-item p")
    sections += collect_text(".accordion-header h3")
    sections += collect_text(".accordion-body p")
    sections += collect_text(".testimonial-item span")
    sections += collect_text(".info-item p")
    sections += collect_text("h1, h2, h3, li")
    sections += [img["alt"] for img in soup.find_all("img", alt=True)]

    page_data["sections"] = list(set(sections))
    return page_data

def get_site_content(url):
    print(f"Scraping {url} ...")
    try:
        html = requests.get(url, timeout=10).text
        return extract_sections_from_html(html)
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return {"title": "", "sections": []}

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

    all_structured_data = []
    for page_url in [base_url] + subpages:
        print(f"Scraping {page_url} ...")
        try:
            page_html = requests.get(page_url, timeout=10).text
            soup = BeautifulSoup(page_html, "html.parser")

            def select_text(selector):
                return [el.get_text(strip=True) for el in soup.select(selector)]

            # Group into meaningful sections
            page_data = {
                "source_url": page_url,
                "sections": {
                    "hero": select_text("#hero h2, #hero p"),
                    "about": select_text(".section-blog .blog_text"),
                    "services": select_text("#services .service-item p, #services .service-item h3"),
                    "testimonials": select_text(".testimonial-item span"),
                    "faq": select_text(".accordion-body p"),
                    "contact": select_text(".info-item p, .info-item h3"),
                    "team": select_text(".member-info h4, .member-info span"),
                    "blog": select_text(".blog_text, .blog_title")
                }
            }
            all_structured_data.append(page_data)

        except Exception as e:
            print(f"Failed to scrape {page_url}: {e}")

    return all_structured_data, subpages

