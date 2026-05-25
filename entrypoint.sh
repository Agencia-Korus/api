#!/bin/sh

# Executar migrações
poetry run alembic upgrade head

# Iniciar aplicação
poetry run uvicorn main:app --app-dir api --host 0.0.0.0 --port 8000