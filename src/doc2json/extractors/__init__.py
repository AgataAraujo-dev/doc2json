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


def listar_documentos(pasta: str | Path) -> list[Path]:
    '''Lista, em ordem alfabética, os documentos suportados de uma pasta (sem entrar em subpastas).'''
    return sorted(
        caminho
        for caminho in Path(pasta).iterdir()
        if caminho.is_file()
        and caminho.suffix.lower() in EXTRATORES
        and not caminho.name.startswith('~$')  # arquivos temporários do Office
    )
