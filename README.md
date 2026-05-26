# API Korus

## Configurando o ambiente

```bash
sudo apt install pipx

pipx install poetry
pipx inject poetry poetry-plugin-shell

poetry python install 3.13
poetry env use 3.13

poetry lock
poetry install
```

## Rodando o projeto

```bash
# Para linter:
task lint
task format

# Subindo a API
task run

# Rodando os testes
task test
```

## Rodando com Docker

```bash
cp .env.example .env
touch .env.google-calendar-service-account.json
docker compose up --build
```

O compose sobe:

- API principal: `http://localhost:8000/docs`
- Auth: `http://localhost:8001/docs`
- Postgres: `localhost:5433`
