## 📄 Sobre este projeto

Este serviço web recebe documentos PDF, extrai o texto (usando leitura nativa quando possível e OCR quando necessário), junta tudo em um único texto e salva o resultado no Google Cloud Storage (GCS).

Em palavras simples: você aponta uma pasta com PDFs, ele lê tudo, transforma em texto e guarda o arquivo TXT de saída no próprio prefixo do GCS.

## 🧭 Como funciona (resumo)

1. Lista os PDFs em um caminho do GCS (ex.: `gs://meu-bucket/prefixo`).
2. Para cada PDF:
	 - Tenta extrair o texto “nativo” do PDF.
	 - Se a qualidade do texto for baixa, aplica OCR (reconhecimento de caracteres) nas páginas para obter o texto.
3. Concatena os textos de todos os PDFs em um único arquivo.
4. Salva o resultado no GCS:
	- TXT concatenado no mesmo prefixo dos PDFs (`pdfs_dir`).

Tudo isso é acionado por um único endpoint HTTP (POST) que você chama com os caminhos de entrada/saída e a URL da sua API.

## 🔌 Endpoint principal

- Rota: `POST /extrator_dados_debentebtures`
- Payload (exemplo mínimo):

```
{
	"pdfs_dir": "gs://meu-bucket/entrada"
}
```

Opcionalmente, você pode ajustar alguns parâmetros:
- `dpi` (padrão 300) e `lang` (`por+eng`) – para o OCR
- `min_tokens`, `repeat_th`, `repeat_pages` – afinam quando o OCR é utilizado
- `timeout` e `retries` – comportamento de rede para utilitários internos
 - Seleção de arquivos:
	 - `file_names`: lista de nomes exatos (ex.: ["a.pdf", "b.pdf"]).
	 - `patterns`: padrões no nome, case/acento-insensitive. Se omitido e `file_names` ausente, o serviço usa defaults ["escritura", "contrato de distribuição", "manual"].

Retorno (exemplo):

```
{
	"message": "Processamento concluído",
	"pdfs_count": 12,
	"txt_uri": "gs://meu-bucket/entrada/concat-text-20251009-163205-118.12s.txt"
}
```

## 🧩 O que tem “por baixo dos panos”

- Camada de Aplicação: `src/application/pdf_processor/service.py`
	- Orquestra o fluxo: lista PDFs → extrai/concatena → salva TXT.
- Serviços internos: `src/infrastructure/services/`
	- `pdf_ocr.py`: leitura nativa de PDF, heurísticas e OCR (pytesseract, pdf2image, OpenCV) + utilitários de GCS.
    
- Rota: `src/application/extrator_dados_debenture/__init__.py`
	- Expõe o endpoint oficial e aceita tanto o comportamento CRUD de exemplo quanto o payload de processamento.
- Registro de rotas: `src/routes.py`
- Bootstrap da aplicação: `src/controller/app.py`, `main.py`
## 📄 Pipeline de PDFs (OCR + extração)

Este serviço processa PDFs, extrai texto (nativo quando possível e via OCR quando necessário), concatena tudo e grava um TXT no mesmo prefixo do GCS indicado por você.

- Entrada: um prefixo GCS com PDFs (ex.: `gs://meu-bucket/entrada`).
- Saída: um TXT concatenado salvo no mesmo prefixo (`pdfs_dir`).

Use o endpoint HTTP ou os utilitários Python internos descritos abaixo.

## 🔌 Endpoints

- POST `/extrator_dados_debenture`
	- Objetivo: Disparar o processamento de PDFs e obter a URI do TXT gerado.
	- Corpo (mínimo):
		```json
		{ "pdfs_dir": "gs://meu-bucket/entrada" }
		```
	- Parâmetros opcionais:
		- file_names: lista de nomes exatos a processar (prioritário sobre patterns).
		- patterns: padrões (case/acento-insensitive) para filtrar PDFs. Se omitido e file_names ausente, usa defaults ["escritura", "contrato de distribuição", "manual"].
		- dpi (int, padrão 300), lang (str, padrão "por+eng"): ajustes do OCR.
		- min_tokens (int, padrão 120), repeat_th (float, padrão 0.30), repeat_pages (float, padrão 0.6): heurísticas de decisão entre extração nativa e OCR.
		- timeout, retries: parâmetros gerais (não críticos após remoção da API externa).
	- Resposta (200):
		```json
		{
			"message": "Processamento concluído",
			"pdfs_count": 3,
			"txt_uri": "gs://meu-bucket/entrada/concat-text-20251009-163205-118.12s.txt"
		}
		```

Exemplo rápido com curl:
```bash
curl -X POST http://localhost:8000/extrator_dados_debenture \
	-H 'Content-Type: application/json' \
	-d '{"pdfs_dir":"gs://meu-bucket/entrada"}'
```

