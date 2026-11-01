
import json
import hashlib
from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image


# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DOWNLOAD_DIR = BASE_DIR / "downloads"
PDF_DIR = DOWNLOAD_DIR / "pdfs"
EXTRACTED_DIR = DOWNLOAD_DIR / "extracted"

DOWNLOAD_MANIFEST = DOWNLOAD_DIR / "download_manifest.json"
EXTRACTION_MANIFEST = DOWNLOAD_DIR / "extraction_manifest.json"


# ==========================================
# 2. TESSERACT CONFIGURATION
# ==========================================

TESSERACT_PATH = Path(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_PATH)


# ==========================================
# 3. CREATE REQUIRED DIRECTORIES
# ==========================================

PDF_DIR.mkdir(parents=True, exist_ok=True)
EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# 4. LOAD DOWNLOAD MANIFEST
# ==========================================

def load_download_manifest():

    if not DOWNLOAD_MANIFEST.exists():
        raise FileNotFoundError(
            f"Download manifest not found: {DOWNLOAD_MANIFEST}"
        )

    with open(DOWNLOAD_MANIFEST, "r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("documents", "files", "downloads"):
            if isinstance(data.get(key), list):
                return data[key]

    raise ValueError("Unexpected download manifest format.")


# ==========================================
# 5. FIND PDF FILE
# ==========================================

def find_pdf(document):

    possible_paths = [
        document.get("pdf_path"),
        document.get("file_path"),
        document.get("local_path"),
        document.get("download_path"),
        document.get("saved_path"),
    ]

    for path in possible_paths:

        if not path:
            continue

        pdf_path = Path(path)

        if not pdf_path.is_absolute():
            pdf_path = BASE_DIR / pdf_path

        if pdf_path.exists():
            return pdf_path

    # Fallback: locate PDF using its SHA-256 filename
    file_hash = document.get("sha256")

    if file_hash:
        candidate = PDF_DIR / f"{file_hash}.pdf"

        if candidate.exists():
            return candidate

    return None


# ==========================================
# 6. CALCULATE SHA-256
# ==========================================

def calculate_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


# ==========================================
# 7. EXTRACT TEXT FROM A PDF PAGE
# ==========================================

def extract_page_text(page):

    # First attempt: normal PDF text extraction
    text = page.get_text("text").strip()

    method = "text_extraction"

    # Second attempt: OCR for pages with almost no text
    if len(text) < 20:

        if not TESSERACT_PATH.exists():
            raise FileNotFoundError(
                f"Tesseract executable not found: {TESSERACT_PATH}"
            )

        pix = page.get_pixmap(
            dpi=300,
            alpha=False
        )

        image = Image.frombytes(
            "RGB",
            [pix.width, pix.height],
            pix.samples
        )

        text = pytesseract.image_to_string(
            image,
            lang="eng"
        ).strip()

        method = "ocr"

    return text, method


# ==========================================
# 8. PROCESS ONE PDF
# ==========================================

def process_pdf(document):

    pdf_path = find_pdf(document)

    if pdf_path is None:

        return {
            **document,
            "extraction_status": "failed",
            "error": "PDF file not found."
        }

    file_hash = calculate_hash(pdf_path)

    output_path = EXTRACTED_DIR / f"{file_hash}.txt"

    print(f"\nProcessing: {pdf_path.name}")

    try:

        pdf = pymupdf.open(pdf_path)

        extracted_pages = []
        total_characters = 0
        ocr_pages = 0

        for page_number, page in enumerate(pdf, start=1):

            text, method = extract_page_text(page)

            if method == "ocr":
                ocr_pages += 1

            total_characters += len(text)

            extracted_pages.append({
                "page": page_number,
                "text": text,
                "method": method
            })

            print(
                f"  Page {page_number}/{len(pdf)}: "
                f"{len(text)} characters ({method})"
            )

        page_count = len(pdf)

        pdf.close()

        # Save extracted text
        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as output:

            for page in extracted_pages:

                output.write(
                    f"\n\n--- PAGE {page['page']} ---\n\n"
                )

                output.write(page["text"])

        result = {
            **document,
            "sha256": file_hash,
            "pdf_path": str(pdf_path),
            "extraction_status": "success",
            "page_count": page_count,
            "total_characters": total_characters,
            "ocr_pages": ocr_pages,
            "text_file": str(output_path),
            "needs_ocr": total_characters == 0,
            "pages": extracted_pages
        }

        print(
            f"Completed: {page_count} pages, "
            f"{total_characters} characters, "
            f"{ocr_pages} OCR pages"
        )

        return result

    except Exception as error:

        print(f"Failed: {error}")

        return {
            **document,
            "pdf_path": str(pdf_path),
            "extraction_status": "failed",
            "error": str(error)
        }


# ==========================================
# 9. MAIN FUNCTION
# ==========================================

def main():

    print("=" * 55)
    print("          CIVILENS PDF TEXT EXTRACTOR")
    print("=" * 55)

    documents = load_download_manifest()

    print(f"\nTotal document records: {len(documents)}")

    results = []

    successful = 0
    failed = 0
    total_ocr_pages = 0

    for document in documents:

        status = document.get("status", "").lower()

        # Process only successfully downloaded PDFs
        if status and status not in (
            "downloaded",
            "already_downloaded",
            "success"
        ):
            print(
                f"\nSkipping document with status: {status}"
            )
            continue

        result = process_pdf(document)

        results.append(result)

        if result.get("extraction_status") == "success":

            successful += 1

            total_ocr_pages += result.get(
                "ocr_pages", 0
            )

        else:
            failed += 1

    # Save extraction manifest
    with open(
        EXTRACTION_MANIFEST,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n" + "=" * 55)
    print("             EXTRACTION SUMMARY")
    print("=" * 55)

    print(f"Total processed: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Pages processed using OCR: {total_ocr_pages}")

    print(f"\nExtracted files: {EXTRACTED_DIR}")
    print(f"Extraction manifest: {EXTRACTION_MANIFEST}")

    print("\nPDF extraction completed!")


# ==========================================
# 10. RUN PROGRAM
# ==========================================

if __name__ == "__main__":
    main()
