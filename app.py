import dotenv
import os

# Carrega .env ANTES de qualquer outro import para garantir
# que LANGCHAIN_API_KEY e LANGCHAIN_TRACING_V2 estejam disponíveis
dotenv.load_dotenv()

import gradio as gr
import pandas as pd
import base64
from pathlib import Path
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from grafo import app, pool_manager, ler_codigo_da_pasta_legada
from exporter import exportar_para_estrutura_clean_arch

DIR_PROJ = Path("projetos_fabrica")
DIR_PROJ.mkdir(exist_ok=True)

def listar_sistemas():
    pastas = [p.name for p in DIR_PROJ.iterdir() if p.is_dir()]
    return pastas if pastas else ["Nenhum projeto encontrado"]

def processar_execucao(modo, requisito, nome_projeto, projeto_existente, codigo_quebrado, erro_log, nova_funcionalidade, arquivos, linguagem, framework):
    if not requisito and modo == "Construir Novo Sistema do Zero":
        return "❌ Erro: Descreva os requisitos do novo software."
        
    ctx_arq = ""
    if arquivos:
        for f in arquivos:
            ext = f.name.split('.')[-1].lower()
            if ext in ['csv', 'xlsx']:
                df = pd.read_csv(f.name) if ext == 'csv' else pd.read_excel(f.name)
                ctx_arq += f"\n### Planilha ({f.name}):\n{df.to_markdown(index=False)}\n"
            elif ext in ['json', 'yaml']:
                with open(f.name, "r", encoding="utf-8") as file_data:
                    ctx_arq += f"\n### Contrato ({f.name}):\n{file_data.read()}\n"
            else:
                with open(f.name, "rb") as img_file:
                    b64 = base64.b64encode(img_file.read()).decode('utf-8')
                chv = pool_manager.obter_chave("openrouter")
                llm_visao = ChatOpenAI(
                    model="google/gemma-4-31b-it:free",
                    openai_api_key=chv,
                    openai_api_base="https://openrouter.ai/api/v1"
                )
                ctx_arq += f"\n### Visão ({f.name}):\n{llm_visao.invoke([HumanMessage(content=[{'type':'text','text':'Traduz o diagrama em especificacoes.'},{'type':'image_url','image_url':{'url':f'data:image/jpeg;base64,{b64}'}}])]).content}\n"

    codigo_legado, hist_erros, e_correcao = "", [], False
    if modo == "Construir Novo Sistema do Zero":
        projeto_final = DIR_PROJ / nome_projeto
        req_final = requisito
    elif modo == "Corrigir Erro de Compilação (Debug Mode)":
        if projeto_existente == "Nenhum projeto encontrado": return "❌ Selecione um projeto válido."
        projeto_final = DIR_PROJ / projeto_existente
        req_final = f"CORREÇÃO DE BUG. Código:\n{codigo_quebrado}"
        hist_erros = [f"Log:\n{erro_log}"]
        e_correcao = True
    else:
        if projeto_existente == "Nenhum projeto encontrado": return "❌ Selecione um projeto válido."
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
        "framework_selecionado": framework
    }
    
    try:
        state = app.invoke(inputs)
        if state.get("status_passo") == "sucesso" or "codigo_producao" in state:
            chv_g = pool_manager.obter_chave("openrouter")
            llm_utils = ChatOpenAI(
                model="google/gemini-2.5-flash-lite",
                max_tokens=4096,
                openai_api_key=chv_g,
                openai_api_base="https://openrouter.ai/api/v1"
            )
            prod = state["codigo_producao"]

            # ── README sem diagramas (o modelo não gera mermaid) ──────────────
            prompt_readme = (
                f"Gere o README.md completo com instruções Docker para o sistema {linguagem}/{framework}.\n"
                f"Domínio: {prod.camada_dominio}\nAplicação: {prod.camada_aplicacao}\nWeb: {prod.camada_infra_web}\n\n"
                "REGRAS OBRIGATÓRIAS:\n"
                "1. NÃO inclua nenhum bloco ```mermaid``` — os diagramas são gerados separadamente\n"
                "2. Todo bloco de código deve ser fechado com ``` em uma linha isolada\n"
                "3. NUNCA adicione texto após o fechamento de um bloco de código\n"
                "4. Cada bloco ```bash ou ```yaml deve conter APENAS comandos/configurações, sem comentários em português dentro\n"
                "5. Termine o README com uma seção ## Licença ou ## Contribuição — nunca termine dentro de um bloco de código\n"
                "6. Não adicione observações, avisos ou notas fora das seções do README\n"
            )
            readme_raw = llm_utils.invoke(prompt_readme).content

            def sanitizar_markdown(texto: str) -> str:
                """Fecha blocos de código abertos e remove texto após o último ```."""
                linhas = texto.split("\n")
                resultado = []
                dentro_bloco = False
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

            readme_sem_diagramas = sanitizar_markdown(readme_raw)

            # ── Diagrama de classes via JSON estruturado ──────────────────────
            prompt_classes_json = (
                f"Analise o código abaixo e retorne APENAS um JSON válido (sem markdown, sem texto) "
                f"descrevendo as classes para um classDiagram Mermaid v11.\n"
                f"Código:\n{prod.camada_dominio}\n{prod.camada_aplicacao}\n\n"
                "Formato EXATO do JSON (sem desvios):\n"
                '{"classes":[{"name":"NomeSemEspacos","attributes":["int id","str titulo"],"methods":["salvar()","buscar(id)"]}],'
                '"relations":[{"from":"ClasseA","to":"ClasseB","type":"inheritance"}]}\n'
                "Tipos permitidos em attributes: int, str, float, bool, List, Dict, datetime\n"
                "Tipos de relação: inheritance, composition, aggregation, association\n"
                "NUNCA use Optional~tipo~, List~tipo~ ou qualquer genericidade com ~"
            )
            import json, re

            def gerar_mermaid_classes(codigo_json: str) -> str:
                try:
                    clean = re.sub(r"```[a-z]*|```", "", codigo_json).strip()
                    data = json.loads(clean)
                except Exception:
                    return ""
                rel_map = {
                    "inheritance": "<|--",
                    "composition": "*--",
                    "aggregation": "o--",
                    "association": "-->"
                }
                lines = ["classDiagram"]
                for cls in data.get("classes", []):
                    name = re.sub(r"[^A-Za-z0-9_]", "_", cls["name"])
                    lines.append(f"    class {name} {{")
                    for attr in cls.get("attributes", []):
                        safe = re.sub(r"[~<>]", "", attr).strip()
                        lines.append(f"        +{safe}")
                    for meth in cls.get("methods", []):
                        safe = re.sub(r"[~<>]", "", meth).strip()
                        if not safe.endswith(")"):
                            safe += "()"
                        lines.append(f"        +{safe}")
                    lines.append("    }")
                for rel in data.get("relations", []):
                    arrow = rel_map.get(rel.get("type", "association"), "-->")
                    frm = re.sub(r"[^A-Za-z0-9_]", "_", rel["from"])
                    to  = re.sub(r"[^A-Za-z0-9_]", "_", rel["to"])
                    lines.append(f"    {frm} {arrow} {to}")
                return "\n".join(lines)

            classes_json = llm_utils.invoke(prompt_classes_json).content
            mermaid_classes = gerar_mermaid_classes(classes_json)

            # ── Diagrama de deploy Docker via JSON estruturado ────────────────
            prompt_deploy_json = (
                f"Analise o sistema {linguagem}/{framework} e retorne APENAS um JSON válido (sem markdown) "
                "descrevendo os containers Docker para um flowchart Mermaid v11.\n"
                '{"nodes":[{"id":"API","label":"API FastAPI","shape":"rect"},{"id":"DB","label":"PostgreSQL","shape":"cylinder"}],'
                '"edges":[{"from":"Client","to":"API","label":"HTTP"},{"from":"API","to":"DB","label":"SQL"}],'
                '"subgraphs":[{"id":"Docker_Compose","label":"Docker Compose","nodes":["API","DB"]}]}\n'
                "Shapes: rect, cylinder, diamond, rounded\n"
                "IDs sem espaços ou acentos"
            )

            def gerar_mermaid_deploy(codigo_json: str) -> str:
                try:
                    clean = re.sub(r"```[a-z]*|```", "", codigo_json).strip()
                    data = json.loads(clean)
                except Exception:
                    return ""
                shape_map = {
                    "rect":     ("[", "]"),
                    "cylinder": ("[(", ")]"),
                    "diamond":  ("{", "}"),
                    "rounded":  ("(", ")"),
                }
                lines = ["flowchart TD"]
                for sg in data.get("subgraphs", []):
                    sg_id    = re.sub(r"[^A-Za-z0-9_]", "_", sg["id"])
                    sg_label = sg.get("label", sg_id)
                    lines.append(f"    subgraph {sg_id}[{sg_label}]")
                    for nid in sg.get("nodes", []):
                        node = next((n for n in data["nodes"] if n["id"] == nid), None)
                        if node:
                            nid_safe = re.sub(r"[^A-Za-z0-9_]", "_", node["id"])
                            lbl = node.get("label", nid_safe)
                            o, c = shape_map.get(node.get("shape", "rect"), ("[", "]"))
                            lines.append(f"        {nid_safe}{o}{lbl}{c}")
                    lines.append("    end")
                subgraph_nodes = {n for sg in data.get("subgraphs", []) for n in sg.get("nodes", [])}
                for node in data.get("nodes", []):
                    if node["id"] not in subgraph_nodes:
                        nid_safe = re.sub(r"[^A-Za-z0-9_]", "_", node["id"])
                        lbl = node.get("label", nid_safe)
                        o, c = shape_map.get(node.get("shape", "rect"), ("[", "]"))
                        lines.append(f"    {nid_safe}{o}{lbl}{c}")
                for edge in data.get("edges", []):
                    frm = re.sub(r"[^A-Za-z0-9_]", "_", edge["from"])
                    to  = re.sub(r"[^A-Za-z0-9_]", "_", edge["to"])
                    lbl = edge.get("label", "")
                    arrow = f"-->|{lbl}|" if lbl else "-->"
                    lines.append(f"    {frm} {arrow} {to}")
                return "\n".join(lines)

            deploy_json  = llm_utils.invoke(prompt_deploy_json).content
            mermaid_deploy = gerar_mermaid_deploy(deploy_json)

            # ── Monta README final com diagramas válidos ──────────────────────
            diagrama_classes = (
                "## Diagrama de Classes\n\n"
                "```mermaid\n" + mermaid_classes + "\n```\n"
            ) if mermaid_classes else ""

            diagrama_deploy = (
                "## Deploy com Docker\n\n"
                "```mermaid\n" + mermaid_deploy + "\n```\n"
            ) if mermaid_deploy else ""

            docs = readme_sem_diagramas + "\n\n" + diagrama_classes + "\n" + diagrama_deploy
            swag = llm_utils.invoke(f"Retorne APENAS o JSON OpenAPI v3 cru para as rotas sem markdown:\n{prod.camada_infra_web}").content
            
            sync = exportar_para_estrutura_clean_arch(prod, state["codigo_teste"], str(projeto_final), docs, swag, linguagem, framework, e_correcao=e_correcao)
            res_git = "☁️ Repositório criado/atualizado com sucesso no GitHub!" if sync else "💾 Salvo localmente."
            return f"🎉 **SUCESSO EXCEPCIONAL!**\n\n**Pasta:** `{projeto_final}`\n**Status:** {res_git}\n\n## 📄 Manual Técnico Gerado (README.md):\n\n{docs}"
        else:
            return "❌ Falha nos guardrails de qualidade ou segurança da esteira."
    except Exception as e:
        return f"🚨 Erro Crítico na Esteira: {str(e)}"

