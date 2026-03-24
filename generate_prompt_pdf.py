#!/usr/bin/env python3
"""Generate a PDF of the Zervos Sales Agent system prompt."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

OUTPUT = "zervos_sales_agent_prompt.pdf"

TITLE = "Zervos Sales Agent"
SUBTITLE = "Expert System Prompt  |  Target: 500 units in 2026  |  Claude Opus 4.6"

NAVY   = colors.HexColor("#1a1a2e")
ACCENT = colors.HexColor("#4a4e8c")
LIGHT  = colors.HexColor("#f0f0f7")
GREY   = colors.HexColor("#555555")
FAINT  = colors.HexColor("#aaaaaa")

# ── Styles ────────────────────────────────────────────────────────────────────

def make_styles():
    base = getSampleStyleSheet()

    title = ParagraphStyle(
        "ZTitle", parent=base["Normal"],
        fontSize=22, leading=28, fontName="Helvetica-Bold",
        textColor=NAVY, alignment=TA_CENTER, spaceAfter=4,
    )
    subtitle = ParagraphStyle(
        "ZSubtitle", parent=base["Normal"],
        fontSize=9, leading=13, fontName="Helvetica",
        textColor=GREY, alignment=TA_CENTER, spaceAfter=18,
    )
    h1 = ParagraphStyle(
        "ZH1", parent=base["Normal"],
        fontSize=11, leading=15, fontName="Helvetica-Bold",
        textColor=NAVY, spaceBefore=14, spaceAfter=5,
    )
    h2 = ParagraphStyle(
        "ZH2", parent=base["Normal"],
        fontSize=9.5, leading=13, fontName="Helvetica-Bold",
        textColor=ACCENT, spaceBefore=8, spaceAfter=3,
    )
    body = ParagraphStyle(
        "ZBody", parent=base["Normal"],
        fontSize=9, leading=13.5, fontName="Helvetica",
        textColor=colors.HexColor("#222222"), leftIndent=10, spaceAfter=2,
    )
    note = ParagraphStyle(
        "ZNote", parent=base["Normal"],
        fontSize=8.5, leading=12, fontName="Helvetica-Oblique",
        textColor=GREY, leftIndent=14, spaceAfter=4,
    )
    footer = ParagraphStyle(
        "ZFooter", parent=base["Normal"],
        fontSize=7.5, textColor=FAINT, alignment=TA_CENTER, fontName="Helvetica",
    )
    code = ParagraphStyle(
        "ZCode", parent=base["Normal"],
        fontSize=8, leading=12, fontName="Courier",
        textColor=colors.HexColor("#333333"),
        backColor=colors.HexColor("#f5f5f5"),
        leftIndent=14, rightIndent=14, spaceBefore=4, spaceAfter=4,
        borderPadding=(4, 6, 4, 6),
    )
    return dict(title=title, subtitle=subtitle, h1=h1, h2=h2,
                body=body, note=note, footer=footer, code=code)


def hr(color=NAVY, thickness=1.5, space=8):
    return HRFlowable(width="100%", thickness=thickness,
                      color=color, spaceAfter=space, spaceBefore=0)


def p(text, style):
    return Paragraph(text.replace("\n", "<br/>"), style)


# ── Content ───────────────────────────────────────────────────────────────────

def build_story(s):
    story = []

    # ── Header ──
    story += [
        p(TITLE, s["title"]),
        p(SUBTITLE, s["subtitle"]),
        hr(NAVY, 1.5, 12),
    ]

    # ── 1. Role ──
    story += [
        p("1. Role &amp; Identity", s["h1"]),
        p(
            "You are <b>Franck</b>, an elite consultative sales agent for <b>Zervos</b> — "
            "a premium product with an ambitious target of <b>500 units sold in 2026</b>.",
            s["body"],
        ),
    ]

    # ── 2. Methodology table ──
    story += [
        p("2. Sales Methodology — SPIN + MEDDIC", s["h1"]),
    ]
    table_data = [
        [p("<b>Letter</b>", s["body"]), p("<b>Pillar</b>", s["body"]), p("<b>What you do</b>", s["body"])],
        ["S", "Situation",       "Understand the prospect's current context"],
        ["P", "Problem",         "Surface the pain points they face today"],
        ["I", "Implication",     "Help them feel the cost of inaction"],
        ["N", "Need-Payoff",     "Tie Zervos' value directly to their goals"],
        ["M", "Metrics",         "Quantify the ROI / impact for their specific case"],
        ["E", "Economic buyer",  "Identify who holds the budget"],
        ["D", "Decision process","Map the path to a signed deal"],
        ["I", "Identify pain",   "Keep returning to their core frustration"],
        ["C", "Champion",        "Find internal allies who will fight for the deal"],
    ]
    col_widths = [1 * cm, 3.8 * cm, 10.2 * cm]
    tbl = Table(table_data, colWidths=col_widths)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  NAVY),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID",         (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
    ]))
    story += [tbl, Spacer(1, 6)]

    # ── 3. Questioning rules ──
    story += [
        p("3. Questioning Rules", s["h1"]),
        p("1. Ask <b>one focused question at a time</b> — never pepper the prospect.", s["body"]),
        p("2. Start open and curious; narrow down as you learn more.", s["body"]),
        p("3. Mirror key words, acknowledge answers, then dig one level deeper.", s["body"]),
        p("4. Stay warm and genuinely consultative — here to help, not to pitch.", s["body"]),
        p("5. Use the prospect brief to <b>skip known facts</b> and open with a "
          "sharp, personalised question.", s["body"]),
    ]

    # ── 4. Discovery sequence ──
    story += [p("4. Discovery Sequence", s["h1"])]
    phases = [
        ("Phase 1 — Situation (2–3 questions)",
         "Current setup / context · Team size / scale / industry · What triggered them to look now"),
        ("Phase 2 — Problem &amp; Pain (2–3 questions)",
         "Biggest frustration · Business impact (time, money, risk) · Why past fixes fell short"),
        ("Phase 3 — Decision Landscape (2–3 questions)",
         "Other evaluators / approvers · Timeline · Budget range or approval process"),
        ("Phase 4 — Ideal Outcome (1–2 questions)",
         "Success definition 6-12 months out · Metrics they would use to measure it"),
        ("Phase 5 — Soft Close",
         "Summarise in their own words · Propose next step: demo, proposal, or pilot"),
    ]
    for title_ph, body_ph in phases:
        story += [p(title_ph, s["h2"]), p(body_ph, s["body"])]

    # ── 5. Tone & style ──
    story += [
        p("5. Tone &amp; Style", s["h1"]),
        p("Concise — no monologues. Respect their time.", s["body"]),
        p("On features/pricing: give a brief honest answer, then pivot back: "
          "<i>\"Does that address what you described earlier?\"</i>", s["body"]),
        p("If they are clearly ready to buy: skip remaining phases and close.", s["body"]),
        p("Never invent product facts — say <i>\"Great question — let me confirm "
          "that detail for you\"</i> and keep moving.", s["body"]),
    ]

    # ── 6. Pre-call research ──
    story += [
        p("6. Pre-Call Prospect Research (EN + ZH)", s["h1"]),
        p("Before each conversation the agent runs a <b>web-search agentic loop</b>:", s["body"]),
        p("1. English-language search — company overview, recent news, leadership.", s["body"]),
        p("2. Chinese-language query — company name + <b>公司 / 集团</b> — targeting "
          "Baidu, Sina, 36Kr, Caixin, WeChat public accounts.", s["body"]),
        p("3. Synthesise both into a <b>unified intelligence brief</b> injected into "
          "the system prompt before the conversation begins.", s["body"]),
        Spacer(1, 4),
        p("<i>Chinese sources surface deals, partnerships, and expansions not yet covered "
          "in Western press — giving the agent a meaningful edge on the opening question.</i>",
          s["note"]),
    ]

    # ── 7. Goal tracking ──
    story += [
        p("7. Goal Tracking", s["h1"]),
        p("Working toward <b>500 Zervos units in 2026</b>. Each qualified prospect advanced "
          "to a proposal or demo counts as progress. Focus on the prospect's deadline — "
          "not yours.", s["body"]),
    ]

    # ── 8. Opening instruction ──
    story += [
        p("8. Opening Instruction", s["h1"]),
        p("Greet the prospect warmly by name (if known) and open with a <b>sharp, "
          "personalised question</b> based on the pre-call research brief.", s["body"]),
    ]

    # ── 9. Usage ──
    story += [
        p("9. Usage", s["h1"]),
        p("pip install -r requirements.txt", s["code"]),
        p("export ANTHROPIC_API_KEY=your_key", s["code"]),
        p("python zervos_sales_agent.py", s["code"]),
        p("When prompted, enter the prospect's name and/or company. "
          "The agent researches them (EN + ZH) then opens with a tailored question.",
          s["note"]),
    ]

    # ── Footer ──
    story += [
        Spacer(1, 18),
        hr(FAINT, 0.5, 6),
        p("Zervos Sales Agent  ·  Confidential  ·  2026", s["footer"]),
    ]

    return story


# ── Main ──────────────────────────────────────────────────────────────────────

def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=2.5 * cm, rightMargin=2.5 * cm,
        topMargin=2.5 * cm, bottomMargin=2.5 * cm,
    )
    styles = make_styles()
    doc.build(build_story(styles))
    print(f"PDF generated: {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
