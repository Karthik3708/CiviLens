# CiviLens — AI-Powered Government Policy Intelligence

> **Tagline:** *See Policy Changes. Understand Their Impact.*

---

## 1. Project Overview

**CiviLens** is an AI-powered government policy intelligence platform that continuously tracks, deduplicates, and analyzes official government documents. Instead of wading through dense PDF guidelines, citizens, students, and researchers can immediately spot meaningful differences between policy documents, understand their practical impact, and verify every finding against authentic public sources.

### Current Hackathon Scope
For this submission, CiviLens focuses strictly and deeply on:
- **Central Government of India**
- **Education Scholarships**
- **National Scholarship Portal (NSP)** (`scholarships.gov.in`)
- **AICTE (All India Council for Technical Education)** scholarship guidelines and FAQs.

---

## 2. Key Features & Screens

CiviLens features a 6-screen SaaS intelligence dashboard designed via **Google Stitch MCP** with a dark midnight navy aesthetic:

1. **📊 Overview Dashboard**
   - High-level KPI telemetry: Total Documents Collected (46), Unique Master Documents (42), Exact Duplicate Groups (4), Near-Duplicate Pairs (1), Policy Comparisons (1).
   - Document Processing Pipeline horizontal flow.
   - Featured Intelligence Callout highlighting the AICTE Diploma vs Degree policy differences.
   - Recent activity timeline and discovered document registry.

2. **🔍 Scholarship Explorer**
   - Searchable, filterable directory of all collected NSP guidelines and FAQs.
   - Filter by Category (Guideline / FAQ), Duplicate Status (Unique / Duplicate), and Sort Options.
   - Real cryptographic SHA-256 signatures, page counts, and character statistics.
   - Clickable links directly to official government PDFs on `scholarships.gov.in`.
   - Expandable drawer with in-app text preview extracted from verified documents.

3. **⚖️ Policy Change Intelligence**
   - Side-by-side comparative analysis between AICTE Diploma (`AICTE_2013_G.pdf`) and Degree (`AICTE_2012_G.pdf`) guidelines.
   - Text similarity analysis (58.44%) and 12 classified textual variations.
   - Substantive vs. formatting change separation:
     - **Course Category:** Diploma track vs Degree track.
     - **Scholarship Duration:** Diploma (Max 3 yrs / 2 yrs lateral entry) vs Degree (Max 4 yrs / 3 yrs lateral entry).
     - **Formatting/Whitespace:** Isolated from substantive policy changes.
   - Prominent ground-truth disclaimer: *These represent parallel guidelines for different educational levels, NOT successive amendments.*

4. **🤖 Ask CiviLens (AI Policy Assistant)**
   - Conversational policy assistant powered by **Gemini 3.5 Flash-Lite**.
   - Grounded strictly on `downloads/policy_analysis.json` and rule-based change detection.
   - Suggested quick prompts (Duration differences, eligibility, lateral entry, source documents).
   - Student guidance, potentially affected student groups, and transparent legal notice.
   - Safe offline fallback that displays rule-based change detection when AI analysis is unavailable.

5. **🏛️ Official Government Sources**
   - Zero-hallucination manifesto ensuring cryptographic traceability.
   - Source directory for National Scholarship Portal (NSP) and AICTE.
   - Filterable provenance table linking all 46 collected documents to their live government URLs.

6. **⚡ System Status & Pipeline Diagnostics**
   - Real-time audit of all 8 backend pipeline stages:
     1. NSP Document Collection (46 records)
     2. PDF Downloading (46/46 files)
     3. PDF Text Extraction (46 extracted via pdfplumber)
     4. OCR Fallback (0 required; native digital vector text)
     5. Exact Deduplication (4 duplicate groups)
     6. Near-Duplicate Analysis (1 pair at 95.59% similarity)
     7. Change Detection (12 categorized changes)
     8. Gemini Policy Interpretation (Structured synthesis)

---

## 3. Technology Stack

- **UI / Frontend:** Streamlit, Custom HTML/CSS (styled from Google Stitch MCP design system)
- **AI & NLP:** Google Gemini 3.5 Flash-Lite / Gemini 3.8 Flash via `google-genai` SDK
- **Design & Prototyping:** Google Stitch MCP (Screens, Design System `af7297b086dc4b399e437a8bedd4a1c8`)
- **Document Processing:** `pdfplumber`, SHA-256 cryptographic hashing, regex-based tokenization
- **Backend Data Pipeline:** Python 3.13, dynamic JSON store, Pandas

---

## 4. Setup & Running Instructions

### Prerequisites
- Python 3.10+ installed
- Git

### 1. Clone & Navigate to Project
```bash
git clone <repository-url>
cd CiviLens/backend
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Set up Environment Variables
If running live Gemini queries (pre-computed analysis in `downloads/policy_analysis.json` is already included):
Create a `.env` file inside `backend/`:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 4. Run the Streamlit Application
```bash
streamlit run streamlit_app.py
```
Open your browser at `http://localhost:8501`.

---

## 5. Deployment Guide

### Deploying to Streamlit Community Cloud
1. Push the repository to GitHub.
2. In [share.streamlit.io](https://share.streamlit.io), connect your repository.
3. Set the **Main file path** to:
   ```
   backend/streamlit_app.py
   ```
4. If using Gemini live queries, add `GEMINI_API_KEY` to the **Secrets** section.
5. Deploy!

---

## 6. Current Scope & Known Limitations

- **Geographic & Sectoral Scope:** Restricted to Government of India education scholarships (NSP/AICTE).
- **Document Versions:** Documents analyzed (such as `AICTE_2013_G` vs `AICTE_2012_G`) are parallel tracks for Diploma vs Degree, not chronological amendments.
- **Continuous Monitoring:** The current dashboard reflects the latest pipeline execution snapshot; continuous daemon polling can be triggered via scheduled cron jobs.
- **Legal Advisory:** CiviLens is an intelligence tool to aid citizen understanding; all official decisions must be confirmed with the respective government department.

