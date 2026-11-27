import csv
import io
import json

import pytest
from docx import Document
from typer.testing import CliRunner

from doc2json import cli
from doc2json.extractors import listar_documentos
from doc2json.llm import FakeLLM

runner = CliRunner()

ESQUEMA = '''nome: Projeto
campos:
  nome:
    tipo: texto
  escopo:
    tipo: lista_texto
'''


def criar_docx(caminho, texto):
    documento = Document()
    documento.add_paragraph(texto)
    documento.save(str(caminho))


@pytest.fixture
def pasta(tmp_path):
    pasta = tmp_path / 'documentos'
    pasta.mkdir()
    criar_docx(pasta / 'b.docx', 'Projeto Beta')
    criar_docx(pasta / 'a.docx', 'Projeto Aurora')
    (pasta / 'notas.txt').write_text('ignorar', encoding='utf-8')
    (pasta / '~$a.docx').write_text('arquivo temporário', encoding='utf-8')
    return pasta


@pytest.fixture
def esquema(tmp_path):
    caminho = tmp_path / 'esquema.yaml'
    caminho.write_text(ESQUEMA, encoding='utf-8')
    return caminho


@pytest.fixture(autouse=True)
def llm_por_documento(monkeypatch):
    '''Responde com o nome do projeto que aparece no texto do documento.'''

    class LLMPorDocumento(FakeLLM):
        def complete(self, prompt):
            self.chamadas.append(prompt)
            nome = 'Aurora' if 'Aurora' in prompt else 'Beta'
            return json.dumps({'nome': nome, 'escopo': ['portal', 'treinamento']})

    monkeypatch.setattr(cli, 'criar_llm', lambda provedor: LLMPorDocumento([]))


def test_lista_so_documentos_suportados(pasta):
    assert [c.name for c in listar_documentos(pasta)] == ['a.docx', 'b.docx']


def test_pasta_gera_json_consolidado(pasta, esquema):
    resultado = runner.invoke(cli.app, ['extrair', str(pasta), '-e', str(esquema)])

    assert resultado.exit_code == 0, resultado.output
    assert json.loads(resultado.output) == [
        {'arquivo': 'a.docx', 'dados': {'nome': 'Aurora', 'escopo': ['portal', 'treinamento']}},
        {'arquivo': 'b.docx', 'dados': {'nome': 'Beta', 'escopo': ['portal', 'treinamento']}},
    ]


def test_pasta_gera_csv_consolidado(pasta, esquema, tmp_path):
    destino = tmp_path / 'saida.csv'
    resultado = runner.invoke(
        cli.app, ['extrair', str(pasta), '-e', str(esquema), '--formato', 'csv', '-o', str(destino)]
    )

    assert resultado.exit_code == 0, resultado.output
    linhas = list(csv.DictReader(io.StringIO(destino.read_text(encoding='utf-8'))))
    assert linhas == [
        {'arquivo': 'a.docx', 'nome': 'Aurora', 'escopo': 'portal; treinamento'},
        {'arquivo': 'b.docx', 'nome': 'Beta', 'escopo': 'portal; treinamento'},
    ]


def test_arquivo_unico_continua_gerando_objeto_json(pasta, esquema):
    resultado = runner.invoke(cli.app, ['extrair', str(pasta / 'a.docx'), '-e', str(esquema)])

    assert resultado.exit_code == 0, resultado.output
    assert json.loads(resultado.output) == {'nome': 'Aurora', 'escopo': ['portal', 'treinamento']}


def test_documento_com_erro_nao_interrompe_a_pasta(pasta, esquema):
    (pasta / 'quebrado.pdf').write_text('não é um PDF', encoding='utf-8')
    (pasta / 'c.docx').write_bytes(b'corrompido')

    resultado = runner.invoke(cli.app, ['extrair', str(pasta), '-e', str(esquema), '-f', 'csv'])

    assert resultado.exit_code == 1
    assert 'a.docx,Aurora' in resultado.output
    assert 'b.docx,Beta' in resultado.output
    assert 'Erro em c.docx' in resultado.output
    assert 'Erro em quebrado.pdf' in resultado.output


def test_pasta_sem_documentos(tmp_path, esquema):
    vazia = tmp_path / 'vazia'
    vazia.mkdir()

    resultado = runner.invoke(cli.app, ['extrair', str(vazia), '-e', str(esquema)])

    assert resultado.exit_code == 1
    assert 'nenhum documento' in resultado.output


def test_formato_desconhecido(pasta, esquema):
    resultado = runner.invoke(cli.app, ['extrair', str(pasta), '-e', str(esquema), '-f', 'xml'])

    assert resultado.exit_code != 0
