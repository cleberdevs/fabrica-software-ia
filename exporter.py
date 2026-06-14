"""
exporter.py — Publicador GitFlow da Fábrica de Software IA

Convenções de nomenclatura:
  Branch feature:  feature/<numero>/<nome-do-sistema>
  Branch fix:      fix/<numero>/<nome-do-sistema>
  Número de feature: contador sequencial por projeto em projetos_fabrica/<nome>/.feature_counter

Commits por camada (descritivos):
  feat(#1/nome): [dominio] entidades, value objects e contratos de interface
  feat(#1/nome): [aplicacao] casos de uso, servicos e regras de negocio
  feat(#1/nome): [infra/banco] persistencia, ORM e repositorios
  feat(#1/nome): [infra/web] rotas HTTP, controladores e middlewares <framework>
  feat(#1/nome): [testes] suite de testes unitarios com mocks — <linguagem>
  feat(#1/nome): [deps] arquivo de dependencias <dep_file> atualizado
  feat(#1/nome): [docs] README, openapi.json, Dockerfile e docker-compose
  feat(#1/nome): feature #1 <nome-do-sistema> finalizada ✅ [dd/mm/yyyy hh:mm]

Fluxo:
  ETAPA 1 — inicializar_repositorio_local(nome)   ← chamado ANTES do LangGraph
    → cria projetos_fabrica/<nome>/
    → incrementa projetos_fabrica/<nome>/.feature_counter
    → cria repo privado na conta pessoal do GitHub (/user/repos)
    → git init + branches main → develop → feature/<n>/<nome>
    → push das 3 branches para o GitHub
    → retorna (Path, numero_feature, nome_branch)

  ETAPA 2 — exportar_para_estrutura_clean_arch()  ← chamado APÓS todos os guardrails
    → escreve arquivos das 4 camadas Clean Architecture
    → 1 commit por camada com mensagem descritiva
    → commit de encerramento: feature #n <nome> finalizada ✅
    → push feature/<n>/<nome> → origin
    → abre Pull Request feature → develop via API GitHub
"""

import os
import re
import json
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime


# Tipos de operação em projetos existentes
TIPO_FEATURE  = "feature"   # evoluir — adiciona funcionalidade
TIPO_FIX      = "fix"       # debug   — corrige defeito
TIPO_REFACTOR = "refactor"  # refatorar — reestrutura sem mudar comportamento




# ── Contador de features ───────────────────────────────────────────────────

def _proximo_numero_feature(base: Path) -> int:
    """Lê e incrementa o contador de features do projeto em base/.feature_counter."""
    counter_file = base / ".feature_counter"
    base.mkdir(parents=True, exist_ok=True)
    try:
        n = int(counter_file.read_text().strip())
    except Exception:
        n = 0
    n += 1
    counter_file.write_text(str(n))
    return n


def _slug(nome: str) -> str:
    """Converte nome do projeto em slug seguro para branch git."""
    return re.sub(r"[^a-zA-Z0-9_-]", "-", nome).lower().strip("-")


def _nome_branch(numero: int, nome_projeto: str, fix: bool = False) -> str:
    """
    Gera nome da branch no padrão GitFlow:
      feature/1/meu-sistema
      fix/2/meu-sistema
    """
    prefix = "fix" if fix else "feature"
    return f"{prefix}/{numero}/{_slug(nome_projeto)}"


# ── Helpers Git ────────────────────────────────────────────────────────────

def _git(cmd: list, cwd: Path, check: bool = True) -> tuple[bool, str]:
    try:
        res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)
        return True, res.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[exporter] Git falhou ({' '.join(cmd)}): {e.stderr.strip()}")
        return False, e.stderr.strip()


def _commit(cwd: Path, mensagem: str) -> bool:
    ok, _ = _git(["git", "add", "."], cwd)
    ok, _ = _git(["git", "commit", "-m", mensagem], cwd)
    return ok


def _url_autenticada(user: str, token: str, repo: str) -> str:
    return f"https://{user}:{token}@github.com/{user}/{repo}.git"


# ── API GitHub ─────────────────────────────────────────────────────────────