## 🧠 Como funciona

1. Lista PDFs no `pdfs_dir` (GCS) usando:
	 - nomes exatos (file_names), ou
	 - padrões (patterns), ou
	 - padrões default ["escritura", "contrato de distribuição", "manual"].
2. Para cada PDF:
	 - Extrai texto nativo com PyPDF2; mede qualidade com heurísticas.
	 - Se a qualidade for baixa, aplica OCR (pytesseract + pdf2image + OpenCV).
3. Concatena tudo e grava um TXT em `pdfs_dir`.

Código principal: `src/application/pdf_processor/service.py`.

## 🧩 Utilitários internos (Python)

Módulo: `src/infrastructure/services/pdf_ocr.py`

- GCS e seleção de arquivos
	- `is_gcs_uri(s: str) -> bool`: verifica `gs://`.
	- `parse_gcs_uri(uri: str) -> tuple[bucket, prefix]`: separa bucket/prefix.
	- `gcs_list_pdfs(dir_uri: str, recursive=True, file_names=None) -> list[str]`: lista PDFs no GCS; filtra por nome se informado.
	- `gcs_read_bytes(gs_path: str) -> bytes`: baixa bytes de um arquivo no GCS.
	- `gcs_write_text(dir_uri: str, filename: str, text: str) -> str`: grava TXT em `dir_uri/filename`.
	- `find_pdfs_by_patterns(root_dir: str, patterns: list[str], recursive=True) -> list[str]`: filtra por padrões no nome (GCS ou local para utilidade).

- Extração de texto
	- `load_pdf_bytes(identifier: str) -> bytes`: lê bytes de `gs://...` ou caminho local.
	- `extract_native_per_page_from_bytes(pdf_bytes: bytes) -> list[str]`: texto nativo por página (PyPDF2).
	- `extract_text(pdf_identifier: str, dpi: int, lang: str, min_tokens: int, repeat_th: float, repeat_pages_frac: float) -> str`:
		aplica heurísticas e decide entre nativo e OCR, retornando o texto com cabeçalhos por página.
	- `concat_many_pdfs_to_text(pdf_identifiers: list[str], dpi: int, lang: str, min_tokens: int, repeat_th: float, repeat_pages_frac: float) -> str`:
		processa vários PDFs e concatena em um único texto legível.

- Heurísticas de qualidade (principais)
	- `tokenize`, `avg_tokens_per_page`, `normalize_line`, `repetition_coverage`.
	- `text_quality_metrics`: calcula métricas (printable, alnum, mean word len, etc.).
	- `should_force_ocr(pages, min_tokens, repeat_threshold, repeat_pages_frac) -> (bool, float, float)`:
		retorna se deve forçar OCR e métricas auxiliares (avg tokens, repetição).

Observação: funções internas de pré-processamento de imagem (`_deskew`, `_preprocess`, `_choose_psm`) são detalhes da implementação e podem mudar.

## ▶️ Rodando o serviço

Local (Python 3.11+):
- Instale dependências: `pip install -r requirements.txt`
- Exporte credenciais GCP (se necessário): `GOOGLE_APPLICATION_CREDENTIALS=/caminho/key.json`
- Inicie: `python main.py`

Docker (recomendado):
- Build: `docker build -t chassi -f docker/Dockerfile .`
- Run: `docker run -p 8000:8000 -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/key.json -v /abs/key.json:/secrets/key.json chassi`

## 🔐 Variáveis de ambiente

- `HOST`, `PORT`, `SERVER_ROOT`: parâmetros do servidor.
- `GOOGLE_APPLICATION_CREDENTIALS`: caminho para credenciais do GCS.

## 🧪 Testes

- `make devdeps` e `make unit-tests`
- Os testes cobrem o orquestrador e utilitários de OCR; chamadas pesadas são mockadas.

## 🛠️ Solução de problemas

- Tesseract/Poppler não encontrados: prefira a imagem Docker (já provisiona ambos).
- Acesso ao GCS falhou: verifique `GOOGLE_APPLICATION_CREDENTIALS` e permissões.

## 🗂️ Estrutura

- `src/application/pdf_processor/` — Orquestra o processamento.
- `src/infrastructure/services/` — OCR e utilitários GCS.
- `src/application/extrator_dados_debenture/` — Endpoint e CRUD de exemplo.
- `src/routes.py` — Registro de rotas.
- `docker/Dockerfile` — Imagem com OCR.
- `requirements*.txt` — Dependências.

—
Se quiser estender para gerar também um JSON de metadados (p.ex., PDFs processados e estatísticas), dá para salvar um `summary.json` no mesmo `pdfs_dir`. Posso incluir isso sob demanda.