with gr.Blocks() as demo:
    gr.Markdown("# 🏭 Fábrica de Software Autônoma Enterprise Pro")
    gr.Markdown("Matriz Híbrida: **Gemini 2.5 Pro** ➔ **Qwen 3 Coder Free** ➔ **Gemini 2.5 Flash**")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🧰 Configuração Técnica")
            linguagem = gr.Dropdown(label="Linguagem-Alvo", choices=["Python", "TypeScript", "Java", "C#", "Rust"], value="Python")
            framework = gr.Dropdown(label="Framework Web", choices=["FastAPI", "Express", "Spring Boot", ".NET Core", "Axum"], value="FastAPI")
            
            def atualizar_frameworks(lang):
                fw_map = {"Python": ["FastAPI"], "TypeScript": ["Express"], "Java": ["Spring Boot"], "C#": [".NET Core"], "Rust": ["Axum"]}
                return gr.update(choices=fw_map.get(lang, ["FastAPI"]), value=fw_map.get(lang, ["FastAPI"])[0])
            linguagem.change(atualizar_frameworks, inputs=[linguagem], outputs=[framework])
            
            modo = gr.Radio(label="Operação de Engenharia", choices=["Construir Novo Sistema do Zero", "Evoluir/Refatorar Sistema Existente", "Corrigir Erro de Compilação (Debug Mode)"], value="Construir Novo Sistema do Zero")
            arquivos = gr.File(label="📎 Anexos (Imagens / Planilhas / OpenAPI)", file_count="multiple")
            
        with gr.Column(scale=2):
            with gr.Group() as p_novo:
                gr.Markdown("#### Novo Projeto")
                requisito = gr.Textbox(label="Requisitos do Software / Prompt", placeholder="Ex: API de e-commerce com carrinho...", lines=4)
                nome_projeto = gr.Textbox(label="Nome da Pasta do Projeto", value="api_enterprise_service")
                
            with gr.Group(visible=False) as p_existente:
                gr.Markdown("#### Seleção de Projeto Salvo")
                opcoes_sistemas = listar_sistemas()
                # 🔄 CORREÇÃO DO VALUE: Passando explicitamente a string do primeiro item em vez da lista bruta
                projeto_existente = gr.Dropdown(label="Escolha o Projeto Alvo", choices=opcoes_sistemas, value=opcoes_sistemas[0])
                
                with gr.Tab("🚀 Injetar Nova Funcionalidade") as tab_evo:
                    nova_funcionalidade = gr.Textbox(label="Instruções de Evolução Incremental", placeholder="Ex: Adicione uma rota GET /historico...", lines=3)
                with gr.Tab("🚨 Debug Mode (Fix Bugs)") as tab_debug:
                    codigo_quebrado = gr.Textbox(label="Trecho do Código com Defeito", lines=3)
                    erro_log = gr.Textbox(label="Stack Trace / Erro do Terminal", lines=3)

            def alternar_modos(m):
                if m == "Construir Novo Sistema do Zero":
                    return gr.update(visible=True), gr.update(visible=False)
                return gr.update(visible=False), gr.update(visible=True)
            modo.change(alternar_modos, inputs=[modo], outputs=[p_novo, p_existente])
            
            btn = gr.Button("⚡ Iniciar Linha de Produção", variant="primary")
            output_text = gr.Markdown(value="💡 Aguardando comandos para iniciar a esteira corporativa...")

    btn.click(
        processar_execucao, 
        inputs=[modo, requisito, nome_projeto, projeto_existente, codigo_quebrado, erro_log, nova_funcionalidade, arquivos, linguagem, framework], 
        outputs=[output_text]
    )

if __name__ == "__main__":
    # 🔄 CORREÇÃO DO LAUNCH: Removido o argumento depreciado 'show_api'
    demo.launch(server_name="0.0.0.0", theme=gr.themes.Soft())