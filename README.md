# API Korus

## Configurando o ambiente

```bash
sudo apt install pipx

pipx install poetry
pipx inject poetry poetry-plugin-shell

poetry python install 3.13
poetry env use 3.13

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
