#!/bin/sh

# Executar migrações
alembic upgrade head

# Executar o comando repassado para o contêiner
exec "$@"