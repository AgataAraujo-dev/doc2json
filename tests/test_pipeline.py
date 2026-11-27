import json
from datetime import date

import pytest
from docx import Document
from pydantic import BaseModel

from doc2json.llm import FakeLLM
from doc2json.pipeline import (
    extrair_dados,
    juntar_resultados,
    limpar_resposta,
    processar_documento,
)

FENCE = '`' * 3


class Mini(BaseModel):
    nome: str | None = None
    prazo: date | None = None
    escopo: list[str] = []


def test_resposta_valida():
    llm = FakeLLM([json.dumps({'nome': 'Aurora', 'prazo': '2026-12-15'})])
    resultado = extrair_dados(llm, 'texto qualquer', Mini)

    assert resultado.nome == 'Aurora'
    assert resultado.prazo == date(2026, 12, 15)


def test_tenta_de_novo_quando_vem_errado():
    llm = FakeLLM(['isso não é json', json.dumps({'nome': 'Aurora'})])
    resultado = extrair_dados(llm, 'texto qualquer', Mini)

    assert resultado.nome == 'Aurora'
    assert len(llm.chamadas) == 2


def test_desiste_depois_das_tentativas():
    llm = FakeLLM(['lixo'])
    with pytest.raises(RuntimeError):
        extrair_dados(llm, 'texto qualquer', Mini, tentativas=2)

    assert len(llm.chamadas) == 2


def test_limpa_cercas_de_codigo():
    resposta = FENCE + 'json\n' + json.dumps({'nome': 'A'}) + '\n' + FENCE
    assert json.loads(limpar_resposta(resposta)) == {'nome': 'A'}


def test_junta_resultados_de_varios_pedacos():
    a = Mini(nome='Aurora', escopo=['portal'])
    b = Mini(prazo=date(2026, 12, 15), escopo=['portal', 'treinamento'])

    final = juntar_resultados([a, b])

    assert final['nome'] == 'Aurora'
    assert final['prazo'] == '2026-12-15'
    assert final['escopo'] == ['portal', 'treinamento']


def test_pipeline_completo_com_word(tmp_path):
    caminho = tmp_path / 'doc.docx'
    documento = Document()
    documento.add_paragraph('Projeto Aurora, prazo em 15 de dezembro de 2026.')
    documento.save(str(caminho))

    llm = FakeLLM([json.dumps({'nome': 'Aurora'})])
    resultado = processar_documento(caminho, Mini, llm)

    assert resultado.nome == 'Aurora'
