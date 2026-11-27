class FakeLLM:
    '''LLM de mentira: devolve respostas prontas. Ótimo para testes.'''

    def __init__(self, respostas: list[str]):
        self.respostas = list(respostas)
        self.chamadas: list[str] = []

    def complete(self, prompt: str) -> str:
        self.chamadas.append(prompt)
        if len(self.respostas) > 1:
            return self.respostas.pop(0)
        return self.respostas[0]
