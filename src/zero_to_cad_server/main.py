from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from zero_to_cad_server.config import load_settings
from zero_to_cad_server.jobs import JobManager
from zero_to_cad_server.model import ModelConfig, ZeroToCadModel
from zero_to_cad_server.schemas import JobAccepted, JobStatus

settings = load_settings()
model = ZeroToCadModel(
    ModelConfig(
        model_id=settings.model_id,
        max_new_tokens=settings.max_new_tokens,
    )
)
jobs = JobManager(
    data_dir=settings.data_dir,
    model=model,
    export_timeout_seconds=settings.export_timeout_seconds,
)

app = FastAPI(title="Zero-to-CAD Server", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/jobs", response_model=JobAccepted, status_code=202)
async def create_job(
    images: Annotated[list[UploadFile], File()],
    formats: Annotated[list[str] | None, Form()] = None,
) -> JobAccepted:
    if len(images) != 8:
        raise HTTPException(status_code=400, detail="Exactly 8 images are required.")

    requested_formats = formats or ["step", "stl"]
    clean_formats = sorted({fmt.lower().lstrip(".") for fmt in requested_formats})
    unsupported = [fmt for fmt in clean_formats if fmt not in {"step", "stl"}]
    if unsupported:
        raise HTTPException(status_code=400, detail=f"Unsupported export formats: {unsupported}")

    temp_dir = Path(tempfile.mkdtemp(prefix="zero-to-cad-upload-"))
    image_paths: list[Path] = []
    try:
        for index, upload in enumerate(images):
            target = temp_dir / f"view_{index}.png"
            target.write_bytes(await upload.read())
            image_paths.append(target)
        status = jobs.submit(image_paths=image_paths, formats=clean_formats)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return JobAccepted(job_id=status.job_id, status=status.status)


@app.get("/v1/jobs/{job_id}", response_model=JobStatus)
def get_job(job_id: str) -> JobStatus:
    status = jobs.get(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return status


@app.get("/v1/jobs/{job_id}/artifacts/{filename}")
def get_artifact(job_id: str, filename: str) -> FileResponse:
    path = jobs.artifact_path(job_id, filename)
    if path is None:
        raise HTTPException(status_code=404, detail="Artifact not found.")
    return FileResponse(path)


def run() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
