#!/usr/bin/env bash
set -e

# Estrutura principal
mkdir -p src/application/extrator_dados_debenture
mkdir -p src/controller
mkdir -p src/domain/models
mkdir -p src/infrastructure/config
mkdir -p src/infrastructure/database
mkdir -p src/openapi
mkdir -p src/tests

# Arquivos vazios em cada nível
touch src/__init__.py
touch src/routes.py

# application/extrator_dados_debenture
touch src/application/__init__.py
touch src/application/extrator_dados_debenture/__init__.py

# controller
touch src/controller/__init__.py
touch src/controller/app.py

# domain/models
touch src/domain/__init__.py
touch src/domain/models/__init__.py

# infrastructure/config
touch src/infrastructure/__init__.py
touch src/infrastructure/config/__init__.py
touch src/infrastructure/config/business_action.py

# infrastructure/database
touch src/infrastructure/database/__init__.py
touch src/infrastructure/database/database_in_memory.py

# openapi
touch src/openapi/__init__.py
touch src/openapi/routes.py
touch src/openapi/openapi.yaml

# tests
touch src/tests/__init__.py
touch src/tests/test_business_action.py
touch src/tests/test_extrator_dados_debenture.py

echo "Estrutura src criada com sucesso."
