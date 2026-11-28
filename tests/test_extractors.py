import sys
from pathlib import Path

import pytest
from docx import Document
from openpyxl import Workbook
from pypdf import PdfWriter

from doc2json.extractors import extract_text, pdf


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


def test_pdf_com_texto_nao_executa_ocr(monkeypatch):
    def ocr_inesperado(_):
        pytest.fail('OCR executado apesar da camada de texto')

    monkeypatch.setattr(pdf, '_ocr_pdf', ocr_inesperado)
    caminho = Path(__file__).resolve().parents[1] / 'examples' / 'projeto_aurora.pdf'

    assert extract_text(caminho).strip()


def test_pdf_sem_texto_orienta_a_instalar_extra(tmp_path, monkeypatch):
    caminho = tmp_path / 'sem-texto.pdf'
    escritor = PdfWriter()
    escritor.add_blank_page(width=200, height=200)
    escritor.write(caminho)
    monkeypatch.setitem(sys.modules, 'pypdfium2', None)

    with pytest.raises(ValueError, match=r'doc2json\[ocr\]'):
        extract_text(caminho)


def test_pdf_escaneado_renderiza_paginas_para_ocr(tmp_path, monkeypatch):
    imagens = pytest.importorskip('PIL.Image')
    pytest.importorskip('pypdfium2')
    tesseract = pytest.importorskip('pytesseract')
    primeira = imagens.new('RGB', (120, 100), 'white')
    segunda = imagens.new('RGB', (120, 100), 'gray')
    caminho = tmp_path / 'escaneado.pdf'
    primeira.save(caminho, save_all=True, append_images=[segunda])
    chamadas = []

    def reconhecer(imagem, *, lang, timeout):
        assert lang == 'por'
        assert timeout == 30
        chamadas.append(imagem.getpixel((0, 0))[0])
        return 'Primeira página' if len(chamadas) == 1 else 'Segunda página'

    monkeypatch.setattr(tesseract, 'image_to_string', reconhecer)

    assert extract_text(caminho) == 'Primeira página\n\nSegunda página'
    assert chamadas[0] > chamadas[1]
