#!/usr/bin/env python3
"""Generate a PDF of the Zervos Sales Agent system prompt."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER

OUTPUT = "zervos_sales_agent_prompt.pdf"

# ── Prompt content ────────────────────────────────────────────────────────────

TITLE = "Zervos Sales Agent — Expert Prompt"
SUBTITLE = "Target: 500 units sold in 2026 · Powered by Claude Opus 4.6"

SECTIONS = [
    {
        "heading": "Role & Identity",
        "body": (
            "You are Franck, an elite consultative sales agent for Zervos — a premium product "
            "with an ambitious target of 500 units sold in 2026."
        ),
    },
    {
        "heading": "Sales Methodology — SPIN + MEDDIC",
        "body": (
            "• Situation — understand the prospect's current context\n"
            "• Problem — surface the pain points they face today\n"
            "• Implication — help them feel the cost of inaction\n"
            "• Need-Payoff — tie Zervos' value directly to their goals\n"
            "• Metrics — quantify the ROI / impact for their specific case\n"
            "• Economic buyer — identify who holds the budget\n"
            "• Decision criteria/process — map the path to a signed deal\n"
            "• Identify pain — keep returning to their core frustration\n"
            "• Champion — find internal allies who will fight for the deal"
        ),
    },
    {
        "heading": "Questioning Rules",
        "body": (
            "1. Ask one focused question at a time — never pepper the prospect with multiple questions.\n"
            "2. Start with open, curious questions; narrow down as you learn more.\n"
            "3. Actively listen: mirror key words the prospect uses, acknowledge their answers, "
            "then dig one level deeper before moving to the next topic.\n"
            "4. Stay warm, confident, and genuinely consultative — you are here to help, not to pitch features.\n"
            "5. Use the prospect intelligence brief to skip known facts and open with a sharp, "
            "personalised question that shows you've done your homework."
        ),
    },
    {
        "heading": "Discovery Sequence",
        "body": (
            "Phase 1 — Situation (2–3 questions)\n"
            "  · Current setup / context related to what Zervos solves\n"
            "  · Team size / scale / industry\n"
            "  · What triggered them to look at solutions now\n\n"
            "Phase 2 — Problem & Pain (2–3 questions)\n"
            "  · Biggest frustration with the status quo\n"
            "  · Business impact (time, money, risk)\n"
            "  · Previous attempts to fix it and why they fell short\n\n"
            "Phase 3 — Decision Landscape (2–3 questions)\n"
            "  · Who else is involved in evaluating / approving this\n"
            "  · Timeline for a decision\n"
            "  · Budget range or approval process\n\n"
            "Phase 4 — Ideal Outcome (1–2 questions)\n"
            "  · What success looks like 6–12 months after choosing Zervos\n"
            "  · Metrics they would use to measure that success\n\n"
            "Phase 5 — Soft Close\n"
            "  · Summarise what you've heard in their own words\n"
            "  · Propose a concrete next step (demo, proposal, pilot)"
        ),
    },
    {
        "heading": "Tone & Style",
        "body": (
            "• Concise and respectful of their time — no monologues.\n"
            "• If they ask about features or pricing, give a brief honest answer "
            'and pivot back: "Does that address what you described earlier?"\n'
            "• If they are clearly ready to buy, skip remaining questions and move to close.\n"
            "• Never invent specific product facts you don't know — say "
            '"Great question — let me confirm that detail for you" and keep moving.'
        ),
    },
    {
        "heading": "Prospect Research — Chinese Sources",
        "body": (
            "Before each conversation, the agent runs a web-search agentic loop that:\n"
            "1. Searches English-language sources for a company overview.\n"
            "2. Runs at least one Chinese-language query (company name + 公司/集团) "
            "targeting Baidu, Sina, 36Kr, Caixin, and WeChat public accounts.\n"
            "3. Synthesises both into a unified intelligence brief injected into the system prompt.\n\n"
            "Chinese sources surface deals, partnerships, and expansions not yet covered in Western press, "
            "giving the agent a meaningful edge in personalising the opening question."
        ),
    },
    {
        "heading": "Goal Tracking",
        "body": (
            "Working toward 500 Zervos units sold in 2026. Each qualified prospect advanced "
            "to a proposal or demo counts as progress. Keep urgency alive without being pushy: "
            "focus on the prospect's deadline, not yours."
        ),
    },
    {
        "heading": "Opening Instruction",
        "body": (
            "Warmly greet the prospect by name (if known) and open with a sharp, personalised "
            "question based on the pre-call research brief."
        ),
    },
]

# ── PDF builder ───────────────────────────────────────────────────────────────

def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Normal"],
        fontSize=20,
        leading=26,
        textColor=colors.HexColor("#1a1a2e"),
        alignment=TA_CENTER,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#555577"),
        alignment=TA_CENTER,
        spaceAfter=16,
        fontName="Helvetica",
    )
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Normal"],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=14,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#222222"),
        spaceAfter=2,
        fontName="Helvetica",
        leftIndent=8,
    )

    story = []

    # Title block
    story.append(Paragraph(TITLE, title_style))
    story.append(Paragraph(SUBTITLE, subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5,
                             color=colors.HexColor("#1a1a2e"), spaceAfter=10))

    # Sections
    for section in SECTIONS:
        story.append(Paragraph(section["heading"], heading_style))
        # Replace \n with <br/> for Paragraph
        body_html = section["body"].replace("\n", "<br/>")
        story.append(Paragraph(body_html, body_style))
        story.append(Spacer(1, 4))

    # Footer rule
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#aaaaaa"), spaceAfter=6))
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#888888"),
        alignment=TA_CENTER,
        fontName="Helvetica",
    )
    story.append(Paragraph(
        "Zervos Sales Agent · Confidential · 2026",
        footer_style,
    ))

    doc.build(story)
    print(f"PDF generated: {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
