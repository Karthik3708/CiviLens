
import json
import re
from pathlib import Path
from difflib import SequenceMatcher
from urllib.parse import urlparse


# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
DOWNLOAD_DIR = BASE_DIR / "downloads"

EXTRACTION_FILE = DOWNLOAD_DIR / "extraction_manifest.json"
DEDUPLICATION_FILE = DOWNLOAD_DIR / "deduplication_report.json"

OUTPUT_FILE = DOWNLOAD_DIR / "change_detection_report.json"


# ==========================================
# 2. LOAD JSON
# ==========================================

def load_json(path):

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


# ==========================================
# 3. TEXT NORMALIZATION
# ==========================================

def normalize_line(text):

    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s₹%]", "", text)

    return text.strip()


def compact_text(lines):

    return " ".join(
        normalize_line(line["text"])
        for line in lines
    ).strip()


# ==========================================
# 4. EXTRACT PAGE-LEVEL TEXT
# ==========================================

def extract_lines(document):

    lines = []

    for page in document.get("pages", []):

        page_number = page.get("page", 0)
        page_text = page.get("text", "")

        for line in page_text.splitlines():

            original = line.strip()

            if not original:
                continue

            lines.append({
                "page": page_number,
                "text": original,
                "normalized": normalize_line(original)
            })

    return lines


# ==========================================
# 5. FIND DOCUMENT BY HASH
# ==========================================

def find_document(documents, file_hash):

    for document in documents:

        if document.get("sha256") == file_hash:
            return document

    return None


# ==========================================
# 6. GET SOURCE URL
# ==========================================

def get_source_url(document):

    for field in (
        "url",
        "source_url",
        "original_url",
        "document_url",
        "pdf_url"
    ):

        value = document.get(field)

        if isinstance(value, str) and value.startswith("https://"):
            return value

    return None


# ==========================================
# 7. GET DOCUMENT TITLE
# ==========================================

def get_document_title(document):

    title = (
        document.get("title")
        or document.get("name")
        or document.get("filename")
    )

    if title:
        return title

    url = get_source_url(document)

    if url:
        return Path(urlparse(url).path).name

    return "Untitled document"


# ==========================================
# 8. DETECT COURSE CATEGORY
# ==========================================

def detect_course_category(document):

    full_text = " ".join(
        page.get("text", "")
        for page in document.get("pages", [])
    ).lower()

    diploma_count = len(
        re.findall(r"\bdiploma\b", full_text)
    )

    degree_count = len(
        re.findall(r"\bdegree\b", full_text)
    )

    if diploma_count >= 2 and diploma_count > degree_count:
        return {
            "category": "Diploma",
            "diploma_mentions": diploma_count,
            "degree_mentions": degree_count
        }

    if degree_count >= 2 and degree_count > diploma_count:
        return {
            "category": "Degree",
            "diploma_mentions": diploma_count,
            "degree_mentions": degree_count
        }

    return {
        "category": "Uncertain",
        "diploma_mentions": diploma_count,
        "degree_mentions": degree_count
    }


# ==========================================
# 9. EXTRACT DURATION INFORMATION
# ==========================================

def extract_durations(document):

    durations = []

    for page in document.get("pages", []):

        page_number = page.get("page", 0)
        text = page.get("text", "")

        pattern = (
            r"(?:maximum|max\.?)\s*"
            r"(\d+)\s*years?"
        )

        matches = re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        for match in matches:

            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)

            durations.append({
                "page": page_number,
                "years": int(match.group(1)),
                "context": text[start:end].strip()
            })

    return durations


# ==========================================
# 10. CLASSIFY A CHANGE BLOCK
# ==========================================


