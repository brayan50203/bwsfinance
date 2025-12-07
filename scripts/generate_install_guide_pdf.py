"""Generate installation guide PDF from INSTALACAO_CASAOS.md using ReportLab.
Output: docs/Instalacao_BWSFinance_Linux.pdf
Simplifies markdown (basic headings, code blocks) to PDF.
"""
import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm

BASE_DIR = Path(__file__).resolve().parent.parent
MD_FILE = BASE_DIR / 'INSTALACAO_CASAOS.md'
OUT_DIR = BASE_DIR / 'docs'
OUT_FILE = OUT_DIR / 'Instalacao_BWSFinance_Linux.pdf'

HEADING_PREFIXES = ('# ', '## ', '### ', '#### ')
CODE_FENCE = '```'


def read_markdown_lines():
    if not MD_FILE.exists():
        raise FileNotFoundError(f'Guide markdown not found: {MD_FILE}')
    with MD_FILE.open('r', encoding='utf-8') as f:
        return f.readlines()


def write_pdf(lines):
    OUT_DIR.mkdir(exist_ok=True)
    c = canvas.Canvas(str(OUT_FILE), pagesize=A4)
    width, height = A4

    styles = getSampleStyleSheet()
    text_obj = c.beginText()
    text_obj.setTextOrigin(15 * mm, height - 20 * mm)
    text_obj.setFont('Helvetica', 11)

    in_code_block = False

    for raw in lines:
        line = raw.rstrip('\n')

        # New page if near bottom
        if text_obj.getY() < 25 * mm:
            c.drawText(text_obj)
            c.showPage()
            text_obj = c.beginText()
            text_obj.setTextOrigin(15 * mm, height - 20 * mm)
            text_obj.setFont('Helvetica', 11)

        if line.strip() == CODE_FENCE:
            in_code_block = not in_code_block
            if in_code_block:
                text_obj.setFont('Courier', 9)
                text_obj.textLine('')
                text_obj.textLine('[ Código ]:')
            else:
                text_obj.setFont('Helvetica', 11)
                text_obj.textLine('')
            continue

        if in_code_block:
            # Preserve indentation
            text_obj.textLine(line)
            continue

        # Headings
        if any(line.startswith(p) for p in HEADING_PREFIXES):
            level = line.count('#', 0, line.find(' '))
            clean = line[level+1:].strip()
            size = 16 - (level * 2)
            text_obj.setFont('Helvetica-Bold', max(size, 10))
            text_obj.textLine(clean.upper())
            text_obj.setFont('Helvetica', 11)
            text_obj.textLine('')
            continue

        if line.strip() == '---':
            # Horizontal rule
            c.drawText(text_obj)
            c.line(15 * mm, text_obj.getY(), width - 15 * mm, text_obj.getY())
            text_obj.moveCursor(0, -12)
            continue

        # Bullet points - simple conversion
        if line.strip().startswith('- '):
            text_obj.textLine('• ' + line.strip()[2:])
            continue

        # Regular paragraph
        text_obj.textLine(line)

    c.drawText(text_obj)
    c.showPage()
    c.save()
    return OUT_FILE


def generate():
    lines = read_markdown_lines()
    pdf_path = write_pdf(lines)
    print(f'[PDF] Guide generated at: {pdf_path}')


if __name__ == '__main__':
    generate()
