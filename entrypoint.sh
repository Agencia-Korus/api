#!/bin/sh

# Executar migrações
poetry run alembic upgrade head

# Executar o comando repassado para o contêiner
exec "$@"