def classify_change(removed, added):

    old_text = compact_text(removed)
    new_text = compact_text(added)

    # Keep original text for accurate currency detection
    old_original = " ".join(
        item["text"] for item in removed
    )

    new_original = " ".join(
        item["text"] for item in added
    )

    # --------------------------------------
    # 1. FORMATTING DIFFERENCES
    # --------------------------------------

    if old_text == new_text:

        return {
            "category": "formatting_difference",
            "description": (
                "The content is the same after text normalization."
            ),
            "policy_impact": "No substantive change detected."
        }

    # --------------------------------------
    # 2. COURSE CATEGORY DIFFERENCES
    # --------------------------------------

    combined_text = old_text + " " + new_text

    if (
        re.search(r"\bdiploma\b", combined_text)
        and re.search(r"\bdegree\b", combined_text)
    ):

        return {
            "category": "course_category_difference",
            "description": (
                "The text contains different course categories."
            ),
            "policy_impact": (
                "May affect which students or courses are covered."
            )
        }

    # --------------------------------------
    # 3. SCHOLARSHIP DURATION DIFFERENCES
    # --------------------------------------

    if (
        re.search(r"\d+\s*years?", combined_text)
        and re.search(r"\byears?\b", combined_text)
    ):

        return {
            "category": "duration_difference",
            "description": (
                "The text contains different duration values."
            ),
            "policy_impact": (
                "May affect the maximum scholarship duration."
            )
        }

    # --------------------------------------
    # 4. FINANCIAL DIFFERENCES
    # --------------------------------------

    def extract_currency_amounts(text):

        patterns = [
            r"(?:₹|rs\.?|inr)\s*"
            r"([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)",

            r"([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)"
            r"\s*(?:rupees|rs\.?)"
        ]

        amounts = []

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            for value in matches:

                normalized_value = value.replace(",", "")

                amounts.append(float(normalized_value))

        return sorted(set(amounts))

    old_amounts = extract_currency_amounts(old_original)
    new_amounts = extract_currency_amounts(new_original)

    if (
        old_amounts != new_amounts
        and (old_amounts or new_amounts)
    ):

        return {
            "category": "financial_difference",
            "description": (
                "Different explicitly marked currency amounts "
                "were detected."
            ),
            "old_amounts": old_amounts,
            "new_amounts": new_amounts,
            "policy_impact": (
                "May affect the scholarship amount or financial benefit."
            )
        }

    # --------------------------------------
    # 5. ELIGIBILITY-RELATED DIFFERENCES
    # --------------------------------------

    eligibility_terms = [
        "eligible",
        "eligibility",
        "income",
        "admission",
        "qualification",
        "percentage",
        "marks",
        "caste",
        "disability"
    ]

    if any(term in combined_text for term in eligibility_terms):

        return {
            "category": "eligibility_related_difference",
            "description": (
                "The text contains potentially relevant "
                "eligibility information."
            ),
            "policy_impact": (
                "Requires review to determine eligibility impact."
            )
        }

    # --------------------------------------
    # 6. OTHER DIFFERENCES
    # --------------------------------------

    return {
        "category": "other_textual_difference",
        "description": "Other textual difference detected.",
        "policy_impact": "Meaning requires further review."
    }



# ==========================================
# 11. COMPARE TWO DOCUMENTS
# ==========================================

def compare_documents(document_1, document_2):

    lines_1 = extract_lines(document_1)
    lines_2 = extract_lines(document_2)

    normalized_1 = [
        line["normalized"] for line in lines_1
    ]

    normalized_2 = [
        line["normalized"] for line in lines_2
    ]

    matcher = SequenceMatcher(
        None,
        normalized_1,
        normalized_2,
        autojunk=False
    )

    changes = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():

        if tag == "equal":
            continue

        removed = [
            {
                "page": line["page"],
                "text": line["text"]
            }
            for line in lines_1[i1:i2]
        ]

        added = [
            {
                "page": line["page"],
                "text": line["text"]
            }
            for line in lines_2[j1:j2]
        ]

        classification = classify_change(
            removed,
            added
        )

        changes.append({

            "change_type": {
                "insert": "added",
                "delete": "removed",
                "replace": "modified"
            }[tag],

            "classification": classification,

            "document_1_text": removed,
            "document_2_text": added

        })

    return changes, matcher.ratio()


# ==========================================
# 12. CLASSIFY DOCUMENT RELATIONSHIP
# ==========================================

