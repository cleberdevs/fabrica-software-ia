---
title: Fábrica de Software IA Enterprise
emoji: 🏭
colorFrom: blue
colorTo: gray
sdk: streamlit
app_file: app.py
pinned: false
---

# 🏭 Fábrica de Software IA Enterprise (Gemini 2.5 + Qwen 3 Engine)

Uma plataforma de *Vibe Coding* industrial e resiliente projetada para o desenvolvimento, evolução incremental e manutenção de microsserviços e APIs corporativas em múltiplas linguagens. O ecossistema utiliza uma **Arquitetura Organizacional de IA por Tiers** orquestrada via **LangGraph**, blindada por portões determinísticos de qualidade (Quality Gates), sandbox de runtime e publicação automatizada na nuvem com criação de repositórios privados no GitHub [INDEX].

Esta versão está totalmente otimizada para rodar em produção no **Hugging Face Spaces** com deploy contínuo automatizado via **GitHub Actions**.

---

## 🎯 Objetivo do Ecossistema
Eliminar completamente as alucinações de escopo, falhas conceituais e brechas de cibersegurança comuns em geradores de código genéricos. Esta fábrica opera sob uma esteira de governança rigorosa e cíclica: o software gerado é testado fisicamente no terminal e auditado semanticamente. **O código só chega ao disco e ao GitHub se for 100% aprovado.**

---

## 🧠 Matriz Híbrida de Inteligência (Custo Zero de Tokens)
Para rodar projetos massivos e evoluções complexas sem custos de faturamento, a fábrica distribui os papéis entre os melhores modelos abertos e gratuitos de 2026:
*   **Tier 0 (Chief):** Controlado pelo **Gemini 2.5 Pro** (Janela massiva de contexto para engolir planilhas, especificações complexas e códigos legados inteiros) [INDEX].
*   **Tier 2 (Developer):** Controlado pelo **Qwen 3 Coder Free** (`qwen/qwen3-coder:free`) via OpenRouter (Modelo especialista em código aberto de altíssima performance estrutural) [INDEX].
*   **Tier 3, QA & Writer:** Controlados pelo **Gemini 2.5 Flash** (Velocidade ultra-rápida e custo zero para auditorias JSON, suítes de teste e documentação em Markdown) [INDEX].

---

## 🧰 Stacks de Tecnologia Homologadas (Multi-Language)
A esteira é agnóstico e adapta-se à tecnologia selecionada na interface gráfica em tempo real, gerando extensões físicas de arquivos, dependências e infraestruturas Docker nativas:
1.  **Python** ➔ Framework **FastAPI** (Banco SQLAlchemy + PyTest + Bandit)
2.  **TypeScript** ➔ Framework **Express** (Gerenciador npm/package.json + Jest)
3.  **Java** ➔ Framework **Spring Boot** (Gerenciador Maven/pom.xml)
4.  **C#** ➔ Framework **.NET Core** (Gerenciador .csproj)
5.  **Rust** ➔ Framework **Axum** (Gerenciador Cargo.toml)

---

## 🚀 Os 5 Agentes de IA em Ação (Hierarquia por Tiers)

*   **Tier 0 – Chief AI Officer (Orquestrador):** Consolida os prompts, especificações (Spec-Driven), planilhas de dados e imagens. Monta a arquitetura de dados e endpoints antes da primeira linha de código ser escrita.
*   **Tier 2 – Especialista Dev (Coder):** Traduz o plano do Chief em código fonte em **Clean Architecture** dividido estritamente em 4 camadas limpas (Domínio, Aplicação, Infra/Banco e Infra/Web).
*   **Tier 3 – Quality Support (Auditor Semântico):** Avalia o código do Dev e atribui notas de 0 a 100 para *Clean Code* (SOLID) e *Clean Arch* (isolamento). Códigos com médias inferiores a 80 são reprovados e devolvidos ao Dev para refatoração automática.
*   **Agente QA (Quality Assurance):** Cria suítes completas de testes unitários funcionais com mocks baseados estritamente nas rotas web geradas.
*   **Agente Tech Writer (Documentador):** Atua na ponta final gerando o arquivo contrato bruto `openapi.json` (Swagger) e o `README.md` explicativo contendo o manual do Docker e o **diagrama de dados interativo em formato Mermaid.js**.

---

## 📂 Estrutura de Pastas Padronizada (HF Spaces Standard)
```text
fabrica-agentes-ia/
│
├── .github/workflows/
│   └── deploy_hf.yml          # Pipeline de CI/CD para o Hugging Face Spaces
│
├── projetos_fabrica/          # Repositório central de sistemas gerados/legados
├── .env                       # Chaves privadas locais (Apenas para Codespaces/PC)
├── requirements.txt           # Dependências estruturais da fábrica (Padrão HF)
├── grafo.py                   # Motor e lógica do LangGraph cíclico
├── exporter.py                # Publicador físico com auto-create de repositórios no GitHub
└── app.py                     # Painel visual em Streamlit (Entrypoint Padrão HF)
```

---

## 🛠️ Configuração de Produção e Deploy Contínuo

### 1. Preparando os Secrets no GitHub
Para permitir que o GitHub Actions espelhe seu código no Hugging Face Spaces, gere um Token com permissão **Write** no Hugging Face e adicione-o nas configurações do seu repositório no GitHub (**Settings ➔ Secrets and variables ➔ Actions**):
*   `HF_TOKEN`: *(Seu token de escrita do Hugging Face)*

### 2. Configurando as Variáveis de Ambiente no Hugging Face Spaces
Nunca suba o arquivo `.env` para a nuvem. Dentro do painel do seu Space criado no Hugging Face, acesse a aba **Settings ➔ Variables and secrets** e cadastre de forma segura os seguintes *Secrets*:
*   `GOOGLE_API_KEY`: *(Sua chave gratuita do Gemini)*
*   `OPENROUTER_API_KEY`: *(Sua chave gratuita do OpenRouter)*
*   `LANGCHAIN_API_KEY`: *(Sua chave do LangSmith)*
*   `LANGCHAIN_TRACING_V2`: `true`
*   `LANGCHAIN_PROJECT`: `fabrica-key-rotation`
*   `GITHUB_TOKEN`: *(Seu Token Classic com escopo 'repo' ativado)*
*   `GITHUB_USER`: *(Seu nome de usuário do GitHub)*

---

## 🏁 Como Rodar

### Rodando Localmente (ou no Codespaces)
Certifique-se de que preencheu o seu `.env` local. Ative o painel com o comando padronizado:
```bash
streamlit run app.py
```

### Rodando em Produção (Hugging Face Spaces)
Sempre que fizer alterações no código, basta empurrar para o GitHub:
```bash
git add .
git commit -m "🚀 feat: deploy automatico via CI/CD"
git push origin main
```
O **GitHub Actions** interceptará o envio, executará o espelhamento e o Hugging Face compilará e deixará a sua fábrica online e segura em um link global estável!