def _gh_request(endpoint: str, token: str, payload: dict = None, method: str = "POST") -> dict | None:
    url = f"https://api.github.com{endpoint}"
    data = json.dumps(payload).encode("utf-8") if payload and method != "GET" else None
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "Fabrica-Software-IA",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"[exporter] Erro HTTP {e.code}: {e.read().decode('utf-8')}")
        return None


def _criar_repo_pessoal(nome: str, token: str) -> bool:
    """Cria repositório privado na conta pessoal (/user/repos, nunca /orgs/)."""
    r = _gh_request("/user/repos", token, {
        "name": nome,
        "description": "Microsserviço corporativo gerado pela Fábrica de Software IA.",
        "private": True,
        "auto_init": False,
    })
    if r:
        print(f"[exporter] Repositório pessoal criado: {r.get('html_url')}")
        return True
    return False


def _abrir_pull_request(nome_repo: str, token: str, user: str,
                        head: str, base: str, titulo: str, corpo: str) -> str | None:
    r = _gh_request(f"/repos/{user}/{nome_repo}/pulls", token, {
        "title": titulo,
        "body": corpo,
        "head": head,
        "base": base,
    })
    if r:
        url = r.get("html_url")
        print(f"[exporter] Pull Request aberto: {url}")
        return url
    return None


def _obter_numero_pr(nome_repo: str, token: str, user: str,
                     head: str, base: str) -> int | None:
    """Busca o número do PR aberto de head → base."""
    r = _gh_request(
        f"/repos/{user}/{nome_repo}/pulls?state=open&head={user}:{head}&base={base}",
        token, method="GET"
    )
    if r and isinstance(r, list) and len(r) > 0:
        return r[0].get("number")
    return None


def _merge_pull_request(nome_repo: str, token: str, user: str,
                        pr_number: int, commit_msg: str) -> bool:
    """Faz merge de um PR pelo número via API do GitHub."""
    r = _gh_request(
        f"/repos/{user}/{nome_repo}/pulls/{pr_number}/merge",
        token,
        {
            "commit_title": commit_msg,
            "merge_method": "merge",   # preserva histórico completo
        }
    )
    if r and r.get("merged"):
        return True
    print(f"[exporter] Merge PR #{pr_number} falhou: {r}")
    return False


# ── ETAPA 1 — Inicialização antecipada ────────────────────────────────────

def inicializar_repositorio_local(nome_projeto: str) -> tuple[Path, int, str]:
    """
    Chamado no INÍCIO da esteira, antes do LangGraph executar.

    Retorna (pasta, numero_feature, nome_branch) para que o app.py
    passe o numero_feature para a Etapa 2.
    """
    base = Path("projetos_fabrica") / nome_projeto
    base.mkdir(parents=True, exist_ok=True)
    print(f"[exporter] Pasta criada: {base}")

    numero   = _proximo_numero_feature(base)
    branch   = _nome_branch(numero, nome_projeto)
    token    = os.getenv("GITHUB_TOKEN", "")
    user     = os.getenv("GITHUB_USER", "")

    # .gitignore inicial
    gitignore = base / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(
            "__pycache__/\nnode_modules/\ntarget/\nbin/\nobj/\n*.pyc\n.env\n",
            encoding="utf-8"
        )

    if not (base / ".git").exists():
        _git(["git", "init"], base)
        _git(["git", "config", "user.email", "fabrica-ia@noreply.local"], base)
        _git(["git", "config", "user.name", "Fábrica de Software IA"], base)

        # main — commit inicial
        _git(["git", "checkout", "-b", "main"], base)
        _git(["git", "add", ".gitignore"], base)
        _git(["git", "commit", "-m",
              f"chore: repositório {nome_projeto} inicializado pela Fábrica IA"], base)

        # develop — a partir da main
        _git(["git", "checkout", "-b", "develop"], base)
        _git(["git", "commit", "--allow-empty", "-m",
              f"chore: branch develop criada — GitFlow de {nome_projeto}"], base)

        # feature/<n>/<nome> — a partir da develop
        _git(["git", "checkout", "-b", branch], base)
        _git(["git", "commit", "--allow-empty", "-m",
              f"chore: feature #{numero} {nome_projeto} aberta"], base)

    # Cria repo no GitHub (pessoal) e sobe as 3 branches
    if token and user:
        _criar_repo_pessoal(base.name, token)
        remote_url = _url_autenticada(user, token, base.name)
        _git(["git", "remote", "remove", "origin"], base, check=False)
        _git(["git", "remote", "add", "origin", remote_url], base)

        _git(["git", "checkout", "main"],    base)
        _git(["git", "push", "-u", "origin", "main"],    base)
        _git(["git", "checkout", "develop"], base)
        _git(["git", "push", "-u", "origin", "develop"], base)
        _git(["git", "checkout", branch],    base)
        _git(["git", "push", "-u", "origin", branch],    base)

        print(f"[exporter] GitFlow: main ← develop ← {branch}")

    return base, numero, branch


