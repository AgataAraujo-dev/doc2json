def dividir_texto(texto: str, tamanho_max: int = 6000, sobreposicao: int = 300) -> list[str]:
    '''Divide o texto em pedaços de no máximo tamanho_max caracteres.'''
    if len(texto) <= tamanho_max:
        return [texto]

    pedacos = []
    atual = ''

    for linha in texto.split('\n'):
        if atual and len(atual) + len(linha) + 1 > tamanho_max:
            pedacos.append(atual)
            atual = atual[-sobreposicao:] + '\n' + linha
        elif atual:
            atual = atual + '\n' + linha
        else:
            atual = linha

    if atual:
        pedacos.append(atual)

    return pedacos
