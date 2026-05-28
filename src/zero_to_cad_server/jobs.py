from __future__ import annotations

import json
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

from zero_to_cad_server.exporter import export_cadquery_code
from zero_to_cad_server.model import ZeroToCadModel
from zero_to_cad_server.schemas import JobStatus


class JobManager:
    def __init__(
        self,
        data_dir: Path,
        model: ZeroToCadModel,
        export_timeout_seconds: int,
    ) -> None:
        self._jobs_dir = data_dir / "jobs"
        self._jobs_dir.mkdir(parents=True, exist_ok=True)
        self._model = model
        self._export_timeout_seconds = export_timeout_seconds
        self._executor = ThreadPoolExecutor(max_workers=1)

    def submit(self, image_paths: list[Path], formats: list[str]) -> JobStatus:
        job_id = uuid.uuid4().hex
        job_dir = self._jobs_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=False)
        for index, source in enumerate(image_paths):
            source.replace(job_dir / f"view_{index}.png")

        status = JobStatus(job_id=job_id, status="queued")
        self._write_status(job_dir, status)
        self._executor.submit(self._run_job, job_id, formats)
        return status

    def get(self, job_id: str) -> JobStatus | None:
        job_dir = self._jobs_dir / job_id
        status_path = job_dir / "status.json"
        if not status_path.exists():
            return None
        return JobStatus.model_validate_json(status_path.read_text(encoding="utf-8"))

    def artifact_path(self, job_id: str, filename: str) -> Path | None:
        job_dir = self._jobs_dir / job_id
        path = (job_dir / filename).resolve()
        if not str(path).startswith(str(job_dir.resolve())):
            return None
        if not path.exists() or not path.is_file():
            return None
        return path

    def _run_job(self, job_id: str, formats: list[str]) -> None:
        job_dir = self._jobs_dir / job_id
        self._write_status(job_dir, JobStatus(job_id=job_id, status="running"))
        try:
            views = [Image.open(job_dir / f"view_{index}.png") for index in range(8)]
            code = self._model.generate_cadquery(views)
            artifacts = export_cadquery_code(
                code=code,
                output_dir=job_dir,
                formats=formats,
                timeout_seconds=self._export_timeout_seconds,
            )
            artifact_names = ["generated.py", *[path.name for path in artifacts]]
            self._write_status(
                job_dir,
                JobStatus(job_id=job_id, status="succeeded", artifacts=artifact_names),
            )
        except Exception:
            self._write_status(
                job_dir,
                JobStatus(
                    job_id=job_id,
                    status="failed",
                    error=traceback.format_exc(),
                ),
            )

    def _write_status(self, job_dir: Path, status: JobStatus) -> None:
        status_path = job_dir / "status.json"
        status_path.write_text(
            json.dumps(status.model_dump(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