# ── ETAPA 1b — Abre nova branch em projeto existente (evoluir / debug / refatorar) ────

def abrir_branch_em_projeto_existente(
    nome_projeto: str,
    tipo: str = TIPO_FEATURE,   # "feature" | "fix" | "refactor"
) -> tuple[Path, int, str]:
    """
    Chamado no INÍCIO da esteira nos modos Evoluir, Debug e Refatorar.

    O projeto já existe em disco e no GitHub — não cria repo novo.
    Apenas:
      1. Incrementa o contador do projeto
      2. Faz checkout da develop (base do GitFlow)
      3. Cria nova branch <tipo>/<n>/<nome>
      4. Push da nova branch para o GitHub
      5. Retorna (pasta, numero_feature, nome_branch)
    """
    base = Path("projetos_fabrica") / nome_projeto
    if not base.exists():
        raise FileNotFoundError(f"Projeto '{nome_projeto}' não encontrado em projetos_fabrica/")

    numero = _proximo_numero_feature(base)
    branch = f"{tipo}/{numero}/{_slug(nome_projeto)}"
    token  = os.getenv("GITHUB_TOKEN", "")
    user   = os.getenv("GITHUB_USER", "")

    descricao = {
        TIPO_FEATURE:  "evolucao — nova funcionalidade",
        TIPO_FIX:      "correcao de defeito",
        TIPO_REFACTOR: "refatoracao — reestruturacao sem mudanca de comportamento",
    }.get(tipo, tipo)

    msg_abertura = f"chore: {tipo} #{numero} {nome_projeto} aberta para {descricao}"

    if (base / ".git").exists():
        _git(["git", "checkout", "develop"], base)
        _git(["git", "pull", "origin", "develop"], base, check=False)
        _git(["git", "checkout", "-b", branch], base)
        _git(["git", "commit", "--allow-empty", "-m", msg_abertura], base)
    else:
        _git(["git", "init"], base)
        _git(["git", "config", "user.email", "fabrica-ia@noreply.local"], base)
        _git(["git", "config", "user.name", "Fábrica de Software IA"], base)
        _git(["git", "checkout", "-b", "main"],    base)
        _git(["git", "checkout", "-b", "develop"], base)
        _git(["git", "checkout", "-b", branch],    base)
        _git(["git", "commit", "--allow-empty", "-m", msg_abertura], base)

    if token and user:
        remote_url = _url_autenticada(user, token, base.name)
        _git(["git", "remote", "remove", "origin"], base, check=False)
        _git(["git", "remote", "add", "origin", remote_url], base)
        _git(["git", "push", "-u", "origin", branch], base)
        print(f"[exporter] Branch aberta: {branch}")

    return base, numero, branch


# ── ETAPA 2 — Exportação final ─────────────────────────────────────────────