def classify_relationship(
    category_1,
    category_2,
    changes
):

    course_1 = category_1["category"]
    course_2 = category_2["category"]

    if (
        course_1 != "Uncertain"
        and course_2 != "Uncertain"
        and course_1 != course_2
    ):

        return {
            "relationship": "related_policy_documents",
            "confidence": "heuristic",
            "reason": (
                f"Different course categories detected: "
                f"{course_1} and {course_2}."
            ),
            "requires_human_review": True
        }

    substantive_categories = {
        "course_category_difference",
        "duration_difference",
        "eligibility_related_difference",
        "financial_difference"
    }

    substantive_changes = [
        change for change in changes
        if change["classification"]["category"]
        in substantive_categories
    ]

    if substantive_changes:

        return {
            "relationship": "possible_revised_version",
            "confidence": "heuristic",
            "reason": (
                "Potential substantive differences were found "
                "within the documents."
            ),
            "requires_human_review": True
        }

    return {
        "relationship": "similar_documents_uncertain",
        "confidence": "heuristic",
        "reason": (
            "The documents are similar, but their relationship "
            "could not be established."
        ),
        "requires_human_review": True
    }


# ==========================================
# 13. PROCESS NEAR-DUPLICATE PAIRS
# ==========================================

def detect_changes():

    extraction_data = load_json(EXTRACTION_FILE)
    deduplication_data = load_json(DEDUPLICATION_FILE)

    near_pairs = deduplication_data.get(
        "near_duplicate_pairs", []
    )

    print("=" * 55)
    print("       CIVILENS POLICY CHANGE DETECTOR")
    print("=" * 55)

    print(f"\nNear-duplicate pairs found: {len(near_pairs)}")

    results = []

    for index, pair in enumerate(near_pairs, start=1):

        print(f"\nComparing pair {index}...")

        hash_1 = pair.get("sha256_1")
        hash_2 = pair.get("sha256_2")

        document_1 = find_document(
            extraction_data,
            hash_1
        )

        document_2 = find_document(
            extraction_data,
            hash_2
        )

        if document_1 is None or document_2 is None:

            results.append({
                "sha256_1": hash_1,
                "sha256_2": hash_2,
                "status": "failed",
                "error": "Document missing from extraction manifest."
            })

            continue

        # Compare text
        changes, similarity = compare_documents(
            document_1,
            document_2
        )

        # Detect course categories
        category_1 = detect_course_category(document_1)
        category_2 = detect_course_category(document_2)

        # Extract durations
        durations_1 = extract_durations(document_1)
        durations_2 = extract_durations(document_2)

        # Classify document relationship
        relationship = classify_relationship(
            category_1,
            category_2,
            changes
        )

        result = {

            "document_1": {
                "title": get_document_title(document_1),
                "sha256": hash_1,
                "source_url": get_source_url(document_1),
                "detected_category": category_1,
                "duration_information": durations_1
            },

            "document_2": {
                "title": get_document_title(document_2),
                "sha256": hash_2,
                "source_url": get_source_url(document_2),
                "detected_category": category_2,
                "duration_information": durations_2
            },

            "text_similarity": round(similarity, 4),

            "relationship_analysis": relationship,

            "total_changes": len(changes),

            "changes": changes,

            "status": "completed",

            "requires_human_review": True,

            "policy_amendment_confirmed": False,

            "note": (
                "Detected differences are not automatically "
                "confirmed policy amendments."
            )
        }

        results.append(result)

        print(f"Text similarity: {similarity:.2%}")

        print(
            f"Document 1 category: {category_1['category']}"
        )

        print(
            f"Document 2 category: {category_2['category']}"
        )

        print(
            "Relationship: "
            f"{relationship['relationship']}"
        )

        print(f"Change blocks: {len(changes)}")

        for change in changes:

            classification = (
                change["classification"]["category"]
            )

            print(
                f"  - {change['change_type']}: "
                f"{classification}"
            )

    # ======================================
    # 14. SAVE REPORT
    # ======================================

    report = {

        "total_pairs_compared": len(near_pairs),

        "successful_comparisons": sum(
            1 for item in results
            if item.get("status") == "completed"
        ),

        "failed_comparisons": sum(
            1 for item in results
            if item.get("status") == "failed"
        ),

        "results": results

    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n" + "=" * 55)
    print("          CHANGE DETECTION SUMMARY")
    print("=" * 55)

    print(f"Pairs compared: {report['total_pairs_compared']}")
    print(f"Successful: {report['successful_comparisons']}")
    print(f"Failed: {report['failed_comparisons']}")

    print(f"\nReport saved at: {OUTPUT_FILE}")

    print("\nChange detection completed!")


# ==========================================
# 15. RUN PROGRAM
# ==========================================

if __name__ == "__main__":
    detect_changes()
