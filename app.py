import streamlit as st
import dotenv, pandas as pd, base64, os
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from grafo import app, pool_manager, ler_codigo_da_pasta_legada
from exporter import exportar_para_estrutura_clean_arch

dotenv.load_dotenv()
st.set_page_config(page_title="Fábrica AI Enterprise", page_icon="🏭", layout="wide")
st.title("🏭 Fábrica de Software Autônoma Enterprise")

DIR_PROJ = Path("projetos_fabrica"); DIR_PROJ.mkdir(exist_ok=True)

st.sidebar.markdown("### 🧠 Distribuição de Inteligência Ativa")
st.sidebar.success("📋 Tier 0 Chief: **Gemini 2.5 Pro**")
st.sidebar.info("🤖 Tier 2 Dev: **Qwen 3 Coder (Free)**")
st.sidebar.warning("🔍 Tier 3 Auditor: **Gemini 2.5 Flash**")
st.sidebar.warning("🧪 QA & Writer: **Gemini 2.5 Flash**")

st.sidebar.markdown("---")
st.sidebar.markdown("### 💻 Matriz de Tecnologia")
linguagem_escolhida = st.sidebar.selectbox("Selecione a Linguagem-Alvo:", ["Python", "TypeScript", "Java", "C#", "Rust"])
frameworks_disponiveis = {"Python": ["FastAPI"], "TypeScript": ["Express"], "Java": ["Spring Boot"], "C#": [".NET Core"], "Rust": ["Axum"]}
framework_escolhido = st.sidebar.selectbox("Selecione o Framework Web:", frameworks_disponiveis.get(linguagem_escolhida, ["FastAPI"]))

modo = st.radio("Operação de Engenharia:", ["Construir Novo Sistema do Zero", "Evoluir/Refatorar Sistema Existente", "Corrigir Erro de Compilação (Debug Mode)"])
arquivos = st.file_uploader("📎 Anexos (Imagens/Planilhas/Especificações):", type=["png", "jpg", "jpeg", "csv", "xlsx", "json", "yaml"], accept_multiple_files=True)

codigo_legado, hist_erros, modo_git, projeto_alvo = "", [], False, None

if modo == "Construir Novo Sistema do Zero":
    requisito = st.text_area("Descreva os requisitos de negócio ou cole a especificação:")
    nome_p = st.text_input("Nome da pasta do projeto:", value="api_enterprise_service")
    projeto_alvo = DIR_PROJ / nome_p
else:
    sistemas = [p.name for p in DIR_PROJ.iterdir() if p.is_dir()]
    if not sistemas: st.error("Nenhum projeto localizado em 'projetos_fabrica/'.")
    else:
        sel = st.selectbox("Selecione o projeto alvo:", sistemas)
        projeto_alvo = DIR_PROJ / sel
        modo_git = True
        if modo == "Debug Mode":
            requisito = f"FIX BUG. Código:\n{st.text_area('Código:')}"
            hist_erros = [f"Log:\n{st.text_area('Erro:')}"]
        else:
            requisito = st.text_area("Descreva a NOVA funcionalidade incremental:")
            codigo_legado = ler_codigo_da_pasta_legada(str(projeto_alvo))

if st.button("⚡ Iniciar Linha de Produção", type="primary") and projeto_alvo and requisito:
    ctx_arq = ""
    for f in arquivos or []:
        ext = f.name.split('.')[-1]
        if ext in ['csv', 'xlsx']:
            df = pd.read_csv(f) if ext == 'csv' else pd.read_excel(f)
            ctx_arq += f"\n### Planilha ({f.name}):\n{df.to_markdown(index=False)}\n"
        elif ext in ['json', 'yaml']:
            ctx_arq += f"\n### Contrato ({f.name}):\n{f.read().decode('utf-8')}\n"
        else:
            b64 = base64.b64encode(f.read()).decode('utf-8')
            chv = pool_manager.obter_chave("google")
            ctx_arq += f"\n### Visão ({f.name}):\n{ChatGoogleGenerativeAI(model='gemini-2.5-flash', google_api_key=chv).invoke([HumanMessage(content=[{'type':'text','text':'Traduz o diagrama em especificacoes.'},{'type':'image_url','image_url':{'url':f'data:image/jpeg;base64,{b64}'}}])]).content}\n"

    inputs = {"requisito": requisito, "codigo_legado": codigo_legado, "contexto_arquivos": ctx_arq, "historico_erros": hist_erros, "status_passo": "dev", "modelo_selecionado": "qwen", "linguagem_selecionada": linguagem_escolhida, "framework_selecionado": framework_escolhido}
    
    st.write("⚙️ Orquestrando Tiers Híbridos (Gemini 2.5 + Qwen 3 Coder)...")
    container_scores = st.container()
    
    try:
        for output in app.stream(inputs):
            for node, state in output.items():
                if node == "quality_gate" and "relatorio_qualidade" in state and state["relatorio_qualidade"]:
                    rep = state["relatorio_qualidade"]
                    with container_scores:
                        col1, col2, col3 = st.columns(3)
                        col1.metric("✨ Score Clean Code", f"{rep.score_clean_code}/100"); col1.progress(rep.score_clean_code/100)
                        col2.metric("🏗️ Score Clean Arch", f"{rep.score_arquitetura}/100"); col2.progress(rep.score_arquitetura/100)
                        media = (rep.score_clean_code + rep.score_arquitetura)/2
                        col3.metric("📈 Média", f"{media}/100")
                        if media < 80: st.error(f"⚠️ Rejeitado: {rep.justificativa_critica}")
                        else: st.success(f"💯 Parecer: {rep.justificativa_critica}")
        
        estado_final = state
        if estado_final.get("status_passo") == "sucesso" or "codigo_producao" in estado_final:
            chv_g = pool_manager.obter_chave("google")
            llm_utils = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=chv_g)
            prod = estado_final["codigo_producao"]
            
            docs = llm_utils.invoke(f"Gere o README.md completo com Docker e diagramas Mermaid para o sistema {linguagem_escolhida}/{framework_escolhido}:\nDomínio: {prod.camada_dominio}\nAplicação: {prod.camada_aplicacao}\nWeb: {prod.camada_infra_web}").content
            swag = llm_utils.invoke(f"Retorne APENAS o JSON OpenAPI v3 cru para as rotas sem markdown:\n{prod.camada_infra_web}").content
            
            sync = exportar_para_estrutura_clean_arch(prod, estado_final["codigo_teste"], str(projeto_alvo), docs, swag, linguagem_escolhida, framework_escolhido, e_correcao=modo_git)
            st.balloons(); st.success(f"🎉 Entrega Finalizada na pasta: `{projeto_alvo}`"); st.markdown("---"); st.markdown(docs)
            if sync: st.success("☁️ GitHub Sincronizado com sucesso!")
        else: st.error("Falha nos guardrails.")
    except Exception as e: st.error(f"Erro Crítico: {e}")


