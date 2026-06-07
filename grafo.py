import subprocess, os
from pathlib import Path
from typing import List, TypedDict
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

class KeyPoolManager:
    def __init__(self):
        self.pools = {
            "google": [k.strip() for k in os.getenv("GOOGLE_API_KEY", "").split(",") if k.strip()],
            "openrouter": [k.strip() for k in os.getenv("OPENROUTER_API_KEY", "").split(",") if k.strip()]
        }
        self.indices = {"google": 0, "openrouter": 0}

    def obter_chave(self, prov: str):
        pool = self.pools.get(prov, [])
        if not pool:
            raise RuntimeError(f"Nenhuma chave configurada para {prov}")
        idx = self.indices.get(prov, 0) % len(pool)
        return pool[idx]

    def rotacionar(self, prov: str):
        pool = self.pools.get(prov, [])
        if len(pool) > 1:
            self.indices[prov] = (self.indices.get(prov, 0) + 1) % len(pool)
            return True  # rotacionou para uma chave diferente
        return False  # pool unitário, não adianta rotacionar

    def tamanho_pool(self, prov: str) -> int:
        return len(self.pools.get(prov, []))

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

# Sequência de fallback para o agente dev quando o modelo primário é bloqueado por rate limit
MODELOS_OPENROUTER_FALLBACK = [
    "qwen/qwen3-coder",          # ~$0.30/1M tokens — especialista em código
    "deepseek/deepseek-chat",    # ~$0.14/1M tokens — fallback barato
    "google/gemini-flash-1.5",   # ~$0.075/1M tokens — mais barato ainda
]

def obter_llm_openrouter(indice_modelo: int = 0):
    modelo = MODELOS_OPENROUTER_FALLBACK[indice_modelo % len(MODELOS_OPENROUTER_FALLBACK)]
    print(f"[llm] Usando modelo OpenRouter: {modelo}")
    return ChatOpenAI(
        model=modelo,
        temperature=0.1,
        openai_api_key=pool_manager.obter_chave("openrouter"),
        openai_api_base="https://openrouter.ai/api/v1"
    )

def obter_llm_google(nome_modelo: str):
    # Todos os modelos passam pelo OpenRouter — usa chave do OpenRouter
    base = {
        "temperature": 0.1,
        "openai_api_key": pool_manager.obter_chave("openrouter"),
        "openai_api_base": "https://openrouter.ai/api/v1"
    }
    if "pro" in nome_modelo.lower():
        return ChatOpenAI(model="google/gemini-flash-1.5", **base)  # ~$0.075/1M tokens
    else:
        return ChatOpenAI(model="google/gemini-flash-1.5", **base)  # ~$0.075/1M tokens

def executar_com_failover(state, prov_nome, bloco, bloco_com_modelo=None):
    """
    Tenta executar `bloco()` com retry e espera progressiva.
    Se `bloco_com_modelo` for fornecido, tentativas avançadas fazem fallback de modelo.
    """
    import time

    # Esperas maiores para modelos gratuitos (rate limit pode durar minutos)
    esperas = [10, 30, 60, 120, 180]

    for tentativa in range(5):
        try:
            # Nas últimas tentativas, tenta um modelo alternativo se disponível
            if tentativa >= 2 and bloco_com_modelo is not None:
                print(f"[failover] Tentando modelo alternativo (tentativa {tentativa + 1}/5)...")
                return bloco_com_modelo(tentativa)
            return bloco()
        except Exception as e:
            err = str(e).lower()
            is_rate = any(p in err for p in [
                "rate_limit", "quota", "limit_exceeded", "429",
                "overloaded", "too many", "ratelimit", "rate limit"
            ])
            is_auth = any(p in err for p in ["auth", "invalid api", "unauthorized", "403", "404"])

            if is_auth:
                rotacionou = pool_manager.rotacionar(prov_nome)
                msg = "rotacionando chave" if rotacionou else "pool unitário, chave inválida"
                print(f"[failover] Erro de autenticação em {prov_nome}: {msg}")
                raise e  # auth inválido não tem como recuperar com espera

            if is_rate:
                rotacionou = pool_manager.rotacionar(prov_nome)
                espera = esperas[tentativa]
                pool_info = f"pool={pool_manager.tamanho_pool(prov_nome)} chave(s)"
                rotacao_info = "chave rotacionada" if rotacionou else "pool unitário (sem rotação útil)"
                print(f"[failover] Rate limit em {prov_nome} ({pool_info}), {rotacao_info}. "
                      f"Tentativa {tentativa + 1}/5. Aguardando {espera}s...")
                time.sleep(espera)
                continue

            # Erro desconhecido — propaga imediatamente
            raise e

    raise RuntimeError(
        f"Pool de chaves esgotado para {prov_nome} após 5 tentativas com espera. "
        f"Dica: adicione mais chaves em {prov_nome.upper()}_API_KEY (separadas por vírgula) "
        f"ou aguarde o cooldown do modelo gratuito."
    )


# ── Agentes ──────────────────────────────────────────────────────────────────

def agente_chief_tier0(state):
    def acao():
        llm = obter_llm_google("gemini-pro")
        prompt = (
            f"Você é o Chief AI Officer (Tier 0). Mapeie o requisito técnico corporativo: {state['requisito']}. "
            f"Analise o código legado: {state.get('codigo_legado')} e anexos extraídos: {state.get('contexto_arquivos')}. "
            f"Estruture um plano detalhado para {state['linguagem_selecionada']} usando o framework {state['framework_selecionado']}."
        )
        return {"plano_do_chief": llm.invoke(prompt).content, "status_passo": "dev"}
    return executar_com_failover(state, "openrouter", acao)

