from contextlib import closing
from pathlib import Path

from pypdf import PdfReader


def extract_pdf(caminho: Path) -> str:
    leitor = PdfReader(str(caminho))
    paginas = [(pagina.extract_text() or '') for pagina in leitor.pages]
    texto = '\n\n'.join(paginas).strip()
    if texto:
        return texto
    return _ocr_pdf(caminho)


def _ocr_pdf(caminho: Path) -> str:
    try:
        import pypdfium2
        import pytesseract
    except ImportError as erro:
        raise ValueError(
            'Nenhum texto encontrado. Para ler PDFs escaneados, instale '
            'doc2json[ocr] e o Tesseract com o idioma português (por).'
        ) from erro

    paginas = []
    try:
        with closing(pypdfium2.PdfDocument(caminho)) as documento:
            for indice in range(len(documento)):
                with (
                    closing(documento[indice]) as pagina,
                    closing(pagina.render(scale=300 / 72)) as bitmap,
                ):
                    texto = pytesseract.image_to_string(bitmap.to_pil(), lang='por', timeout=30)
                if texto.strip():
                    paginas.append(texto.strip())
    except pytesseract.TesseractNotFoundError as erro:
        raise ValueError('Instale o Tesseract e adicione o executável ao PATH para usar OCR.') from erro
    except pytesseract.TesseractError as erro:
        raise ValueError(f'Falha no OCR. Verifique o idioma português (por): {erro}') from erro

    if not paginas:
        raise ValueError('Nenhum texto encontrado após o OCR.')
    return '\n\n'.join(paginas)
