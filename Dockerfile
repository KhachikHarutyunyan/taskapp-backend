# Build Stage
FROM python:3.12-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.1.3 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN apt-get update && \ 
    apt-get install -y --no-install-recommends curl build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

COPY pyproject.toml poetry.lock ./

RUN /opt/poetry/bin/poetry install --only main --no-root

# Final Stage
FROM python:3.12-slim

WORKDIR /app

# User configuration arguments
ARG UID=10000
ARG GID=10001


# Create user and group
RUN groupadd -g ${GID} appgroup && \
    useradd -u ${UID} -g appgroup -m -d /app appuser && \
    mkdir -p /app/logs && \
    chown -R ${UID}:${GID} /app


# Set Python path
ENV PYTHONPATH=/app

# Copy dependencies from building stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code with correct ownership
COPY --chown=appuser:appgroup src ./src
COPY --chown=appuser:appgroup entrypoint.sh ./
COPY --chown=appuser:appgroup run.py alembic.ini ./
COPY --chown=appuser:appgroup alembic ./alembic 
COPY --chown=appuser:appgroup logs ./logs 

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

USER appuser

EXPOSE 8201

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8201"]