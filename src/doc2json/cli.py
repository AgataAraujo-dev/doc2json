import csv
import io
import json
from pathlib import Path

import typer
from pydantic import BaseModel

from .extractors import listar_documentos
from .llm import LLM, FakeLLM
from .pipeline import processar_documento
from .schema import carregar_esquema

app = typer.Typer(help='Transforma PDF, Word e Excel em JSON validado usando um LLM.')

FORMATOS = ('json', 'csv')


def criar_llm(provedor: str) -> LLM:
    if provedor == 'fake':
        return FakeLLM(['{}'])
    if provedor == 'bedrock':
        from .llm.bedrock import BedrockLLM

        return BedrockLLM()
    if provedor == 'groq':
        from .llm.groq import GroqLLM

        return GroqLLM()
    raise typer.BadParameter(f'Provedor desconhecido: {provedor}. Use fake, groq ou bedrock.')


def gerar_csv(colunas: list[str], linhas: list[dict]) -> str:
    '''Uma linha por documento; listas viram texto separado por "; ".'''
    buffer = io.StringIO()
    escritor = csv.DictWriter(buffer, fieldnames=colunas, lineterminator='\n')
    escritor.writeheader()
    for linha in linhas:
        escritor.writerow(
            {
                coluna: '; '.join(str(item) for item in valor) if isinstance(valor, list) else valor
                for coluna, valor in linha.items()
            }
        )
    return buffer.getvalue()


@app.callback()
def principal() -> None:
    '''doc2json: do documento ao dado estruturado.'''


@app.command()
def extrair(
    arquivo: Path = typer.Argument(
        ..., exists=True, help='Documento (.pdf, .docx ou .xlsx) ou pasta com documentos'
    ),
    esquema: Path = typer.Option(..., '--esquema', '-e', exists=True, help='YAML com os campos'),
    provedor: str = typer.Option('fake', '--provedor', '-p', help='fake ou bedrock'),
    saida: Path | None = typer.Option(None, '--saida', '-o', help='Salva o resultado neste arquivo'),
    formato: str = typer.Option('json', '--formato', '-f', help='json ou csv'),
) -> None:
    '''Lê um documento (ou todos de uma pasta) e devolve os campos do esquema em JSON ou CSV.'''
    if formato not in FORMATOS:
        raise typer.BadParameter(f'Formato desconhecido: {formato}. Use json ou csv.')

    modelo = carregar_esquema(esquema)
    llm = criar_llm(provedor)

    if arquivo.is_dir():
        documentos = listar_documentos(arquivo)
        if not documentos:
            typer.echo(f'Erro: nenhum documento .pdf, .docx ou .xlsx em {arquivo}', err=True)
            raise typer.Exit(code=1)
    else:
        documentos = [arquivo]

    # Numa pasta, um documento com problema (corrompido, ilegível...) não interrompe os demais.
    erros_tratados = Exception if arquivo.is_dir() else (ValueError, RuntimeError)
    resultados: list[tuple[str, BaseModel]] = []
    falhas = 0
    for documento in documentos:
        try:
            resultado = processar_documento(documento, modelo, llm)
        except erros_tratados as erro:
            falhas += 1
            prefixo = f'Erro em {documento.name}' if arquivo.is_dir() else 'Erro'
            typer.echo(f'{prefixo}: {erro}', err=True)
            continue
        resultados.append((documento.name, resultado))

    if not arquivo.is_dir() and falhas:
        raise typer.Exit(code=1)

    if formato == 'csv':
        linhas = [{'arquivo': nome, **dados.model_dump(mode='json')} for nome, dados in resultados]
        texto = gerar_csv(['arquivo', *modelo.model_fields], linhas)
    elif arquivo.is_dir():
        consolidado = [
            {'arquivo': nome, 'dados': dados.model_dump(mode='json')} for nome, dados in resultados
        ]
        texto = json.dumps(consolidado, ensure_ascii=False, indent=2)
    else:
        texto = resultados[0][1].model_dump_json(indent=2)

    if saida:
        saida.write_text(texto, encoding='utf-8')
        typer.echo(f'Salvo em {saida}')
    else:
        typer.echo(texto.rstrip('\n'))

    if falhas:
        raise typer.Exit(code=1)
