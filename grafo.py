import subprocess, os
from pathlib import Path
from typing import List, TypedDict
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

class KeyPoolManager:
    def __init__(self):
        self.pools = {
            "google": [k.strip() for k in os.getenv("GOOGLE_API_KEY", "").split(",") if k.strip()],
            "openrouter": [k.strip() for k in os.getenv("OPENROUTER_API_KEY", "").split(",") if k.strip()]
        }
    def obter_chave(self, prov: str):
        if prov in self.pools and self.pools[prov]: return self.pools[prov]
        raise RuntimeError(f"Chaves esgotadas para {prov}")
    def rotacionar(self, prov: str):
        if prov in self.pools and self.pools[prov]: self.pools[prov].pop(0)

pool_manager = KeyPoolManager()

class ComponenteMultiLinguagem(BaseModel):
    camada_dominio: str = Field(description="Entidades puras do domínio e contratos de interfaces.")
    camada_aplicacao: str = Field(description="Casos de uso/Serviços que orquestram as regras de negócio.")
    camada_infra_banco: str = Field(description="Implementação física de persistência usando ORM nativo.")
    camada_infra_web: str = Field(description="Controladores HTTP/Rotas utilizando o Framework Web corporativo escolhido.")
    gerenciador_dependencias: str = Field(description="Arquivo completo de dependências: requirements.txt, package.json, pom.xml, .csproj ou Cargo.toml.")
    justificativa: str = Field(description="Defesa arquitetural detalhada.")

class UnitTestComponent(BaseModel):
    codigo_teste: str = Field(description="Suite de testes robusta utilizando o framework de testes nativo da linguagem.")

class QualityReport(BaseModel):
    score_clean_code: int = Field(description="Nota de 0 a 100.")
    score_arquitetura: int = Field(description="Nota de 0 a 100.")
    justificativa_critica: str = Field(description="Feedback de auditoria para o time.")

class EstadoEngenharia(TypedDict):
    requisito: str; codigo_legado: str; contexto_arquivos: str; plano_do_chief: str
    linguagem_selecionada: str; framework_selecionado: str; modelo_selecionado: str
    codigo_producao: ComponenteMultiLinguagem; codigo_teste: UnitTestComponent
    relatorio_qualidade: QualityReport; historico_erros: List[str]; status_passo: str

def obter_llm_dinamica(nome_modelo: str):
    if "qwen" in nome_modelo.lower():
        return ChatOpenAI(
            model="qwen/qwen3-coder:free",
            temperature=0.1,
            openai_api_key=pool_manager.obter_chave("openrouter"),
            openai_api_base="https://openrouter.ai"
        )
    elif "pro" in nome_modelo.lower():
        return ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.1, google_api_key=pool_manager.obter_chave("google"))
    else:
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1, google_api_key=pool_manager.obter_chave("google"))

def executar_com_failover(state, prov_nome, bloco):
    for _ in range(5):
        try: return bloco()
        except Exception as e:
            err = str(e).lower()
            if any(p in err for p in ["rate_limit", "quota", "limit_exceeded", "429", "auth", "overloaded"]):
                pool_manager.rotacionar(prov_nome)
                continue
            raise e
    raise RuntimeError(f"Pool de chaves esgotado para {prov_nome}!")

def agente_chief_tier0(state):
    def acao():
        llm = obter_llm_dinamica("gemini-pro")
        prompt = f"Você é o Chief AI Officer (Tier 0). Mapeie o requisito técnico corporativo: {state['requisito']}. Analise o código legado: {state.get('codigo_legado')} e anexos extraídos: {state.get('contexto_arquivos')}. Estruture um plano detalhado para {state['linguagem_selecionada']} usando o framework {state['framework_selecionado']}."
        return {"plano_do_chief": llm.invoke(prompt).content, "status_passo": "dev"}
    return executar_com_failover(state, "google", acao)

def agente_desenvolvedor_tier2(state):
    def acao():
        llm = obter_llm_dinamica("qwen").with_structured_output(ComponenteMultiLinguagem)
        prompt = f"Você é o Especialista Dev (Tier 2). Implemente o código limpo completo nas camadas usando {state['linguagem_selecionada']} e {state['framework_selecionado']}. Siga o plano do Chief:\n{state['plano_do_chief']}\nFeedbacks para correção:\n{state.get('historico_erros')}"
        return {"codigo_producao": llm.invoke(prompt), "status_passo": "quality_gate"}
    return executar_com_failover(state, "openrouter", acao)

