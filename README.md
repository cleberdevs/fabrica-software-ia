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

Suporta geração, evolução incremental, debug e refatoração de microsserviços corporativos em **5 linguagens**, com publicação automatizada no GitHub seguindo o fluxo **GitFlow completo**.

---

## 🧠 Matriz Híbrida de Modelos (via OpenRouter)

| Tier | Papel | Modelo |
|------|-------|--------|
| **Tier 0-1** | Chief AI Officer — Orquestrador arquitetural + Arquiteto | `google/gemini-2.5-flash-lite` |
| **Tier 2** | Especialista Dev — Geração de código multi-camada | `deepseek/deepseek-v4-pro` → `moonshot/kimi-k2` → `qwen/qwen3-coder-next` *(fallback automático)* |
| **Tier 3 / QA** | Quality Gate, Testes e Documentação | `google/gemini-2.5-flash-lite` |
| **Visão** | Análise multimodal de imagens e diagramas | `google/gemma-4-31b-it:free` |

> **Fallback inteligente:** o Tier 2 faz fallback automático em caso de rate limit (429) **e** créditos insuficientes (402) — tenta `deepseek-v4-pro` → `kimi-k2` → `qwen3-coder-next` sem intervenção manual. Para rate limit aplica espera progressiva (10s → 30s → 60s → 120s → 180s); para 402 vai direto ao modelo mais barato sem espera.

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

Possui **fallback automático** entre modelos com tratamento de rate limit (429) e créditos insuficientes (402).

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
- Diagrama de classes Mermaid (`classDiagram`) — labels sanitizados para compatibilidade total
- Diagrama de deploy Docker Mermaid (`flowchart TD`) — labels sanitizados para compatibilidade total
- `openapi.json` — contrato Swagger/OpenAPI v3

---

## 🔀 GitFlow Automatizado

A fábrica implementa GitFlow completo com numeração sequencial de features **por projeto**.

### Nomenclatura de branches

| Modo | Branch criada | Prefixo de commit |
|------|--------------|-------------------|
| **Novo** | `feature/<n>/<nome>` | `feat` |
| **Evoluir** | `feature/<n>/<nome>` | `feat` |
| **Debug** | `fix/<n>/<nome>` | `fix` |
| **Refatorar** | `refactor/<n>/<nome>` | `refactor` |

O número `<n>` é sequencial por projeto, armazenado em `projetos_fabrica/<nome>/.feature_counter`.

### Fluxo completo por execução

```
INÍCIO DA ESTEIRA
  ↓
Cria pasta + repo privado no GitHub (conta pessoal)
  ↓
git init → main → develop → feature/<n>/<nome>
  ↓
[LangGraph executa — Chief → Dev → QA → SAST → Testes]
  ↓
FIM DA ESTEIRA (guardrails aprovados)
  ↓
1 commit por camada com mensagem descritiva:
  feat(#1/nome): [dominio] entidades, value objects e contratos de interface
  feat(#1/nome): [aplicacao] casos de uso, servicos e regras de negocio
  feat(#1/nome): [infra/banco] persistencia, ORM e repositorios
  feat(#1/nome): [infra/web] rotas HTTP, controladores e middlewares
  feat(#1/nome): [testes] suite de testes unitarios com mocks
  feat(#1/nome): [deps] arquivo de dependencias atualizado
  feat(#1/nome): [docs] README, openapi.json, Dockerfile e docker-compose
  feat(#1/nome): feature #1 nome finalizada ✅ [dd/mm/yyyy hh:mm]
  ↓
Push feature/<n>/<nome> → origin
  ↓
PR aberto: feature/<n>/<nome> → develop
  ↓
Merge automático: feature → develop ✅
  ↓
PR develop → main fica disponível para revisão manual
```

### Repositório no GitHub — o que você verá

Após a execução, o repositório gerado terá:

```
main        ← produção (você faz o merge manualmente)
develop     ← integração (merge automático da feature)
feature/1/nome  ← branch da fábrica (mergeada no develop)
```

---

## 🖥️ Modos de Operação (Interface Web)

| Modo | Branch | Descrição |
|------|--------|-----------|
| **🏗️ Novo** | `feature/<n>/<nome>` | Cria repo + gera projeto completo do zero |
| **⚙️ Evoluir** | `feature/<n>/<nome>` | Adiciona nova funcionalidade ao projeto existente |
| **🚨 Debug** | `fix/<n>/<nome>` | Corrige defeito com stack trace fornecido |
| **♻️ Refatorar** | `refactor/<n>/<nome>` | Reestrutura código sem alterar comportamento externo |

