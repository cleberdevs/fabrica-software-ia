---
title: Fábrica de Software IA Enterprise
emoji: 🏭
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# 🏭 Fábrica de Software IA Enterprise

> **Gemini 2.5 Flash · DeepSeek v4 · Kimi K2 · Qwen 3 Coder** — Plataforma de *Vibe Coding* industrial com orquestração via **LangGraph**, interface web em **FastAPI + HTML** e deploy contínuo no **Hugging Face Spaces**.

---

## 🎯 O que é

Uma esteira de governança de software que elimina alucinações de escopo, falhas conceituais e brechas de segurança comuns em geradores de código genéricos. O código só chega ao disco e ao GitHub se passar por **todos os portões de qualidade** — auditoria semântica (score ≥ 80), SAST via Bandit e sandbox de testes PyTest.

Suporta geração, evolução incremental e debug de microsserviços corporativos em **5 linguagens**, com publicação automatizada de repositórios privados no GitHub.

---

## 🧠 Matriz Híbrida de Modelos (via OpenRouter)

| Tier | Papel | Modelo |
|------|-------|--------|
| **Tier 0-1** | Chief AI Officer — Orquestrador arquitetural + Arquiteto | `google/gemini-2.5-flash-lite` |
| **Tier 2** | Especialista Dev — Geração de código multi-camada | `deepseek/deepseek-v4-pro` → `moonshot/kimi-k2` → `qwen/qwen3-coder-next` *(fallback automático)* |
| **Tier 3 / QA** | Quality Gate, Testes e Documentação | `google/gemini-2.5-flash-lite` |
| **Visão** | Análise multimodal de imagens e diagramas | `google/gemma-4-31b-it:free` |

> **Custo zero de tokens:** toda a esteira roda sobre a camada gratuita do OpenRouter. A fábrica rotaciona automaticamente entre modelos e chaves de API quando há rate limit — basta separar múltiplas chaves por vírgula em `OPENROUTER_API_KEY`.

---

## 🧰 Stacks Homologadas

| Linguagem | Framework Web | Gerenciador | Testes | SAST |
|-----------|---------------|-------------|--------|------|
| **Python** | FastAPI | `requirements.txt` | PyTest | Bandit ✓ |
| **TypeScript** | Express | `package.json` | Jest | — |
| **Java** | Spring Boot | `pom.xml` | JUnit | — |
| **C#** | .NET Core | `.csproj` | xUnit | — |
| **Rust** | Axum | `Cargo.toml` | `cargo test` | — |

---

## 🚀 Os Agentes em Ação

### Tier 0-1 — Chief AI Officer + Arquiteto
Consolida requisitos, código legado, planilhas (CSV/XLSX) e imagens (via visão multimodal). Acumula os papéis de **Chief** (decisão estratégica) e **Arquiteto** (desenho de domínios e endpoints) — aproveitando a janela de contexto massiva do Gemini para eliminar a necessidade de um agente intermediário. Produz o `plano_do_chief` antes da primeira linha de código.

### Tier 2 — Especialista Dev (Coder)
Traduz o plano do Chief em código-fonte em **Clean Architecture** com 4 camadas rígidas:

- `camada_dominio` — Entidades puras e contratos de interfaces
- `camada_aplicacao` — Casos de uso e regras de negócio
- `camada_infra_banco` — Persistência via ORM nativo
- `camada_infra_web` — Controladores HTTP / rotas do framework escolhido

Possui **fallback automático** entre modelos com espera progressiva em caso de rate limit: 10s → 30s → 60s → 120s → 180s.

### Tier 3 — Quality Gate (Auditor Semântico)
Avalia notas de 0–100 para *Clean Code* (SOLID) e *Clean Architecture* (isolamento de camadas). Média < 80 devolve ao Dev para refatoração automática.

### Agente QA — Gerador de Testes
Cria suítes de testes unitários funcionais com mocks baseados nas rotas da `camada_infra_web`.

