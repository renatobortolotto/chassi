FROM python:3.9-slim

WORKDIR /app

RUN apt-get update \
	&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
		 tesseract-ocr \
		 tesseract-ocr-por \
		 tesseract-ocr-eng \
	   poppler-utils \
	   libglib2.0-0 libsm6 libxrender1 libxext6 \
	&& rm -rf /var/lib/apt/lists/*

COPY config/ config/
COPY src/ src/
COPY main.py main.py
COPY requirements.txt requirements.txt 
# Observação: arquivo de config do gunicorn neste repo é 'gunicorn.py'
COPY gunicorn.py gunicorn.py

# Instala dependências Python do chassi (serviços internos não precisam de requirements separados)
RUN pip3 install --no-cache-dir -r requirements.txt

# Variáveis para o Atomic/Flask ouvir fora do container
ENV HOST=0.0.0.0
ENV PORT=8000
ENV SERVER_ROOT=/api

# Opcional: caminho para credencial GCP (monte um volume para o JSON e aponte aqui)
# ENV GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-service-account.json

EXPOSE 8000

# Execute via Python simples (Atomic app) ou ajuste para usar gunicorn
CMD ["python", "main.py"]

