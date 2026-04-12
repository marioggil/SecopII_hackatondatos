# Build stage para máxima velocidad usando Astrals UV
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar/instalar GIS y Postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libgdal-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
# Instalamos resolviendo a la velocidad de la luz y empaquetamos en .venv
RUN uv sync --frozen --no-install-project

# Run stage ultra-ligero para Producción
FROM python:3.11-slim-bookworm

WORKDIR /code

# Copiamos librerías dinámicas necesarias para Postgres (libpq5) en runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 libgdal32 && \
    rm -rf /var/lib/apt/lists/*

# Copiamos el entorno virtual ya resuelto
COPY --from=builder /app/.venv /code/.venv

# Agregamos entorno virtual al PATH
ENV PATH="/code/.venv/bin:$PATH"

# Copiamos el código final
COPY app/ ./app/

# Entrar al directorio app para que las rutas relativas (templates/, static/, databases/) funcionen igual que en local
WORKDIR /code/app

EXPOSE 5021

# Comando por defecto para arrancar la app en modo producción apuntando a la raíz del workdir
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5021", "--proxy-headers"]
