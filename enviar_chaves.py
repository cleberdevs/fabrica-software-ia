import os
from dotenv import dotenv_values
from huggingface_hub import HfApi

# 1. Carrega todas as chaves do seu arquivo .env local
config = dotenv_values('.env')

# 2. Conecta com a API do Hugging Face
api = HfApi()

# SUBSTITUA pelo seu usuário e nome do Space
SPACE_ID = "cleberfx/fabrica-software-ia" 

print(f"Iniciando o envio limpo de {len(config)} chaves para o Space {SPACE_ID}...\n")

# 3. Envia cada chave automaticamente removendo aspas residuais
for key, value in config.items():
    if value:  # Ignora linhas em branco
        # Remove aspas simples, duplas ou espaços que possam ter sobrado
        clean_value = str(value).strip("'\" ")
        
        try:
            api.add_space_secret(repo_id=SPACE_ID, key=key, value=clean_value)
            print(f"✅ Sucesso: {key} enviado como string limpa.")
        except Exception as e:
            print(f"❌ Erro ao enviar {key}: {e}")

print("\nProcesso finalizado! Lembre-se de dar Restart no seu Space.")
