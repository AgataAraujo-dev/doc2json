# Do PDF ao dado estruturado
## Construindo um pipeline com Python e LLMs

[nome do evento] · [data]

---

# Quem sou eu

**Ágata**

[cargo e trajetória — preencher com sua história]

[contato: LinkedIn, GitHub, etc.]

---

# O problema dos dados presos

Informações importantes vivem trancadas em documentos:
- Contratos
- Relatórios
- Planilhas

Extrair manualmente é lento, chato e cheio de erros.

---

# O que vamos construir

Um comando que transforma isso:

> "Projeto Aurora. Responsável: Marina Souza. Prazo: 15 de dezembro de 2026."

Nisso:

```json
{
  "nome": "Projeto Aurora",
  "responsavel": "Marina Souza",
  "prazo": "2026-12-15"
}
```

---

# O mapa do pipeline

[DIAGRAMA: caixas conectadas por setas]

```
documento → extrair texto → dividir → LLM → validar → JSON
                                        ▲         │
                                        └─ retry ─┘
```

Cada etapa tem uma responsabilidade só.

---

# Por que um pipeline?

- Cada peça pode ser testada separadamente
- Fácil trocar o LLM depois
- Erros ficam isolados
- Funciona com documentos de qualquer tamanho

---

# Etapa 1: Extrair texto

O LLM só entende texto. Precisamos converter PDF, Word e Excel.

```python
from pypdf import PdfReader

def extract_pdf(caminho):
    leitor = PdfReader(caminho)
    paginas = [p.extract_text() for p in leitor.pages]
    return '\n\n'.join(paginas)
```

---

# A "porteira" dos formatos

Uma função que escolhe o extrator certo pela extensão:

```python
EXTRATORES = {
    '.pdf': extract_pdf,
    '.docx': extract_word,
    '.xlsx': extract_excel,
}

def extract_text(caminho):
    extensao = Path(caminho).suffix.lower()
    return EXTRATORES[extensao](caminho)
```

---

# Pegadinhas de cada formato

**PDF**: se for escaneado, não tem texto — precisa de OCR

**Word**: tabelas ficam separadas dos parágrafos

**Excel**: várias abas, fórmulas vs valores

---

# O esquema: o que queremos de volta

Usamos Pydantic para definir os campos:

```python
class Projeto(BaseModel):
    nome: str
    responsavel: str | None = None
    prazo: date | None = None
    escopo: list[str] = []
```

O `| None` é importante: se a info não existe, fica vazio.

---

# Dividindo textos longos

[DIAGRAMA: texto grande sendo cortado em pedaços com sobreposição]

O LLM tem limite de contexto. Documentos grandes precisam ser divididos.

A sobreposição garante que nada se perca na divisa.

```python
def dividir_texto(texto, tamanho_max=6000):
    # corta por linhas, com sobreposição
```

---

# Etapa 2: LLM como parser

O prompt é a instrução para a IA:

```python
def montar_prompt(texto, modelo):
    return f'''Extraia informações do documento.
Responda APENAS com JSON válido.

Regras:
- Se a info não aparecer, use null
- Datas no formato AAAA-MM-DD

<documento>
{texto}
</documento>'''
```

---

# A interface plugável

Qualquer classe com `complete(prompt) -> str` serve:

```python
class LLM(Protocol):
    def complete(self, prompt: str) -> str: ...
```

Isso permite trocar de provedor sem mudar o resto.

---

# FakeLLM: testando sem IA

```python
class FakeLLM:
    def __init__(self, respostas):
        self.respostas = list(respostas)
    
    def complete(self, prompt):
        return self.respostas.pop(0)
```

Testes rodam rápido, sem custo, sem internet.

---

# BedrockLLM: IA de verdade

```python
class BedrockLLM:
    def complete(self, prompt):
        resposta = self.client.converse(
            modelId=self.model_id,
            messages=[{'role': 'user', 
                      'content': [{'text': prompt}]}],
        )
        return resposta['output']['message']['content'][0]['text']
```

---

# O resultado

```bash
doc2json extrair documento.docx \
    --esquema projeto.yaml \
    --provedor bedrock
```

```json
{
  "nome": "Projeto Aurora",
  "responsavel": "Marina Souza",
  "prazo": "2026-12-15",
  "prioridade": "alta",
  "escopo": ["portal", "migração", "treinamento"]
}
```

---

# Quando dá errado

A IA pode responder:
- JSON inválido
- Campos faltando
- Tipos errados
- Texto junto com o JSON

Nunca confie cegamente na resposta.

---

# O laço de nova tentativa

[DIAGRAMA: fluxo com retry — LLM → validar → erro → prompt com correção → LLM]

```python
for _ in range(tentativas):
    resposta = llm.complete(prompt)
    try:
        return modelo.model_validate_json(resposta)
    except ValidationError as erro:
        prompt = f"{prompt_base}\nErro: {erro}\nCorrija."
```

---

# Validação com Pydantic

O Pydantic faz o trabalho pesado:
- Verifica se o JSON é válido
- Converte tipos (string → date)
- Lista exatamente o que está errado

A mensagem de erro vai pro LLM corrigir.

---

# Demonstração ao vivo

[espaço para demo de 4 minutos]

1. Documento de entrada
2. Comando com --provedor bedrock
3. JSON de saída
4. Teste de correção automática

---

# O que você aprendeu

- Pipeline em etapas isoladas e testáveis
- Esquema define o contrato
- Interface permite trocar provedores
- Validação + retry = robustez
- Testes com FakeLLM

---

# O repositório

**github.com/AgataAraujo-dev/doc2json**

[espaço para QR code]

- MIT License
- Issues `good first issue` abertas
- PRs são bem-vindos!

---

# Perguntas?

[espaço para QR code]

**github.com/AgataAraujo-dev/doc2json**

[contato]

Obrigada! 🐍
