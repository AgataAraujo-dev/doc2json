from pathlib import Path

from docx import Document


def extract_word(caminho: Path) -> str:
    documento = Document(str(caminho))
    partes = [p.text for p in documento.paragraphs if p.text.strip()]

    for tabela in documento.tables:
        for linha in tabela.rows:
            celulas = [celula.text.strip() for celula in linha.cells]
            partes.append(' | '.join(celulas))

    return '\n'.join(partes)
