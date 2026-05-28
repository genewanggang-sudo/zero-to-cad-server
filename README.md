# zero-to-cad-server

Zero-to-CAD Server is a deployable HTTP service that accepts eight rendered
views of a CAD object, runs the Zero-to-CAD model, generates CadQuery code, and
exports CAD artifacts such as STEP and STL.

This project is the service version of the earlier local verification scripts.
The old Docker-only validation flow has been removed. Docker is now used as a
deployment package for the service.

## What It Provides

- `POST /v1/jobs`: submit eight images and start an async inference job
- `GET /v1/jobs/{job_id}`: inspect job status and artifact names
- `GET /v1/jobs/{job_id}/artifacts/{filename}`: download generated files
- `GET /health`: lightweight process health check

Each completed job writes files under `data/jobs/{job_id}/`:

- `generated.py`: model-generated CadQuery code
- `output.step`: exported STEP file when requested
- `output.stl`: exported STL file when requested
- `status.json`: job status metadata

## Local Development

Create a virtual environment and install the package:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

Run the service:

```powershell
uvicorn zero_to_cad_server.main:app --reload --host 0.0.0.0 --port 8000
```

Run local checks after installing the development dependencies:

```powershell
python -m pip install -e ".[dev]"
.\scripts\check.ps1
```

Submit a job:

```powershell
curl.exe -X POST http://localhost:8000/v1/jobs `
  -F "images=@view_0.png" `
  -F "images=@view_1.png" `
  -F "images=@view_2.png" `
  -F "images=@view_3.png" `
  -F "images=@view_4.png" `
  -F "images=@view_5.png" `
  -F "images=@view_6.png" `
  -F "images=@view_7.png"
```

## Docker Deployment

Build and run with Docker Compose:

```powershell
docker compose up --build
```

Run checks inside the Docker development image:

```powershell
.\scripts\check-container.ps1
```

Or build and run directly:

```powershell
docker build -t zero-to-cad-server:service .
docker run --rm --gpus all -p 8000:8000 `
  -v "${PWD}\data:/app/data" `
  -v "${PWD}\hf-cache:/app/hf-cache" `
  zero-to-cad-server:service
```

On a server, install Docker and the NVIDIA Container Toolkit first if GPU
inference is required. Then deploy this project directory, build the image, and
start the container.

## Configuration

Environment variables:

- `ZERO_TO_CAD_MODEL_ID`: model id, default `ADSKAILab/Zero-To-CAD-Qwen3-VL-2B`
- `ZERO_TO_CAD_DATA_DIR`: service data directory, default `data`
- `ZERO_TO_CAD_MAX_NEW_TOKENS`: generation length, default `4096`
- `ZERO_TO_CAD_EXPORT_TIMEOUT_SECONDS`: CadQuery export timeout, default `120`

Copy `.env.example` when you need a local environment file:

```powershell
Copy-Item .env.example .env
```

## Operational Notes

The generated CadQuery code is executed in a separate Python process before
exporting STEP/STL. This protects the API process from most runtime failures,
but it is still code execution. For untrusted public traffic, run this service
inside a locked-down container or isolate the export worker further.
