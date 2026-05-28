FROM pytorch/pytorch:2.7.1-cuda12.8-cudnn9-runtime AS base

ENV DEBIAN_FRONTEND=noninteractive \
    HF_HOME=/app/hf-cache \
    HF_HUB_CACHE=/app/hf-cache/hub \
    TRANSFORMERS_CACHE=/app/hf-cache/transformers \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        git \
        libgl1 \
        libglib2.0-0 \
        libxrender1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY src /app/src

FROM base AS dev

COPY tests /app/tests

RUN python -m pip install --upgrade pip && \
    python -m pip install ".[dev]"

EXPOSE 8000

CMD ["uvicorn", "zero_to_cad_server.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS production

RUN python -m pip install --upgrade pip && \
    python -m pip install .

EXPOSE 8000

CMD ["uvicorn", "zero_to_cad_server.main:app", "--host", "0.0.0.0", "--port", "8000"]