def agente_desenvolvedor_tier2(state):
    prompt = (
        f"Você é o Especialista Dev (Tier 2). Implemente o código limpo completo nas camadas usando "
        f"{state['linguagem_selecionada']} e {state['framework_selecionado']}. "
        f"Siga o plano do Chief:\n{state['plano_do_chief']}\n"
        f"Feedbacks para correção:\n{state.get('historico_erros')}"
    )

    def acao():
        llm = obter_llm_openrouter(0).with_structured_output(ComponenteMultiLinguagem)
        return {"codigo_producao": llm.invoke(prompt), "status_passo": "quality_gate"}

    def acao_com_modelo(tentativa):
        # Testa modelos alternativos nas tentativas avançadas
        llm = obter_llm_openrouter(tentativa).with_structured_output(ComponenteMultiLinguagem)
        return {"codigo_producao": llm.invoke(prompt), "status_passo": "quality_gate"}

    return executar_com_failover(state, "openrouter", acao, acao_com_modelo)

def agente_quality_gate_tier3(state):
    def acao():
        llm = obter_llm_google("gemini-flash").with_structured_output(QualityReport)
        prod = state["codigo_producao"]
        prompt = (
            f"Audite o código dando notas de 0 a 100 para Clean Code e Clean Arch "
            f"para a stack {state['linguagem_selecionada']}:\n"
            f"{prod.camada_dominio}\n{prod.camada_aplicacao}\n{prod.camada_infra_web}"
        )
        return {"relatorio_qualidade": llm.invoke(prompt), "status_passo": "validar_score"}
    return executar_com_failover(state, "openrouter", acao)

def executar_sast_seguranca(state):
    prod = state["codigo_producao"]
    if state["linguagem_selecionada"] == "Python":
        with open("app_code_temp.py", "w") as f:
            f.write(f"{prod.camada_dominio}\n{prod.camada_aplicacao}\n{prod.camada_infra_banco}\n{prod.camada_infra_web}")
        res = subprocess.run(["bandit", "-r", "app_code_temp.py"], capture_output=True, text=True)
        if os.path.exists("app_code_temp.py"):
            os.remove("app_code_temp.py")
        if res.returncode != 0:
            return {
                "status_passo": "chief_retry",
                "historico_erros": state.get("historico_erros", []) + [f"SAST Error:\n{res.stdout}"]
            }
    return {"status_passo": "test_gen"}

def agente_gerador_testes(state):
    def acao():
        llm = obter_llm_google("gemini-flash").with_structured_output(UnitTestComponent)
        prompt = (
            f"Gere a suíte de testes unitários funcionais nativos para o código gerado em "
            f"{state['linguagem_selecionada']}:\n{state['codigo_producao'].camada_infra_web}"
        )
        return {"codigo_teste": llm.invoke(prompt), "status_passo": "test_run"}
    return executar_com_failover(state, "openrouter", acao)

def executor_runtime_pytest(state):
    prod = state["codigo_producao"]
    if state["linguagem_selecionada"] == "Python":
        with open("app_code.py", "w") as f:
            f.write(f"{prod.camada_dominio}\n{prod.camada_aplicacao}\n{prod.camada_infra_banco}\n{prod.camada_infra_web}")
        with open("test_app.py", "w") as f:
            f.write(state["codigo_teste"].codigo_teste)
        res = subprocess.run(["pytest", "test_app.py"], capture_output=True, text=True)
        for f in ["app_code.py", "test_app.py"]:
            if os.path.exists(f):
                os.remove(f)
        if res.returncode != 0:
            return {
                "status_passo": "chief_retry",
                "historico_erros": state.get("historico_erros", []) + [f"PyTest Sandbox Fail:\n{res.stdout}"]
            }
    return {"status_passo": "sucesso"}

def ler_codigo_da_pasta_legada(caminho):
    p = Path(caminho)
    if not p.exists():
        return ""
    exts = ["*.py", "*.ts", "*.java", "*.cs", "*.rs"]
    arqs = []
    for ext in exts:
        for f in p.rglob(ext):
            if not any(d in f.parts for d in ["venv", ".git", "__pycache__", "bin", "obj", "target", "node_modules"]):
                arqs.append(f"--- ARQUIVO: {f.name} ---\n" + f.read_text(encoding="utf-8") + "\n")
    return "\n".join(arqs)


# ── Grafo ────────────────────────────────────────────────────────────────────

def roteador(state):
    st = state["status_passo"]
    # FIX: chief_retry agora volta ao chief para gerar novo plano, não direto ao dev
    if st == "chief_retry":
        return "chief"
    if st == "dev":
        return "desenvolvedor"
    if st == "test_gen":
        return "gerador_testes"
    if st == "test_run":
        return "executor_pytest"
    if st == "sucesso":
        return END
    # validar_score
    media = (state["relatorio_qualidade"].score_clean_code + state["relatorio_qualidade"].score_arquitetura) / 2
    return "desenvolvedor" if media < 80 else "sast"

w = StateGraph(EstadoEngenharia)
w.add_node("chief", agente_chief_tier0)
w.add_node("desenvolvedor", agente_desenvolvedor_tier2)
w.add_node("quality_gate", agente_quality_gate_tier3)
w.add_node("sast", executar_sast_seguranca)
w.add_node("gerador_testes", agente_gerador_testes)
w.add_node("executor_pytest", executor_runtime_pytest)

w.set_entry_point("chief")
w.add_edge("chief", "desenvolvedor")
w.add_edge("desenvolvedor", "quality_gate")

w.add_conditional_edges("quality_gate", roteador)
w.add_conditional_edges("sast", roteador, {"chief": "chief", "desenvolvedor": "desenvolvedor", "gerador_testes": "gerador_testes", END: END})
w.add_conditional_edges("executor_pytest", roteador, {"chief": "chief", END: END})

app = w.compile()