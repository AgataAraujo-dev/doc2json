# doc2json

Transforma PDF, Word e Excel em JSON validado usando um LLM.

## O problema

Dados importantes vivem presos em documentos: contratos, relatórios, planilhas. Extrair essas informações manualmente é lento e propenso a erros. O doc2json automatiza esse processo usando inteligência artificial.

## Como funciona

```
documento → extrair texto → dividir em pedaços → perguntar ao LLM → validar → JSON
                                                      ▲                │
                                                      └── tenta de novo ◄┘
```

## Instalação

```bash
git clone https://github.com/AgataAraujo-dev/doc2json.git
cd doc2json
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# ou: source .venv/bin/activate  # Linux/Mac
pip install -e '.[dev,groq]'
```

## Exemplo de uso

1. Crie um arquivo `esquema.yaml` com os campos que quer extrair:

```yaml
nome: Projeto
campos:
  nome:
    tipo: texto
    descricao: Nome do projeto
  responsavel:
    tipo: texto
    descricao: Pessoa responsável
  prazo:
    tipo: data
    descricao: Data final no formato AAAA-MM-DD
```

2. Configure a chave do Groq:

```bash
export GROQ_API_KEY="sua-chave-aqui"
```

3. Execute:

```bash
doc2json extrair documento.docx --esquema esquema.yaml --provedor groq
```

4. Resultado:

```json
{
  "nome": "Projeto Aurora",
  "responsavel": "Marina Souza",
  "prazo": "2026-12-15"
}
```

## Provedores de IA

| Provedor | Descrição |
|----------|-----------|
| `fake` | Resposta vazia, para testar o fluxo sem IA |
| `groq` | Groq Cloud (grátis, rápido) |
| `bedrock` | Amazon Bedrock (requer AWS configurada) |

### Configurando o Groq (recomendado)

1. Crie uma conta em [console.groq.com](https://console.groq.com)
2. Gere uma API key
3. Defina a variável de ambiente:

```bash
export GROQ_API_KEY="sua-chave-aqui"
```

### Configurando o Bedrock (alternativa)

1. Configure suas credenciais AWS (`aws configure`)
2. Habilite o modelo no console do Bedrock
3. Defina a variável de ambiente:

```bash
export BEDROCK_MODEL_ID="anthropic.claude-3-haiku-20240307-v1:0"
```

## Formatos suportados

- PDF (com texto, não escaneado)
- Word (.docx)
- Excel (.xlsx)

## Roadmap

- [ ] Provedor local (Ollama)
- [ ] OCR para PDFs escaneados
- [ ] Tabelas do Word na ordem correta
- [ ] Processar pasta inteira
- [ ] Saída em CSV

## Testes

```bash
pytest -v
ruff check .
```

## Como contribuir

Veja [CONTRIBUTING.md](CONTRIBUTING.md). Issues com o rótulo `good first issue` são ótimas para começar!

## Licença

MIT — veja [LICENSE](LICENSE).
