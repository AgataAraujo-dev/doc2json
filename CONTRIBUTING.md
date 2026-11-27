# Como contribuir

Obrigada pelo interesse em contribuir com o doc2json! 🎉

## Preparando o ambiente

```bash
git clone https://github.com/AgataAraujo-dev/doc2json.git
cd doc2json
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# ou: source .venv/bin/activate  # Linux/Mac
pip install -e '.[dev]'
```

## Rodando os testes

```bash
pytest -v
ruff check .
```

## Tipos de contribuição

- **Bugs**: abra uma issue descrevendo o problema e como reproduzir
- **Melhorias**: abra uma issue primeiro para discutir a ideia
- **Código**: faça um fork, crie uma branch e abra um PR

## Boas práticas

- Mudanças pequenas e focadas são mais fáceis de revisar
- Inclua testes para novas funcionalidades
- Mantenha o código limpo (ruff não pode reclamar)

## Issues para iniciantes

Procure issues com o rótulo `good first issue` — são tarefas mais simples, ideais para começar.

## Dúvidas?

Abra uma issue! Toda pergunta é bem-vinda.
