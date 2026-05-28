from __future__ import annotations

import json
import sys
from pathlib import Path

import cadquery as cq


def main() -> int:
    generated_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    formats = json.loads(sys.argv[3])

    namespace: dict[str, object] = {
        "cq": cq,
        "show_object": lambda *args, **kwargs: None,
    }
    code = generated_path.read_text(encoding="utf-8")
    exec(code, namespace, namespace)

    result = namespace.get("result")
    if result is None:
        raise RuntimeError("Generated code did not define `result`.")

    for fmt in formats:
        cq.exporters.export(result, str(output_dir / f"output.{fmt}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
