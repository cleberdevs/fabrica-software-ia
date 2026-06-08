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

            prompt_docs = (
                f"Gere o README.md completo com Docker e diagramas Mermaid v11 para o sistema {linguagem}/{framework}.\n"
                f"Domínio: {prod.camada_dominio}\nAplicação: {prod.camada_aplicacao}\nWeb: {prod.camada_infra_web}\n\n"
                "REGRAS OBRIGATÓRIAS para o diagrama Mermaid (classDiagram):\n"
                "1. Use APENAS sintaxe Mermaid v11 válida\n"
                "2. Nomes de classes sem espaços, acentos ou caracteres especiais\n"
                "3. Tipos de atributos SIMPLES apenas: string, int, float, bool, List, Dict, datetime\n"
                "4. NUNCA use Optional~tipo~, List~tipo~, Dict~k,v~ — proibido, causa syntax error\n"
                "5. Para Optional use apenas o tipo base: int em vez de Optional~int~\n"
                "6. Métodos sem parênteses vazios duplos — use apenas nomeMetodo()\n"
                "7. Relacionamentos: <|-- para herança, *-- para composição, o-- para agregação\n"
                "8. Cada linha da classe em uma linha separada\n"
                "9. Underscores duplos em métodos como __init__ podem ser escritos como init()\n"
                "REGRAS para o diagrama de deploy Docker (use flowchart TD):\n"
                "10. Use flowchart TD para o diagrama de deploy — NUNCA graph TD\n"
                "11. Nomes de nós sem espaços — use underscore: API_Server, Postgres_DB\n"
                "12. Labels de nós entre colchetes simples: API_Server[API Server]\n"
                "13. Setas simples: A --> B ou A -->|label| B\n"
                "14. Subgraphs com nome simples sem acentos: subgraph Docker_Network\n"
                "15. Feche todo subgraph com end na mesma indentação\n"
                "Exemplo válido de deploy:\n"
                "```mermaid\n"
                "flowchart TD\n"
                "    subgraph Docker_Compose\n"
                "        API[API FastAPI]\n"
                "        DB[(PostgreSQL)]\n"
                "    end\n"
                "    Client-->API\n"
                "    API-->DB\n"
                "```\n"
                "Exemplo válido de classDiagram:\n"
                "```mermaid\n"
                "classDiagram\n"
                "    class Pedido {\n"
                "        +int id\n"
                "        +string status\n"
                "        +calcularTotal()\n"
                "    }\n"
                "```"
            )
            docs = llm_utils.invoke(prompt_docs).content
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