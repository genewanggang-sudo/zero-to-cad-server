$ErrorActionPreference = 'Stop'

ruff format --check .
ruff check .
pytest
