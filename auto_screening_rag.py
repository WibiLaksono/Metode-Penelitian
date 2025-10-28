#!/usr/bin/env python3
"""
auto_screening_rag_enhanced.py
Automasi Screening: Crossref + Unpaywall.
Versi lebih informatif, dengan ringkasan, filter full-text, dan statistik per tahap.
"""

import os
import json
import requests
import bibtexparser
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from pdfminer.high_level import extract_text
from sentence_transformers import SentenceTransformer, util
import matplotlib.pyplot as plt
import textwrap

# ---------- CONFIG ----------
CONFIG = {
    "mailto": "wibilaksonowijaya@mail.ugm.ac.id",
    "unpaywall_email": "wibilaksonowijaya@mail.ugm.ac.id",
    "query": '"retrieval augmented generation" OR "document chunking" OR "text segmentation"',
    "filters": {
        "from_pub_date": 2018,
        "until_pub_date": 2025,
        "has_full_text": True,
    },
    "max_results": 1000,   # ambil lebih banyak
    "output_dir": "screening_output",
    "semantic_model": "all-MiniLM-L6-v2",
    "similarity_threshold": 0.55,
    "rule_includes": ["document chunking", "text segmentation", "semantic chunk", "chunking"],
    "rule_excludes": ["editorial", "blog", "preprint", "arXiv"],
    "download_pdfs": True,
}
# ----------------------------

OUT = Path(CONFIG["output_dir"])
OUT.mkdir(parents=True, exist_ok=True)
PDF_DIR = OUT / "pdfs"
PDF_DIR.mkdir(exist_ok=True)

CROSSREF_API = "https://api.crossref.org/works"
UNPAYWALL_API = "https://api.unpaywall.org/v2/"
HEADERS = {"User-Agent": f"AutoScreening/1.0 (mailto:{CONFIG['mailto']})"}

print("Loading semantic model...")
model = SentenceTransformer(CONFIG["semantic_model"])

# --- Step 1: Crossref Search ---
def crossref_search(query, max_results=200, from_year=None, until_year=None):
    print(f"🔍 Searching Crossref for query: {query}")
    rows = []
    per_page = 100
    cursor = "*"
    retrieved = 0

    while retrieved < max_results:
        params = {
            "query.bibliographic": query,
            "rows": min(per_page, max_results - retrieved),
            "mailto": CONFIG["mailto"],
            "cursor": cursor
        }
        filters = []
        if from_year:
            filters.append(f"from-pub-date:{from_year}")
        if until_year:
            filters.append(f"until-pub-date:{until_year}")
        if filters:
            params["filter"] = ",".join(filters)

        r = requests.get(CROSSREF_API, headers=HEADERS, params=params, timeout=40)
        r.raise_for_status()
        data = r.json()["message"]
        items = data.get("items", [])
        rows.extend(items)
        retrieved += len(items)
        cursor = data.get("next-cursor")
        if not cursor or len(items) == 0:
            break
        print(f"  → Retrieved {retrieved} so far...")
    print(f"✅ Total retrieved from Crossref: {len(rows)}")
    return rows

# --- Step 2: Unpaywall ---
def call_unpaywall(doi):
    url = UNPAYWALL_API + doi
    params = {"email": CONFIG["unpaywall_email"]}
    try:
        r = requests.get(url, params=params, timeout=30)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

def get_best_pdf_link(unpaywall_json):
    if not unpaywall_json:
        return None, None
    if unpaywall_json.get("best_oa_location"):
        loc = unpaywall_json["best_oa_location"]
        pdf = loc.get("url_for_pdf") or loc.get("url")
        source = loc.get("host_type", "unpaywall")
        return pdf, source
    for loc in unpaywall_json.get("oa_locations", []):
        pdf = loc.get("url_for_pdf") or loc.get("url")
        if pdf:
            return pdf, loc.get("host_type", "unpaywall")
    return None, None

# --- Helper: Extract Metadata ---
def brief_metadata_from_crossref(item):
    doi = item.get("DOI", "")
    title = " ".join(item.get("title", []))
    abstract = item.get("abstract", "") or ""
    authors = "; ".join(
        [" ".join(filter(None, [a.get("given", ""), a.get("family", "")])) for a in item.get("author", [])]
    )
    year = item.get("issued", {}).get("date-parts", [[None]])[0][0]
    journal = item.get("container-title", [""])[0]
    return {"doi": doi, "title": title, "abstract": abstract, "authors": authors, "year": year, "journal": journal}

# --- Step 3: Rule & Semantic Screening ---
def rule_based_screen(title, abstract):
    txt = (title + " " + abstract).lower()
    for ex in CONFIG["rule_excludes"]:
        if ex in txt:
            return False, f"Excluded (rule: {ex})"
    for inc in CONFIG["rule_includes"]:
        if inc in txt:
            return True, f"Included (rule: {inc})"
    return None, "No rule match"

