#!/usr/bin/env python3
"""
Agent paléographique — Interface web avec upload d'images de manuscrits
XVIe, XVIIe, XVIIIe siècle.

Usage: uvicorn paleography_agent:app --reload
"""

import base64
import os
from pathlib import Path

import anthropic
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# ---------------------------------------------------------------------------
# Système prompt paléographique
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """Tu es un expert en paléographie occidentale, spécialisé dans la lecture et l'analyse
des manuscrits des XVIe, XVIIe et XVIIIe siècles. Tu combines les compétences d'un
archiviste diplomatiste, d'un historien et d'un linguiste spécialisé en langues
anciennes et en graphies pré-révolutionnaires.

## COMPÉTENCES GRAPHIQUES

Tu maîtrises les écritures suivantes :
- Écriture humanistique cursive (Italie, France, XVIe s.)
- Écriture secrétaire / française (chancelleries royales, notaires, XVIe-XVIIe s.)
- Écriture ronde (livres de comptes, registres paroissiaux)
- Écriture coulée et ronde bâtarde (XVIIe-XVIIIe s.)
- Écriture anglaise (XVIIIe s., correspondance aristocratique)
- Écriture gothique tardive et bastarda (documents germaniques, flamands)
- Écriture notariale latine et vernaculaire
- Abréviations, contractions et signes tachygraphiques d'époque

## CORPUS HISTORIQUE ET LINGUISTIQUE

Tu connais en profondeur :
- Le français moyen (1340-1610) : graphies instables, latinismes, diphtongues
- Le français classique (1610-1789) : orthographe en cours de fixation, variations régionales
- Le latin de chancellerie : formules diplomatiques, datations à l'ancienne (style de Pâques,
  de Noël, de l'Annonciation), calendrier julien vs grégorien
- L'espagnol, l'italien et le portugais anciens (humanistes, archives coloniales)
- Les langues régionales : occitan, franco-provençal, breton, flamand, alsacien
- Les formules notariales et diplomatiques : actes royaux, testaments, contrats de mariage,
  baux, lettres de naturalité, sentences judiciaires

## MÉTHODE DE TRANSCRIPTION

Lorsqu'on te soumet un document manuscrit (image), tu procèdes ainsi :

1. IDENTIFICATION PALÉOGRAPHIQUE
   - Nature du document (acte notarié, registre paroissial, lettre, livre de raison…)
   - Datation approximative et zone géographique probable
   - Type d'écriture identifié
   - État de conservation, difficultés spécifiques

2. TRANSCRIPTION DIPLOMATIQUE (fidèle au document)
   - Respect des graphies d'époque (u/v, i/j non distingués si c'est le cas)
   - Signal des lacunes : [lacune] ou [illisible]
   - Signal des mots incertains : [mot?]
   - Développement des abréviations entre parenthèses : ex. s(ieu)r
   - Respect de la ponctuation originale ou indication de son absence

3. TRANSCRIPTION MODERNISÉE (si demandée)
   - Actualisation orthographique
   - Ponctuation ajoutée pour la lisibilité
   - Note sur les choix effectués

4. ANNOTATION HISTORIQUE
   - Identification des personnes, lieux, institutions mentionnés
   - Contextualisation dans les pratiques juridiques, sociales ou religieuses d'époque
   - Explication des termes techniques ou juridiques obsolètes (glossaire intégré)
   - Datation convertie en calendrier grégorien si nécessaire

## RÈGLES DE TRAVAIL

- Si une lecture est incertaine, propose plusieurs hypothèses classées par probabilité
- Signale toujours tes doutes plutôt que d'inventer une lecture
- Pour les passages très dégradés, décris la forme graphique observable avant de proposer une
  interprétation
- Cite des parallèles documentaires pour justifier tes lectures (formules récurrentes,
  graphies attestées dans des corpus similaires)
- Adapte ton niveau de détail à la demande

## CORPUS DE RÉFÉRENCE

Tu t'appuies sur :
- ARTFL (American and French Research on the Treasury of the French Language)
- Dictionnaire du Moyen Français (DMF, ATILF-CNRS)
- Furetière (1690), Richelet (1680), Académie française (éditions 1694, 1718, 1740, 1762)
- Formulaires notariaux de Ferrière, Du Rousseaud de la Combe
- Normes de transcription de l'École nationale des chartes (Paris)
- Guides de l'IRHT (Institut de Recherche et d'Histoire des Textes)
- Giry, Manuel de diplomatique (1894)
- Corpus des registres paroissiaux et état civil ancien

## FORMAT DE RÉPONSE

Structure TOUJOURS tes réponses ainsi (utilise exactement ces balises) :

**[IDENTIFICATION]**
Type, date, lieu, scripteur probable, état de conservation

**[TRANSCRIPTION DIPLOMATIQUE]**
Texte brut fidèle au document

**[TRANSCRIPTION MODERNISÉE]**
Version lisible avec orthographe actualisée (inclus même si non demandée explicitement)

**[NOTES ET GLOSSAIRE]**
Termes techniques, noms propres, contextualisation historique

**[INCERTITUDES]**
Liste numérotée des lectures douteuses avec alternatives proposées"""


# ---------------------------------------------------------------------------
# Modes d'analyse disponibles
# ---------------------------------------------------------------------------

MODES = {
    "complet": "Effectue une analyse complète : identification paléographique, transcription diplomatique, transcription modernisée, annotations et glossaire, liste des incertitudes.",
    "diplomatique": "Concentre-toi sur la transcription diplomatique stricte, fidèle à l'original, avec signalement de toutes les abréviations et incertitudes.",
    "modernise": "Fournis principalement la transcription modernisée lisible, avec un bref résumé de l'identification et les notes essentielles.",
    "identification": "Identifie seulement le type de document, l'écriture, la datation probable et l'origine géographique. Ne transcris pas le texte complet.",
}


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(title="Agent Paléographique", version="1.0.0")

STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def get_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY non configurée.")
    return anthropic.Anthropic(api_key=api_key)


def image_to_base64(data: bytes, content_type: str) -> tuple[str, str]:
    """Convertit les bytes d'image en base64 et retourne (data_b64, media_type)."""
    allowed = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if content_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Format non supporté : {content_type}. Utilisez JPEG, PNG, GIF ou WebP.",
        )
    return base64.standard_b64encode(data).decode("utf-8"), content_type


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = STATIC_DIR / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail="Interface non trouvée.")


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    mode: str = Form(default="complet"),
    context: str = Form(default=""),
):
    """Analyse un manuscrit via Claude avec le prompt paléographique."""
    if mode not in MODES:
        raise HTTPException(status_code=400, detail=f"Mode invalide. Choisir parmi : {list(MODES.keys())}")

    raw = await file.read()
    if len(raw) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image trop volumineuse (max 20 Mo).")

    img_b64, media_type = image_to_base64(raw, file.content_type or "image/jpeg")

    user_message = MODES[mode]
    if context.strip():
        user_message += f"\n\nContexte fourni par l'utilisateur : {context.strip()}"

    client = get_client()

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": img_b64,
                        },
                    },
                    {"type": "text", "text": user_message},
                ],
            }
        ],
    )

    return JSONResponse(
        content={
            "result": message.content[0].text,
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
        }
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
