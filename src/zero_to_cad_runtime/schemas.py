from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


JobState = Literal["queued", "running", "succeeded", "failed"]


class JobAccepted(BaseModel):
    job_id: str
    status: JobState


class JobStatus(BaseModel):
    job_id: str
    status: JobState
    artifacts: list[str] = Field(default_factory=list)
    error: str | None = None
