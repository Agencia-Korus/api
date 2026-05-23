FROM python:3.13-slim

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

#não reinstala poetry se não forem adicionadas bibliotecas novas
COPY pyproject.toml poetry.lock* ./

RUN pip install --no-cache-dir poetry \
&& poetry config installer.max-workers 10 \
&& poetry install --no-interaction --no-ansi --without dev --no-root

#copia o código do backend
COPY . .

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "main:app", "--app-dir", "api", "--host", "0.0.0.0"]
