FROM python:3.8-slim as base

ARG POETRY_VERSION=1.1.14

RUN apt-get update \
    && apt-get install -y curl libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | POETRY_VERSION=$POETRY_VERSION python3 -

RUN pip install psycopg2-binary --user

ENV PATH="${PATH}:/root/.local/bin"

COPY ./pyproject.toml ./app/
WORKDIR ./app

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-root

ENV PYTHONPATH=${PYTHONPATH}:.

COPY src/common ./common


FROM base as web

EXPOSE 8000

COPY src/web ./web

CMD ["python", "web/app.py"]


FROM base as worker

COPY ./src/worker ./worker

CMD ["python", "worker/app.py"]
