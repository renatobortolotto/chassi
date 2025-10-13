README.md tem como objetivo demonstrar a estrutura de arquivos e pastas que foi adotada para o python internamente.

Caminho	Especificação
docker/	Diretório padrão para conter o arquivo Dockerfile
docker/Dockerfile	Arquivo usado para gerar o POD
infra-as-code/	Diretório padrão para conter o arquivo infra.yml
infra-as-code/infra.yml	Arquivo contendo os valores das variáveis usadas pela esteira de desenvolvimento
src/	Diretório contendo o código da aplicação
src/application/	Diretório contendo a camada de aplicação
src/application/extrator_dados_debenture/	Diretório contendo a rota /extrator_dados_debenture
src/application/extrator_dados_debenture/init.py	Arquivo que implementa o callable para a rota /extrator_dados_debenture
src/controller/	Diretório contendo a camada de controle
src/controller/init.py	Arquivo que inicializa o módulo controller
src/controller/app.py	Arquivo que instancia a biblioteca BVAtomic
src/infrastructure/	Diretório contendo a camada de infraestrutura
src/infrastructure/openapi/	Diretório que inicializa o módulo infrastructure
src/infrastructure/openapi/openapi.yml	Arquivo yaml para configuração do OpenApi
src/init.py	Arquivo que inicializa os módulos de src
src/routes.py	Arquivo que inicializa os módulos de src
tests/	Diretório padrão para conter as rotas da aplicação
tests/init.py	Arquivo de inicialização do módulo "tests" usado para incluir os caminhos das pastas onde ficarão os módulos do projeto a serem incluídos nos testes unitários
tests/generic_tests.py	Arquivo contendo os testes unitários dos módulos padrões
.atle.yml	Arquivo yaml contendo configurações da aplicação
.dockerignore	Arquivo ou pastas que serão ignorados pelo docker
.gitignore	Arquivos ou pastas que serão ignorados pelo git
dependencias.bat	Arquivo de instalação de dependência
config.json	Arquivo json de configuração
jenkins.properties	Arquivo contendo variáveis para serem pegas pelo jenkins (compondo a esteira de desenvolvimento)
Makefile	Arquivo contendo o projeto
requirements.txt	Arquivo contendo todos os requisitos necessários para executar o projeto, sendo assim ele fará o download dos módulos a partir do requirements, gerará o ambiente entre outros (compondo a esteira de desenvolvimento)
README.md	Arquivo contendo as instruções do extrator_dados_debenture-base
requirements-dev.txt	Arquivo de requeridos para rodar o processo da esteira

Novidades adicionadas neste projeto de exemplo:
- Rota POST `/extrator_dados_debentures` (POST) também aceita payload de processamento e usa os serviços internos em `src/infrastructure/services/`, que:
	- lista PDFs em um prefixo GCS,
	- extrai/concatena texto (OCR quando necessário),
	- grava um TXT no mesmo prefixo,
	- envia o texto a uma API externa e grava o payload JSON em outro prefixo GCS.
		- Código nas camadas:
			- `src/application/pdf_processor/` (Service)
			- `src/infrastructure/services/` (pdf_ocr e txt_to_api internos)
		- Rota conectada em `src/routes.py` e acionada via POST em `/extrator_dados_debentures`.