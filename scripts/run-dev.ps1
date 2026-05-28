$ErrorActionPreference = 'Stop'

uvicorn zero_to_cad_server.main:app --reload --host 0.0.0.0 --port 8000
