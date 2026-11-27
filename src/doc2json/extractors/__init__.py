from pathlib import Path

from .excel import extract_excel
from .pdf import extract_pdf
from .word import extract_word

EXTRATORES = {
    '.pdf': extract_pdf,
    '.docx': extract_word,
    '.xlsx': extract_excel,
}


def extract_text(caminho: str | Path) -> str:
    caminho = Path(caminho)
    extensao = caminho.suffix.lower()

    if extensao not in EXTRATORES:
        aceitos = ', '.join(EXTRATORES)
        raise ValueError(f'Formato não suportado: {extensao}. Use um destes: {aceitos}')

    return EXTRATORES[extensao](caminho)
