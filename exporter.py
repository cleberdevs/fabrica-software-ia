import os, subprocess, json, urllib.request
from pathlib import Path


def _detectar_tipo_owner(owner: str, token: str) -> str:
    """Retorna 'org' se o owner for uma organização, 'user' caso contrário."""
    try:
        req = urllib.request.Request(
            f"https://api.github.com/users/{owner}",
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Fabrica-Agentes-IA"
            }
        )
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            return "org" if data.get("type") == "Organization" else "user"
    except Exception:
        return "user"


def criar_repositorio_remoto_no_github(nome_repo: str, token: str) -> bool:
    owner = os.getenv("GITHUB_USER", "")
    tipo  = _detectar_tipo_owner(owner, token) if owner else "user"

    # Organização usa /orgs/{org}/repos, usuário pessoal usa /user/repos
    if tipo == "org" and owner:
        url = f"https://api.github.com/orgs/{owner}/repos"
        print(f"[exporter] Criando repo em organização: {owner}")
    else:
        url = "https://api.github.com/user/repos"
        print(f"[exporter] Criando repo em conta pessoal")

    payload = json.dumps({
        "name":        nome_repo,
        "description": "Microservico corporativo multinivel gerado por Fabrica AI.",
        "private":     True
    }).encode("utf-8")
    headers = {
        "Authorization": f"token {token}",
        "Accept":        "application/vnd.github.v3+json",
        "User-Agent":    "Fabrica-Agentes-IA"
    }
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as res:
            sucesso = res.status == 201
            if sucesso:
                print(f"[exporter] Repo criado com sucesso.")
            return sucesso
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 422 and "already exists" in body:
            print(f"[exporter] Repo ja existe — prosseguindo com push.")
            return True
        print(f"[exporter] Erro HTTP {e.code}: {body[:200]}")
        return False
    except Exception as e:
        print(f"[exporter] Erro ao criar repositorio: {e}")
        return False


def executar_git(cmd, cwd):
    try:
        subprocess.run(cmd, cwd=cwd, capture_output=True, check=True)
        return True
    except Exception as e:
        print(f"[exporter] Git falhou ({' '.join(str(c) for c in cmd)}): {e}")
        return False


