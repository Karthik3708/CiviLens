
import json
import re
from pathlib import Path
from collections import defaultdict


# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DOWNLOAD_DIR = BASE_DIR / "downloads"
EXTRACTED_DIR = DOWNLOAD_DIR / "extracted"

INPUT_FILE = DOWNLOAD_DIR / "extraction_manifest.json"

OUTPUT_FILE = DOWNLOAD_DIR / "deduplicated_documents.json"
REPORT_FILE = DOWNLOAD_DIR / "deduplication_report.json"


# ==========================================
# 2. CONFIGURATION
# ==========================================

# Near-duplicate similarity threshold
SIMILARITY_THRESHOLD = 0.90

# Minimum document length for near-duplicate checks
MINIMUM_TEXT_LENGTH = 100


# ==========================================
# 3. LOAD EXTRACTION MANIFEST
# ==========================================

def load_documents():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Extraction manifest not found: {INPUT_FILE}"
        )

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        documents = json.load(file)

    if not isinstance(documents, list):
        raise ValueError(
            "Expected a list of documents in extraction_manifest.json"
        )

    return documents


# ==========================================
# 4. GET DOCUMENT SOURCE URLS
# ==========================================

def get_source_urls(document):

    possible_fields = [
        "url",
        "source_url",
        "original_url",
        "document_url",
        "pdf_url",
        "link"
    ]

    urls = []

    for field in possible_fields:

        value = document.get(field)

        if isinstance(value, str) and value.startswith("http"):
            urls.append(value)

    return sorted(set(urls))


# ==========================================
# 5. LOAD EXTRACTED TEXT
# ==========================================

def load_text(document):

    text_file = document.get("text_file")

    if not text_file:
        return ""

    path = Path(text_file)

    if not path.is_absolute():
        path = BASE_DIR / path

    if not path.exists():
        print(f"Warning: Text file missing: {path}")
        return ""

    with open(path, "r", encoding="utf-8") as file:
        return file.read()


# ==========================================
# 6. NORMALIZE TEXT
# ==========================================

def normalize_text(text):

    # Convert text to lowercase
    text = text.lower()

    # Remove page labels
    text = re.sub(r"--- page \d+ ---", " ", text)

    # Remove unnecessary whitespace and punctuation
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Remove repeated spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ==========================================
# 7. CREATE TEXT SHINGLES
# ==========================================

def create_shingles(text, size=3):

    words = text.split()

    if len(words) < size:
        return set(words)

    return {
        " ".join(words[index:index + size])
        for index in range(len(words) - size + 1)
    }


# ==========================================
# 8. CALCULATE SIMILARITY
# ==========================================

def calculate_similarity(text1, text2):

    shingles1 = create_shingles(text1)
    shingles2 = create_shingles(text2)

    if not shingles1 or not shingles2:
        return 0.0

    intersection = len(shingles1 & shingles2)
    union = len(shingles1 | shingles2)

    return intersection / union if union else 0.0


# ==========================================
# 9. EXACT DUPLICATE DETECTION
# ==========================================

def detect_exact_duplicates(documents):

    groups = defaultdict(list)

    for document in documents:

        if document.get("extraction_status") != "success":
            continue

        file_hash = document.get("sha256")

        if not file_hash:
            continue

        groups[file_hash].append(document)

    unique_documents = []
    duplicate_groups = []

    for file_hash, records in groups.items():

        primary = records[0]

        all_urls = set()

        for record in records:
            all_urls.update(get_source_urls(record))

        unique_document = {
            "sha256": file_hash,
            "title": (
                primary.get("title")
                or primary.get("name")
                or primary.get("filename")
                or "Untitled document"
            ),
            "text_file": primary.get("text_file"),
            "page_count": primary.get("page_count", 0),
            "total_characters": primary.get("total_characters", 0),
            "source_urls": sorted(all_urls),
            "duplicate_count": len(records),
            "original_records": records
        }

        unique_documents.append(unique_document)

        if len(records) > 1:

            duplicate_groups.append({
                "sha256": file_hash,
                "duplicate_count": len(records),
                "source_urls": sorted(all_urls)
            })

    return unique_documents, duplicate_groups


