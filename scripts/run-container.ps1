$ErrorActionPreference = 'Stop'

$root = Resolve-Path -LiteralPath "$PSScriptRoot\.."

docker run --rm --gpus all `
  -p 8000:8000 `
  -v "${root}\data:/app/data" `
  -v "${root}\hf-cache:/app/hf-cache" `
  zero-to-cad-server:service