### Agente SAST — Sandbox de Segurança
Executa análise estática com **Bandit** (Python) em arquivo temporário isolado. Vulnerabilidades disparam `chief_retry` com o log completo no histórico de erros.

### Executor PyTest — Runtime Sandbox
Executa a suíte de testes em subprocess isolado. Falha aciona novo ciclo a partir do Chief.

### Tech Writer — Documentador Final
Gera via JSON estruturado (sem markdown livre):
- `README.md` com instruções Docker
- Diagrama de classes Mermaid (`classDiagram`)
- Diagrama de deploy Docker Mermaid (`flowchart TD`)
- `openapi.json` — contrato Swagger/OpenAPI v3

---

## 📂 Estrutura do Repositório

```
fabrica-software-ia/
│
├── .github/workflows/
│   └── deploy_hf.yml          # CI/CD: espelha automaticamente no Hugging Face Spaces
│
├── projetos_fabrica/          # Projetos gerados (Clean Arch por pasta)
│
├── .env                       # Chaves locais (nunca sobe para a nuvem)
├── Dockerfile                 # Container para o HF Spaces (SDK: docker)
├── requirements.txt           # Dependências da fábrica
├── grafo.py                   # Motor LangGraph — agentes, guardrails e failover
├── exporter.py                # Publica no GitHub com auto-criação de repo privado
├── enviar_chaves.py           # Utilitário para configurar variáveis no HF Spaces
├── index.html                 # Interface web (servida pelo FastAPI)
└── app.py                     # Servidor FastAPI — entrypoint do Hugging Face
```

---

## 🔄 Fluxo de Execução do LangGraph

```
[Chief Tier 0-1]
      │
      ▼
[Dev Tier 2] ◄──────────────────────────┐
      │                                  │ score < 80
      ▼                                  │
[Quality Gate Tier 3] ───────────────────┘
      │ score ≥ 80
      ▼
[SAST / Bandit] ──── falha ──► [Chief 0-1 retry]
      │ ok
      ▼
[Gerador de Testes QA]
      │
      ▼
[Executor PyTest Sandbox] ──── falha ──► [Chief 0-1 retry]
      │ ok
      ▼
[Tech Writer → README + Mermaid + OpenAPI]
      │
      ▼
[Exporter → GitHub + Disco]
```

---

## 🖥️ Modos de Operação (Interface Web)

| Modo | Descrição |
|------|-----------|
| **🏗️ Novo** | Requisitos em texto + anexos opcionais. Gera o projeto completo do zero. |
| **⚙️ Evoluir** | Seleciona projeto existente e descreve a nova funcionalidade a injetar. |
| **🚨 Debug** | Cola código quebrado + stack trace. Ciclo autônomo de diagnóstico e correção. |

### Anexos Suportados

| Tipo | Extensões | Processamento |
|------|-----------|---------------|
| Planilhas | `.csv`, `.xlsx` | Convertidas para Markdown e injetadas no contexto do Chief |
| Contratos | `.json`, `.yaml`, `.yml` | Injetados como especificação de API |
| Imagens | `.png`, `.jpg`, `.webp` | Analisadas via modelo de visão multimodal (`gemma-4-31b-it`) |

### Resposta em Tempo Real (SSE)
A interface recebe o log da esteira em **Server-Sent Events** — cada etapa do LangGraph aparece na tela assim que é concluída, sem polling.

---

## 📦 Saídas por Projeto

Cada projeto gerado em `projetos_fabrica/<nome>/` contém:

```
<nome>/
├── domain/             # Entidades puras (camada_dominio)
├── application/        # Casos de uso (camada_aplicacao)
├── infrastructure/
│   ├── database/       # ORM e persistência (camada_infra_banco)
│   └── web/            # Rotas HTTP (camada_infra_web)
├── tests/              # Suíte de testes gerada pelo QA
├── openapi.json        # Contrato Swagger/OpenAPI v3
└── README.md           # Manual com diagramas Mermaid e instruções Docker
```

