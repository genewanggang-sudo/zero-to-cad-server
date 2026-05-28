from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def export_cadquery_code(
    code: str,
    output_dir: Path,
    formats: list[str],
    timeout_seconds: int,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_path = output_dir / "generated.py"
    generated_path.write_text(code, encoding="utf-8")

    command = [
        sys.executable,
        "-m",
        "zero_to_cad_runtime.export_runner",
        str(generated_path),
        str(output_dir),
        json.dumps(formats),
    ]
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    if result.returncode != 0:
        details = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"CadQuery export failed: {details}")

    return [output_dir / f"output.{fmt}" for fmt in formats]
