from pathlib import Path

from pypdf import PdfReader


def extract_pdf(caminho: Path) -> str:
    leitor = PdfReader(str(caminho))
    paginas = [(pagina.extract_text() or '') for pagina in leitor.pages]
    texto = '\n\n'.join(paginas).strip()

    if not texto:
        raise ValueError('Nenhum texto encontrado. O PDF pode ser escaneado e precisar de OCR.')

    return texto
