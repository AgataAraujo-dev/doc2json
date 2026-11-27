from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, create_model


class Prioridade(str, Enum):
    baixa = 'baixa'
    media = 'media'
    alta = 'alta'


class Projeto(BaseModel):
    '''Exemplo de esquema escrito como classe Python.'''

    nome: str = Field(description='Nome do projeto')
    responsavel: str | None = Field(None, description='Responsável; null se não aparecer')
    prazo: date | None = Field(None, description='Data final no formato AAAA-MM-DD')
    prioridade: Prioridade | None = None
    escopo: list[str] = Field(default_factory=list, description='Principais entregas')


TIPOS = {
    'texto': str,
    'inteiro': int,
    'decimal': float,
    'data': date,
    'booleano': bool,
}


def carregar_esquema(caminho: str | Path) -> type[BaseModel]:
    '''Lê um arquivo YAML e devolve uma classe Pydantic com os campos pedidos.'''
    dados = yaml.safe_load(Path(caminho).read_text(encoding='utf-8'))
    campos: dict[str, Any] = {}

    for nome, config in dados['campos'].items():
        tipo_nome = config.get('tipo', 'texto')
        descricao = config.get('descricao', '')

        if tipo_nome == 'lista_texto':
            campos[nome] = (list[str], Field(default_factory=list, description=descricao))
        elif tipo_nome in TIPOS:
            campos[nome] = (TIPOS[tipo_nome] | None, Field(None, description=descricao))
        else:
            raise ValueError(f'Tipo desconhecido no campo {nome}: {tipo_nome}')

    return create_model(dados.get('nome', 'Documento'), **campos)
