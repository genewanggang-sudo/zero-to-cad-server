FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

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
        libxrender1 \
        python3 \
        python3-pip \
        python3-venv && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY src /app/src

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install .

EXPOSE 8000

CMD ["uvicorn", "zero_to_cad_runtime.main:app", "--host", "0.0.0.0", "--port", "8000"]
