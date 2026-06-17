# syntax=docker/dockerfile:1

###############################
# Stage 1 - build das deps
###############################
FROM python:3.12-slim AS builder

ENV POETRY_VERSION=2.3.3 \
	POETRY_VIRTUALENVS_CREATE=false \
	POETRY_NO_INTERACTION=1 \
	PIP_NO_CACHE_DIR=1 \
	PIP_DISABLE_PIP_VERSION_CHECK=1 \
	VIRTUAL_ENV=/opt/venv

WORKDIR /app

# Toolchain só no builder (não vai pra imagem final)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential \
	&& rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==${POETRY_VERSION}"

# Cria o venv (ativado via VIRTUAL_ENV) que será copiado para o estágio final.
# Com VIRTUAL_ENV setado, o poetry instala as deps dentro dele.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Camada de cache: só reinstala deps se o lock mudar
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root


###############################
# Stage 2 - runtime
###############################
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
	PYTHONDONTWRITEBYTECODE=1 \
	PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Apenas o venv pronto, sem poetry/toolchain
COPY --from=builder /opt/venv /opt/venv

# Código da aplicação
COPY . .

# Usuário não-root
RUN useradd --create-home --uid 1000 appuser \
	&& chown -R appuser:appuser /app /opt/venv \
	&& chmod +x entrypoint.sh
USER appuser

EXPOSE 8000

# Roda as migrações e em seguida o comando (CMD)
ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "main:app", "--app-dir", "api", "--host", "0.0.0.0", "--port", "8000"]