def exportar_para_estrutura_clean_arch(comp, teste, nome, docs, swagger, linguagem, framework, e_correcao=False):
    base_dir = Path(nome)
    base_dir.mkdir(parents=True, exist_ok=True)

    config_tech = {
        "Python": {
            "ext":       ".py",
            "dep_file":  "requirements.txt",
            "src_path":  base_dir / "app",
            "test_path": base_dir / "tests" / "test_app.py"
        },
        "TypeScript": {
            "ext":       ".ts",
            "dep_file":  "package.json",
            "src_path":  base_dir / "src",
            "test_path": base_dir / "tests" / "app.test.ts"
        },
        "Java": {
            "ext":       ".java",
            "dep_file":  "pom.xml",
            "src_path":  base_dir / "src" / "main" / "java" / "com" / "company" / "app",
            "test_path": base_dir / "src" / "test" / "java" / "com" / "company" / "app" / "AppTest.java"
        },
        "C#": {
            "ext":       ".cs",
            "dep_file":  f"{base_dir.name}.csproj",
            "src_path":  base_dir / "src",
            "test_path": base_dir / "tests" / "AppTest.cs"
        },
        "Rust": {
            "ext":       ".rs",
            "dep_file":  "Cargo.toml",
            "src_path":  base_dir / "src",
            "test_path": base_dir / "tests" / "app_test.rs"
        }
    }

    cfg = config_tech.get(linguagem, config_tech["Python"])
    ext = cfg["ext"]
    src = cfg["src_path"]

    if linguagem != "Java":
        ent_f = src / f"domain/entities{ext}"
        srv_f = src / f"use_cases/services{ext}"
        rep_f = src / f"adapters/repository{ext}"
        web_f = src / f"adapters/http_api{ext}"
    else:
        ent_f = src / "domain"    / f"Entities{ext}"
        srv_f = src / "use_cases" / f"Services{ext}"
        rep_f = src / "adapters"  / f"Repository{ext}"
        web_f = src / "adapters"  / f"HttpApi{ext}"

    mapeamento = {
        ent_f:                              comp.camada_dominio,
        srv_f:                              comp.camada_aplicacao,
        rep_f:                              comp.camada_infra_banco,
        web_f:                              comp.camada_infra_web,
        cfg["test_path"]:                   teste.codigo_teste,
        base_dir / "README.md":             docs,
        base_dir / "openapi.json":          swagger,
        base_dir / cfg["dep_file"]:         comp.gerenciador_dependencias
    }

    for caminho, conteudo in mapeamento.items():
        caminho = Path(caminho)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(conteudo, encoding="utf-8")
        # Cria __init__.py para pacotes Python
        if linguagem == "Python" and caminho.suffix == ".py" and caminho.name != "test_app.py":
            init = caminho.parent / "__init__.py"
            if not init.exists():
                init.write_text("", encoding="utf-8")

    dockerfiles = {
        "Python":     "FROM python:3.11-slim\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD [\"python\", \"main.py\"]",
        "TypeScript": "FROM node:18-slim\nWORKDIR /app\nCOPY . .\nRUN npm install && npm run build\nCMD [\"node\", \"dist/main.js\"]",
        "Java":       "FROM maven:3.8-openjdk-17 AS build\nWORKDIR /app\nCOPY . .\nRUN mvn clean package\nFROM openjdk:17-slim\nCOPY --from=build /app/target/*.jar app.jar\nCMD [\"java\", \"-jar\", \"app.jar\"]",
        "C#":         "FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build\nWORKDIR /app\nCOPY . .\nRUN dotnet publish -c Release -o out\nFROM mcr.microsoft.com/dotnet/aspnet:8.0\nWORKDIR /app\nCOPY --from=build /app/out .\nCMD [\"dotnet\", \"app.dll\"]",
        "Rust":       "FROM rust:1.70 AS build\nWORKDIR /app\nCOPY . .\nRUN cargo build --release\nFROM debian:bullseye-slim\nCOPY --from=build /app/target/release/app /app\nCMD [\"/app\"]"
    }

    (base_dir / "Dockerfile").write_text(
        dockerfiles.get(linguagem, dockerfiles["Python"]), encoding="utf-8"
    )

    (base_dir / "docker-compose.yml").write_text(
        "version: '3.8'\n"
        "services:\n"
        "  web_api:\n"
        "    build: .\n"
        "    ports: [\"8000:8000\"]\n"
        "    depends_on:\n"
        "      db_postgres:\n"
        "        condition: service_healthy\n"
        "  db_postgres:\n"
        "    image: postgres:15-alpine\n"
        "    environment:\n"
        "      - POSTGRES_USER=user\n"
        "      - POSTGRES_PASSWORD=pass\n"
        "      - POSTGRES_DB=db_app\n"
        "    ports: [\"5432:5432\"]\n"
        "    healthcheck:\n"
        "      test: [\"CMD-SHELL\", \"pg_isready -U user -d db_app\"]\n"
        "      interval: 5s\n"
        "      timeout: 5s\n"
        "      retries: 5\n",
        encoding="utf-8"
    )

    # ── Git local ────────────────────────────────────────────────────────────
    if not (base_dir / ".git").exists():
        executar_git(["git", "init"], base_dir)
        executar_git(["git", "checkout", "-b", "main"], base_dir)

    with open(base_dir / ".gitignore", "w") as f:
        f.write("__pycache__/\nnode_modules/\ntarget/\nbin/\nobj/\n*.pyc\n.env\n")

    executar_git(["git", "add", "."], base_dir)
    msg_commit = f"🔧 fix: patch [{framework}]" if e_correcao else f"🚀 feat: init [{linguagem}/{framework}]"
    executar_git(["git", "commit", "-m", msg_commit], base_dir)

    # ── Push para o GitHub ───────────────────────────────────────────────────
    tk = os.getenv("GITHUB_TOKEN")
    us = os.getenv("GITHUB_USER")

    if tk and us:
        repo_name = base_dir.name
        if not e_correcao:
            criar_repositorio_remoto_no_github(repo_name, tk)
            # Remove remote antigo se existir (idempotente)
            executar_git(["git", "remote", "remove", "origin"], base_dir)
            # URL autenticada correta
            remote_url = f"https://{us}:{tk}@github.com/{us}/{repo_name}.git"
            executar_git(["git", "remote", "add", "origin", remote_url], base_dir)

        # Garante que o remote está correto mesmo em modo correção
        remote_url = f"https://{us}:{tk}@github.com/{us}/{repo_name}.git"
        executar_git(["git", "remote", "set-url", "origin", remote_url], base_dir)

        return executar_git(["git", "push", "-u", "origin", "main"], base_dir)

    return False