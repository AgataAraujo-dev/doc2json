from doc2json.chunking import dividir_texto


def test_texto_curto_vira_um_pedaco():
    assert dividir_texto('olá mundo', tamanho_max=100) == ['olá mundo']


def test_texto_longo_e_dividido():
    texto = '\n'.join(f'linha numero {i}' for i in range(50))
    pedacos = dividir_texto(texto, tamanho_max=100, sobreposicao=10)

    assert len(pedacos) > 1
    assert all(len(pedaco) <= 100 for pedaco in pedacos)