---

## 🛠️ Configuração e Deploy

### 1. Secrets no GitHub (CI/CD)

Em **Settings → Secrets and variables → Actions**:

| Secret | Valor |
|--------|-------|
| `HF_TOKEN` | Token de escrita do Hugging Face |

### 2. Secrets no Hugging Face Spaces

Em **Settings → Variables and secrets** do seu Space:

| Variável | Descrição |
|----------|-----------|
| `OPENROUTER_API_KEY` | Chave(s) do OpenRouter — separe múltiplas por vírgula para rotação automática |
| `GOOGLE_API_KEY` | Chave da Google AI Studio (Gemini) — opcional |
| `LANGCHAIN_API_KEY` | Chave do LangSmith (rastreamento de execuções) |
| `LANGCHAIN_TRACING_V2` | `true` |
| `LANGCHAIN_PROJECT` | `fabrica-key-rotation` |
| `GITHUB_TOKEN` | Token Classic com escopo `repo` para publicação automática |
| `GITHUB_USER` | Seu nome de usuário do GitHub |

---

## 📊 Rastreamento com LangSmith

O LangSmith é a camada de **observabilidade** da fábrica. Toda execução do grafo LangGraph é automaticamente instrumentada — cada nó, cada chamada LLM e cada decisão de roteamento fica registrada no projeto `fabrica-key-rotation` em tempo real.

### O que exatamente é rastreado

O LangSmith captura o `EstadoEngenharia` completo (o TypedDict que trafega entre os nós do grafo) em cada transição. Na prática, para cada execução você vê:

#### Nó `chief` — Chief AI Officer
- **Entrada:** `requisito`, `codigo_legado`, `contexto_arquivos` (planilhas/contratos/visão de imagens), `linguagem_selecionada`, `framework_selecionado`
- **Saída:** `plano_do_chief` — o plano arquitetural completo gerado pelo Gemini 2.5 Flash Lite
- **LLM call:** prompt exato enviado ao `google/gemini-2.5-flash-lite` via OpenRouter + resposta bruta + tokens + latência

#### Nó `desenvolvedor` — Especialista Dev Tier 2
- **Entrada:** `plano_do_chief` + `historico_erros` (feedbacks de ciclos anteriores)
- **Saída:** objeto `ComponenteMultiLinguagem` com as 4 camadas de código em JSON estruturado
- **LLM call:** qual modelo foi usado (`deepseek-v4-pro`, `kimi-k2` ou `qwen3-coder-next`), quantas tentativas de failover ocorreram, esperas progressivas aplicadas (10s → 30s → 60s → 120s → 180s)
- **Fallback:** cada troca de modelo pelo `executar_com_failover` aparece como uma sub-run separada

#### Nó `quality_gate` — Auditor Semântico Tier 3
- **Entrada:** `camada_dominio` + `camada_aplicacao` + `camada_infra_web`
- **Saída:** `QualityReport` com `score_clean_code` (0–100), `score_arquitetura` (0–100) e `justificativa_critica`
- **Decisão de roteamento:** se a média dos scores for < 80, o roteador manda de volta ao `desenvolvedor` — cada ciclo de reprovação fica registrado com os scores exatos

#### Nó `sast` — Sandbox Bandit (Python)
- **Entrada:** as 4 camadas de código escritas em `app_code_temp.py`
- **Saída:** `returncode` do Bandit + stdout completo com as vulnerabilidades encontradas
- **Em caso de falha:** o log do Bandit é appended em `historico_erros` e o roteador dispara `chief_retry`

#### Nó `gerador_testes` — Agente QA
- **Entrada:** `camada_infra_web` (rotas HTTP do projeto)
- **Saída:** objeto `UnitTestComponent` com a suíte de testes completa em mock
- **LLM call:** chamada ao `gemini-2.5-flash-lite` com output estruturado via Pydantic

