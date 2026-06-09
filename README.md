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