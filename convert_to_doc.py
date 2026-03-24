#!/usr/bin/env python3
"""Convert markdown files to styled HTML, then to DOCX via LibreOffice."""

import markdown
import subprocess
import sys
from pathlib import Path

CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.7;
    color: #1a1a2e;
    background: #ffffff;
    max-width: 900px;
    margin: 0 auto;
    padding: 40px 60px;
  }

  h1 {
    font-size: 26pt;
    font-weight: 700;
    color: #0f3460;
    border-bottom: 3px solid #0f3460;
    padding-bottom: 12px;
    margin-bottom: 24px;
    margin-top: 0;
  }

  h2 {
    font-size: 16pt;
    font-weight: 700;
    color: #16213e;
    border-left: 4px solid #e94560;
    padding-left: 14px;
    margin-top: 40px;
    margin-bottom: 16px;
  }

  h3 {
    font-size: 13pt;
    font-weight: 600;
    color: #0f3460;
    margin-top: 28px;
    margin-bottom: 10px;
  }

  h4 {
    font-size: 11pt;
    font-weight: 600;
    color: #533483;
    margin-top: 20px;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  p {
    margin-bottom: 12px;
    color: #2d2d44;
  }

  blockquote {
    background: #f0f4ff;
    border-left: 4px solid #0f3460;
    padding: 12px 18px;
    margin: 16px 0;
    border-radius: 0 6px 6px 0;
    font-style: italic;
    color: #3a3a5c;
  }

  blockquote strong {
    font-style: normal;
  }

  code {
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 9pt;
    background: #f5f5f5;
    color: #c7254e;
    padding: 2px 6px;
    border-radius: 3px;
  }

  pre {
    background: #1e1e2e;
    color: #cdd6f4;
    padding: 16px 20px;
    border-radius: 8px;
    margin: 16px 0;
    overflow-x: auto;
    line-height: 1.5;
  }

  pre code {
    background: none;
    color: #cdd6f4;
    padding: 0;
    font-size: 9pt;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 10pt;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    border-radius: 8px;
    overflow: hidden;
  }

  thead tr {
    background: #0f3460;
    color: #ffffff;
  }

  thead th {
    padding: 10px 16px;
    text-align: left;
    font-weight: 600;
  }

  tbody tr:nth-child(even) {
    background: #f7f9ff;
  }

  tbody tr:nth-child(odd) {
    background: #ffffff;
  }

  tbody td {
    padding: 9px 16px;
    border-bottom: 1px solid #e8eaf6;
    color: #2d2d44;
  }

  ul, ol {
    padding-left: 24px;
    margin-bottom: 12px;
    color: #2d2d44;
  }

  li {
    margin-bottom: 5px;
  }

  hr {
    border: none;
    border-top: 1px solid #e8eaf6;
    margin: 32px 0;
  }

  strong { color: #0f3460; }

  a { color: #e94560; text-decoration: none; }
  a:hover { text-decoration: underline; }

  .toc {
    background: #f7f9ff;
    border: 1px solid #dde4f5;
    border-radius: 8px;
    padding: 20px 28px;
    margin-bottom: 36px;
  }

  .toc p { font-weight: 700; color: #0f3460; margin-bottom: 10px; font-size: 12pt; }
  .toc ol { margin: 0; }
  .toc li { margin-bottom: 4px; }

  .cover {
    text-align: center;
    padding: 60px 0 40px 0;
    margin-bottom: 40px;
    border-bottom: 2px solid #e8eaf6;
  }

  .cover .subtitle {
    font-size: 13pt;
    color: #6b7280;
    margin-top: 10px;
  }

  .cover .badge {
    display: inline-block;
    background: #0f3460;
    color: white;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 9pt;
    margin-top: 16px;
    font-weight: 500;
  }
</style>
"""

MD_EXTENSIONS = [
    'markdown.extensions.tables',
    'markdown.extensions.fenced_code',
    'markdown.extensions.codehilite',
    'markdown.extensions.toc',
    'markdown.extensions.nl2br',
]

def md_to_html(md_path: Path, title: str) -> str:
    text = md_path.read_text(encoding='utf-8')
    body = markdown.markdown(text, extensions=MD_EXTENSIONS)
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  {CSS}
</head>
<body>
{body}
</body>
</html>"""

def to_docx(html_path: Path, output_path: Path):
    result = subprocess.run(
        [
            'libreoffice', '--headless', '--convert-to', 'docx',
            '--outdir', str(output_path.parent),
            str(html_path)
        ],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  STDERR: {result.stderr}", file=sys.stderr)
        raise RuntimeError(f"LibreOffice failed: {result.returncode}")
    # LibreOffice names the output after the input stem
    generated = output_path.parent / (html_path.stem + '.docx')
    if generated != output_path and generated.exists():
        generated.rename(output_path)

FILES = [
    {
        "md": Path("/home/user/franck-serrano/expert-prompt-guide.md"),
        "title": "Guide Expert — Ingénierie de Prompts pour Claude",
        "out_stem": "expert-prompt-guide",
    },
    {
        "md": Path("/home/user/franck-serrano/.claude/skills/expert-prompt/SKILL.md"),
        "title": "Skill — expert-prompt (Claude Code)",
        "out_stem": "expert-prompt-skill",
    },
]

out_dir = Path("/home/user/franck-serrano/documents")
out_dir.mkdir(exist_ok=True)

for f in FILES:
    print(f"Processing: {f['md'].name}")
    html_path = out_dir / (f['out_stem'] + '.html')
    docx_path = out_dir / (f['out_stem'] + '.docx')

    html = md_to_html(f['md'], f['title'])
    html_path.write_text(html, encoding='utf-8')
    print(f"  HTML → {html_path}")

    try:
        to_docx(html_path, docx_path)
        print(f"  DOCX → {docx_path}")
    except Exception as e:
        print(f"  DOCX conversion failed: {e}")

print("\nDone.")