# ==========================================
# 10. NEAR-DUPLICATE DETECTION
# ==========================================

def detect_near_duplicates(unique_documents):

    near_duplicates = []

    print("\nChecking for near-duplicate documents...")

    # Cache normalized text to avoid loading it repeatedly
    normalized_documents = []

    for document in unique_documents:

        text = load_text(document)
        normalized = normalize_text(text)

        normalized_documents.append({
            "sha256": document["sha256"],
            "title": document["title"],
            "normalized_text": normalized,
            "text_length": len(normalized)
        })

    total = len(normalized_documents)

    for i in range(total):

        first = normalized_documents[i]

        if first["text_length"] < MINIMUM_TEXT_LENGTH:
            continue

        for j in range(i + 1, total):

            second = normalized_documents[j]

            if second["text_length"] < MINIMUM_TEXT_LENGTH:
                continue

            # Avoid comparing documents with very different lengths
            length_ratio = (
                min(first["text_length"], second["text_length"])
                / max(first["text_length"], second["text_length"])
            )

            if length_ratio < 0.75:
                continue

            similarity = calculate_similarity(
                first["normalized_text"],
                second["normalized_text"]
            )

            if similarity >= SIMILARITY_THRESHOLD:

                near_duplicates.append({
                    "document_1": first["title"],
                    "document_2": second["title"],
                    "sha256_1": first["sha256"],
                    "sha256_2": second["sha256"],
                    "similarity": round(similarity, 4),
                    "status": "needs_review"
                })

                print(
                    f"Possible match: {first['title']} "
                    f"<-> {second['title']} "
                    f"({similarity:.2%})"
                )

    return near_duplicates


# ==========================================
# 11. SAVE RESULTS
# ==========================================

def save_results(unique_documents, report):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            unique_documents,
            file,
            indent=4,
            ensure_ascii=False
        )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )


# ==========================================
# 12. MAIN FUNCTION
# ==========================================

def main():

    print("=" * 55)
    print("       CIVILENS DOCUMENT DEDUPLICATOR")
    print("=" * 55)

    documents = load_documents()

    print(f"\nTotal extracted records: {len(documents)}")

    # Exact duplicate detection
    unique_documents, exact_groups = (
        detect_exact_duplicates(documents)
    )

    print("\nExact duplicate detection completed.")

    # Near duplicate detection
    near_duplicates = detect_near_duplicates(
        unique_documents
    )

    # Build report
    total_records = len(documents)
    unique_count = len(unique_documents)

    report = {
        "total_records": total_records,
        "unique_documents": unique_count,
        "exact_duplicate_groups": exact_groups,
        "exact_duplicate_group_count": len(exact_groups),
        "near_duplicate_pairs": near_duplicates,
        "near_duplicate_pair_count": len(near_duplicates),
        "similarity_threshold": SIMILARITY_THRESHOLD,
        "original_pdfs_deleted": False
    }

    save_results(unique_documents, report)

    # Final summary
    print("\n" + "=" * 55)
    print("          DEDUPLICATION SUMMARY")
    print("=" * 55)

    print(f"Original records: {total_records}")
    print(f"Unique documents: {unique_count}")
    print(
        f"Exact duplicate groups: {len(exact_groups)}"
    )
    print(
        f"Near-duplicate pairs: {len(near_duplicates)}"
    )

    print("\nOriginal PDFs have NOT been deleted.")

    print(f"\nUnique documents: {OUTPUT_FILE}")
    print(f"Deduplication report: {REPORT_FILE}")

    print("\nDeduplication completed!")


# ==========================================
# 13. RUN PROGRAM
# ==========================================

if __name__ == "__main__":
    main()
