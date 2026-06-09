import dotenv
import os

dotenv.load_dotenv()

import base64
import json
import asyncio
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from grafo import app as langgraph_app, pool_manager, ler_codigo_da_pasta_legada
from exporter import exportar_para_estrutura_clean_arch

# ── Setup ──────────────────────────────────────────────────────────────────
DIR_PROJ = Path("projetos_fabrica")
DIR_PROJ.mkdir(exist_ok=True)

app = FastAPI(title="Fábrica de Software IA Enterprise")

# Serve arquivos estáticos (index.html, assets)
# O HF Spaces expõe a porta 7860 por padrão
HTML_FILE = Path("index.html")


# ── Rotas ──────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve a interface principal."""
    if HTML_FILE.exists():
        return HTMLResponse(content=HTML_FILE.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>index.html não encontrado</h1>", status_code=500)


@app.get("/projetos", response_class=JSONResponse)
async def listar_projetos():
    """Retorna a lista de projetos salvos em projetos_fabrica/."""
    pastas = [p.name for p in DIR_PROJ.iterdir() if p.is_dir()]
    return {"projetos": pastas if pastas else []}


@app.post("/gerar")
async def gerar(
    modo: str = Form(...),
    requisito: str = Form(""),
    nome_projeto: str = Form("api_enterprise_service"),
    projeto_existente: str = Form(""),
    codigo_quebrado: str = Form(""),
    erro_log: str = Form(""),
    nova_funcionalidade: str = Form(""),
    linguagem: str = Form("Python"),
    framework: str = Form("FastAPI"),
    arquivos: list[UploadFile] = File(default=[]),
):
    """
    Endpoint principal da esteira. Aceita multipart/form-data e retorna
    streaming de texto (Server-Sent Events) com o log de execução e resultado.
    """

    async def event_stream():
        try:
            yield _sse("log", "🔍 Processando anexos...")

            # ── Contexto de arquivos ───────────────────────────────────────
            ctx_arq = ""
            for f in arquivos:
                if not f.filename:
                    continue
                ext = f.filename.split(".")[-1].lower()
                conteudo = await f.read()

                if ext in ("csv", "xlsx"):
                    import io
                    if ext == "csv":
                        df = pd.read_csv(io.BytesIO(conteudo))
                    else:
                        df = pd.read_excel(io.BytesIO(conteudo))
                    ctx_arq += f"\n### Planilha ({f.filename}):\n{df.to_markdown(index=False)}\n"

                elif ext in ("json", "yaml", "yml"):
                    ctx_arq += f"\n### Contrato ({f.filename}):\n{conteudo.decode('utf-8')}\n"

                else:
                    # Imagem → visão multimodal
                    b64 = base64.b64encode(conteudo).decode("utf-8")
                    chv = pool_manager.obter_chave("openrouter")
                    llm_visao = ChatOpenAI(
                        model="google/gemma-4-31b-it:free",
                        openai_api_key=chv,
                        openai_api_base="https://openrouter.ai/api/v1",
                    )
                    descricao = llm_visao.invoke(
                        [
                            HumanMessage(
                                content=[
                                    {"type": "text", "text": "Traduz o diagrama em especificações técnicas detalhadas."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                                ]
                            )
                        ]
                    ).content
                    ctx_arq += f"\n### Visão ({f.filename}):\n{descricao}\n"

            # ── Prepara inputs por modo ────────────────────────────────────
            codigo_legado, hist_erros, e_correcao = "", [], False

            if modo == "novo":
                if not requisito.strip():
                    yield _sse("erro", "❌ Descreva os requisitos do software.")
                    return
                projeto_final = DIR_PROJ / nome_projeto
                req_final = requisito

            elif modo == "debug":
                if not projeto_existente:
                    yield _sse("erro", "❌ Selecione um projeto válido.")
                    return
                projeto_final = DIR_PROJ / projeto_existente
                req_final = f"CORREÇÃO DE BUG.\nCódigo:\n{codigo_quebrado}"
                hist_erros = [f"Log de erro:\n{erro_log}"]
                e_correcao = True

            else:  # evoluir
                if not projeto_existente:
                    yield _sse("erro", "❌ Selecione um projeto válido.")
                    return
                projeto_final = DIR_PROJ / projeto_existente
                req_final = nova_funcionalidade
                codigo_legado = ler_codigo_da_pasta_legada(str(projeto_final))
                e_correcao = True

            inputs = {
                "requisito": req_final,
                "codigo_legado": codigo_legado,
                "contexto_arquivos": ctx_arq,
                "historico_erros": hist_erros,
                "status_passo": "dev",
                "modelo_selecionado": "qwen",
                "linguagem_selecionada": linguagem,
                "framework_selecionado": framework,
            }

            yield _sse("log", f"🏗️ Iniciando esteira · {linguagem}/{framework}...")

            # ── Execução do LangGraph (síncrono em thread pool) ───────────
            loop = asyncio.get_event_loop()
            state = await loop.run_in_executor(None, lambda: langgraph_app.invoke(inputs))

            if state.get("status_passo") == "sucesso" or "codigo_producao" in state:
                yield _sse("log", "✅ Código aprovado em todos os guardrails. Gerando documentação...")

                chv_g = pool_manager.obter_chave("openrouter")
                llm_utils = ChatOpenAI(
                    model="google/gemini-2.5-flash-lite",
                    max_tokens=4096,
                    openai_api_key=chv_g,
                    openai_api_base="https://openrouter.ai/api/v1",
                )
                prod = state["codigo_producao"]

                # README sem diagramas
                prompt_readme = (
                    f"Gere o README.md completo com instruções Docker para o sistema {linguagem}/{framework}.\n"
                    f"Domínio: {prod.camada_dominio}\nAplicação: {prod.camada_aplicacao}\nWeb: {prod.camada_infra_web}\n\n"
                    "REGRAS OBRIGATÓRIAS:\n"
                    "1. NÃO inclua nenhum bloco ```mermaid```\n"
                    "2. Todo bloco de código deve ser fechado com ``` em linha isolada\n"
                    "3. Termine com ## Licença ou ## Contribuição\n"
                )
                readme_raw = llm_utils.invoke(prompt_readme).content
                readme_sem_diagramas = _sanitizar_markdown(readme_raw)

                # Diagramas Mermaid via JSON estruturado
                import re

                prompt_classes_json = (
                    f"Analise o código abaixo e retorne APENAS um JSON válido (sem markdown) "
                    f"descrevendo as classes para um classDiagram Mermaid v11.\n"
                    f"Código:\n{prod.camada_dominio}\n{prod.camada_aplicacao}\n\n"
                    '{"classes":[{"name":"NomeSemEspacos","attributes":["int id","str titulo"],"methods":["salvar()","buscar(id)"]}],'
                    '"relations":[{"from":"ClasseA","to":"ClasseB","type":"inheritance"}]}\n'
                    "Tipos permitidos: int,str,float,bool,List,Dict,datetime | "
                    "Relações: inheritance,composition,aggregation,association | NUNCA use ~"
                )
                classes_json = llm_utils.invoke(prompt_classes_json).content
                mermaid_classes = _gerar_mermaid_classes(classes_json)

                prompt_deploy_json = (
                    f"Analise o sistema {linguagem}/{framework} e retorne APENAS um JSON válido (sem markdown) "
                    "descrevendo os containers Docker para um flowchart Mermaid v11.\n"
                    '{"nodes":[{"id":"API","label":"API FastAPI","shape":"rect"}],'
                    '"edges":[{"from":"Client","to":"API","label":"HTTP"}],'
                    '"subgraphs":[{"id":"Docker_Compose","label":"Docker Compose","nodes":["API"]}]}\n'
                    "Shapes: rect, cylinder, diamond, rounded | IDs sem espaços"
                )
                deploy_json = llm_utils.invoke(prompt_deploy_json).content
                mermaid_deploy = _gerar_mermaid_deploy(deploy_json)

                diagrama_classes = (
                    "## Diagrama de Classes\n\n```mermaid\n" + mermaid_classes + "\n```\n"
                ) if mermaid_classes else ""

                diagrama_deploy = (
                    "## Deploy com Docker\n\n```mermaid\n" + mermaid_deploy + "\n```\n"
                ) if mermaid_deploy else ""

                docs = readme_sem_diagramas + "\n\n" + diagrama_classes + "\n" + diagrama_deploy

                swag = llm_utils.invoke(
                    f"Retorne APENAS o JSON OpenAPI v3 cru para as rotas sem markdown:\n{prod.camada_infra_web}"
                ).content

                sync = exportar_para_estrutura_clean_arch(
                    prod, state["codigo_teste"], str(projeto_final),
                    docs, swag, linguagem, framework, e_correcao=e_correcao
                )

                res_git = (
                    "☁️ Repositório criado/atualizado no GitHub!" if sync
                    else "💾 Salvo localmente em projetos_fabrica/"
                )

                yield _sse("sucesso", json.dumps({
                    "pasta": str(projeto_final),
                    "git": res_git,
                    "docs": docs,
                }, ensure_ascii=False))

            else:
                yield _sse("erro", "❌ Falha nos guardrails de qualidade ou segurança da esteira.")

        except Exception as e:
            yield _sse("erro", f"🚨 Erro crítico na esteira: {str(e)}")

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ── Helpers ────────────────────────────────────────────────────────────────

def _sse(tipo: str, dados: str) -> str:
    """Formata uma mensagem Server-Sent Event."""
    payload = json.dumps({"tipo": tipo, "dados": dados}, ensure_ascii=False)
    return f"data: {payload}\n\n"


def _sanitizar_markdown(texto: str) -> str:
    linhas = texto.split("\n")
    resultado, dentro_bloco = [], False
    for linha in linhas:
        stripped = linha.strip()
        if stripped.startswith("```") and not dentro_bloco:
            dentro_bloco = True
            resultado.append(linha)
        elif stripped == "```" and dentro_bloco:
            dentro_bloco = False
            resultado.append(linha)
        elif dentro_bloco and not stripped.startswith("```"):
            resultado.append(linha)
        elif not dentro_bloco:
            resultado.append(linha)
    if dentro_bloco:
        resultado.append("```")
    return "\n".join(resultado)


def _gerar_mermaid_classes(codigo_json: str) -> str:
    import json, re
    try:
        clean = re.sub(r"```[a-z]*|```", "", codigo_json).strip()
        data = json.loads(clean)
    except Exception:
        return ""
    rel_map = {"inheritance": "<|--", "composition": "*--", "aggregation": "o--", "association": "-->"}
    lines = ["classDiagram"]
    for cls in data.get("classes", []):
        name = re.sub(r"[^A-Za-z0-9_]", "_", cls["name"])
        lines.append(f"  class {name} {{")
        for attr in cls.get("attributes", []):
            lines.append(f"    +{re.sub(r'[~<>]', '', attr).strip()}")
        for meth in cls.get("methods", []):
            safe = re.sub(r"[~<>]", "", meth).strip()
            if not safe.endswith(")"):
                safe += "()"
            lines.append(f"    +{safe}")
        lines.append("  }")
    for rel in data.get("relations", []):
        arrow = rel_map.get(rel.get("type", "association"), "-->")
        frm = re.sub(r"[^A-Za-z0-9_]", "_", rel["from"])
        to = re.sub(r"[^A-Za-z0-9_]", "_", rel["to"])
        lines.append(f"  {frm} {arrow} {to}")
    return "\n".join(lines)


def _gerar_mermaid_deploy(codigo_json: str) -> str:
    import json, re
    try:
        clean = re.sub(r"```[a-z]*|```", "", codigo_json).strip()
        data = json.loads(clean)
    except Exception:
        return ""
    shape_map = {"rect": ("[", "]"), "cylinder": ("[(", ")]"), "diamond": ("{", "}"), "rounded": ("(", ")")}
    lines = ["flowchart TD"]
    for sg in data.get("subgraphs", []):
        sg_id = re.sub(r"[^A-Za-z0-9_]", "_", sg["id"])
        lines.append(f"  subgraph {sg_id}[{sg.get('label', sg_id)}]")
        for nid in sg.get("nodes", []):
            node = next((n for n in data["nodes"] if n["id"] == nid), None)
            if node:
                nid_safe = re.sub(r"[^A-Za-z0-9_]", "_", node["id"])
                o, c = shape_map.get(node.get("shape", "rect"), ("[", "]"))
                lines.append(f"    {nid_safe}{o}{node.get('label', nid_safe)}{c}")
        lines.append("  end")
    subgraph_nodes = {n for sg in data.get("subgraphs", []) for n in sg.get("nodes", [])}
    for node in data.get("nodes", []):
        if node["id"] not in subgraph_nodes:
            nid_safe = re.sub(r"[^A-Za-z0-9_]", "_", node["id"])
            o, c = shape_map.get(node.get("shape", "rect"), ("[", "]"))
            lines.append(f"  {nid_safe}{o}{node.get('label', nid_safe)}{c}")
    for edge in data.get("edges", []):
        frm = re.sub(r"[^A-Za-z0-9_]", "_", edge["from"])
        to = re.sub(r"[^A-Za-z0-9_]", "_", edge["to"])
        lbl = edge.get("label", "")
        lines.append(f"  {frm} -->{'|' + lbl + '|' if lbl else ''} {to}")
    return "\n".join(lines)


# ── Entrypoint ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)