import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scraper import get_all_site_content, SITE_URL
from app.retrieval import update_vector_store
from app.config import VECTOR_COLLECTION

# Compute base directory and data path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

if __name__ == "__main__":
    print("Refreshing knowledge base...")
    content, pages = get_all_site_content(SITE_URL)
    update_vector_store(VECTOR_COLLECTION, content)
    print("Knowledge base refreshed.")
    print(f"{len(content)} website content items embedded and stored.")

    with open(os.path.join(DATA_DIR, "website_data.json"), "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    with open(os.path.join(DATA_DIR, "scraped_pages.json"), "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=2)
    print("Saved data to data/website_data.json and scraped_pages.json")