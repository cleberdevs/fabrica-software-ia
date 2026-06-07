import os, subprocess, json, urllib.request
from pathlib import Path

def criar_repositorio_remoto_no_github(nome_repo: str, token: str) -> bool:
    url = "https://github.com"
    payload = json.dumps({"name": nome_repo, "description": "Microservico corporativo multinivel gerado por Fabrica AI.", "private": True}).encode("utf-8")
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json", "User-Agent": "Fabrica-Agentes-IA"}
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as res: return res.status == 201
    except: return False

def executar_git(cmd, cwd):
    try: subprocess.run(cmd, cwd=cwd, capture_output=True, check=True); return True
    except: return False

def exportar_para_estrutura_clean_arch(comp, teste, nome, docs, swagger, linguagem, framework, e_correcao=False):
    base_dir = Path(nome); base_dir.mkdir(parents=True, exist_ok=True)
    
    config_tech = {
        "Python": {"ext": ".py", "dep_file": "requirements.txt", "src_path": base_dir / "app", "test_path": base_dir / "tests" / "test_app.py"},
        "TypeScript": {"ext": ".ts", "dep_file": "package.json", "src_path": base_dir / "src", "test_path": base_dir / "tests" / "app.test.ts"},
        "Java": {"ext": ".java", "dep_file": "pom.xml", "src_path": base_dir / "src" / "main" / "java" / "com" / "company" / "app", "test_path": base_dir / "src" / "test" / "java" / "com" / "company" / "app" / "AppTest.java"},
        "C#": {"ext": ".cs", "dep_file": f"{base_dir.name}.csproj", "src_path": base_dir / "src", "test_path": base_dir / "tests" / "AppTest.cs"},
        "Rust": {"ext": ".rs", "dep_file": "Cargo.toml", "src_path": base_dir / "src", "test_path": base_dir / "tests" / "app_test.rs"}
    }
    
    cfg = config_tech.get(linguagem, config_tech["Python"])
    ext = cfg["ext"]
    src = cfg["src_path"]
    
    ent_f = src / f"domain/entities{ext}" if linguagem != "Java" else src / "domain" / f"Entities{ext}"
    srv_f = src / f"use_cases/services{ext}" if linguagem != "Java" else src / "use_cases" / f"Services{ext}"
    rep_f = src / f"adapters/repository{ext}" if linguagem != "Java" else src / "adapters" / f"Repository{ext}"
    web_f = src / f"adapters/http_api{ext}" if linguagem != "Java" else src / "adapters" / f"HttpApi{ext}"
    
    mapeamento = {
        ent_f: comp.camada_dominio,
        srv_f: comp.camada_aplicacao,
        rep_f: comp.camada_infra_banco,
        web_f: comp.camada_infra_web,
        cfg["test_path"]: teste.codigo_teste,
        base_dir / "README.md": docs,
        base_dir / "openapi.json": swagger,
        base_dir / cfg["dep_file"]: comp.gerenciador_dependencias
    }
    
    for caminho, conteudo in mapeamento.items():
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(conteudo, encoding="utf-8")
        if linguagem in ["Python", "TypeScript"] and caminho.name != "package.json":
            (caminho.parent / "__init__.py" if linguagem == "Python" else caminho.parent).mkdir(parents=True, exist_ok=True)

    dockerfiles = {
        "Python": "FROM python:3.11-slim\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD python main.py",
        "TypeScript": "FROM node:18-slim\nWORKDIR /app\nCOPY . .\nRUN npm install && npm run build\nCMD [\"node\", \"dist/main.js\"]",
        "Java": "FROM maven:3.8-openjdk-17 AS build\nWORKDIR /app\nCOPY . .\nRUN mvn clean package\nFROM openjdk:17-slim\nCOPY --from=build /app/target/*.jar app.jar\nCMD [\"java\", \"-jar\", \"app.jar\"]",
        "C#": "FROM ://microsoft.com AS build\nWORKDIR /app\nCOPY . .\nRUN dotnet publish -c Release -o out\nFROM ://microsoft.com\nWORKDIR /app\nCOPY --from=build /app/out .\nCMD [\"dotnet\", \"app.dll\"]",
        "Rust": "FROM rust:1.70 AS build\nWORKDIR /app\nCOPY . .\nRUN cargo build --release\nFROM debian:bullseye-slim\nCOPY --from=build /app/target/release/app /app\nCMD [\"/app\"]"
    }
    
    (base_dir / "Dockerfile").write_text(dockerfiles.get(linguagem, dockerfiles["Python"]), encoding="utf-8")
    (base_dir / "docker-compose.yml").write_text(f"version: '3.8'\nservices:\n  web_api:\n    build: .\n    ports: [\"8000:8000\"]\n    depends_on:\n      db_postgres:\n        condition: service_healthy\n  db_postgres:\n    image: postgres:15-alpine\n    environment: [POSTGRES_USER=user, POSTGRES_PASSWORD=pass, POSTGRES_DB=db_app]\n    ports: [\"5432:5432\"]\n    healthcheck:\n      test: [\"CMD-SHELL\", \"pg_isready -U user -d db_app\"]\n      interval: 5s\n      timeout: 5s\n      retries: 5", encoding="utf-8")

    if not (base_dir / ".git").exists(): 
        executar_git(["git", "init"], base_dir)
        executar_git(["git", "checkout", "-b", "main"], base_dir)
        with open(base_dir / ".gitignore", "w") as f: f.write("__pycache__/\nnode_modules/\ntarget/\nbin/\nobj/\n*.pyc\n.env\n")
        
    executar_git(["git", "add", "."], base_dir)
    msg_commit = f"🔧 fix: patch [{framework}]" if e_correcao else f"🚀 feat: init [{linguagem}/{framework}]"
    executar_git(["git", "commit", "-m", msg_commit], base_dir)
    
    tk, us = os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_USER")
    if tk and us:
        if not e_correcao:
            criar_repositorio_remoto_no_github(base_dir.name, tk)
            executar_git(["git", "remote", "add", "origin", f"https://github.com{us}/{base_dir.name}.git"], base_dir)
        url_autenticada = f"https://{us}:{tk}@://github.com{us}/{base_dir.name}.git"
        return executar_git(["git", "push", "-u", url_autenticada, "main"], base_dir)
    return False