#### Nó `executor_pytest` — Runtime Sandbox
- **Entrada:** código de produção (`app_code.py`) + testes (`test_app.py`) escritos em disco
- **Saída:** `returncode` do PyTest + stdout com resultado de cada teste
- **Em caso de falha:** stderr/stdout do PyTest appended em `historico_erros`, roteador dispara `chief_retry`

### Custos visíveis no LangSmith

Como todos os modelos passam pelo OpenRouter, o LangSmith registra:

| Métrica | O que aparece |
|---------|---------------|
| **Tokens de entrada** | Tamanho do prompt por chamada — útil para ver quanto o código legado ou histórico de erros pesa no contexto |
| **Tokens de saída** | Tamanho do JSON gerado por camada de código |
| **Latência por nó** | Tempo de resposta de cada modelo — permite comparar deepseek vs kimi vs qwen na prática |
| **Número de retries** | Quantos ciclos quality_gate → desenvolvedor ocorreram até aprovação |
| **Total da run** | Tempo de ponta a ponta da esteira completa |

> O custo financeiro real é gerenciado pelo OpenRouter (não pelo LangSmith). O LangSmith mostra a contagem de tokens; o painel do OpenRouter em [openrouter.ai/activity](https://openrouter.ai/activity) mostra o custo em dólares por chamada.

### Como acessar

1. Acesse [smith.langchain.com](https://smith.langchain.com)
2. Selecione o projeto **`fabrica-key-rotation`**
3. Cada execução aparece como uma árvore com 6 nós expansíveis — clique em qualquer nó para ver o estado de entrada, saída e os prompts exatos enviados a cada modelo

### Como configurar

| Variável | Valor |
|----------|-------|
| `LANGCHAIN_API_KEY` | Chave gerada em smith.langchain.com → Settings → API Keys |
| `LANGCHAIN_TRACING_V2` | `true` para ativar, `false` para desativar sem alterar o código |
| `LANGCHAIN_PROJECT` | `fabrica-key-rotation` — nome do projeto no painel do LangSmith |

> **Erro 403 Forbidden:** a chave está inválida ou expirada. Gere uma nova em smith.langchain.com ou mude `LANGCHAIN_TRACING_V2` para `false` — a fábrica funciona normalmente sem rastreamento.

---

## 🏁 Como Rodar

### Localmente

```bash
# Clone e instale
git clone https://github.com/cleberdevs/fabrica-software-ia
cd fabrica-software-ia
pip install -r requirements.txt

# Configure as chaves
cp .env.example .env
# Preencha OPENROUTER_API_KEY, GITHUB_TOKEN, etc.

# Suba o servidor
python app.py
# Acesse: http://localhost:7860
```

### Deploy Contínuo (Hugging Face Spaces)

O Space usa **SDK: docker** com a porta `7860`. Qualquer push para `main` aciona o pipeline:

```bash
git add .
git commit -m "🚀 feat: atualização"
git push origin main
```

O GitHub Actions espelha o código e o Hugging Face reconstrói o container automaticamente.

### Dockerfile (necessário para SDK docker)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 7860
CMD ["python", "app.py"]
```

---

## 📋 Dependências Principais

```
fastapi
uvicorn[standard]
python-multipart
langgraph
langchain
langchain-openai
pandas
openpyxl
python-dotenv
pydantic
bandit
pytest
PyGithub
```

---

## 🔐 Segurança

- Nenhuma chave de API é exposta em código ou logs
- Arquivo `.env` listado no `.gitignore`
- Análise SAST com Bandit em todo código Python gerado
- Testes executados em subprocess isolado antes da escrita em disco
- Código só chega ao GitHub após aprovação em todos os guardrails

---

## 📄 Licença

MIT — use, adapte e contribua livremente.