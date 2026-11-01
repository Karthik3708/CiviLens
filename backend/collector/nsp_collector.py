
import requests
import json
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag

NSP_URL = "https://scholarships.gov.in/All-Scholarships"

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = DOWNLOAD_DIR / "nsp_documents.json"

ALLOWED_HOST = "scholarships.gov.in"

EXCLUDED_KEYWORDS = [
    "usermanual",
    "nodalofficers",
    "grievance",
    "not_available",
    "dno_sno"
]


def collect_nsp_links():

    headers = {
        "User-Agent": "CiviLens-ResearchBot/1.0"
    }

    try:
        response = requests.get(
            NSP_URL,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

    except requests.RequestException as error:
        print("Connection error:", error)
        return []

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    documents = {}

    for anchor in soup.find_all("a", href=True):

        title = anchor.get_text(" ", strip=True)

        url = urljoin(NSP_URL, anchor["href"])
        url, _ = urldefrag(url)

        parsed = urlparse(url)

        # Only accept official NSP PDF documents
        if parsed.hostname != ALLOWED_HOST:
            continue

        if not parsed.path.lower().endswith(".pdf"):
            continue

        url_lower = url.lower()

        if any(
            word in url_lower
            for word in EXCLUDED_KEYWORDS
        ):
            continue

        # Accept scheme guidelines and scheme FAQs
        if not (
            "/public/schemeguidelines/" in url_lower
            or "/public/faq/" in url_lower
        ):
            continue

        if not title:
            title = "Scholarship Document"

        if url not in documents:

            if "/public/faq/" in url_lower:
                category = "FAQ"
            else:
                category = "Guideline"

            documents[url] = {
                "title": title,
                "url": url,
                "source": "National Scholarship Portal",
                "category": category
            }

    return list(documents.values())


if __name__ == "__main__":

    results = collect_nsp_links()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            results,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n========== CIVILENS ==========")
    print("FILTERED NSP COLLECTION")
    print("=============================")

    print("Total relevant documents:", len(results))

    print(
        "Guidelines:",
        sum(d["category"] == "Guideline" for d in results)
    )

    print(
        "FAQs:",
        sum(d["category"] == "FAQ" for d in results)
    )

    print("\nSaved to:", OUTPUT_FILE)

    for index, document in enumerate(results, 1):
        print(f"\n{index}. {document['title']}")
        print("Category:", document["category"])
        print("URL:", document["url"])
