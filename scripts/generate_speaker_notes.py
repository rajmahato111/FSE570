#!/usr/bin/env python3
"""
Generate docs/speaker_notes.docx — slide-by-slide speaker script for the
osint-swarm-architecture.pptx presentation.

Speaker assignment (6-minute target, demo excluded):
  Taljinder Singh  — Slides 1–3   (~1 min 30 sec)
  Arnab Mitra      — Slides 4–6   (~1 min 30 sec)
  Raj Kumar Mahto  — Slides 7–9   (~1 min 30 sec)
  Aditya Pokharna  — Slides 10–13 (~1 min 30 sec)
  Jacob Kuriakose  — Slide 14 + Demo  [PLACEHOLDER]

Usage:
    python scripts/generate_speaker_notes.py
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

OUT_PATH = Path(__file__).resolve().parents[1] / "docs" / "speaker_notes.docx"

# ---------------------------------------------------------------------------
# Script content
# ---------------------------------------------------------------------------

SLIDES = [
    # (slide_number, title, speaker, approx_time, script)
    (
        1,
        "Title Slide",
        "Taljinder Singh",
        "~20 sec",
        (
            "Good [morning / afternoon], everyone. I'm Taljinder Singh, and on behalf of our team "
            "— welcome to our FSE 570 capstone presentation. Today we're presenting the Autonomous "
            "OSINT Investigation Swarm: a multi-agent AI system that turns a plain-English question "
            "into a fully cited, audit-ready financial misconduct investigation — in under three seconds."
        ),
    ),
    (
        2,
        "The Problem",
        "Taljinder Singh",
        "~40 sec",
        (
            "Let me start with the problem we set out to solve. Imagine you're a compliance analyst "
            "and your manager asks: is Tesla tied to money laundering? You would open five browser "
            "tabs — SEC EDGAR, the OFAC sanctions list, court dockets, news archives — read hundreds "
            "of filings, cross-reference everything, and write it up. That takes roughly two and a half "
            "hours. Per investigation. Our system does the same thing in 2.7 seconds — a 3,100-times "
            "speedup. That is not a rough estimate — we benchmarked every step against a manual baseline."
        ),
    ),
    (
        3,
        "What It Delivers",
        "Taljinder Singh",
        "~30 sec",
        (
            "Here is what that looks like in concrete numbers. One plain-English query pulls from four "
            "public sources — SEC, OFAC, CourtListener, and GDELT news. For Tesla, that produces 1,125 "
            "individual evidence rows, 98 percent of which carry a direct citation link you can click and "
            "verify. The pipeline runs entirely cache-first — no API calls at runtime — so every "
            "investigation replays instantly from disk."
        ),
    ),
    (
        4,
        "System Architecture",
        "Arnab Mitra",
        "~35 sec",
        (
            "I'm Arnab — I built the core backend: the orchestrator, the three specialist agents, the "
            "MCP data layer, reflexion, the output layer, and the knowledge graph. The system runs in "
            "seven-and-a-half layers. At the base is the core library — raw connectors to each data "
            "source. Above that, the MCP layer handles caching and confidence processing. The Lead Agent "
            "resolves the entity and uses an LLM to plan tasks. Three specialist agents execute those "
            "tasks. The Reflexion Layer cross-checks findings and surfaces gaps. The Output Layer "
            "assembles the report and audit trail. And finally, Llama 3.1 writes the analyst narrative."
        ),
    ),
    (
        5,
        "Architecture Diagram",
        "Arnab Mitra",
        "~25 sec",
        (
            "Here is that flow visually. A query enters the Lead Agent, which resolves the entity and "
            "builds a task queue. The three specialists — Corporate, Legal, and Social Graph — each hit "
            "different data sources in parallel. Their findings pool into the Evidence store, pass through "
            "Reflexion and the Knowledge Graph, then into the Output Layer. The LLM writes the final "
            "narrative at the very end, after all evidence is locked."
        ),
    ),
    (
        6,
        "LLM Integration",
        "Arnab Mitra",
        "~30 sec",
        (
            "We use a single model — Llama 3.1-8b-instant via Groq — for five distinct policies. "
            "The Planner decomposes the query into three to five bounded subtasks. The Action Policy "
            "tells each specialist which tool to call next. The Stop Policy decides when we have enough "
            "evidence. The Reflexion Ranker prioritizes follow-up actions after detecting gaps or "
            "conflicts. And the Final Narrative produces the structured analyst report. Every single "
            "LLM call uses strict JSON mode with retry-with-repair — if the model returns malformed "
            "output, we fix and retry rather than failing silently."
        ),
    ),
    (
        7,
        "Data Sources",
        "Raj Kumar Mahto",
        "~30 sec",
        (
            "I'm Raj — I owned the task planner and shared context management across the agent swarm. "
            "Let me walk through the data layer Taljinder built. We pull from four fully public sources. "
            "SEC EDGAR gives us up to 500 filings per entity — 10-Ks, 8-Ks, Form 4s, proxy statements. "
            "The OFAC SDN list covers over 18,000 sanctioned entities with no API key required. "
            "CourtListener gives us up to 20 federal dockets. GDELT gives us up to 100 English-language "
            "adverse media articles. All of this is cached after the first pull — investigations at "
            "runtime hit zero network endpoints."
        ),
    ),
    (
        8,
        "Specialist Agents",
        "Raj Kumar Mahto",
        "~30 sec",
        (
            "The three specialist agents each own a slice of those sources. The Corporate Agent handles "
            "SEC filings and classifies each by form type — an 8-K gets a confidence of 0.95, a Form 4 "
            "gets 0.75. The Legal Agent fuzzy-matches against the OFAC SDN list and queries CourtListener "
            "for federal dockets. The Social Graph Agent pulls GDELT articles, filters for English, and "
            "scores each by relevance — does the title mention both the entity name and a risk keyword? "
            "All three agents share the same interface: receive a task, return a list of Evidence objects. "
            "The LLM Action Policy decides which tool each agent calls at each step."
        ),
    ),
    (
        9,
        "Runtime Pipeline",
        "Raj Kumar Mahto",
        "~30 sec",
        (
            "Putting it all together: entity resolution takes 0.1 seconds — 'Tesla' maps to CIK "
            "0001318605. LLM planning takes 0.2 seconds. The three agents run and gather 1,125 evidence "
            "rows in 1.2 seconds — that is the bulk of the work. Reflexion and LLM ranking take 0.6 "
            "seconds — surfacing 88 cross-check conflicts. Output generation and the Llama narrative "
            "take the final 0.6 seconds. Total: 2.7 seconds, overall confidence 0.81."
        ),
    ),
    (
        10,
        "Evaluation — Per-Entity Metrics",
        "Aditya Pokharna",
        "~25 sec",
        (
            "I'm Aditya — I built the Flask UI. Let me walk through our evaluation. Across all five "
            "entities — Tesla, Ford, Boeing, Alphabet, JPMorgan — we average 1,010 findings per "
            "investigation, 2.67 seconds end-to-end, 97.7 percent citation rate, and full four-of-four "
            "source coverage every time. Tesla leads at 1,125 findings. Ford comes in lower at 598, "
            "largely because GDELT news coverage for automotive companies is sparser than for tech. "
            "Every entity hits full source coverage — no investigation returns a partial result."
        ),
    ),
    (
        11,
        "Speedup, Confidence & Test Coverage",
        "Aditya Pokharna",
        "~25 sec",
        (
            "The 3,100-times speedup figure breaks down by task. SEC review alone is 1,800 times faster. "
            "Adverse media scanning is 2,700 times faster. Our confidence scoring is tiered by source "
            "reliability — an SEC 8-K starts at 0.95, OFAC at 0.90, CourtListener at 0.85, and GDELT "
            "low-relevance articles at 0.30. We back the entire system with 219 unit tests spread across "
            "all eight layers — from raw connectors up through the LLM narrative module."
        ),
    ),
    (
        12,
        "Evaluation Framework",
        "Aditya Pokharna",
        "~20 sec",
        (
            "We evaluated against five formal criteria. Correctness and depth: 97 to 98 percent citation "
            "rate, 598 to 1,125 findings per entity. Cross-agent verification: Reflexion runs on all "
            "three agents. System generality: five entities across three industries, and the entity "
            "resolver handles any publicly traded US company on the fly. Code quality: 219 tests, full "
            "deployment runbook, live on Render. Speed: 3,100 times faster than manual. All five met."
        ),
    ),
    (
        13,
        "Design Decisions",
        "Aditya Pokharna",
        "~30 sec",
        (
            "Six decisions shaped the architecture. First, LLM drives orchestration but evidence stays "
            "source-grounded — that is how we hit 97 to 98 percent citation rather than hallucinating "
            "findings. Second, everything is cache-first, so there are zero runtime API dependencies. "
            "Third, Entity and Evidence are frozen dataclasses — agents literally cannot mutate each "
            "other's findings. Fourth, missing data is explicit: confidence zero, cache_missing flag "
            "set — gaps surface in the UI rather than disappearing silently. Fifth, every LLM call "
            "validates against a JSON schema with retry-on-failure. Sixth, the system deploys to "
            "Render.com with a single Procfile and no external dependencies at runtime."
        ),
    ),
    (
        14,
        "The Team",
        "Jacob Kuriakose",
        "~20 sec + demo",
        (
            "[ PLACEHOLDER — Jacob ]\n\n"
            "Suggested content:\n"
            "  • Briefly introduce each team member and their ownership area "
            "(~10 sec — the slide does this visually).\n"
            "  • Transition line: 'Let me show you what this looks like in practice — "
            "I'll run a live query now.'\n\n"
            "Demo walkthrough (keep to ~2–3 min):\n"
            "  1. Open https://osint-investigation-swarm.onrender.com\n"
            "  2. Type: Investigate Tesla for money laundering → Submit\n"
            "  3. Overview tab — point to LLM narrative and key metrics\n"
            "  4. Knowledge Graph tab — highlight interactive vis-network canvas\n"
            "  5. Evidence tab — scroll to show citation links\n"
            "  6. Close: 'Questions?'"
        ),
    ),
]

# ---------------------------------------------------------------------------
# Speaker colour map  (light fill for section headers)
# ---------------------------------------------------------------------------

SPEAKER_COLORS = {
    "Taljinder Singh": RGBColor(0x1F, 0x49, 0x7D),   # dark blue
    "Arnab Mitra":     RGBColor(0x37, 0x5A, 0x2F),   # dark green
    "Raj Kumar Mahto": RGBColor(0x7B, 0x2C, 0x2C),   # dark red
    "Aditya Pokharna": RGBColor(0x4A, 0x2C, 0x6E),   # dark purple
    "Jacob Kuriakose": RGBColor(0x8B, 0x55, 0x1A),   # dark orange
}


def add_speaker_heading(doc: Document, speaker: str, color: RGBColor) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"  {speaker}  ")
    run.bold = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), "%02X%02X%02X" % (color[0], color[1], color[2]))
    pPr.append(shd)


def build_doc() -> None:
    doc = Document()

    # Page margins
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # --- Title ---
    title = doc.add_heading("Speaker Script", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].font.size = Pt(20)

    sub = doc.add_paragraph("Autonomous OSINT Investigation Swarm  ·  FSE 570 Capstone  ·  Spring 2026")
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.runs[0].font.size = Pt(11)
    sub.runs[0].font.color.rgb = RGBColor(0x60, 0x60, 0x60)

    timing = doc.add_paragraph("Target runtime: 6 minutes (slides 1–13)  +  demo (Jacob, no fixed time)")
    timing.alignment = WD_ALIGN_PARAGRAPH.CENTER
    timing.runs[0].font.size = Pt(10)
    timing.runs[0].italic = True

    doc.add_paragraph()

    # --- Speaker overview table ---
    doc.add_heading("Speaker Overview", level=2)
    table = doc.add_table(rows=1, cols=4)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, text in enumerate(["Speaker", "Slides", "Content", "Time"]):
        hdr[i].text = text
        hdr[i].paragraphs[0].runs[0].bold = True

    overview = [
        ("Taljinder Singh",  "1 – 3",  "Introduction, Problem, Deliverables",        "~1 min 30 sec"),
        ("Arnab Mitra",      "4 – 6",  "Architecture, Diagram, LLM Integration",      "~1 min 30 sec"),
        ("Raj Kumar Mahto",  "7 – 9",  "Data Sources, Specialist Agents, Pipeline",   "~1 min 30 sec"),
        ("Aditya Pokharna",  "10 – 13","Evaluation (×3), Design Decisions",           "~1 min 30 sec"),
        ("Jacob Kuriakose",  "14 + Demo","Team intro + live demo",                    "[PLACEHOLDER]"),
    ]
    for row_data in overview:
        row = table.add_row().cells
        for i, val in enumerate(row_data):
            row[i].text = val

    doc.add_paragraph()

    # --- Per-slide scripts ---
    doc.add_heading("Slide-by-Slide Script", level=2)

    current_speaker = None
    for slide_num, title_text, speaker, timing_str, script in SLIDES:
        color = SPEAKER_COLORS[speaker]

        # Speaker section break when speaker changes
        if speaker != current_speaker:
            doc.add_paragraph()
            add_speaker_heading(doc, speaker, color)
            current_speaker = speaker

        # Slide header
        slide_heading = doc.add_heading("", level=3)
        slide_heading.clear()
        run_num = slide_heading.add_run(f"Slide {slide_num}  —  ")
        run_num.font.color.rgb = color
        run_title = slide_heading.add_run(title_text)
        run_title.font.color.rgb = color
        run_time = slide_heading.add_run(f"  [{timing_str}]")
        run_time.font.size = Pt(9)
        run_time.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
        run_time.bold = False

        # Script body
        p = doc.add_paragraph(script)
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_after = Pt(4)
        for run in p.runs:
            run.font.size = Pt(11)

        doc.add_paragraph()

    # --- Notes ---
    doc.add_heading("Delivery Notes", level=2)
    notes = [
        "Pace: aim for ~150 words per minute for a clear, deliberate delivery.",
        "Transitions: each speaker should end their last slide with a one-sentence hand-off "
        "(e.g. 'I'll hand it over to Arnab to walk through the architecture.').",
        "Slide 14 / Demo: Jacob has a placeholder — fill in the exact demo steps and team "
        "intro wording before the presentation.",
        "The 6-minute target covers slides 1–13 only. The demo is additional time.",
        "Q&A: plan for ~2 minutes after the demo.",
    ]
    for note in notes:
        p = doc.add_paragraph(note, style="List Bullet")
        p.runs[0].font.size = Pt(10)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT_PATH)
    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    build_doc()
