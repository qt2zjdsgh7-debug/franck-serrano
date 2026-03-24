#!/usr/bin/env python3
"""
Génère un PDF récapitulatif du projet avec reportlab.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Preformatted,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import date

OUTPUT = "recap_projet.pdf"

# ── Couleurs ──────────────────────────────────────────────────────────────
DARK   = colors.HexColor("#1a1a1a")
BLUE   = colors.HexColor("#1c4fa0")
LGRAY  = colors.HexColor("#f2f2f2")
MGRAY  = colors.HexColor("#c8c8c8")
WHITE  = colors.white
ACCENT = colors.HexColor("#3b6fd4")

# ── Styles ────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

S = {
    "title": ParagraphStyle("title", fontSize=24, fontName="Helvetica-Bold",
                             textColor=DARK, alignment=TA_CENTER, spaceAfter=6),
    "subtitle_page": ParagraphStyle("subtitle_page", fontSize=13, fontName="Helvetica",
                                    textColor=colors.HexColor("#555555"), alignment=TA_CENTER, spaceAfter=4),
    "date": ParagraphStyle("date", fontSize=10, fontName="Helvetica-Oblique",
                            textColor=colors.HexColor("#888888"), alignment=TA_CENTER, spaceAfter=20),
    "intro": ParagraphStyle("intro", fontSize=10, fontName="Helvetica",
                             textColor=colors.HexColor("#dddddd"), backColor=DARK,
                             leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=16,
                             leading=15, borderPad=8),
    "section": ParagraphStyle("section", fontSize=14, fontName="Helvetica-Bold",
                               textColor=DARK, backColor=LGRAY, spaceBefore=12, spaceAfter=8,
                               leftIndent=4, borderPad=4),
    "h2": ParagraphStyle("h2", fontSize=11, fontName="Helvetica-Bold",
                          textColor=BLUE, spaceBefore=10, spaceAfter=4),
    "body": ParagraphStyle("body", fontSize=10, fontName="Helvetica",
                            textColor=DARK, leading=15, spaceAfter=4),
    "bullet": ParagraphStyle("bullet", fontSize=10, fontName="Helvetica",
                              textColor=DARK, leading=14, leftIndent=12,
                              bulletIndent=4, spaceAfter=2),
    "code": ParagraphStyle("code", fontSize=8, fontName="Courier",
                            textColor=colors.HexColor("#1e1e1e"),
                            backColor=colors.HexColor("#f8f8f8"),
                            leftIndent=6, rightIndent=6, spaceBefore=4, spaceAfter=8,
                            leading=12, borderWidth=0.5, borderColor=MGRAY, borderPad=5),
}


def section(text):
    return [Paragraph(f"  {text}", S["section"]), Spacer(1, 2*mm)]

def h2(text):
    return [Paragraph(text, S["h2"])]

def body(text):
    return [Paragraph(text, S["body"])]

def bullets(items):
    return [Paragraph(f"• {i}", S["bullet"]) for i in items]

def code(text):
    return [Preformatted(text.strip(), S["code"])]

def spacer(h=4):
    return [Spacer(1, h*mm)]

def hr():
    return [HRFlowable(width="100%", thickness=0.5, color=MGRAY, spaceAfter=4)]

def table(headers, rows, col_widths):
    data = [headers] + rows
    t = Table(data, colWidths=[w*mm for w in col_widths])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), BLUE),
        ("TEXTCOLOR",   (0,0), (-1,0), WHITE),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, colors.HexColor("#eef2ff")]),
        ("TEXTCOLOR",   (0,1), (-1,-1), DARK),
        ("FONTNAME",    (0,1), (-1,-1), "Helvetica"),
        ("GRID",        (0,0), (-1,-1), 0.4, MGRAY),
        ("TOPPADDING",  (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0), (-1,-1), 3),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
    ]))
    return [t, Spacer(1, 4*mm)]


# ── Contenu ───────────────────────────────────────────────────────────────

story = []

# — Titre
story += [
    Spacer(1, 18*mm),
    Paragraph("Ingénierie de Prompts &amp; iCloud Drive", S["title"]),
    Paragraph("Récapitulatif du projet — Claude Opus/Sonnet/Haiku", S["subtitle_page"]),
    Paragraph(f"24 mars 2026", S["date"]),
]

intro_text = (
    "Ce projet regroupe (1) un guide complet d'ingénierie de prompts pour Claude, "
    "(2) un skill Claude Code prêt à l'emploi, et (3) deux scripts Python pour "
    "télécharger et uploader des documents vers iCloud Drive."
)
story.append(Paragraph(intro_text, S["intro"]))
story += spacer(8)

# ══════════════════════════════════════════════════════════════════════════
# SECTION 1 — Guide
# ══════════════════════════════════════════════════════════════════════════
story += section("1.  Guide — Ingénierie de Prompts pour Claude")
story += body(
    "Guide de référence basé sur la documentation officielle Anthropic (2026). "
    "Couvre tous les modèles : <b>Opus 4.6</b>, <b>Sonnet 4.6</b>, <b>Haiku 4.5</b>."
)
story += spacer(2)
story += h2("Chapitres")
story += bullets([
    "1. Fondamentaux — le principe du contrat, clarté avant longueur",
    "2. Structure d'un prompt expert — ordre des éléments, squelettes",
    "3. Techniques essentielles — XML tags, few-shot, permission d'incertitude",
    "4. Contrôle du format de sortie — JSON, prose, supprimer les préambules",
    "5. Raisonnement et Thinking — CoT, thinking adaptatif, auto-vérification",
    "6. Utilisation des outils — appels parallèles, comportement proactif/conservateur",
    "7. Systèmes agentiques — contexte long, actions réversibles, suivi d'état",
    "8. Techniques avancées — meta-prompting, prompt chaining, RAG, constitutional",
    "9. Anti-patterns à éviter",
    "10. Checklists et templates",
])
story += spacer(3)
story += h2("Règle d'or")
story += code("Montre ton prompt à un collègue sans contexte.\nS'il est confus, Claude le sera aussi.")

story += h2("Squelette universel")
story += code(
    "You are [RÔLE EN UNE PHRASE].\n\n"
    "<context>[Contexte, audience, enjeux]</context>\n\n"
    "<instructions>\n"
    "1. [Règle principale]\n"
    "2. [Contraintes]\n"
    "3. [Comportement incertitude]\n"
    "</instructions>\n\n"
    "<output_format>[JSON / Markdown / prose / longueur]</output_format>\n\n"
    "<examples>\n"
    "  <example>\n"
    "    <input>[Input type]</input>\n"
    "    <output>[Output idéal]</output>\n"
    "  </example>\n"
    "</examples>\n\n"
    "If you are not certain, say so. Do not guess.\n"
    "Before finalizing, verify your response against the output format."
)

# ══════════════════════════════════════════════════════════════════════════
# SECTION 2 — Techniques
# ══════════════════════════════════════════════════════════════════════════
story.append(PageBreak())
story += section("2.  Techniques clés résumées")

story += h2("Anti-patterns à éviter")
story += table(
    ["Anti-pattern", "Conséquence", "Correction"],
    [
        ["Instructions vagues", "Comportement imprévisible", "Critères de succès précis"],
        ["Tâches multiples", "Attention fragmentée", "Chainer les appels API"],
        ["Instructions négatives", "Moins fiable", "Formuler positivement"],
        ["Documents après requête", "-30 % de performance", "Documents → requête"],
        ["Pas d'exemples", "Format aléatoire", "3–5 exemples <example>"],
        ["Pas de permission incertitude", "Hallucinations confiantes", "Clause d'incertitude"],
        ["Pas d'auto-vérification", "Erreurs non détectées", "Étape de vérification finale"],
    ],
    col_widths=[54, 54, 62],
)

story += h2("Paramètres API recommandés")
story += table(
    ["Cas d'usage", "Modèle", "Effort", "Thinking"],
    [
        ["Classification, extraction simple", "Haiku 4.5", "low", "disabled"],
        ["Rédaction, résumé, Q&A", "Sonnet 4.6", "medium", "disabled"],
        ["Code, analyse technique", "Sonnet 4.6", "medium", "adaptive"],
        ["Agent autonome multi-étapes", "Opus 4.6", "high", "adaptive"],
        ["Recherche longue, migration", "Opus 4.6", "max", "adaptive"],
    ],
    col_widths=[72, 36, 26, 36],
)

story += h2("Checklist avant déploiement")
story += bullets([
    "Critères de succès définis et mesurables",
    "Modèle optimal choisi (Haiku / Sonnet / Opus)",
    "Rôle défini en une phrase",
    "XML tags utilisés pour séparer les sections",
    "Documents placés avant la requête",
    "3–5 exemples few-shot si format critique",
    "Format de sortie précisément décrit",
    "Permission d'incertitude ajoutée",
    "Auto-vérification finale demandée",
    "Testé sur 5+ cas représentatifs (dont cas limites)",
    "Version trackée (git / système de versioning)",
])

# ══════════════════════════════════════════════════════════════════════════
# SECTION 3 — Scripts iCloud
# ══════════════════════════════════════════════════════════════════════════
story.append(PageBreak())
story += section("3.  Scripts Python — iCloud Drive")
story += body(
    "Deux scripts utilisent la bibliothèque <b>pyicloud</b> pour interagir avec iCloud Drive "
    "via l'API Apple. L'authentification 2FA est gérée automatiquement."
)
story += spacer(2)

story += h2("download_icloud.py — Téléchargement &amp; organisation")
story += body(
    "Télécharge tous les fichiers iCloud Drive localement et recrée la même structure "
    "de dossiers directement dans iCloud Drive."
)
story += code(
    "python download_icloud.py --username votre@apple.com\n"
    "python download_icloud.py --username votre@apple.com --by-year\n"
    "python download_icloud.py --username votre@apple.com --no-upload"
)
story += table(
    ["Option", "Description"],
    [
        ["--username / -u", "Identifiant Apple (obligatoire)"],
        ["--password / -p", "Mot de passe (demandé si absent)"],
        ["--output / -o", "Dossier local (défaut : ~/iCloud_Backup)"],
        ["--by-year", "Ajouter sous-dossier par année de modification"],
        ["--no-upload", "Mode local uniquement, sans upload vers iCloud Drive"],
        ["--verbose / -v", "Logs détaillés"],
    ],
    col_widths=[52, 118],
)

story += h2("upload_docs_icloud.py — Upload ciblé")
story += body(
    "Uploade uniquement les fichiers du dossier <b>documents/</b> (DOCX, HTML) vers un "
    "dossier configurable dans iCloud Drive."
)
story += code(
    "python upload_docs_icloud.py --username votre@apple.com\n"
    "python upload_docs_icloud.py --username votre@apple.com --folder \"Mes Prompts\""
)
story += table(
    ["Option", "Description"],
    [
        ["--username / -u", "Identifiant Apple (obligatoire)"],
        ["--password / -p", "Mot de passe (demandé si absent)"],
        ["--folder / -f", "Nom du dossier iCloud Drive (défaut : Prompts_Expert)"],
        ["--docs-dir", "Dossier source local (défaut : ./documents/)"],
    ],
    col_widths=[52, 118],
)

story += h2("Structure des dossiers dans iCloud Drive")
story += code(
    "Documents_Organisés/\n"
    "├── PDF/\n"
    "├── Texte/\n"
    "├── Tableurs/\n"
    "├── Présentations/\n"
    "├── Images/\n"
    "├── Vidéos/\n"
    "├── Audio/\n"
    "├── Archives/\n"
    "├── Code/\n"
    "└── Autres/"
)

story += h2("Installation")
story += code("pip install -r requirements.txt")
story += body("Dépendances : pyicloud >= 1.0.0, click >= 8.0.0, tqdm >= 4.60.0")

# ══════════════════════════════════════════════════════════════════════════
# SECTION 4 — Fichiers
# ══════════════════════════════════════════════════════════════════════════
story.append(PageBreak())
story += section("4.  Fichiers du projet")
story += table(
    ["Fichier", "Type", "Description"],
    [
        ["expert-prompt-guide.md", "Markdown", "Guide complet d'ingénierie de prompts"],
        ["documents/expert-prompt-guide.docx", "Word", "Version Word du guide"],
        ["documents/expert-prompt-guide.html", "HTML", "Version HTML du guide"],
        ["documents/expert-prompt-skill.docx", "Word", "Skill Claude Code (Word)"],
        ["documents/expert-prompt-skill.html", "HTML", "Skill Claude Code (HTML)"],
        ["download_icloud.py", "Python", "Téléchargement & organisation iCloud Drive"],
        ["upload_docs_icloud.py", "Python", "Upload ciblé vers iCloud Drive"],
        ["convert_to_doc.py", "Python", "Conversion Markdown → DOCX/HTML"],
        ["make_docx.py", "Python", "Génération DOCX avancée"],
        ["make_pdf_recap.py", "Python", "Génération de ce PDF récapitulatif"],
        ["requirements.txt", "Config", "Dépendances Python"],
        ["README.md", "Markdown", "Documentation principale du projet"],
    ],
    col_widths=[68, 20, 82],
)

# ── Build ─────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=18*mm, rightMargin=18*mm,
    topMargin=20*mm, bottomMargin=18*mm,
    title="Récapitulatif Projet — Ingénierie de Prompts & iCloud Drive",
    author="Claude Code",
)
doc.build(story)
print(f"PDF généré : {OUTPUT}")
