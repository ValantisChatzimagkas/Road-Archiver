FROM python:3.13-slim


RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libzbar0 \
    libpq-dev \
    && apt-get clean

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main


COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]