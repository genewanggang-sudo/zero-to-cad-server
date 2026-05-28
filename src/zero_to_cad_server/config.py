from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    model_id: str
    data_dir: Path
    max_new_tokens: int
    export_timeout_seconds: int


def load_settings() -> Settings:
    return Settings(
        model_id=os.getenv("ZERO_TO_CAD_MODEL_ID", "ADSKAILab/Zero-To-CAD-Qwen3-VL-2B"),
        data_dir=Path(os.getenv("ZERO_TO_CAD_DATA_DIR", "data")).resolve(),
        max_new_tokens=int(os.getenv("ZERO_TO_CAD_MAX_NEW_TOKENS", "4096")),
        export_timeout_seconds=int(os.getenv("ZERO_TO_CAD_EXPORT_TIMEOUT_SECONDS", "120")),
    )
