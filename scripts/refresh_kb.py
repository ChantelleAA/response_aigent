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

def merge_section_lines(section_data, min_chars=250):
    merged = []
    for section, lines in section_data.items():
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
    page_data, subpages = get_all_site_content(SITE_URL)

    structured_pages = []
    flattened_sections = []

    for page in page_data:
        sections = merge_section_lines(page.get("sections", {}))
        structured_pages.append({
            "url": page.get("source_url", ""),
            "title": page.get("title", ""),
            "sections": sections
        })
        flattened_sections.extend(sections)

    update_vector_store(VECTOR_COLLECTION, flattened_sections)

    with open(os.path.join(DATA_DIR, "website_data.json"), "w", encoding="utf-8") as f:
        json.dump(structured_pages, f, indent=2, ensure_ascii=False)

    print(f"Knowledge base refreshed. {len(flattened_sections)} sections embedded.")

    query = "Where is NileEdge located?"
    result = query_vector_store(query, VECTOR_COLLECTION)
    print(result)
