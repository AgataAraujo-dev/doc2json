from pathlib import Path

from openpyxl import load_workbook


def extract_excel(caminho: Path) -> str:
    planilha = load_workbook(str(caminho), data_only=True, read_only=True)
    partes = []

    for aba in planilha.worksheets:
        partes.append(f'## Aba: {aba.title}')
        for linha in aba.iter_rows(values_only=True):
            if any(celula is not None for celula in linha):
                partes.append(' | '.join('' if c is None else str(c) for c in linha))

    planilha.close()
    return '\n'.join(partes)
