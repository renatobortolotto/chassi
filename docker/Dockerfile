# Alpine-based (company standard). If your org provides a custom base, replace with it (e.g., company/python:3.9-alpine3.22)
FROM python:3.9-alpine

WORKDIR /app

# System deps for OCR and PDF rendering on Alpine
# Build poppler from source for version 25.10.0
RUN apk add --no-cache \
	tesseract-ocr \
	tesseract-ocr-data-por \
	tesseract-ocr-data-eng \
	glib \
	libsm \
	libxrender \
	libxext \
	libstdc++ \
	# Runtime deps for poppler
	cairo \
	fontconfig \
	freetype \
	libjpeg-turbo \
	libpng \
	openjpeg \
	lcms2 \
	tiff \
	curl \
	&& apk add --no-cache --virtual .build-deps \
	build-base \
	cmake \
	cairo-dev \
	fontconfig-dev \
	freetype-dev \
	libjpeg-turbo-dev \
	libpng-dev \
	openjpeg-dev \
	lcms2-dev \
	tiff-dev \
	glib-dev \
	&& cd /tmp \
	&& curl -L -o poppler-25.10.0.tar.xz https://poppler.freedesktop.org/poppler-25.10.0.tar.xz \
	&& tar -xf poppler-25.10.0.tar.xz \
	&& cd poppler-25.10.0 \
	&& mkdir build && cd build \
	&& cmake -DCMAKE_BUILD_TYPE=Release \
	         -DCMAKE_INSTALL_PREFIX=/usr \
	         -DENABLE_UNSTABLE_API_ABI_HEADERS=ON \
	         -DENABLE_BOOST=OFF \
	         -DENABLE_QT5=OFF \
	         -DENABLE_QT6=OFF \
	         -DENABLE_GLIB=ON \
	         -DENABLE_UTILS=ON \
	         .. \
	&& make -j$(nproc) \
	&& make install \
	&& cd / \
	&& rm -rf /tmp/poppler-25.10.0* \
	&& apk del .build-deps

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