def exportar_para_estrutura_clean_arch(
    comp, teste, nome: str,
    docs: str, swagger: str,
    linguagem: str, framework: str,
    e_correcao: bool = False,
    numero_feature: int = 0,
    tipo_operacao: str = TIPO_FEATURE,   # "feature" | "fix" | "refactor"
) -> bool:
    """
    Chamado no FIM da esteira, após todos os guardrails aprovarem.

    Faz 1 commit por camada com mensagem descritiva, depois fecha a feature
    com commit de encerramento e abre PR → develop.
    """
    base = Path(nome)
    base.mkdir(parents=True, exist_ok=True)

    # Número da feature (usa o passado ou lê o contador do projeto)
    if numero_feature == 0:
        try:
            numero_feature = int((base / ".feature_counter").read_text().strip())
        except Exception:
            numero_feature = 1

    nome_projeto = base.name
    slug         = _slug(nome_projeto)
    scope        = f"#{numero_feature}/{slug}"
    branch       = f"{tipo_operacao}/{numero_feature}/{slug}"
    prefix       = tipo_operacao  # feat / fix / refactor nos commits

    # ── Garante que estamos na branch correta ─────────────────────────────
    if not (base / ".git").exists():
        _git(["git", "init"], base)
        _git(["git", "config", "user.email", "fabrica-ia@noreply.local"], base)
        _git(["git", "config", "user.name", "Fábrica de Software IA"], base)
        _git(["git", "checkout", "-b", "main"],    base)
        _git(["git", "checkout", "-b", "develop"], base)
        _git(["git", "checkout", "-b", branch],    base)
    else:
        _, current = _git(["git", "rev-parse", "--abbrev-ref", "HEAD"], base)
        if current != branch:
            _git(["git", "checkout", "-b", branch], base, check=False)
            _git(["git", "checkout", branch],        base, check=False)

    # ── Mapeamento de arquivos por linguagem ──────────────────────────────
    config_tech = {
        "Python":     {"ext": ".py",   "dep_file": "requirements.txt",
                       "src": base / "app",  "test": base / "tests" / "test_app.py"},
        "TypeScript": {"ext": ".ts",   "dep_file": "package.json",
                       "src": base / "src",  "test": base / "tests" / "app.test.ts"},
        "Java":       {"ext": ".java", "dep_file": "pom.xml",
                       "src": base / "src/main/java/com/company/app",
                       "test": base / "src/test/java/com/company/app/AppTest.java"},
        "C#":         {"ext": ".cs",   "dep_file": f"{base.name}.csproj",
                       "src": base / "src",  "test": base / "tests" / "AppTest.cs"},
        "Rust":       {"ext": ".rs",   "dep_file": "Cargo.toml",
                       "src": base / "src",  "test": base / "tests" / "app_test.rs"},
    }
    cfg = config_tech.get(linguagem, config_tech["Python"])
    ext = cfg["ext"]
    src = cfg["src"]

    if linguagem == "Java":
        ent_f = src / f"domain/Entities{ext}"
        srv_f = src / f"use_cases/Services{ext}"
        rep_f = src / f"adapters/Repository{ext}"
        web_f = src / f"adapters/HttpApi{ext}"
    else:
        ent_f = src / f"domain/entities{ext}"
        srv_f = src / f"use_cases/services{ext}"
        rep_f = src / f"adapters/repository{ext}"
        web_f = src / f"adapters/http_api{ext}"

    # ── Escreve e commita camada por camada ───────────────────────────────

    def _escrever_e_commitar(caminho: Path, conteudo: str, mensagem: str):
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(conteudo or "", encoding="utf-8")
        _commit(base, mensagem)

    _escrever_e_commitar(
        ent_f, comp.camada_dominio,
        f"{prefix}({scope}): [dominio] entidades, value objects e contratos de interface"
    )
    _escrever_e_commitar(
        srv_f, comp.camada_aplicacao,
        f"{prefix}({scope}): [aplicacao] casos de uso, servicos e regras de negocio"
    )
    _escrever_e_commitar(
        rep_f, comp.camada_infra_banco,
        f"{prefix}({scope}): [infra/banco] persistencia, ORM e repositorios"
    )
    _escrever_e_commitar(
        web_f, comp.camada_infra_web,
        f"{prefix}({scope}): [infra/web] rotas HTTP, controladores e middlewares {framework}"
    )

    # __init__.py para Python
    if linguagem == "Python":
        for d in [src / "domain", src / "use_cases", src / "adapters", base / "tests"]:
            d.mkdir(parents=True, exist_ok=True)
            init = d / "__init__.py"
            if not init.exists():
                init.write_text("", encoding="utf-8")

    # Testes
    test_path = cfg["test"]
    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.write_text(teste.codigo_teste or "", encoding="utf-8")
    _commit(base, f"{prefix}({scope}): [testes] suite de testes unitarios com mocks — {linguagem}")

    # Dependências
    dep_path = base / cfg["dep_file"]
    dep_path.write_text(comp.gerenciador_dependencias or "", encoding="utf-8")
    _commit(base, f"{prefix}({scope}): [deps] arquivo de dependencias {cfg['dep_file']} atualizado")

    # Docs e contratos
    (base / "README.md").write_text(docs or "", encoding="utf-8")
    (base / "openapi.json").write_text(swagger or "", encoding="utf-8")

    # Dockerfiles
    dockerfiles = {
        "Python":     'FROM python:3.11-slim\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nEXPOSE 8000\nCMD ["uvicorn", "app.adapters.http_api:app", "--host", "0.0.0.0", "--port", "8000"]',
        "TypeScript": 'FROM node:20-slim\nWORKDIR /app\nCOPY . .\nRUN npm install && npm run build\nEXPOSE 3000\nCMD ["node", "dist/main.js"]',
        "Java":       "FROM maven:3.9-eclipse-temurin-21 AS build\nWORKDIR /app\nCOPY . .\nRUN mvn clean package -DskipTests\nFROM eclipse-temurin:21-jre-jammy\nCOPY --from=build /app/target/*.jar app.jar\nEXPOSE 8080\nCMD [\"java\", \"-jar\", \"app.jar\"]",
        "C#":         "FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build\nWORKDIR /app\nCOPY . .\nRUN dotnet publish -c Release -o out\nFROM mcr.microsoft.com/dotnet/aspnet:8.0\nWORKDIR /app\nCOPY --from=build /app/out .\nEXPOSE 5000\nCMD [\"dotnet\", \"app.dll\"]",
        "Rust":       "FROM rust:1.78 AS build\nWORKDIR /app\nCOPY . .\nRUN cargo build --release\nFROM debian:bookworm-slim\nCOPY --from=build /app/target/release/app /usr/local/bin/app\nEXPOSE 8080\nCMD [\"app\"]",
    }
    (base / "Dockerfile").write_text(dockerfiles.get(linguagem, dockerfiles["Python"]), encoding="utf-8")
    (base / "docker-compose.yml").write_text(
        "version: '3.8'\nservices:\n  web_api:\n    build: .\n    ports: [\"8000:8000\"]\n"
        "    depends_on:\n      db_postgres:\n        condition: service_healthy\n"
        "  db_postgres:\n    image: postgres:16-alpine\n"
        "    environment:\n      POSTGRES_USER: user\n      POSTGRES_PASSWORD: pass\n      POSTGRES_DB: db_app\n"
        "    ports: [\"5432:5432\"]\n"
        "    healthcheck:\n      test: [\"CMD-SHELL\", \"pg_isready -U user -d db_app\"]\n"
        "      interval: 5s\n      timeout: 5s\n      retries: 5\n",
        encoding="utf-8"
    )
    _commit(base, f"{prefix}({scope}): [docs] README, openapi.json, Dockerfile e docker-compose")

    # ── Commit de encerramento ─────────────────────────────────────────────
    ts = datetime.now().strftime("%d/%m/%Y %H:%M")
    descricao_encerramento = {
        TIPO_FEATURE:  "finalizada",
        TIPO_FIX:      "correcao finalizada",
        TIPO_REFACTOR: "refatoracao finalizada",
    }.get(tipo_operacao, "finalizada")

    msg_final = f"{prefix}({scope}): {tipo_operacao} #{numero_feature} {nome_projeto} {descricao_encerramento} ✅ [{ts}]"
    _git(["git", "commit", "--allow-empty", "-m", msg_final], base)
    print(f"[exporter] {msg_final}")

    # ── Push e Pull Request ───────────────────────────────────────────────
    token = os.getenv("GITHUB_TOKEN", "")
    user  = os.getenv("GITHUB_USER", "")

    if not (token and user):
        print("[exporter] GITHUB_TOKEN/GITHUB_USER não configurados — pulando push.")
        return False

    remote_url = _url_autenticada(user, token, base.name)
    _git(["git", "remote", "remove", "origin"], base, check=False)
    _git(["git", "remote", "add", "origin", remote_url], base)

    ok, _ = _git(["git", "push", "-u", "origin", branch], base)
    if not ok:
        print(f"[exporter] Push falhou para {branch}.")
        return False

    # Emoji e título do PR por tipo de operação
    emoji_pr = {"feature": "🚀", "fix": "🔧", "refactor": "♻️"}.get(tipo_operacao, "🚀")
    label_pr = {
        TIPO_FEATURE:  f"feat #{numero_feature}: {nome_projeto}",
        TIPO_FIX:      f"fix #{numero_feature}: Correção — {nome_projeto}",
        TIPO_REFACTOR: f"refactor #{numero_feature}: Refatoração — {nome_projeto}",
    }.get(tipo_operacao, f"feat #{numero_feature}: {nome_projeto}")

    titulo_pr = f"{emoji_pr} {label_pr} [{linguagem}/{framework}]"

    nota_pr = {
        TIPO_FEATURE:  "Esta branch adiciona nova funcionalidade. Revisar endpoints e casos de uso.",
        TIPO_FIX:      "Esta branch corrige um defeito. Confirmar que os testes de regressão passam.",
        TIPO_REFACTOR: "⚠️ Esta branch reestrutura o código sem alterar o comportamento externo. Confirmar que todos os testes existentes continuam passando após o merge.",
    }.get(tipo_operacao, "")

    corpo_pr = (
        f"## {tipo_operacao.capitalize()} #{numero_feature} — {nome_projeto}\n\n"
        f"| Campo | Valor |\n|-------|-------|\n"
        f"| **Tipo** | {tipo_operacao} |\n"
        f"| **Stack** | {linguagem} / {framework} |\n"
        f"| **Branch** | `{branch}` → `develop` |\n"
        f"| **Gerado em** | {ts} |\n\n"
        f"### Commits desta branch\n"
        f"- `[dominio]` entidades, value objects e contratos de interface\n"
        f"- `[aplicacao]` casos de uso, serviços e regras de negócio\n"
        f"- `[infra/banco]` persistência, ORM e repositórios\n"
        f"- `[infra/web]` rotas HTTP, controladores e middlewares {framework}\n"
        f"- `[testes]` suíte de testes unitários com mocks\n"
        f"- `[deps]` arquivo de dependências\n"
        f"- `[docs]` README, OpenAPI v3, Dockerfile e docker-compose\n"
        f"- ✅ {tipo_operacao} #{numero_feature} {nome_projeto} {descricao_encerramento}\n\n"
        f"### Guardrails aprovados\n"
        f"- ✅ Quality Gate — score ≥ 80 em Clean Code e Clean Architecture\n"
        f"- ✅ SAST Bandit — sem vulnerabilidades de segurança\n"
        f"- ✅ PyTest Sandbox — todos os testes passaram\n\n"
        f"> {nota_pr}\n\n"
        f"> Após o merge em `develop`, abra PR de `develop` → `main` para produção."
    )

    pr_url = _abrir_pull_request(
        nome_repo=base.name,
        token=token, user=user,
        head=branch, base="develop",
        titulo=titulo_pr, corpo=corpo_pr,
    )

    if not pr_url:
        return False

    # ── Merge automático: feature → develop ──────────────────────────────
    pr_number = _obter_numero_pr(base.name, token, user, branch, "develop")
    if pr_number:
        merged = _merge_pull_request(base.name, token, user, pr_number,
                                     f"Merge automático: {branch} → develop")
        if merged:
            print(f"[exporter] ✅ Merge concluído: {branch} → develop")
            print(f"[exporter] 📋 PR develop → main disponível para revisão manual no GitHub")

    return True