# Do PDF ao dado estruturado

## Construindo um pipeline com Python e LLMs

Ágata Araújo · PythOnSerra · [data]

---

# Quem sou eu

**Ágata Araújo** · Rio de Janeiro
Consultora de Projetos Dados & IA na Select Soluções

**Trajetória:**
- 2024: Escola da Nuvem → AWS Cloud Practitioner
- 2025: TechSelekrs → Estágio → AI Practitioner + Solutions Architect
- 2026: PMO → Data Engineer Associate → Consultora de IA

**Certificações:** 5× AWS + IA Business Strategist, Datadog, Scrum, Cyber Academy

[LinkedIn — preencher]

---

# O problema: dados presos em documentos

- A informação importante vive em PDFs, planilhas e arquivos Word
- Alguém abre, lê e copia campo por campo
- Lento, cansativo e cheio de erros

**E se um programa fizesse isso por nós?**

---

# O que vamos construir

**Antes:** texto solto

> Projeto Aurora. Responsável: Marina Souza. O prazo final é 15 de dezembro de 2026 e a prioridade é alta.

**Depois:** dado estruturado

```json
{
  "nome": "Projeto Aurora",
  "responsavel": "Marina Souza",
  "prazo": "2026-12-15",
  "prioridade": "alta"
}
```

A data já vem no formato certo.

---

# O mapa do pipeline

Diagrama em linha, da esquerda para a direita:

Documento → 1. Extrair texto → 2. Dividir em pedaços → 3. Perguntar ao LLM → 4. Validar → JSON

Uma seta de volta, do passo 4 para o passo 3: se a resposta vier errada, tenta de novo.

---

# O que vamos usar

| Etapa | Ferramenta |
| --- | --- |
| Ler PDF | pypdf |
| Ler Word | python-docx |
| Ler Excel | openpyxl |
| Validar | Pydantic |
| Linha de comando | Typer |
| LLM | Qualquer provedor (Bedrock, Groq, Ollama...) |

---

# Etapa 1: extrair texto

O LLM só entende texto. Cada formato precisa do seu leitor.

- PDF → pypdf
- Word → python-docx
- Excel → openpyxl

---

# PDF: o texto está lá dentro?

- O leitor percorre o PDF página por página
- O texto sai corrido, às vezes com quebras de linha estranhas
- **Pegadinha:** PDF escaneado é imagem, não tem texto. Precisa de OCR
- Nosso programa avisa, em vez de mandar texto vazio para a IA

---

# Word e Excel: as pegadinhas

**Word**

- Tabelas ficam separadas dos parágrafos
- Extraímos cada linha como "célula | célula"

**Excel**

- Um arquivo tem várias abas: marcamos cada uma com o nome
- Lemos o resultado da fórmula, não a fórmula

---

# Código: a porteira de extratores

```python
EXTRATORES = {
    '.pdf': extract_pdf,
    '.docx': extract_word,
    '.xlsx': extract_excel,
}

def extract_text(caminho):
    extensao = Path(caminho).suffix.lower()
    if extensao not in EXTRATORES:
        raise ValueError(f'Formato não suportado: {extensao}')
    return EXTRATORES[extensao](caminho)
```

Uma função por formato. Um dicionário escolhe a certa pela extensão.

---

# Textos longos: dividir em pedaços

- O LLM lê só um limite de texto por vez (a janela de contexto)
- Cortamos o documento em pedaços e juntamos as respostas
- **Sobreposição:** cada pedaço repete o final do anterior

Diagrama: Pedaço 1 | Pedaço 2 | Pedaço 3, com a ponta de cada pedaço repetida no começo do seguinte.

---

# LLM como parser: um contrato

Em vez de pedir "resuma este documento", pedimos:

**"Devolva exatamente estes campos, neste formato."**

Texto livre → LLM → JSON previsível

O esquema é o contrato.

---

# O esquema com Pydantic

```python
class Projeto(BaseModel):
    nome: str = Field(description='Nome do projeto')
    responsavel: str | None = Field(None, description='Responsável; null se não aparecer')
    prazo: date | None = Field(None, description='Data final, AAAA-MM-DD')
    prioridade: Prioridade | None = None
    escopo: list[str] = Field(default_factory=list)
```

Os tipos dizem o que é aceito: texto, data, lista, opções.

---

# A descrição é instrução para a IA

- Cada campo tem uma descrição em português claro
- A mesma descrição documenta o código e orienta o modelo
- `Projeto.model_json_schema()` gera o esquema que vai no prompt

---

# Três formas de pedir saída estruturada

1. **Só no prompt:** "responda em JSON" → simples, mas frágil
2. **Esquema dentro do prompt** → mais confiável
3. **Recurso nativo do provedor** (saída estruturada ou tool use) → o modelo é forçado a seguir o esquema

Nosso projeto usa a 2 e valida o resultado.

---

# Três dicas de prompt que valem ouro

1. Peça `null` quando não achar: nunca inventar
2. Defina o formato da data: AAAA-MM-DD
3. Peça só o JSON, sem texto em volta

---

# Validar o que voltou

```python
try:
    projeto = Projeto.model_validate_json(resposta)
except ValidationError as erro:
    print(erro)
```

**Tudo o que vem de uma IA deve ser conferido antes de ser usado.**

---

# Quando dá errado

- Texto maior que a janela de contexto
- Resposta fora do formato: JSON quebrado, texto extra
- Campo inventado quando a informação não existe
- Documentos inconsistentes: cada um de um jeito

---

# O laço de nova tentativa

Diagrama de fluxo:

A IA responde → Validação

- Válido → segue para o resultado
- Inválido → devolve o erro à IA e pede a correção (até 3 tentativas)
- Esgotou as tentativas → erro com mensagem clara

---

# Código: extrair_dados

```python
for _ in range(tentativas):
    resposta = llm.complete(prompt)
    try:
        return modelo.model_validate_json(limpar_resposta(resposta))
    except ValidationError as erro:
        prompt = f'{prompt_base}\n\nResposta inválida:\n{erro}\n\nCorrija.'
raise RuntimeError('JSON inválido após várias tentativas')
```

Versão resumida do código do repositório.

---

# Demo ao vivo

1. **O documento:** Projeto Aurora, em Word
2. **O comando:**

```bash
doc2json extrair projeto_aurora.docx \
    --esquema projeto.yaml \
    --provedor groq
```

3. **O resultado:** JSON validado
4. **Quando a IA erra:** o teste que simula o erro e a correção

---

# O que levar daqui

- Trate a IA como parser, com um contrato (o esquema)
- Valide tudo o que ela devolve
- Deixe o LLM plugável: troque de provedor sem reescrever
- Teste sem IA: um FakeLLM deixa tudo testável

---

# O repositório é um presente

**github.com/AgataAraujo-dev/doc2json**

- Open source, licença MIT
- Teste o fluxo sem conta na nuvem, com o FakeLLM
- Issues "good first issue" esperando por você

[QR code do repositório]

---

# Perguntas?

Obrigada! 🐍

**github.com/AgataAraujo-dev/doc2json**

[LinkedIn — preencher]

[QR code do repositório]
