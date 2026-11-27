import json

from pydantic import BaseModel, ValidationError

from .chunking import dividir_texto
from .extractors import extract_text
from .llm.base import LLM

FENCE = '`' * 3


def montar_prompt(texto: str, modelo: type[BaseModel]) -> str:
    esquema = json.dumps(modelo.model_json_schema(), ensure_ascii=False, indent=2)
    return f'''Você extrai informações de documentos.

Leia o texto e responda APENAS com um JSON válido que siga este esquema:
{esquema}

Regras:
- Se uma informação não aparecer no texto, use null. Nunca invente valores.
- Datas no formato AAAA-MM-DD.
- Não escreva nada além do JSON.

<documento>
{texto}
</documento>'''


def limpar_resposta(resposta: str) -> str:
    '''Remove a cerca de código (três crases) que alguns modelos colocam em volta do JSON.'''
    resposta = resposta.strip()
    if resposta.startswith(FENCE):
        resposta = resposta.split('\n', 1)[1] if '\n' in resposta else ''
    if resposta.endswith(FENCE):
        resposta = resposta[:-3]
    return resposta.strip()


def extrair_dados(llm: LLM, texto: str, modelo: type[BaseModel], tentativas: int = 3) -> BaseModel:
    '''Pergunta à IA e valida a resposta. Se vier errada, pede correção.'''
    prompt_base = montar_prompt(texto, modelo)
    prompt = prompt_base
    ultimo_erro = None

    for _ in range(tentativas):
        resposta = llm.complete(prompt)
        try:
            return modelo.model_validate_json(limpar_resposta(resposta))
        except ValidationError as erro:
            ultimo_erro = erro
            prompt = f'''{prompt_base}

Sua resposta anterior foi:
{resposta}

Ela é inválida. Erros encontrados:
{erro}

Corrija e responda APENAS com o JSON válido.'''

    raise RuntimeError(f'Não foi possível obter um JSON válido após {tentativas} tentativas: {ultimo_erro}')


def juntar_resultados(resultados: list[BaseModel]) -> dict:
    '''Une os resultados de vários pedaços: o primeiro valor preenchido vence; listas são somadas.'''
    final: dict = {}

    for resultado in resultados:
        for campo, valor in resultado.model_dump(mode='json').items():
            if isinstance(valor, list):
                lista = final.setdefault(campo, [])
                for item in valor:
                    if item not in lista:
                        lista.append(item)
            elif final.get(campo) is None:
                final[campo] = valor

    return final


def processar_documento(
    caminho,
    modelo: type[BaseModel],
    llm: LLM,
    tamanho_max: int = 6000,
    tentativas: int = 3,
) -> BaseModel:
    '''Fluxo completo: extrair texto, dividir, perguntar à IA, validar e juntar.'''
    texto = extract_text(caminho)
    pedacos = dividir_texto(texto, tamanho_max)
    resultados = [extrair_dados(llm, pedaco, modelo, tentativas) for pedaco in pedacos]

    if len(resultados) == 1:
        return resultados[0]

    return modelo.model_validate(juntar_resultados(resultados))