def semantic_screen(title, abstract, rqs):
    combined = (title + " " + abstract).strip()
    if not combined:
        return 0.0, None, False
    emb_doc = model.encode(combined, convert_to_tensor=True)
    sims = [util.cos_sim(emb_doc, model.encode(rq, convert_to_tensor=True)).item() for rq in rqs]
    max_sim = max(sims)
    best_rq = rqs[sims.index(max_sim)]
    return max_sim, best_rq, max_sim >= CONFIG["similarity_threshold"]

# --- Helper: Extract Text ---
def extract_text_from_pdf(path):
    try:
        return extract_text(str(path))
    except:
        return ""

# --- Summary Generator ---
def summarize_text(text):
    text = text.replace("\n", " ")
    sentences = text.split(". ")
    summary = " ".join(sentences[:3])
    return textwrap.shorten(summary, width=350, placeholder="...")

# --- MAIN WORKFLOW ---
def main():
    RQS = [
        "How do different chunking strategies (fixed-size, semantic-based, sliding window, hierarchical) compare in performance?",
        "How does document chunking method affect retrieval accuracy, generation quality, and efficiency?",
    ]

    # Step 1: Search
    items = crossref_search(CONFIG["query"], max_results=CONFIG["max_results"],
                            from_year=CONFIG["filters"]["from_pub_date"],
                            until_year=CONFIG["filters"]["until_pub_date"])

    # Deduplication
    print("\n🧹 Removing duplicates...")
    seen, unique = set(), []
    for it in items:
        key = (it.get("DOI") or " ".join(it.get("title", []))).lower()
        if key not in seen:
            seen.add(key)
            unique.append(it)
    print(f"✅ {len(unique)} unique records (removed {len(items)-len(unique)} duplicates)")

    # Step 2: Screening
    screening_rows, extracted_rows = [], []
    print("\n📄 Checking open access + screening papers...\n")

    for rec in tqdm(unique, desc="Processing"):
        meta = brief_metadata_from_crossref(rec)
        doi = meta["doi"]
        if not doi:
            continue

        unp = call_unpaywall(doi)
        pdf_url, pdf_source = get_best_pdf_link(unp)
        is_oa = bool(unp and unp.get("is_oa", False))
        pdf_path, text_extracted = None, ""

        # Filter only OA with PDF link
        if not (is_oa and pdf_url):
            continue

        # Download + Extract
        fn = doi.replace("/", "_") + ".pdf"
        pdf_path = PDF_DIR / fn
        try:
            pdf_data = requests.get(pdf_url, timeout=25)
            if pdf_data.status_code == 200 and "pdf" in pdf_data.headers.get("content-type", "").lower():
                with open(pdf_path, "wb") as f:
                    f.write(pdf_data.content)
                text_extracted = extract_text_from_pdf(pdf_path)
        except:
            pass

        if not text_extracted.strip():
            continue  # skip if no full text

        # Rule + semantic screen
        rule_decision, rule_reason = rule_based_screen(meta["title"], meta["abstract"])
        sim_score, best_rq, sim_decision = semantic_screen(meta["title"], meta["abstract"], RQS)

        if rule_decision is True or sim_decision:
            final_decision = "Include"
        else:
            final_decision = "Exclude"

        if final_decision == "Include":
            snippet_method = summarize_text(text_extracted[:2500])
            snippet_findings = summarize_text(text_extracted[-2500:])
            summary = summarize_text(text_extracted)

            extracted_rows.append({
                "doi": doi,
                "title": meta["title"],
                "authors": meta["authors"],
                "year": meta["year"],
                "journal": meta["journal"],
                "method_snippet": snippet_method,
                "key_findings_snippet": snippet_findings,
                "summary": summary,
                "pdf_source": pdf_source,
                "pdf_path": str(pdf_path),
            })

        screening_rows.append({
            "doi": doi,
            "title": meta["title"],
            "year": meta["year"],
            "is_oa": is_oa,
            "pdf_source": pdf_source,
            "pdf_url": pdf_url,
            "decision": final_decision,
            "similarity_score": sim_score,
        })

    df_screen = pd.DataFrame(screening_rows)
    df_extract = pd.DataFrame(extracted_rows)

    print(f"\n📊 Screening completed:")
    print(f"  Total unique records     : {len(unique)}")
    print(f"  With full text available : {len(df_screen[df_screen['is_oa']])}")
    print(f"  Included after screening : {len(df_extract)}")

    df_screen.to_csv(OUT / "screening_log.csv", index=False)
    df_extract.to_csv(OUT / "extracted_data.csv", index=False)
    print(f"✅ Saved outputs to folder: {OUT.absolute()}")

if __name__ == "__main__":
    main()
