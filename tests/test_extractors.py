import pytest
from docx import Document
from openpyxl import Workbook

from doc2json.extractors import extract_text


def test_extrai_texto_do_word(tmp_path):
    caminho = tmp_path / 'teste.docx'
    documento = Document()
    documento.add_paragraph('Projeto Aurora')
    documento.save(str(caminho))

    assert 'Projeto Aurora' in extract_text(caminho)


def test_extrai_texto_do_excel(tmp_path):
    caminho = tmp_path / 'teste.xlsx'
    planilha = Workbook()
    aba = planilha.active
    aba.title = 'Dados'
    aba.append(['nome', 'prazo'])
    aba.append(['Aurora', '2026-12-15'])
    planilha.save(str(caminho))

    texto = extract_text(caminho)
    assert 'Aurora' in texto
    assert 'Dados' in texto


def test_formato_nao_suportado(tmp_path):
    with pytest.raises(ValueError):
        extract_text(tmp_path / 'arquivo.txt')
