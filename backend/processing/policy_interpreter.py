
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ==========================================
# 1. PROJECT CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
DOWNLOAD_DIR = BASE_DIR / "downloads"

INPUT_FILE = DOWNLOAD_DIR / "change_detection_report.json"
OUTPUT_FILE = DOWNLOAD_DIR / "policy_analysis.json"

ENV_FILE = BASE_DIR / ".env"

MODEL_NAME = "gemini-3.5-flash-lite"

# ==========================================
# 2. LOAD API KEY
# ==========================================

load_dotenv(ENV_FILE)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "Gemini API key not found. Check backend/.env"
    )


# ==========================================
# 3. LOAD CHANGE DETECTION REPORT
# ==========================================

def load_change_report():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Change report not found: {INPUT_FILE}"
        )

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# ==========================================
# 4. PREPARE EVIDENCE FOR GEMINI
# ==========================================

def prepare_evidence(report):

    evidence = []

    for result_index, result in enumerate(
        report.get("results", []), start=1
    ):

        if result.get("status") != "completed":
            continue

        document_1 = result.get("document_1", {})
        document_2 = result.get("document_2", {})

        for change_index, change in enumerate(
            result.get("changes", []), start=1
        ):

            evidence_id = (
                f"PAIR_{result_index}_CHANGE_{change_index}"
            )

            evidence.append({

                "evidence_id": evidence_id,

                "classification": change.get(
                    "classification", {}
                ),

                "change_type": change.get("change_type"),

                "document_1": {
                    "title": document_1.get("title"),
                    "source_url": document_1.get("source_url"),
                    "text": change.get(
                        "document_1_text", []
                    )
                },

                "document_2": {
                    "title": document_2.get("title"),
                    "source_url": document_2.get("source_url"),
                    "text": change.get(
                        "document_2_text", []
                    )
                }

            })

    return evidence


# ==========================================
# 5. PREPARE DOCUMENT INFORMATION
# ==========================================

def prepare_documents(report):

    documents = []

    for result in report.get("results", []):

        if result.get("status") != "completed":
            continue

        documents.append({

            "document_1": result.get("document_1", {}),

            "document_2": result.get("document_2", {}),

            "relationship_analysis": result.get(
                "relationship_analysis", {}
            ),

            "text_similarity": result.get(
                "text_similarity"
            ),

            "policy_amendment_confirmed": result.get(
                "policy_amendment_confirmed", False
            )

        })

    return documents


# ==========================================
# 6. CREATE AI INSTRUCTIONS
# ==========================================

def create_prompt(documents, evidence):

    instructions = """
You are the policy interpretation assistant for CiviLens.

CiviLens monitors public government documents and explains
changes in scholarship policies to students.

Your task is to interpret the supplied document information
and extracted text differences.

STRICT RULES:

1. Use only the information supplied in the input.
2. Never invent scholarship rules, dates, amounts or eligibility.
3. Do not treat two different scholarship categories as
   successive versions of the same policy.
4. A detected textual difference is not automatically
   an official policy amendment.
5. Distinguish confirmed information from possible impacts.
6. If information is insufficient, clearly say so.
7. Never decide whether an individual student is eligible.
8. Do not make legal or official government determinations.
9. Every important finding must reference one or more
   supplied evidence IDs.
10. Preserve the distinction between Diploma and Degree
    scholarship categories.
11. Do not interpret a document filename number as a year
    or version date without supporting evidence.
12. Use simple English that students can understand.

Return ONLY valid JSON using this structure:

{
  "overall_summary": "Simple explanation",
  "document_relationship": {
    "interpretation": "Explanation of relationship",
    "is_confirmed_amendment": false,
    "reason": "Reason"
  },
  "key_findings": [
    {
      "title": "Finding title",
      "category": "Category",
      "explanation": "What the evidence shows",
      "possible_student_impact": "Possible impact",
      "evidence_ids": ["PAIR_1_CHANGE_1"],
      "confidence": "high, medium or low"
    }
  ],
  "potentially_affected_students": [
    {
      "student_group": "Group described by evidence",
      "reason": "Why this group may be affected",
      "evidence_ids": ["PAIR_1_CHANGE_1"]
    }
  ],
  "student_guidance": [
    "Practical guidance supported by the evidence"
  ],
  "uncertainties": [
    "Information that cannot be confirmed"
  ],
  "important_notice": "Explain that this is an AI analysis
  of public documents, not an official government decision."
}

If no reliable evidence supports a section, return an
empty array for that section.

Do not create evidence IDs. Only use IDs supplied in the input.
"""

    input_data = {
        "documents": documents,
        "evidence": evidence
    }

    return instructions + "\n\nINPUT DATA:\n" + json.dumps(
        input_data,
        ensure_ascii=False,
        indent=2
    )


# ==========================================
# 7. GENERATE AI POLICY ANALYSIS
# ==========================================

def generate_analysis(prompt):

    client = genai.Client(api_key=API_KEY)

    try:

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=prompt,

            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2
            )

        )

        if not response.text:
            raise ValueError(
                "Gemini returned an empty response."
            )

        return json.loads(response.text)

    finally:
        client.close()


# ==========================================
# 8. SAVE POLICY ANALYSIS
# ==========================================

def save_analysis(
    analysis,
    documents,
    evidence
):

    output = {

        "project": "CiviLens",

        "analysis_type": "AI_POLICY_INTERPRETATION",

        "model": MODEL_NAME,

        "total_documents": len(documents),

        "total_evidence_blocks": len(evidence),

        "source_documents": documents,

        "source_evidence": evidence,

        "ai_analysis": analysis,

        "human_review_required": True

    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    return output


# ==========================================
# 9. MAIN EXECUTION
# ==========================================

def main():

    print("=" * 55)
    print("       CIVILENS AI POLICY INTERPRETER")
    print("=" * 55)

    print("\nLoading change detection report...")

    report = load_change_report()

    documents = prepare_documents(report)

    evidence = prepare_evidence(report)

    print(f"Documents compared: {len(documents)}")
    print(f"Evidence blocks: {len(evidence)}")

    if not evidence:

        print("\nNo evidence available for interpretation.")
        return

    print("\nPreparing evidence for Gemini...")

    prompt = create_prompt(documents, evidence)

    print("Sending evidence to Gemini...")

    analysis = generate_analysis(prompt)

    print("\nAI interpretation generated successfully!")

    save_analysis(
        analysis,
        documents,
        evidence
    )

    print("\n" + "=" * 55)
    print("           POLICY ANALYSIS SUMMARY")
    print("=" * 55)

    print("\nOVERALL SUMMARY:\n")
    print(analysis.get("overall_summary", "Not available"))

    print("\nKEY FINDINGS:\n")

    for finding in analysis.get("key_findings", []):

        print(f"- {finding.get('title')}")
        print(f"  {finding.get('explanation')}")
        print(
            f"  Evidence: "
            f"{', '.join(finding.get('evidence_ids', []))}"
        )
        print()

    print("\nUNCERTAINTIES:\n")

    for uncertainty in analysis.get("uncertainties", []):
        print(f"- {uncertainty}")

    print("\n" + "=" * 55)

    print(f"Full report saved at:\n{OUTPUT_FILE}")

    print("\nCiviLens AI interpretation completed!")


if __name__ == "__main__":
    main()
