$ErrorActionPreference = 'Stop'

docker build --target dev -t zero-to-cad-server:dev .
docker run --rm zero-to-cad-server:dev ruff format --check .
docker run --rm zero-to-cad-server:dev ruff check .
docker run --rm zero-to-cad-server:dev pytest
