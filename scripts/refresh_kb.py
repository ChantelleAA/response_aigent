import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.scraper import get_all_site_content, SITE_URL
from app.retrieval import update_vector_store, query_vector_store
from app.config import VECTOR_COLLECTION

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)


def merge_content_chunks(lines, min_chars=300):
    merged = []
    buffer = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        buffer += line + " "
        if len(buffer) >= min_chars:
            merged.append(buffer.strip())
            buffer = ""
    if buffer:
        merged.append(buffer.strip())
    return merged

if __name__ == "__main__":
    print("Refreshing knowledge base...")
    content, pages = get_all_site_content(SITE_URL)

    # Merge scraped lines into chunks with meaning
    merged_content = merge_content_chunks(content)
    update_vector_store(VECTOR_COLLECTION, merged_content)

    print("Knowledge base refreshed.")
    print(f"{len(merged_content)} website content items embedded and stored.")

    with open(os.path.join(DATA_DIR, "website_data.json"), "w", encoding="utf-8") as f:
        json.dump(merged_content, f, indent=2, ensure_ascii=False)

    with open(os.path.join(DATA_DIR, "scraped_pages.json"), "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=2)

    print("Saved data to data/website_data.json and scraped_pages.json")


query = "Where is NileEdge located?"
result = query_vector_store(query, "nileedge_content")
print(result)