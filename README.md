## 📄 Sobre este projeto

Este serviço web recebe documentos PDF, extrai o texto (usando leitura nativa quando possível e OCR quando necessário), junta tudo em um único texto e envia esse conteúdo para outra API. Depois salva os resultados em nuvem (Google Cloud Storage – GCS).

Em palavras simples: você aponta uma pasta com PDFs, ele lê tudo, transforma em texto, manda esse texto para uma API e guarda os arquivos de saída (TXT e JSON) em pastas do GCS.

## 🧭 Como funciona (resumo)

1. Lista os PDFs em um caminho do GCS (ex.: `gs://meu-bucket/prefixo`).
2. Para cada PDF:
	 - Tenta extrair o texto “nativo” do PDF.
	 - Se a qualidade do texto for baixa, aplica OCR (reconhecimento de caracteres) nas páginas para obter o texto.
3. Concatena os textos de todos os PDFs em um único arquivo.
4. Envia esse texto para uma API externa (ex.: sua API de processamento).
5. Salva os resultados no GCS:
	- TXT concatenado no mesmo prefixo dos PDFs (`pdfs_dir`).
	- JSON de resposta no prefixo de saída (`payload_dir`).

Tudo isso é acionado por um único endpoint HTTP (POST) que você chama com os caminhos de entrada/saída e a URL da sua API.

## 🔌 Endpoint principal

- Rota: `POST /extrator_dados_debentebtures`
- Payload (exemplo mínimo):

```
{
	"pdfs_dir": "gs://meu-bucket/entrada",
	"payload_dir": "gs://meu-bucket/saida"
}
```

Opcionalmente, você pode ajustar alguns parâmetros:
- `auth_header` – ex.: `Bearer <token>` (a API externa é fixa no serviço)
- `dpi` (padrão 300) e `lang` (`por+eng`) – para o OCR
- `min_tokens`, `repeat_th`, `repeat_pages` – afinam quando o OCR é utilizado
- `timeout` e `retries` – comportamento de rede ao chamar a API externa
 - Seleção de arquivos:
	 - `file_names`: lista de nomes exatos (ex.: ["a.pdf", "b.pdf"]).
	 - `patterns`: padrões no nome, case/acento-insensitive. Se omitido e `file_names` ausente, o serviço usa defaults ["escritura", "contrato de distribuição", "manual"].

Retorno (exemplo):

```
{
	"message": "Processamento concluído",
	"pdfs_count": 12,
	"txt_uri": "gs://meu-bucket/entrada/concat-text-20251009-163205-118.12s.txt",
	"payload_uri": "gs://meu-bucket/saida/payload-concat-text-...json",
		"api_url": "http://llm-api:8000/api/extrator_dados_debentures"
}
```

## 🧩 O que tem “por baixo dos panos”

- Camada de Aplicação: `src/application/pdf_processor/service.py`
	- Orquestra o fluxo: lista PDFs → extrai/concatena → salva TXT → chama API → salva JSON.
- Serviços internos: `src/infrastructure/services/`
	- `pdf_ocr.py`: leitura nativa de PDF, heurísticas e OCR (pytesseract, pdf2image, OpenCV) + utilitários de GCS.
	- `txt_to_api.py`: POST com retries e salvamento de JSON no GCS.
- Rota: `src/application/extrator_dados_debenture/__init__.py`
	- Expõe o endpoint oficial e aceita tanto o comportamento CRUD de exemplo quanto o payload de processamento.
- Registro de rotas: `src/routes.py`
- Bootstrap da aplicação: `src/controller/app.py`, `main.py`

## ✅ Dependências

Dependências de Python (principais):
- Extração/OCR: `PyPDF2`, `pdf2image`, `pytesseract`, `pillow`, `opencv-python-headless`, `numpy`
- Rede: `requests`
- Armazenamento GCS: `google-cloud-storage`
- Framework interno: `pylib-atle-base-atomic`, `pylib-atle-base-storage` (fornecidas no ambiente corporativo)

Dependências de sistema (para OCR e conversão de PDF):
- `tesseract-ocr` (com idiomas `por` e `eng`)
- `poppler-utils` (para `pdf2image`)

O Dockerfile já instala tudo isso na imagem.

## ▶️ Como executar

Opção A — Local (com Python):
1. Crie/ative um ambiente Python 3.11+.
2. Instale as dependências:
	 - `pip install -r requirements.txt`
3. Exporte as variáveis se necessário (ex.: `GOOGLE_APPLICATION_CREDENTIALS` para GCS).
4. Rode a aplicação:
	 - `python main.py`

Opção B — Docker (recomendado):
1. Construa a imagem (no diretório do projeto):
	 - `docker build -t chassi -f docker/Dockerfile .`
2. Execute o container, montando as credenciais do GCS se necessário:
	 - `docker run -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/key.json -v /caminho/key.json:/secrets/key.json -p 8000:8000 chassi`

Depois de subir, chame o endpoint POST conforme descrito acima.

## 🔐 Variáveis e segredos

- `HOST`, `PORT`, `SERVER_ROOT`: ajustes do servidor (default configurado na app).
- `GOOGLE_APPLICATION_CREDENTIALS`: caminho do JSON de credenciais do GCP para acessar GCS.
- `auth_header` no payload: para autenticar na sua API externa (ex.: Bearer token).

Use a esteira do Jenkins para injetar esses valores com segurança (não suba segredos no repositório).

## 🧪 Testes

- Rode os testes:
	- `make devdeps`
	- `make unit-tests`

Os testes cobrem a rota principal e o fluxo de orquestração. Partes pesadas (rede/OCR) são mockadas.

## 🛠️ Solução de problemas (FAQ rápida)

- “Erro: `tesseract` não encontrado” → instale `tesseract-ocr` no host ou use a imagem Docker fornecida.
- “Erro: `poppler`/`pdftoppm` não encontrado” → instale `poppler-utils` no host, ou use Docker.
- “Falha ao acessar `gs://...`” → verifique `GOOGLE_APPLICATION_CREDENTIALS` e permissões da conta de serviço.
- “A API externa devolveu erro” → verifique `api_url`, `endpoint`, `auth_header` e conectividade/rede.

## 🗂️ Estrutura de pastas (essencial)

- `src/application/pdf_processor/` — Orquestrador do processamento.
- `src/infrastructure/services/` — OCR e integração com API/GCS.
- `src/application/extrator_dados_debenture/` — Endpoint/CRUD de exemplo e POST de processamento.
- `src/routes.py` — Registro de rotas.
- `docker/Dockerfile` — Build com OCR e dependências de sistema.
- `requirements.txt` — Dependências de produção.
- `requirements-dev.txt` — Dependências de desenvolvimento/testes.

---

Se você precisa garantir saída e desempenho idênticos aos seus PDFs “golden”, compartilhe 2–3 amostras e ajustamos rapidamente DPI/PSM/limiares do OCR para ficar 1:1.