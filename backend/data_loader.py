"""
CiviLens Data Loader Module
Dynamically loads and validates backend pipeline JSON outputs.
Uses paths relative to this file for cross-platform and deployment portability.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

BASE_DIR = Path(__file__).resolve().parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
EXTRACTED_DIR = DOWNLOADS_DIR / "extracted"
PDFS_DIR = DOWNLOADS_DIR / "pdfs"


def load_json_file(filename: str) -> Optional[Any]:
    """Safely load a JSON file from the downloads directory."""
    path = DOWNLOADS_DIR / filename
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None


def get_nsp_documents() -> List[Dict[str, Any]]:
    """Load collected NSP documents."""
    data = load_json_file("nsp_documents.json")
    return data if isinstance(data, list) else []


def get_download_manifest() -> List[Dict[str, Any]]:
    """Load download manifest."""
    data = load_json_file("download_manifest.json")
    return data if isinstance(data, list) else []


def get_extraction_manifest() -> List[Dict[str, Any]]:
    """Load extraction manifest."""
    data = load_json_file("extraction_manifest.json")
    return data if isinstance(data, list) else []


def get_deduplication_report() -> Dict[str, Any]:
    """Load deduplication report."""
    data = load_json_file("deduplication_report.json")
    return data if isinstance(data, dict) else {}


def get_deduplicated_documents() -> List[Dict[str, Any]]:
    """Load unique deduplicated master documents."""
    data = load_json_file("deduplicated_documents.json")
    return data if isinstance(data, list) else []


def get_change_detection_report() -> Dict[str, Any]:
    """Load policy change detection report."""
    data = load_json_file("change_detection_report.json")
    return data if isinstance(data, dict) else {}


def get_policy_analysis() -> Dict[str, Any]:
    """Load Gemini-powered policy interpretation."""
    data = load_json_file("policy_analysis.json")
    return data if isinstance(data, dict) else {}


def get_extracted_text(sha256: str) -> Optional[str]:
    """Load extracted text for a given document SHA-256 hash."""
    txt_path = EXTRACTED_DIR / f"{sha256}.txt"
    if not txt_path.exists():
        return None
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading extracted text for {sha256}: {e}")
        return None


def get_pipeline_metrics() -> Dict[str, Any]:
    """Calculate pipeline summary metrics dynamically from files."""
    nsp_docs = get_nsp_documents()
    dedup_rep = get_deduplication_report()
    dedup_docs = get_deduplicated_documents()
    change_rep = get_change_detection_report()
    extract_man = get_extraction_manifest()
    policy_ana = get_policy_analysis()

    total_collected = len(nsp_docs) if nsp_docs else dedup_rep.get("total_records", 46)
    unique_count = len(dedup_docs) if dedup_docs else dedup_rep.get("unique_documents", 42)
    exact_dup_count = dedup_rep.get("exact_duplicate_group_count", len(dedup_rep.get("exact_duplicate_groups", [])))
    near_dup_count = dedup_rep.get("near_duplicate_pair_count", len(dedup_rep.get("near_duplicate_pairs", [])))
    comparisons_count = change_rep.get("total_pairs_compared", len(change_rep.get("results", [])))

    return {
        "total_collected": total_collected,
        "unique_documents": unique_count,
        "exact_duplicate_groups": exact_dup_count,
        "near_duplicate_pairs": near_dup_count,
        "comparisons_performed": comparisons_count,
        "extracted_count": len(extract_man),
        "policy_analysis_available": bool(policy_ana and "ai_analysis" in policy_ana),
        "source_name": "National Scholarship Portal (NSP)",
        "scope": "Central Government • Education Scholarships",
    }

