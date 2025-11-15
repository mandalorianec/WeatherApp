FROM python:3.12-slim

# Создаём пользователя
RUN groupadd -r groupdjango && useradd -r -g groupdjango userdj

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG DEBUG=false

WORKDIR /app

COPY pyproject.toml poetry.lock ./

# Системные зависимости для сборки psycopg2 и др.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Ставим Poetry
RUN pip install poetry

# Отключаем создание виртуальных окружений — всё ставится в системный site-packages
RUN poetry config virtualenvs.create false

# Устанавливаем Python-зависимости без установки самого проекта (no-root)
RUN if [ "$(echo "$DEBUG" | tr '[:upper:]' '[:lower:]')" = "true" ] ; then \
      # Если DEBUG=true (или True, TRUE...), устанавливаем ВСЕ зависимости
      poetry install --no-root ; \
    else \
      # Иначе, ставим только основные, БЕЗ dev
      poetry install --without dev --no-root ; \
    fi

COPY . .

USER userdj
