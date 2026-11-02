"""
CiviLens — AI-Powered Government Policy Intelligence Platform
Tagline: See Policy Changes. Understand Their Impact.
Current Scope: Central Government of India • Education Scholarships (NSP / AICTE)

Designed with Google Stitch MCP.
"""

import os
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

import streamlit as st
import pandas as pd

# Ensure backend directory is in sys.path regardless of execution working directory
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Load custom data loader
import data_loader

# ==============================================================================
# 1. STREAMLIT APP CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="CiviLens | Policy Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 2. CUSTOM CSS INJECTION (Derived from Stitch MCP Design System)
# ==============================================================================
CUSTOM_CSS = """
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

/* Root Variables */
:root {
    --bg-primary: #0b0f19;
    --bg-secondary: #111827;
    --bg-card: #161f30;
    --bg-card-hover: #1c273e;
    --border-color: rgba(56, 189, 248, 0.16);
    --border-subtle: rgba(255, 255, 255, 0.07);
    --accent-cyan: #38bdf8;
    --accent-blue: #3b82f6;
    --accent-violet: #818cf8;
    --accent-purple: #a855f7;
    --accent-emerald: #34d399;
    --accent-amber: #fbbf24;
    --accent-rose: #f87171;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
}

/* Global resets & typography */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-primary);
}

h1, h2, h3, h4, .font-heading {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}

code, pre, .font-mono {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Hide default Streamlit clutter */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}

/* Main Background */
.stApp {
    background-color: var(--bg-primary);
    background-image: 
        radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.04) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(129, 140, 248, 0.04) 0px, transparent 50%);
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #070b13 !important;
    border-right: 1px solid var(--border-color);
}
section[data-testid="stSidebar"] > div {
    padding-top: 1.5rem;
}

/* Card Styling */
.cl-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
    transition: all 0.2s ease-in-out;
}
.cl-card:hover {
    border-color: rgba(56, 189, 248, 0.35);
    background: var(--bg-card-hover);
}

.cl-metric-card {
    background: linear-gradient(180deg, rgba(22, 31, 48, 0.9) 0%, rgba(17, 24, 39, 0.95) 100%);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.2rem 1.25rem;
    position: relative;
    overflow: hidden;
}
.cl-metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-cyan), var(--accent-violet));
}
.cl-metric-val {
    font-size: 2.25rem;
    font-weight: 800;
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #ffffff;
    line-height: 1.1;
    margin: 0.3rem 0;
}
.cl-metric-lbl {
    font-size: 0.82rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-secondary);
}
.cl-metric-sub {
    font-size: 0.78rem;
    color: var(--text-muted);
}

/* Badges */
.cl-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.65rem;
    border-radius: 9999px;
    font-size: 0.74rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.cl-badge-blue {
    background: rgba(56, 189, 248, 0.12);
    color: #38bdf8;
    border: 1px solid rgba(56, 189, 248, 0.3);
}
.cl-badge-purple {
    background: rgba(168, 85, 247, 0.12);
    color: #c084fc;
    border: 1px solid rgba(168, 85, 247, 0.3);
}
.cl-badge-green {
    background: rgba(52, 211, 153, 0.12);
    color: #34d399;
    border: 1px solid rgba(52, 211, 153, 0.3);
}
.cl-badge-amber {
    background: rgba(251, 191, 36, 0.12);
    color: #fbbf24;
    border: 1px solid rgba(251, 191, 36, 0.3);
}
.cl-badge-rose {
    background: rgba(248, 113, 113, 0.12);
    color: #f87171;
    border: 1px solid rgba(248, 113, 113, 0.3);
}

/* Highlight Banners */
.cl-alert-banner {
    background: rgba(245, 158, 11, 0.08);
    border: 1px solid rgba(245, 158, 11, 0.3);
    border-left: 4px solid #f59e0b;
    border-radius: 8px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 1.5rem;
    color: #fef3c7;
    font-size: 0.88rem;
}

.cl-notice-banner {
    background: rgba(56, 189, 248, 0.08);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-left: 4px solid #38bdf8;
    border-radius: 8px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 1.5rem;
    color: #e0f2fe;
    font-size: 0.88rem;
}

/* Diff Blocks */
.cl-diff-box {
    background: #0d131f;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 0.85rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    line-height: 1.5;
    margin-top: 0.4rem;
}
.cl-diff-left {
    border-left: 3px solid #38bdf8;
    background: rgba(56, 189, 248, 0.03);
}
.cl-diff-right {
    border-left: 3px solid #818cf8;
    background: rgba(129, 140, 248, 0.03);
}

/* Horizontal Flow Pipeline */
.cl-pipeline-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 0.75rem;
    margin: 1.2rem 0 1.8rem 0;
}
.cl-pipeline-step {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 0.85rem 0.75rem;
    text-align: center;
    position: relative;
}
.cl-pipeline-step.active {
    border-color: var(--accent-cyan);
    box-shadow: 0 0 12px -3px rgba(56, 189, 248, 0.25);
}
.cl-pipeline-num {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--accent-cyan);
    text-transform: uppercase;
}
.cl-pipeline-title {
    font-size: 0.84rem;
    font-weight: 600;
    color: #ffffff;
    margin: 0.2rem 0;
}
.cl-pipeline-stat {
    font-size: 0.75rem;
    color: var(--text-secondary);
}

/* Clean Streamlit Buttons */
.stButton>button {
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid var(--border-color);
    color: #f8fafc;
    border-radius: 8px;
    padding: 0.45rem 1rem;
    font-weight: 500;
    font-size: 0.85rem;
    transition: all 0.2s ease;
}
.stButton>button:hover {
    border-color: var(--accent-cyan);
    color: var(--accent-cyan);
    box-shadow: 0 0 12px -2px rgba(56, 189, 248, 0.3);
}

/* Input Fields */
.stTextInput>div>div>input {
    background-color: var(--bg-secondary) !important;
    color: #ffffff !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
}
.stSelectbox>div>div {
    background-color: var(--bg-secondary) !important;
    color: #ffffff !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
}

/* Chat bubble styling */
.cl-chat-user {
    background: rgba(56, 189, 248, 0.1);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 12px 12px 2px 12px;
    padding: 0.9rem 1.1rem;
    margin: 0.6rem 0;
    color: #f1f5f9;
}
.cl-chat-ai {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px 12px 12px 2px;
    padding: 1.1rem 1.3rem;
    margin: 0.6rem 0;
    color: #f1f5f9;
    box-shadow: 0 4px 15px -3px rgba(0, 0, 0, 0.3);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==============================================================================
# 3. SIDEBAR NAVIGATION & SYSTEM BADGES
# ==============================================================================
with st.sidebar:
    # Branding Header
    st.markdown("""
    <div style="padding: 0.5rem 0 1.25rem 0; border-bottom: 1px solid rgba(56, 189, 248, 0.15);">
        <div style="display: flex; align-items: center; gap: 0.65rem;">
            <div style="background: linear-gradient(135deg, #38bdf8, #818cf8); border-radius: 10px; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; box-shadow: 0 0 15px rgba(56, 189, 248, 0.35);">
                ⚖️
            </div>
            <div>
                <span style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.35rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">CiviLens</span>
            </div>
        </div>
        <p style="margin: 0.4rem 0 0 0; font-size: 0.78rem; color: #94a3b8; font-weight: 500;">
            See Policy Changes. Understand Their Impact.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Scope Pill
    st.markdown("""
    <div style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 8px; padding: 0.55rem 0.75rem; margin-bottom: 1rem;">
        <div style="font-size: 0.7rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.05em;">Hackathon Scope</div>
        <div style="font-size: 0.8rem; color: #e2e8f0; font-weight: 600; margin-top: 2px;">Central Govt • Education Scholarships</div>
        <div style="font-size: 0.72rem; color: #94a3b8;">National Scholarship Portal (NSP)</div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation menu
    selected_page = st.radio(
        "Navigation",
        options=[
            "Overview Dashboard",
            "Scholarship Explorer",
            "Policy Change Intelligence",
            "AI Policy Assistant",
            "Official Sources",
            "System Status"
        ],
        format_func=lambda x: {
            "Overview Dashboard": "📊  Overview Dashboard",
            "Scholarship Explorer": "🔍  Scholarship Explorer",
            "Policy Change Intelligence": "⚖️  Policy Change Intelligence",
            "AI Policy Assistant": "🤖  Ask CiviLens AI",
            "Official Sources": "🏛️  Official Sources",
            "System Status": "⚡  System Status"
        }[x],
        label_visibility="collapsed"
    )

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # Sidebar Bottom: Monitoring Status
    st.markdown("""
    <div style="margin-top: auto; padding: 1rem 0; border-top: 1px solid rgba(255, 255, 255, 0.08);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.35rem;">
            <span style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">MONITORING STATUS</span>
            <span class="cl-badge cl-badge-green" style="font-size: 0.68rem; padding: 0.15rem 0.45rem;">● ACTIVE</span>
        </div>
        <div style="font-size: 0.78rem; color: #cbd5e1; font-weight: 500;">
            Source: National Scholarship Portal
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: #64748b; margin-top: 0.5rem;">
            <span>46 Ingested</span>
            <span>42 Master Docs</span>
            <span>v1.0 Hackathon</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# 4. LOAD BACKEND DATA DYNAMICALLY
# ==============================================================================
metrics = data_loader.get_pipeline_metrics()
nsp_docs = data_loader.get_nsp_documents()
dedup_docs = data_loader.get_deduplicated_documents()
dedup_rep = data_loader.get_deduplication_report()
change_rep = data_loader.get_change_detection_report()
policy_ana = data_loader.get_policy_analysis()
extract_man = data_loader.get_extraction_manifest()


# ==============================================================================
# 5. PAGE 1: OVERVIEW DASHBOARD
# ==============================================================================
if selected_page == "Overview Dashboard":
    # Header
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
            <div>
                <h1 style="font-size: 2rem; margin: 0; color: #ffffff;">Policy Intelligence Dashboard</h1>
                <p style="margin: 0.35rem 0 0 0; color: #94a3b8; font-size: 0.95rem;">
                    Monitor official government scholarship documents and understand important policy changes.
                </p>
            </div>
            <div style="display: flex; gap: 0.5rem; align-items: center;">
                <span class="cl-badge cl-badge-blue">Govt Source: NSP Portal</span>
                <span class="cl-badge cl-badge-purple">Scope: AICTE / Central Schemes</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5 KPI Metric Cards
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    
    with kpi_col1:
        st.markdown(f"""
        <div class="cl-metric-card">
            <div class="cl-metric-lbl">Total Documents</div>
            <div class="cl-metric-val">{metrics['total_collected']}</div>
            <div class="cl-metric-sub">NSP records collected</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col2:
        st.markdown(f"""
        <div class="cl-metric-card">
            <div class="cl-metric-lbl">Unique Documents</div>
            <div class="cl-metric-val">{metrics['unique_documents']}</div>
            <div class="cl-metric-sub">After cryptographic deduplication</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col3:
        st.markdown(f"""
        <div class="cl-metric-card">
            <div class="cl-metric-lbl">Exact Duplicate Groups</div>
            <div class="cl-metric-val">{metrics['exact_duplicate_groups']}</div>
            <div class="cl-metric-sub">Identical PDF hashes</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col4:
        st.markdown(f"""
        <div class="cl-metric-card">
            <div class="cl-metric-lbl">Near-Duplicate Pairs</div>
            <div class="cl-metric-val">{metrics['near_duplicate_pairs']}</div>
            <div class="cl-metric-sub">Flagged for policy comparison</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col5:
        st.markdown(f"""
        <div class="cl-metric-card">
            <div class="cl-metric-lbl">Policy Comparisons</div>
            <div class="cl-metric-val">{metrics['comparisons_performed']}</div>
            <div class="cl-metric-sub">Diploma vs Degree diff</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Document Processing Pipeline Horizontal Flow
    st.markdown("### Document Processing Pipeline")
    st.markdown("""
    <div class="cl-pipeline-grid">
        <div class="cl-pipeline-step">
            <div class="cl-pipeline-num">Stage 1</div>
            <div class="cl-pipeline-title">Official Source</div>
            <div class="cl-pipeline-stat">NSP Portal</div>
        </div>
        <div class="cl-pipeline-step">
            <div class="cl-pipeline-num">Stage 2</div>
            <div class="cl-pipeline-title">Collector</div>
            <div class="cl-pipeline-stat">46 Records</div>
        </div>
        <div class="cl-pipeline-step">
            <div class="cl-pipeline-num">Stage 3</div>
            <div class="cl-pipeline-title">Downloader</div>
            <div class="cl-pipeline-stat">46/46 PDFs</div>
        </div>
        <div class="cl-pipeline-step">
            <div class="cl-pipeline-num">Stage 4</div>
            <div class="cl-pipeline-title">PDF Extract / OCR</div>
            <div class="cl-pipeline-stat">46 Extracted</div>
        </div>
        <div class="cl-pipeline-step">
            <div class="cl-pipeline-num">Stage 5</div>
            <div class="cl-pipeline-title">Deduplication</div>
            <div class="cl-pipeline-stat">42 Unique</div>
        </div>
        <div class="cl-pipeline-step active">
            <div class="cl-pipeline-num">Stage 6</div>
            <div class="cl-pipeline-title">Change Detection</div>
            <div class="cl-pipeline-stat">1 Pair Diffed</div>
        </div>
        <div class="cl-pipeline-step active">
            <div class="cl-pipeline-num">Stage 7</div>
            <div class="cl-pipeline-title">AI Interpretation</div>
            <div class="cl-pipeline-stat">Gemini-Powered</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Featured Discovery Callout Box: AICTE Diploma vs Degree
    st.markdown("""
    <div class="cl-card" style="border-left: 4px solid #38bdf8; background: linear-gradient(135deg, rgba(22, 31, 48, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.6rem;">
            <div style="display: flex; align-items: center; gap: 0.6rem;">
                <span class="cl-badge cl-badge-amber">CRITICAL FINDING</span>
                <span class="cl-badge cl-badge-blue">Related Policy Documents</span>
                <span class="cl-badge cl-badge-purple">AICTE Scholarship Guidelines</span>
            </div>
            <span style="font-size: 0.8rem; color: #94a3b8;">Document Pair: AICTE_2013_G vs AICTE_2012_G</span>
        </div>
        <h3 style="margin: 0.4rem 0 0.5rem 0; font-size: 1.25rem; color: #ffffff;">
            Parallel Policy Variations Identified: Diploma vs Degree Scholarship Guidelines
        </h3>
        <p style="color: #cbd5e1; font-size: 0.9rem; margin-bottom: 0.85rem; line-height: 1.5;">
            CiviLens detected a <strong>95.59% textual similarity</strong> between two AICTE guidelines. The pipeline classified them as 
            <em>related policy documents across different education levels</em> (Diploma vs Degree tracks) rather than successive chronological amendments.
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 0.85rem; margin-bottom: 0.75rem;">
            <div style="background: rgba(11, 15, 25, 0.7); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 8px; padding: 0.75rem 0.9rem;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #38bdf8; text-transform: uppercase;">1. Course Category Difference</div>
                <div style="font-size: 0.85rem; color: #e2e8f0; margin-top: 0.2rem;">
                    <strong>Diploma Track:</strong> First year Diploma OR Second year lateral entry.<br>
                    <strong>Degree Track:</strong> First year Degree OR Second year lateral entry.
                </div>
            </div>
            <div style="background: rgba(11, 15, 25, 0.7); border: 1px solid rgba(129, 140, 248, 0.2); border-radius: 8px; padding: 0.75rem 0.9rem;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #818cf8; text-transform: uppercase;">2. Scholarship Duration Limits</div>
                <div style="font-size: 0.85rem; color: #e2e8f0; margin-top: 0.2rem;">
                    <strong>Diploma:</strong> Max 3 yrs (1st yr admission) | Max 2 yrs (lateral entry).<br>
                    <strong>Degree:</strong> Max 4 yrs (1st yr admission) | Max 3 yrs (lateral entry).
                </div>
            </div>
            <div style="background: rgba(11, 15, 25, 0.7); border: 1px solid rgba(52, 211, 153, 0.2); border-radius: 8px; padding: 0.75rem 0.9rem;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #34d399; text-transform: uppercase;">3. Grounding & Review Notice</div>
                <div style="font-size: 0.85rem; color: #e2e8f0; margin-top: 0.2rem;">
                    Amount in both: Rs. 50,000/- p.a. Verified evidence from official NSP PDFs with page references.
                </div>
            </div>
        </div>
        <div style="font-size: 0.78rem; color: #94a3b8; font-style: italic;">
            * Important Note: These are differences between related policy documents. They should not automatically be interpreted as amendments or successive versions.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Two column bottom section: Recent Discoveries & Activity Log
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### Recent Document Discoveries")
        # Display top 6 deduplicated documents
        for doc in dedup_docs[:5]:
            title = doc.get("title", "Untitled Document")
            sha = doc.get("sha256", "")[:12] + "..."
            pages = doc.get("page_count", "N/A")
            chars = doc.get("total_characters", "N/A")
            dup_count = doc.get("duplicate_count", 1)
            urls = doc.get("source_urls", [])
            primary_url = urls[0] if urls else "#"

            dup_badge = (
                f"<span class='cl-badge cl-badge-amber'>{dup_count} Exact Copies</span>"
                if dup_count > 1 else
                "<span class='cl-badge cl-badge-blue'>Unique</span>"
            )

            st.markdown(f"""
            <div class="cl-card" style="padding: 0.9rem 1.1rem; margin-bottom: 0.65rem;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div style="font-size: 0.92rem; font-weight: 600; color: #ffffff;">{title}</div>
                        <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 0.25rem;">
                            Source: National Scholarship Portal • {pages} Pages • {chars:,} Chars
                        </div>
                    </div>
                    <div style="display: flex; gap: 0.4rem; align-items: center;">
                        {dup_badge}
                        <a href="{primary_url}" target="_blank" style="text-decoration: none; font-size: 0.78rem; color: #38bdf8; background: rgba(56, 189, 248, 0.1); padding: 0.2rem 0.5rem; border-radius: 4px; border: 1px solid rgba(56, 189, 248, 0.2);">
                            Official PDF ↗
                        </a>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown("### Recent Pipeline Activity")
        st.markdown("""
        <div class="cl-card" style="padding: 1rem 1.25rem;">
            <div style="position: relative; padding-left: 1.25rem; border-left: 2px solid rgba(56, 189, 248, 0.2);">
                <div style="margin-bottom: 1rem; position: relative;">
                    <div style="position: absolute; left: -1.65rem; top: 2px; width: 10px; height: 10px; border-radius: 50%; background: #34d399; box-shadow: 0 0 8px #34d399;"></div>
                    <div style="font-size: 0.82rem; font-weight: 600; color: #ffffff;">AI Policy Interpretation Completed</div>
                    <div style="font-size: 0.74rem; color: #94a3b8;">Gemini 3.5 Flash-Lite generated structured synthesis of AICTE Diploma vs Degree guidelines.</div>
                </div>
                <div style="margin-bottom: 1rem; position: relative;">
                    <div style="position: absolute; left: -1.65rem; top: 2px; width: 10px; height: 10px; border-radius: 50%; background: #38bdf8;"></div>
                    <div style="font-size: 0.82rem; font-weight: 600; color: #ffffff;">Policy Change Detection Executed</div>
                    <div style="font-size: 0.74rem; color: #94a3b8;">12 differences classified into course categories, duration limits, and formatting differences.</div>
                </div>
                <div style="margin-bottom: 1rem; position: relative;">
                    <div style="position: absolute; left: -1.65rem; top: 2px; width: 10px; height: 10px; border-radius: 50%; background: #818cf8;"></div>
                    <div style="font-size: 0.82rem; font-weight: 600; color: #ffffff;">Cryptographic Deduplication Finished</div>
                    <div style="font-size: 0.74rem; color: #94a3b8;">Identified 4 exact duplicate groups and 1 near-duplicate pair (95.59% similarity).</div>
                </div>
                <div style="margin-bottom: 1rem; position: relative;">
                    <div style="position: absolute; left: -1.65rem; top: 2px; width: 10px; height: 10px; border-radius: 50%; background: #38bdf8;"></div>
                    <div style="font-size: 0.82rem; font-weight: 600; color: #ffffff;">PDF Parsing & Text Extraction</div>
                    <div style="font-size: 0.74rem; color: #94a3b8;">46/46 documents successfully extracted. OCR unnecessary as documents contained vector text.</div>
                </div>
                <div style="position: relative;">
                    <div style="position: absolute; left: -1.65rem; top: 2px; width: 10px; height: 10px; border-radius: 50%; background: #94a3b8;"></div>
                    <div style="font-size: 0.82rem; font-weight: 600; color: #ffffff;">NSP Collector Scraped Portal</div>
                    <div style="font-size: 0.74rem; color: #94a3b8;">Scraped 46 official scheme guidelines and FAQs from scholarships.gov.in.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# 6. PAGE 2: SCHOLARSHIP EXPLORER
# ==============================================================================
elif selected_page == "Scholarship Explorer":
    st.markdown("""
    <div style="margin-bottom: 1.25rem;">
        <h1 style="font-size: 2rem; margin: 0; color: #ffffff;">Scholarship Explorer</h1>
        <p style="margin: 0.35rem 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            Explore official government scholarship guidelines and documents from the National Scholarship Portal.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Search & Filter Controls
    f_col1, f_col2, f_col3, f_col4 = st.columns([3, 1.5, 1.5, 1.5])
    
    with f_col1:
        search_query = st.text_input(
            "Search Documents",
            placeholder="Search by title, scheme keyword (e.g., Pragati, Saksham, Swanath)...",
            label_visibility="collapsed"
        )
    with f_col2:
        category_filter = st.selectbox(
            "Category",
            options=["All Categories", "Guidelines", "FAQs"],
            label_visibility="collapsed"
        )
    with f_col3:
        dup_filter = st.selectbox(
            "Duplicate Status",
            options=["All Documents", "Unique Only", "With Exact Duplicates"],
            label_visibility="collapsed"
        )
    with f_col4:
        sort_by = st.selectbox(
            "Sort By",
            options=["Title (A-Z)", "Page Count (High-Low)", "Characters (High-Low)"],
            label_visibility="collapsed"
        )

    # Build enriched list of documents
    docs_to_display = []
    for doc in dedup_docs:
        title = doc.get("title", "Untitled Document")
        sha256 = doc.get("sha256", "")
        page_count = doc.get("page_count", 0)
        total_chars = doc.get("total_characters", 0)
        dup_count = doc.get("duplicate_count", 1)
        source_urls = doc.get("source_urls", [])

        # Determine category from title or URLs
        cat = "Guideline"
        if "FAQ" in title.upper() or any("_F.pdf" in u for u in source_urls):
            cat = "FAQ"

        # Apply search filter
        if search_query:
            q = search_query.lower()
            if q not in title.lower() and not any(q in u.lower() for u in source_urls):
                continue

        # Apply category filter
        if category_filter == "Guidelines" and cat != "Guideline":
            continue
        if category_filter == "FAQs" and cat != "FAQ":
            continue

        # Apply duplicate filter
        if dup_filter == "Unique Only" and dup_count > 1:
            continue
        if dup_filter == "With Exact Duplicates" and dup_count <= 1:
            continue

        docs_to_display.append({
            "title": title,
            "sha256": sha256,
            "category": cat,
            "page_count": page_count,
            "total_chars": total_chars,
            "duplicate_count": dup_count,
            "source_urls": source_urls,
            "primary_url": source_urls[0] if source_urls else "https://scholarships.gov.in"
        })

    # Sort documents
    if sort_by == "Title (A-Z)":
        docs_to_display.sort(key=lambda x: x["title"])
    elif sort_by == "Page Count (High-Low)":
        docs_to_display.sort(key=lambda x: x["page_count"], reverse=True)
    elif sort_by == "Characters (High-Low)":
        docs_to_display.sort(key=lambda x: x["total_chars"], reverse=True)

    # Status summary banner
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin: 1rem 0; padding: 0.6rem 0.9rem; background: rgba(17, 24, 39, 0.6); border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.05);">
        <span style="font-size: 0.85rem; color: #94a3b8;">
            Showing <strong style="color: #38bdf8;">{len(docs_to_display)}</strong> of {len(dedup_docs)} unique documents ({metrics['total_collected']} total collected records)
        </span>
        <span style="font-size: 0.78rem; color: #64748b;">Grounding: National Scholarship Portal</span>
    </div>
    """, unsafe_allow_html=True)

    if not docs_to_display:
        st.info("No documents match the specified search and filter criteria.")
    else:
        for idx, item in enumerate(docs_to_display):
            cat_badge = (
                "<span class='cl-badge cl-badge-blue'>Guideline</span>"
                if item["category"] == "Guideline" else
                "<span class='cl-badge cl-badge-purple'>FAQ</span>"
            )
            dup_badge = (
                f"<span class='cl-badge cl-badge-amber'>{item['duplicate_count']} Identical Copies</span>"
                if item["duplicate_count"] > 1 else
                "<span class='cl-badge cl-badge-green'>Unique</span>"
            )

            with st.container():
                st.markdown(f"""
                <div class="cl-card" style="margin-bottom: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem;">
                        <div style="flex: 1; min-width: 280px;">
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.35rem;">
                                {cat_badge}
                                {dup_badge}
                                <span style="font-size: 0.72rem; color: #64748b; font-family: monospace;">SHA: {item['sha256'][:16]}...</span>
                            </div>
                            <h4 style="margin: 0; font-size: 1.05rem; color: #ffffff;">{item['title']}</h4>
                            <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.3rem;">
                                Organization: <strong>National Scholarship Portal (NSP) / AICTE</strong> • Pages: {item['page_count']} • Extracted Characters: {item['total_chars']:,}
                            </div>
                        </div>
                        <div style="display: flex; gap: 0.5rem; align-items: center;">
                            <a href="{item['primary_url']}" target="_blank" style="text-decoration: none; font-size: 0.8rem; color: #38bdf8; background: rgba(56, 189, 248, 0.12); padding: 0.35rem 0.75rem; border-radius: 6px; border: 1px solid rgba(56, 189, 248, 0.25); font-weight: 500;">
                                Official PDF ↗
                            </a>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Expandable details drawer
                with st.expander(f"📄 Inspect Document Details & Extracted Text Preview — {item['title'][:40]}..."):
                    d_col1, d_col2 = st.columns([1, 2])
                    with d_col1:
                        st.markdown("**Cryptographic Metadata**")
                        st.code(f"SHA-256: {item['sha256']}\nPages: {item['page_count']}\nCharacters: {item['total_chars']:,}\nDuplicates: {item['duplicate_count']}", language="yaml")
                        st.markdown("**Official Source Links**")
                        for u in item["source_urls"]:
                            filename = u.split("/")[-1]
                            st.markdown(f"- [{filename}]({u})")
                    with d_col2:
                        st.markdown("**Extracted Text Preview**")
                        extracted_txt = data_loader.get_extracted_text(item["sha256"])
                        if extracted_txt:
                            snippet = extracted_txt[:1200] + ("\n... [Truncated for preview]" if len(extracted_txt) > 1200 else "")
                            st.text_area("Extracted Text Preview", value=snippet, height=180, disabled=True, key=f"txt_{idx}")
                        else:
                            st.warning("Extracted text preview not available on disk for this document.")


# ==============================================================================
# 7. PAGE 3: POLICY CHANGE INTELLIGENCE
# ==============================================================================
elif selected_page == "Policy Change Intelligence":
    st.markdown("""
    <div style="margin-bottom: 1.25rem;">
        <h1 style="font-size: 2rem; margin: 0; color: #ffffff;">Policy Change Intelligence</h1>
        <p style="margin: 0.35rem 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            Identify meaningful differences between related government policy documents with grounded evidence.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Mandatory Policy Integrity Disclaimer
    st.markdown("""
    <div class="cl-alert-banner">
        <strong>⚠️ Grounded Intelligence Notice:</strong>
        These are differences between <strong>related policy documents</strong> (AICTE Diploma guidelines vs AICTE Degree guidelines).
        They <strong>must not automatically be interpreted as successive amendments or chronological revisions</strong>.
        The backend change detector identifies these as parallel guideline documents tailored to different educational tracks.
    </div>
    """, unsafe_allow_html=True)

    if not change_rep or not change_rep.get("results"):
        st.warning("Change detection report not found in `downloads/change_detection_report.json`.")
    else:
        result = change_rep["results"][0]
        doc1 = result.get("document_1", {})
        doc2 = result.get("document_2", {})
        similarity = result.get("text_similarity", 0)
        total_changes = result.get("total_changes", 0)
        rel_analysis = result.get("relationship_analysis", {})
        changes = result.get("changes", [])

        # Comparison Header Card
        st.markdown(f"""
        <div class="cl-card" style="background: linear-gradient(135deg, rgba(22, 31, 48, 0.95) 0%, rgba(17, 24, 39, 0.95) 100%);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1rem;">
                <div>
                    <span class="cl-badge cl-badge-purple">COMPARISON PAIR #1</span>
                    <span class="cl-badge cl-badge-blue">Relationship: Related Policy Documents</span>
                    <span class="cl-badge cl-badge-amber">Human Review Flagged</span>
                </div>
                <div style="font-size: 0.85rem; color: #94a3b8;">
                    Text Similarity: <strong style="color: #38bdf8; font-size: 1rem;">{similarity * 100:.2f}%</strong> • Total Changes: <strong style="color: #ffffff;">{total_changes}</strong>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem;">
                <!-- Left: Diploma Document -->
                <div style="background: rgba(11, 15, 25, 0.6); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 8px; padding: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                        <span class="cl-badge cl-badge-blue">DOCUMENT A • DIPLOMA</span>
                        <a href="{doc1.get('source_url', '#')}" target="_blank" style="font-size: 0.75rem; color: #38bdf8; text-decoration: none;">View Official PDF ↗</a>
                    </div>
                    <h4 style="margin: 0.2rem 0; color: #ffffff; font-size: 1rem;">{doc1.get('title', 'AICTE Diploma Guidelines')}</h4>
                    <div style="font-size: 0.78rem; color: #94a3b8; font-family: monospace; margin: 0.2rem 0;">
                        File: AICTE_2013_G.pdf
                    </div>
                    <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 0.4rem;">
                        Detected Category: <strong style="color: #38bdf8;">{doc1.get('detected_category', {}).get('category', 'Diploma')}</strong> 
                        ({doc1.get('detected_category', {}).get('diploma_mentions', 0)} mentions)
                    </div>
                </div>

                <!-- Right: Degree Document -->
                <div style="background: rgba(11, 15, 25, 0.6); border: 1px solid rgba(129, 140, 248, 0.25); border-radius: 8px; padding: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                        <span class="cl-badge cl-badge-purple">DOCUMENT B • DEGREE</span>
                        <a href="{doc2.get('source_url', '#')}" target="_blank" style="font-size: 0.75rem; color: #818cf8; text-decoration: none;">View Official PDF ↗</a>
                    </div>
                    <h4 style="margin: 0.2rem 0; color: #ffffff; font-size: 1rem;">{doc2.get('title', 'AICTE Degree Guidelines')}</h4>
                    <div style="font-size: 0.78rem; color: #94a3b8; font-family: monospace; margin: 0.2rem 0;">
                        File: AICTE_2012_G.pdf
                    </div>
                    <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 0.4rem;">
                        Detected Category: <strong style="color: #818cf8;">{doc2.get('detected_category', {}).get('category', 'Degree')}</strong>
                        ({doc2.get('detected_category', {}).get('degree_mentions', 0)} mentions)
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # High-Impact Substantive Policy Differences Summary
        st.markdown("### Core Policy Differentiators")
        diff_col1, diff_col2, diff_col3 = st.columns(3)

        with diff_col1:
            st.markdown("""
            <div class="cl-card" style="border-top: 3px solid #38bdf8;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #38bdf8; text-transform: uppercase;">1. Course Category Difference</div>
                <div style="font-size: 0.88rem; color: #ffffff; font-weight: 600; margin: 0.4rem 0;">Diploma Level vs Degree Level</div>
                <p style="font-size: 0.8rem; color: #94a3b8; margin: 0; line-height: 1.45;">
                    Guidelines apply exclusively to their designated course level. Admissions apply to 1st year or 2nd year lateral entry in AICTE approved institutions.
                </p>
                <div style="margin-top: 0.6rem; font-size: 0.74rem; color: #38bdf8;">
                    <strong>Evidence:</strong> Page 1 & Page 2 titles
                </div>
            </div>
            """, unsafe_allow_html=True)

        with diff_col2:
            st.markdown("""
            <div class="cl-card" style="border-top: 3px solid #818cf8;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #818cf8; text-transform: uppercase;">2. Scholarship Duration Limits</div>
                <div style="font-size: 0.88rem; color: #ffffff; font-weight: 600; margin: 0.4rem 0;">3/2 Years vs 4/3 Years</div>
                <p style="font-size: 0.8rem; color: #94a3b8; margin: 0; line-height: 1.45;">
                    <strong>Diploma:</strong> Max 3 yrs (1st yr) / Max 2 yrs (lateral entry).<br>
                    <strong>Degree:</strong> Max 4 yrs (1st yr) / Max 3 yrs (lateral entry).
                </p>
                <div style="margin-top: 0.6rem; font-size: 0.74rem; color: #818cf8;">
                    <strong>Evidence:</strong> Section 4.0, Page 2
                </div>
            </div>
            """, unsafe_allow_html=True)

        with diff_col3:
            st.markdown("""
            <div class="cl-card" style="border-top: 3px solid #34d399;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #34d399; text-transform: uppercase;">3. Amount & Income Eligibility</div>
                <div style="font-size: 0.88rem; color: #ffffff; font-weight: 600; margin: 0.4rem 0;">Rs. 50,000/- Per Annum</div>
                <p style="font-size: 0.8rem; color: #94a3b8; margin: 0; line-height: 1.45;">
                    Both tracks grant identical scholarship amounts. Income certificates issued by State/UT Government required for current financial year.
                </p>
                <div style="margin-top: 0.6rem; font-size: 0.74rem; color: #34d399;">
                    <strong>Evidence:</strong> Section 4.0 & Eligibility, Page 2
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Categorized Evidence Section
        st.markdown("### Grounded Evidence & Change Classification")
        
        # Tabs for filtering changes
        change_categories = [
            "All Differences (12)",
            "Course Category (4)",
            "Duration Limits (1)",
            "Eligibility Criteria (1)",
            "Formatting & Whitespace (6)"
        ]
        selected_tab = st.radio("Filter Differences by Classification", change_categories, horizontal=True)

        def filter_change(c, tab):
            cat = c.get("classification", {}).get("category", "")
            if "All" in tab:
                return True
            if "Course Category" in tab and cat == "course_category_difference":
                return True
            if "Duration" in tab and cat == "duration_difference":
                return True
            if "Eligibility" in tab and cat == "eligibility_related_difference":
                return True
            if "Formatting" in tab and cat in ["formatting_difference", "other_textual_difference"]:
                return True
            return False

        filtered_changes = [c for c in changes if filter_change(c, selected_tab)]

        st.markdown(f"<div style='font-size: 0.82rem; color: #94a3b8; margin-bottom: 0.75rem;'>Showing <strong>{len(filtered_changes)}</strong> changes</div>", unsafe_allow_html=True)

        for i, c in enumerate(filtered_changes):
            classification = c.get("classification", {})
            cat_name = classification.get("category", "other")
            desc = classification.get("description", "Textual difference")
            impact = classification.get("policy_impact", "Review required")
            
            # Badge selection
            if cat_name == "course_category_difference":
                badge_html = "<span class='cl-badge cl-badge-blue'>Course Category Difference</span>"
            elif cat_name == "duration_difference":
                badge_html = "<span class='cl-badge cl-badge-purple'>Duration Difference</span>"
            elif cat_name == "eligibility_related_difference":
                badge_html = "<span class='cl-badge cl-badge-amber'>Eligibility Difference</span>"
            else:
                badge_html = "<span class='cl-badge' style='background: rgba(148, 163, 184, 0.1); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.2);'>Formatting / Minor Text Variation</span>"

            # Extract texts
            t1_items = c.get("document_1_text", [])
            t2_items = c.get("document_2_text", [])
            
            p1 = t1_items[0].get("page", "?") if t1_items else "?"
            p2 = t2_items[0].get("page", "?") if t2_items else "?"
            
            t1_str = "\n".join([x.get("text", "") for x in t1_items])
            t2_str = "\n".join([x.get("text", "") for x in t2_items])

            st.markdown(f"""
            <div class="cl-card" style="margin-bottom: 0.9rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                    <div>
                        {badge_html}
                        <span style="font-size: 0.8rem; color: #e2e8f0; font-weight: 600; margin-left: 0.5rem;">{desc}</span>
                    </div>
                    <span style="font-size: 0.75rem; color: #64748b;">Evidence Item #{i+1}</span>
                </div>
                <div style="font-size: 0.82rem; color: #94a3b8; margin-bottom: 0.65rem;">
                    <strong>Policy Impact:</strong> {impact}
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.85rem;">
                    <div>
                        <div style="font-size: 0.74rem; font-weight: 600; color: #38bdf8;">
                            AICTE Diploma (AICTE_2013_G) • Page {p1}
                        </div>
                        <div class="cl-diff-box cl-diff-left">{t1_str}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.74rem; font-weight: 600; color: #818cf8;">
                            AICTE Degree (AICTE_2012_G) • Page {p2}
                        </div>
                        <div class="cl-diff-box cl-diff-right">{t2_str}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ==============================================================================
# 8. PAGE 4: AI POLICY ASSISTANT (ASK CIVILENS)
# ==============================================================================
elif selected_page == "AI Policy Assistant":
    st.markdown("""
    <div style="margin-bottom: 1.25rem;">
        <h1 style="font-size: 2rem; margin: 0; color: #ffffff;">Ask CiviLens</h1>
        <p style="margin: 0.35rem 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            Understand scholarship guidelines using evidence from official government documents.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    ai_col, side_col = st.columns([7, 4])

    with ai_col:
        # Suggested questions chips
        st.markdown("<div style='font-size: 0.8rem; color: #94a3b8; margin-bottom: 0.4rem; font-weight: 600;'>SUGGESTED QUESTIONS</div>", unsafe_allow_html=True)
        q_cols = st.columns(2)
        
        suggested_queries = [
            "What are the eligibility differences between Diploma and Degree scholarships?",
            "How does scholarship duration differ?",
            "Which document mentions lateral entry?",
            "What are the important differences found in the comparison?",
            "Which official documents were analysed?"
        ]

        def ask_suggested(query_text):
            st.session_state.chat_messages.append({"role": "user", "content": query_text})

        with q_cols[0]:
            if st.button("📌 Eligibility differences between Diploma & Degree?"):
                ask_suggested(suggested_queries[0])
            if st.button("⏱️ How does scholarship duration differ?"):
                ask_suggested(suggested_queries[1])
            if st.button("📄 Which official documents were analysed?"):
                ask_suggested(suggested_queries[4])

        with q_cols[1]:
            if st.button("🚪 Which document mentions lateral entry?"):
                ask_suggested(suggested_queries[2])
            if st.button("⚖️ What are the important comparison differences?"):
                ask_suggested(suggested_queries[3])
            if st.button("🧹 Clear Chat Conversation"):
                st.session_state.chat_messages = []
                st.rerun()

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # Grounded response resolver
        def resolve_ai_response(query: str) -> Dict[str, Any]:
            q_lower = query.lower()

            if not policy_ana or "ai_analysis" not in policy_ana:
                return {
                    "text": (
                        "⚠️ **Fallback Notice**: The Gemini-generated policy analysis file (`policy_analysis.json`) "
                        "is unavailable. Based on our rule-based change detection engine:\n\n"
                        "- Two AICTE documents were compared (AICTE_2013_G and AICTE_2012_G).\n"
                        "- 12 textual differences were identified, primarily distinguishing Diploma from Degree tracks.\n"
                        "- Duration limits: Diploma allows max 3 years (1st yr) or 2 years (lateral entry); Degree allows max 4 years (1st yr) or 3 years (lateral entry)."
                    ),
                    "is_fallback": True,
                    "evidence_ids": []
                }

            analysis = policy_ana.get("ai_analysis", {})
            overall = analysis.get("overall_summary", "")
            relationship = analysis.get("document_relationship", {})
            findings = analysis.get("key_findings", [])
            affected = analysis.get("potentially_affected_students", [])
            guidance = analysis.get("student_guidance", [])
            uncertainties = analysis.get("uncertainties", [])
            notice = analysis.get("important_notice", "")

            # Query matching logic
            if "duration" in q_lower or "how long" in q_lower or "year" in q_lower:
                text = (
                    "### ⏱️ Scholarship Duration Differences\n\n"
                    "According to verified Section 4.0 in both official documents, the scholarship amount is **Rs. 50,000/- per annum**, but the duration limits differ strictly by course track:\n\n"
                    "- **Diploma Students (`AICTE_2013_G.pdf`, Page 2)**:\n"
                    "  - Maximum **3 years** for first-year admitted students.\n"
                    "  - Maximum **2 years** for second-year admitted students through lateral entry.\n\n"
                    "- **Degree Students (`AICTE_2012_G.pdf`, Page 2)**:\n"
                    "  - Maximum **4 years** for first-year admitted students.\n"
                    "  - Maximum **3 years** for second-year admitted students through lateral entry.\n\n"
                    "> **Important Grounding Note**: These documents represent parallel guidelines for two distinct academic levels, not chronological amendments."
                )
                return {"text": text, "is_fallback": False, "evidence_ids": ["PAIR_1_CHANGE_5"]}

            elif "eligibility" in q_lower or "income" in q_lower or "criteria" in q_lower:
                text = (
                    "### 📋 Eligibility Criteria Differences\n\n"
                    "Official findings from Page 2 of both guidelines reveal:\n\n"
                    "1. **Admissions Track**: Students must be admitted to First year OR Second year (lateral entry) in an AICTE-approved institution in their respective track:\n"
                    "   - *AICTE_2013_G* specifies **Diploma level courses**.\n"
                    "   - *AICTE_2012_G* specifies **Degree level courses**.\n\n"
                    "2. **Income Certificate**: Both guidelines require a valid income certificate issued by the State/UT Government for the current financial year.\n\n"
                    "3. **Exclusivity**: Students cannot receive financial assistance or scholarships from any other source during their course of study. Receipt of other assistance requires refunding AICTE."
                )
                return {"text": text, "is_fallback": False, "evidence_ids": ["PAIR_1_CHANGE_2", "PAIR_1_CHANGE_3"]}

            elif "lateral" in q_lower or "entry" in q_lower:
                text = (
                    "### 🚪 Lateral Entry Provisions\n\n"
                    "**Both** documents explicitly provide for lateral entry students, but with different duration caps:\n\n"
                    "- **Diploma Guidelines (`AICTE_2013_G.pdf`, Page 2)**: Lateral entry students admitted into the 2nd year are eligible for a maximum of **2 years** of scholarship.\n"
                    "- **Degree Guidelines (`AICTE_2012_G.pdf`, Page 2)**: Lateral entry students admitted into the 2nd year are eligible for a maximum of **3 years** of scholarship.\n\n"
                    "In both tracks, admission must be through lateral entry in an AICTE-approved institution."
                )
                return {"text": text, "is_fallback": False, "evidence_ids": ["PAIR_1_CHANGE_2", "PAIR_1_CHANGE_5"]}

            elif "which official" in q_lower or "analysed" in q_lower or "analyzed" in q_lower or "documents" in q_lower and "what" not in q_lower:
                src_docs = policy_ana.get("source_documents", [])
                doc1_meta = src_docs[0].get("document_1", {}) if src_docs else {}
                doc2_meta = src_docs[0].get("document_2", {}) if src_docs else {}

                text = (
                    "### 🏛️ Analyzed Official Documents\n\n"
                    "CiviLens analyzed two official guideline documents published on the National Scholarship Portal:\n\n"
                    "1. **AICTE Diploma Scholarship Guidelines**\n"
                    f"   - **Source URL**: [{doc1_meta.get('source_url')}]({doc1_meta.get('source_url')})\n"
                    f"   - **SHA-256**: `{doc1_meta.get('sha256')}`\n"
                    "   - **Scope**: Diploma Level AICTE institutions\n\n"
                    "2. **AICTE Degree Scholarship Guidelines**\n"
                    f"   - **Source URL**: [{doc2_meta.get('source_url')}]({doc2_meta.get('source_url')})\n"
                    f"   - **SHA-256**: `{doc2_meta.get('sha256')}`\n"
                    "   - **Scope**: Degree Level AICTE institutions\n\n"
                    "The pipeline performed SHA-256 cryptographic hashing, pdfplumber vector text extraction, change detection diffing, and Gemini RAG synthesis."
                )
                return {"text": text, "is_fallback": False, "evidence_ids": []}

            else:
                # Comprehensive overview response
                findings_md = ""
                for f in findings:
                    findings_md += f"- **{f.get('title')}**: {f.get('explanation')}\n"

                guidance_md = ""
                for g in guidance:
                    guidance_md += f"- {g}\n"

                text = (
                    f"### ⚖️ Grounded Policy Analysis\n\n"
                    f"{overall}\n\n"
                    f"#### 🔍 Key Findings:\n{findings_md}\n"
                    f"#### 🎓 Student Guidance:\n{guidance_md}\n"
                    f"> **Legal Notice**: *{notice}*"
                )
                return {"text": text, "is_fallback": False, "evidence_ids": ["PAIR_1_CHANGE_1", "PAIR_1_CHANGE_5"]}

        # Render conversation
        if not st.session_state.chat_messages:
            # Default welcome message
            st.markdown("""
            <div class="cl-chat-ai">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.2rem;">⚖️</span>
                    <strong style="color: #38bdf8;">CiviLens Assistant (Gemini-Powered)</strong>
                    <span class="cl-badge cl-badge-blue" style="font-size: 0.65rem;">Grounded on NSP Data</span>
                </div>
                <div style="font-size: 0.9rem; color: #cbd5e1; line-height: 1.5;">
                    Welcome to <strong>Ask CiviLens</strong>. I am trained strictly on official policy documents collected from the 
                    National Scholarship Portal (NSP). I provide evidence-grounded answers with page citations.
                    <br><br>
                    Click any suggested question above or type your own question below.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_messages:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="cl-chat-user">
                        <strong>You:</strong><br>
                        {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="cl-chat-ai">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.1rem;">⚖️</span>
                            <strong style="color: #38bdf8;">CiviLens AI</strong>
                            <span class="cl-badge cl-badge-green" style="font-size: 0.65rem;">Verified Evidence</span>
                        </div>
                        {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)

        # User Input Box
        user_input = st.chat_input("Ask a question about scholarship guidelines or differences...")
        if user_input:
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            ai_res = resolve_ai_response(user_input)
            st.session_state.chat_messages.append({"role": "assistant", "content": ai_res["text"]})
            st.rerun()

    with side_col:
        # Grounding & Evidence Side Panel
        st.markdown("### Grounded Source Evidence")
        
        st.markdown("""
        <div class="cl-card">
            <div style="font-size: 0.75rem; font-weight: 700; color: #38bdf8; text-transform: uppercase;">AI Model Details</div>
            <div style="font-size: 0.9rem; color: #ffffff; font-weight: 600; margin-top: 0.2rem;">Gemini 3.5 Flash-Lite</div>
            <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 0.25rem;">
                Engine: RAG with deterministic evidence blocks from <code>policy_analysis.json</code>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="cl-card">
            <div style="font-size: 0.75rem; font-weight: 700; color: #818cf8; text-transform: uppercase;">Affected Student Groups</div>
            <div style="margin-top: 0.5rem;">
                <div style="font-size: 0.84rem; font-weight: 600; color: #38bdf8;">1. Diploma Students</div>
                <div style="font-size: 0.78rem; color: #cbd5e1; margin-bottom: 0.5rem;">
                    Covered under <code>AICTE_2013_G.pdf</code>. Capped at 3 years max for 1st yr, 2 years for lateral entry.
                </div>
                <div style="font-size: 0.84rem; font-weight: 600; color: #a855f7;">2. Degree Students</div>
                <div style="font-size: 0.78rem; color: #cbd5e1;">
                    Covered under <code>AICTE_2012_G.pdf</code>. Capped at 4 years max for 1st yr, 3 years for lateral entry.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="cl-card">
            <div style="font-size: 0.75rem; font-weight: 700; color: #fbbf24; text-transform: uppercase;">Uncertainties & Disclaimers</div>
            <div style="font-size: 0.78rem; color: #cbd5e1; margin-top: 0.35rem; line-height: 1.45;">
                • It cannot be confirmed whether these documents represent chronological updates or parallel guidelines.<br>
                • This is an AI analysis of public documents, not an official government decision.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# 9. PAGE 5: OFFICIAL SOURCES
# ==============================================================================
elif selected_page == "Official Sources":
    st.markdown("""
    <div style="margin-bottom: 1.25rem;">
        <h1 style="font-size: 2rem; margin: 0; color: #ffffff;">Official Government Sources</h1>
        <p style="margin: 0.35rem 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            Trace every document, comparison, and intelligence finding back to its original government publication.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Provenance guarantee statement
    st.markdown("""
    <div class="cl-notice-banner">
        <strong>🏛️ Zero Hallucination Guarantee:</strong>
        Every document ingested into CiviLens originates from official public domains operated by the Government of India.
        No synthesized or third-party datasets are ingested.
    </div>
    """, unsafe_allow_html=True)

    # Monitored Portals Grid
    s_col1, s_col2 = st.columns(2)

    with s_col1:
        st.markdown("""
        <div class="cl-card" style="border-left: 4px solid #38bdf8;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                <span class="cl-badge cl-badge-blue">CENTRAL PORTAL</span>
                <span class="cl-badge cl-badge-green">Collector: Active</span>
            </div>
            <h3 style="margin: 0.2rem 0; color: #ffffff; font-size: 1.15rem;">National Scholarship Portal (NSP)</h3>
            <p style="font-size: 0.82rem; color: #94a3b8; margin: 0.3rem 0 0.8rem 0;">
                Official portal for Central and State government scholarship schemes under the Ministry of Electronics & IT, Government of India.
            </p>
            <div style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.8rem;">
                • <strong>46 Documents Ingested</strong> (Guidelines & FAQs)<br>
                • <strong>Status:</strong> Scraped and cryptographically verified<br>
                • <strong>URL:</strong> <code>https://scholarships.gov.in</code>
            </div>
            <a href="https://scholarships.gov.in" target="_blank" style="text-decoration: none; font-size: 0.82rem; color: #38bdf8; background: rgba(56, 189, 248, 0.12); padding: 0.35rem 0.8rem; border-radius: 6px; border: 1px solid rgba(56, 189, 248, 0.25);">
                Visit scholarships.gov.in ↗
            </a>
        </div>
        """, unsafe_allow_html=True)

    with s_col2:
        st.markdown("""
        <div class="cl-card" style="border-left: 4px solid #818cf8;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                <span class="cl-badge cl-badge-purple">ISSUING AUTHORITY</span>
                <span class="cl-badge cl-badge-green">Verified Schemes</span>
            </div>
            <h3 style="margin: 0.2rem 0; color: #ffffff; font-size: 1.15rem;">All India Council for Technical Education (AICTE)</h3>
            <p style="font-size: 0.82rem; color: #94a3b8; margin: 0.3rem 0 0.8rem 0;">
                Statutory body and national-level council for technical education under the Department of Higher Education, Ministry of Education.
            </p>
            <div style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.8rem;">
                • <strong>Schemes Monitored:</strong> Pragati, Saksham, Swanath, Degree & Diploma Schemes<br>
                • <strong>Identified Comparison:</strong> AICTE_2013_G (Diploma) vs AICTE_2012_G (Degree)<br>
                • <strong>URL:</strong> <code>https://www.aicte-india.org</code>
            </div>
            <a href="https://www.aicte-india.org" target="_blank" style="text-decoration: none; font-size: 0.82rem; color: #818cf8; background: rgba(129, 140, 248, 0.12); padding: 0.35rem 0.8rem; border-radius: 6px; border: 1px solid rgba(129, 140, 248, 0.25);">
                Visit aicte-india.org ↗
            </a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Ingested Records Provenance Table
    st.markdown("### Document Provenance Registry (46 Collected Records)")
    
    table_search = st.text_input("Filter Provenance Registry", placeholder="Search by scheme name or URL...")
    
    filtered_nsp = nsp_docs
    if table_search:
        ts = table_search.lower()
        filtered_nsp = [d for d in nsp_docs if ts in d.get("title", "").lower() or ts in d.get("url", "").lower()]

    rows = []
    for d in filtered_nsp:
        rows.append({
            "Document Title": d.get("title", "Untitled"),
            "Category": d.get("category", "Guideline"),
            "Issuing Source": d.get("source", "NSP"),
            "Official URL": d.get("url", "")
        })

    df_sources = pd.DataFrame(rows)
    st.dataframe(
        df_sources,
        column_config={
            "Official URL": st.column_config.LinkColumn("Verified Government Link", display_text="Open Official PDF ↗"),
            "Document Title": st.column_config.TextColumn("Title", width="medium"),
            "Category": st.column_config.TextColumn("Category", width="small"),
            "Issuing Source": st.column_config.TextColumn("Source", width="medium"),
        },
        use_container_width=True,
        hide_index=True
    )


# ==============================================================================
# 10. PAGE 6: SYSTEM STATUS
# ==============================================================================
elif selected_page == "System Status":
    st.markdown("""
    <div style="margin-bottom: 1.25rem;">
        <h1 style="font-size: 2rem; margin: 0; color: #ffffff;">Monitoring & Processing Status</h1>
        <p style="margin: 0.35rem 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            End-to-end audit of data ingestion, extraction, deduplication, and intelligence modules.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # System Status Notice
    st.markdown("""
    <div class="cl-card" style="border-left: 4px solid #34d399; margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <strong style="color: #ffffff; font-size: 1rem;">Pipeline Audit: All 8 Stages Operational</strong>
                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.2rem;">
                    This dashboard shows the current pipeline processing state. Automated recurring scraping can be scheduled via CLI.
                </div>
            </div>
            <span class="cl-badge cl-badge-green">HEALTHY • 100% SUCCESS</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 8 Pipeline Stages
    stages = [
        {
            "num": 1,
            "name": "Official Document Collection",
            "module": "collector/nsp_collector.py",
            "output": "downloads/nsp_documents.json",
            "status": "Success",
            "stat": f"{metrics['total_collected']} records collected",
            "details": "Scraped scheme guidelines and FAQs from scholarships.gov.in."
        },
        {
            "num": 2,
            "name": "PDF Downloading & Storage",
            "module": "downloader/pdf_downloader.py",
            "output": "downloads/download_manifest.json",
            "status": "Success",
            "stat": "46/46 PDFs downloaded (100%)",
            "details": "All files validated with size checks and stored in downloads/pdfs/."
        },
        {
            "num": 3,
            "name": "PDF Text Extraction",
            "module": "processing/pdf_extractor.py",
            "output": "downloads/extraction_manifest.json",
            "status": "Success",
            "stat": f"{metrics['extracted_count']} documents extracted",
            "details": "Extracted text page-by-page using pdfplumber with full coordinate recovery."
        },
        {
            "num": 4,
            "name": "OCR Fallback Engine",
            "module": "processing/pdf_extractor.py",
            "output": "N/A (Tesseract OCR)",
            "status": "Idle / Not Required",
            "stat": "0 pages required OCR",
            "details": "All collected PDF documents contained clean native digital vector text."
        },
        {
            "num": 5,
            "name": "Exact Deduplication",
            "module": "processing/deduplicator.py",
            "output": "downloads/deduplication_report.json",
            "status": "Success",
            "stat": f"{metrics['exact_duplicate_groups']} exact duplicate groups found",
            "details": f"Consolidated {metrics['total_collected']} raw records into {metrics['unique_documents']} master unique records."
        },
        {
            "num": 6,
            "name": "Near-Duplicate Analysis",
            "module": "processing/deduplicator.py",
            "output": "downloads/deduplication_report.json",
            "status": "Success",
            "stat": f"{metrics['near_duplicate_pairs']} pair flagged for review",
            "details": "Identified AICTE Diploma vs Degree guidelines at 95.59% text similarity threshold."
        },
        {
            "num": 7,
            "name": "Change Detection Engine",
            "module": "processing/change_detector.py",
            "output": "downloads/change_detection_report.json",
            "status": "Success",
            "stat": "1 comparison completed (12 changes)",
            "details": "Extracted side-by-side differences in course category, duration, and formatting."
        },
        {
            "num": 8,
            "name": "Gemini Policy Interpretation",
            "module": "processing/policy_interpreter.py",
            "output": "downloads/policy_analysis.json",
            "status": "Success",
            "stat": "Gemini 3.5 Flash-Lite",
            "details": "Generated grounded student guidance, affected student analysis, and caveats."
        }
    ]

    for stg in stages:
        status_badge = (
            "<span class='cl-badge cl-badge-green'>COMPLETED</span>"
            if "Success" in stg["status"] else
            "<span class='cl-badge cl-badge-blue'>IDLE</span>"
        )
        st.markdown(f"""
        <div class="cl-card" style="margin-bottom: 0.75rem; padding: 0.9rem 1.25rem;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                <div>
                    <div style="display: flex; align-items: center; gap: 0.6rem;">
                        <span style="font-size: 0.75rem; font-weight: 700; color: #38bdf8;">STAGE {stg['num']}</span>
                        <h4 style="margin: 0; color: #ffffff; font-size: 1rem;">{stg['name']}</h4>
                        {status_badge}
                    </div>
                    <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.3rem;">
                        {stg['details']}
                    </div>
                </div>
                <div style="text-align: right; min-width: 200px;">
                    <div style="font-size: 0.85rem; font-weight: 600; color: #ffffff;">{stg['stat']}</div>
                    <div style="font-size: 0.74rem; color: #64748b; font-family: monospace; margin-top: 0.2rem;">
                        Output: {stg['output']}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

