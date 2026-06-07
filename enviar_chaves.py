import os
from dotenv import dotenv_values
from huggingface_hub import HfApi

# 1. Carrega todas as chaves do seu arquivo .env local
config = dotenv_values('.env')

# 2. Conecta com a API do Hugging Face
api = HfApi()

# SUBSTITUA pelo nome do seu usuário e do seu Space
SPACE_ID = "cleberfx/fabrica-software-ia" 

print(f"Iniciando o envio de {len(config)} chaves para o Space {SPACE_ID}...\n")

# 3. Envia cada chave automaticamente
for key, value in config.items():
    if value:  # Ignora linhas em branco no .env
        try:
            api.add_space_secret(repo_id=SPACE_ID, key=key, value=value)
            print(f"✅ Sucesso: {key} enviado.")
        except Exception as e:
            print(f"❌ Erro ao enviar {key}: {e}")

print("\nProcesso finalizado!")