def agente_quality_gate_tier3(state):
    def acao():
        llm = obter_llm_dinamica("gemini-flash").with_structured_output(QualityReport)
        prod = state["codigo_producao"]
        prompt = f"Audite o código dando notas de 0 a 100 para Clean Code e Clean Arch para a stack {state['linguagem_selecionada']}:\n{prod.camada_dominio}\n{prod.camada_aplicacao}\n{prod.camada_infra_web}"
        return {"relatorio_qualidade": llm.invoke(prompt), "status_passo": "validar_score"}
    return executar_com_failover(state, "google", acao)

def executar_sast_seguranca(state):
    prod = state["codigo_producao"]
    if state["linguagem_selecionada"] == "Python":
        with open("app_code_temp.py", "w") as f: f.write(f"{prod.camada_dominio}\n{prod.camada_aplicacao}\n{prod.camada_infra_banco}\n{prod.camada_infra_web}")
        res = subprocess.run(["bandit", "-r", "app_code_temp.py"], capture_output=True, text=True)
        if os.path.exists("app_code_temp.py"): os.remove("app_code_temp.py")
        if res.returncode != 0:
            return {"status_passo": "chief_retry", "historico_erros": state.get("historico_erros", []) + [f"SAST Error:\n{res.stdout}"]}
    return {"status_passo": "test_gen"}

def agente_gerador_testes(state):
    def acao():
        llm = obter_llm_dinamica("gemini-flash").with_structured_output(UnitTestComponent)
        prompt = f"Gere a suíte de testes unitários funcionais nativos para o código gerado em {state['linguagem_selecionada']}:\n{state['codigo_producao'].camada_infra_web}"
        return {"codigo_teste": llm.invoke(prompt), "status_passo": "test_run"}
    return executar_com_failover(state, "google", acao)

def executor_runtime_pytest(state):
    prod = state["codigo_producao"]
    if state["linguagem_selecionada"] == "Python":
        with open("app_code.py", "w") as f: f.write(f"{prod.camada_dominio}\n{prod.camada_aplicacao}\n{prod.camada_infra_banco}\n{prod.camada_infra_web}")
        with open("test_app.py", "w") as f: f.write(state["codigo_teste"].codigo_teste)
        res = subprocess.run(["pytest", "test_app.py"], capture_output=True, text=True)
        for f in ["app_code.py", "test_app.py"]:
            if os.path.exists(f): os.remove(f)
        if res.returncode != 0:
            return {"status_passo": "chief_retry", "historico_erros": state.get("historico_erros", []) + [f"PyTest Sandbox Fail:\n{res.stdout}"]}
    return {"status_passo": "sucesso"}

def ler_codigo_da_pasta_legada(caminho):
    p = Path(caminho)
    if not p.exists(): return ""
    exts = ["*.py", "*.ts", "*.java", "*.cs", "*.rs"]
    arqs = []
    for ext in exts:
        for f in p.rglob(ext):
            if not any(d in f.parts for d in ["venv", ".git", "__pycache__", "bin", "obj", "target", "node_modules"]):
                arqs.append(f"--- ARQUIVO: {f.name} ---\n" + f.read_text(encoding="utf-8") + "\n")
    return "\n".join(arqs)

w = StateGraph(EstadoEngenharia)
w.add_node("chief", agente_chief_tier0); w.add_node("desenvolvedor", agente_desenvolvedor_tier2)
w.add_node("quality_gate", agente_quality_gate_tier3); w.add_node("sast", executar_sast_seguranca)
w.add_node("gerador_testes", agente_gerador_testes); w.add_node("executor_pytest", executor_runtime_pytest)
w.set_entry_point("chief"); w.add_edge("chief", "desenvolvedor"); w.add_edge("desenvolvedor", "quality_gate")

def roteador(state):
    st = state["status_passo"]
    if st in ["chief_retry", "dev"]: return "desenvolvedor"
    if st == "test_gen": return "gerador_testes"
    if st == "test_run": return "executor_pytest"
    if st == "sucesso": return END
    media = (state["relatorio_qualidade"].score_clean_code + state["relatorio_qualidade"].score_arquitetura) / 2
    return "desenvolvedor" if media < 80 else "sast"

w.add_conditional_edges("quality_gate", roteador); w.add_conditional_edges("sast", roteador); w.add_conditional_edges("executor_pytest", roteador)
app = w.compile()
