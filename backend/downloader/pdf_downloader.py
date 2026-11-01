
import json
import hashlib
import time
from pathlib import Path
from urllib.parse import urlparse

import requests


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "downloads" / "nsp_documents.json"
PDF_DIR = BASE_DIR / "downloads" / "pdfs"
MANIFEST_FILE = BASE_DIR / "downloads" / "download_manifest.json"

PDF_DIR.mkdir(parents=True, exist_ok=True)

# Download safety limits
ALLOWED_HOSTS = {"scholarships.gov.in"}
MAX_FILE_SIZE = 30 * 1024 * 1024  # 30 MB
CHUNK_SIZE = 8192


def is_trusted_url(url):
    """Allow only HTTPS URLs from the official NSP domain."""

    parsed = urlparse(url)

    return (
        parsed.scheme == "https"
        and parsed.hostname in ALLOWED_HOSTS
    )


def download_pdf(document, session):
    """Download and verify one PDF document."""

    url = document.get("url", "")

    if not is_trusted_url(url):
        return {
            "status": "rejected",
            "reason": "URL is not from the trusted NSP domain"
        }

    try:
        with session.get(
            url,
            stream=True,
            timeout=(10, 45),
            allow_redirects=True
        ) as response:

            response.raise_for_status()

            # Check redirected destination too
            if not is_trusted_url(response.url):
                return {
                    "status": "rejected",
                    "reason": "Redirected to an untrusted domain"
                }

            content_length = response.headers.get("Content-Length")

            if content_length and int(content_length) > MAX_FILE_SIZE:
                return {
                    "status": "rejected",
                    "reason": "File exceeds 30 MB limit"
                }

            temp_file = None
            file_hash = hashlib.sha256()
            total_size = 0
            first_chunk = True

            try:
                for chunk in response.iter_content(
                    chunk_size=CHUNK_SIZE
                ):
                    if not chunk:
                        continue

                    if first_chunk:
                        if not chunk.startswith(b"%PDF-"):
                            return {
                                "status": "rejected",
                                "reason": "Downloaded content is not a valid PDF"
                            }

                        first_chunk = False

                    total_size += len(chunk)

                    if total_size > MAX_FILE_SIZE:
                        return {
                            "status": "rejected",
                            "reason": "File exceeds 30 MB limit"
                        }

                    if temp_file is None:
                        temp_file = PDF_DIR / "temporary_download.part"
                        output = open(temp_file, "wb")

                    output.write(chunk)
                    file_hash.update(chunk)

                if first_chunk or total_size == 0:
                    return {
                        "status": "rejected",
                        "reason": "Empty download"
                    }

                output.close()
                output = None

                digest = file_hash.hexdigest()
                filename = f"{digest}.pdf"
                final_path = PDF_DIR / filename

                if final_path.exists():
                    temp_file.unlink(missing_ok=True)
                    return {
                        "status": "already_downloaded",
                        "filename": filename,
                        "sha256": digest,
                        "size_bytes": total_size,
                        "local_path": str(final_path.relative_to(BASE_DIR))
                    }

                temp_file.replace(final_path)

                return {
                    "status": "downloaded",
                    "filename": filename,
                    "sha256": digest,
                    "size_bytes": total_size,
                    "local_path": str(final_path.relative_to(BASE_DIR))
                }

            finally:
                if "output" in locals() and output is not None:
                    output.close()

                if temp_file and temp_file.exists():
                    temp_file.unlink()

    except requests.RequestException as error:
        return {
            "status": "failed",
            "reason": str(error)
        }

    except (OSError, ValueError) as error:
        return {
            "status": "failed",
            "reason": str(error)
        }


def main():

    if not INPUT_FILE.exists():
        print("ERROR: NSP JSON file not found:", INPUT_FILE)
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        documents = json.load(file)

    if not isinstance(documents, list):
        print("ERROR: Expected a JSON list of documents.")
        return

    session = requests.Session()
    session.headers.update({
        "User-Agent": "CiviLens-ResearchBot/1.0"
    })

    manifest = []
    downloaded = 0
    existing = 0
    failed = 0
    rejected = 0

    print("\n========== CIVILENS ==========")
    print("NSP PDF DOWNLOADER")
    print("==============================\n")

    for index, document in enumerate(documents, 1):

        print(f"\n[{index}/{len(documents)}] {document.get('title', 'Untitled')}")

        result = download_pdf(document, session)

        record = {
            **document,
            **result
        }

        manifest.append(record)

        status = result["status"]

        if status == "downloaded":
            downloaded += 1
            print("Downloaded:", result["filename"])

        elif status == "already_downloaded":
            existing += 1
            print("Already exists:", result["filename"])

        elif status == "rejected":
            rejected += 1
            print("Rejected:", result["reason"])

        else:
            failed += 1
            print("Failed:", result["reason"])

        # Be polite to the government server
        time.sleep(1)

    with open(MANIFEST_FILE, "w", encoding="utf-8") as file:
        json.dump(
            manifest,
            file,
            indent=4,
            ensure_ascii=False
        )

    session.close()

    print("\n========== DOWNLOAD SUMMARY ==========")
    print("Total documents:", len(documents))
    print("Downloaded:", downloaded)
    print("Already downloaded:", existing)
    print("Rejected:", rejected)
    print("Failed:", failed)
    print("PDF folder:", PDF_DIR)
    print("Manifest:", MANIFEST_FILE)


if __name__ == "__main__":
    main()
