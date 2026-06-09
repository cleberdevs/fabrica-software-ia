
FROM python:3.11-slim
 
WORKDIR /app
 
# Copia dependências primeiro (cache de camadas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# Copia o restante do projeto
COPY . .
 
# Cria pasta de projetos gerados
RUN mkdir -p projetos_fabrica
 
# Porta padrão do Hugging Face Spaces
EXPOSE 7860
 
CMD ["python", "app.py"]
 