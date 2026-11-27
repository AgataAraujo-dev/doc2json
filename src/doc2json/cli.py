from pathlib import Path

import typer

from .llm import LLM, FakeLLM
from .pipeline import processar_documento
from .schema import carregar_esquema

app = typer.Typer(help='Transforma PDF, Word e Excel em JSON validado usando um LLM.')


def criar_llm(provedor: str) -> LLM:
    if provedor == 'fake':
        return FakeLLM(['{}'])
    if provedor == 'bedrock':
        from .llm.bedrock import BedrockLLM

        return BedrockLLM()
    raise typer.BadParameter(f'Provedor desconhecido: {provedor}. Use fake ou bedrock.')


@app.callback()
def principal() -> None:
    '''doc2json: do documento ao dado estruturado.'''


@app.command()
def extrair(
    arquivo: Path = typer.Argument(..., exists=True, help='Documento (.pdf, .docx ou .xlsx)'),
    esquema: Path = typer.Option(..., '--esquema', '-e', exists=True, help='YAML com os campos'),
    provedor: str = typer.Option('fake', '--provedor', '-p', help='fake ou bedrock'),
    saida: Path | None = typer.Option(None, '--saida', '-o', help='Salva o JSON neste arquivo'),
) -> None:
    '''Lê um documento e devolve os campos do esquema em JSON.'''
    modelo = carregar_esquema(esquema)

    try:
        resultado = processar_documento(arquivo, modelo, criar_llm(provedor))
    except (ValueError, RuntimeError) as erro:
        typer.echo(f'Erro: {erro}', err=True)
        raise typer.Exit(code=1)

    texto_json = resultado.model_dump_json(indent=2)

    if saida:
        saida.write_text(texto_json, encoding='utf-8')
        typer.echo(f'Salvo em {saida}')
    else:
        typer.echo(texto_json)