### Refatoração — instrução opcional
No modo Refatorar, o campo de instrução é opcional. Se deixado vazio, a fábrica aplica automaticamente SOLID, DRY, KISS e Clean Architecture. Se preenchido, usa a instrução do usuário como foco prioritário — mantendo sempre as regras de não alterar contratos de API e manter testes passando.

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
├── .feature_counter    # Contador sequencial de features do projeto
├── .gitignore
├── app/
│   ├── domain/         # Entidades puras (camada_dominio)
│   ├── use_cases/      # Casos de uso (camada_aplicacao)
│   └── adapters/
│       ├── repository  # ORM e persistência (camada_infra_banco)
│       └── http_api    # Rotas HTTP (camada_infra_web)
├── tests/              # Suíte de testes gerada pelo QA
├── openapi.json        # Contrato Swagger/OpenAPI v3
├── requirements.txt    # Dependências do projeto
├── Dockerfile          # Container do projeto gerado
├── docker-compose.yml  # Stack completa com PostgreSQL
└── README.md           # Manual com diagramas Mermaid e instruções Docker
```

---

## 📂 Estrutura do Repositório da Fábrica

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
├── exporter.py                # GitFlow + publicação no GitHub
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
[Exporter → GitFlow → GitHub]
      │
      ├── feature/<n>/<nome> → develop  (merge automático)
      └── develop → main                (revisão manual)
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
| `LANGCHAIN_TRACING_V2` | `true` para ativar, `false` para desativar |
| `LANGCHAIN_PROJECT` | `fabrica-key-rotation` |
| `GITHUB_TOKEN` | Token Classic com escopo `repo` — gerado na conta pessoal em github.com/settings/tokens |
| `GITHUB_USER` | Seu nome de usuário pessoal do GitHub |

> **Atenção:** o `GITHUB_TOKEN` deve ser gerado estando logado na sua **conta pessoal** (não em uma organização). Tokens gerados em contexto de organização retornam 403 ao tentar criar repositórios via `/user/repos`.

---

## 📊 Rastreamento com LangSmith

O LangSmith é a camada de **observabilidade** da fábrica. Toda execução do grafo LangGraph é automaticamente instrumentada — cada nó, cada chamada LLM e cada decisão de roteamento fica registrada no projeto `fabrica-key-rotation` em tempo real.

### O que exatamente é rastreado

O LangSmith captura o `EstadoEngenharia` completo (o TypedDict que trafega entre os nós do grafo) em cada transição. Na prática, para cada execução você vê:

#### Nó `chief` — Chief AI Officer
- **Entrada:** `requisito`, `codigo_legado`, `contexto_arquivos`, `linguagem_selecionada`, `framework_selecionado`
- **Saída:** `plano_do_chief` — o plano arquitetural completo gerado pelo Gemini 2.5 Flash Lite
- **LLM call:** prompt exato + resposta bruta + tokens + latência

#### Nó `desenvolvedor` — Especialista Dev Tier 2
- **Entrada:** `plano_do_chief` + `historico_erros`
- **Saída:** objeto `ComponenteMultiLinguagem` com as 4 camadas em JSON estruturado
- **LLM call:** qual modelo foi usado, quantas tentativas de failover (429 ou 402), esperas aplicadas
- **Fallback:** cada troca de modelo aparece como sub-run separada

#### Nó `quality_gate` — Auditor Semântico Tier 3
- **Entrada:** `camada_dominio` + `camada_aplicacao` + `camada_infra_web`
- **Saída:** `QualityReport` com `score_clean_code` (0–100), `score_arquitetura` (0–100) e `justificativa_critica`
- **Decisão de roteamento:** ciclos de reprovação (score < 80) registrados com scores exatos

#### Nó `sast` — Sandbox Bandit
- **Entrada:** 4 camadas escritas em `app_code_temp.py`
- **Saída:** `returncode` do Bandit + stdout com vulnerabilidades

#### Nó `gerador_testes` — Agente QA
- **Entrada:** `camada_infra_web`
- **Saída:** `UnitTestComponent` com suíte de testes completa

#### Nó `executor_pytest` — Runtime Sandbox
- **Entrada:** `app_code.py` + `test_app.py` em disco
- **Saída:** `returncode` do PyTest + stdout com resultado de cada teste

### Custos visíveis no LangSmith

| Métrica | O que aparece |
|---------|---------------|
| **Tokens de entrada** | Tamanho do prompt por chamada |
| **Tokens de saída** | Tamanho do JSON gerado por camada |
| **Latência por nó** | Tempo de resposta de cada modelo |
| **Número de retries** | Ciclos quality_gate → desenvolvedor até aprovação |
| **Total da run** | Tempo de ponta a ponta da esteira completa |

> O custo financeiro real é gerenciado pelo OpenRouter. O painel em [openrouter.ai/activity](https://openrouter.ai/activity) mostra o custo em dólares por chamada.

### Como configurar

| Variável | Valor |
|----------|-------|
| `LANGCHAIN_API_KEY` | Chave gerada em smith.langchain.com → Settings → API Keys |
| `LANGCHAIN_TRACING_V2` | `true` para ativar, `false` para desativar |
| `LANGCHAIN_PROJECT` | `fabrica-key-rotation` |

> **Erro 403 Forbidden:** chave inválida ou expirada. Gere uma nova em smith.langchain.com ou mude `LANGCHAIN_TRACING_V2` para `false`.

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
# Preencha OPENROUTER_API_KEY, GITHUB_TOKEN, GITHUB_USER etc.

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

### Dockerfile

```dockerfile
FROM python:3.11
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"
WORKDIR /app
COPY --chown=user requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY --chown=user . /app
RUN mkdir -p /app/projetos_fabrica
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
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
- `GITHUB_TOKEN` nunca é logado — usado apenas em URLs autenticadas em memória
- Análise SAST com Bandit em todo código Python gerado
- Testes executados em subprocess isolado antes da escrita em disco
- Código só chega ao GitHub após aprovação em todos os guardrails

---

## 📄 Licença

MIT — use, adapte e contribua livremente.