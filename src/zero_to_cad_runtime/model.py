from __future__ import annotations

from dataclasses import dataclass
from threading import Lock

from PIL import Image


@dataclass(frozen=True)
class ModelConfig:
    model_id: str
    max_new_tokens: int


class ZeroToCadModel:
    def __init__(self, config: ModelConfig) -> None:
        self._config = config
        self._lock = Lock()
        self._model = None
        self._processor = None

    def generate_cadquery(self, views: list[Image.Image]) -> str:
        if len(views) != 8:
            raise ValueError("Zero-to-CAD expects exactly 8 input views.")

        model, processor = self._load()
        rgb_views = [view.convert("RGB") for view in views]
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a CAD code assistant. Given multiple rendered views "
                    "of a 3D shape, generate clean CadQuery Python code that "
                    "recreates the geometry. Define the final object as `result`."
                ),
            },
            {
                "role": "user",
                "content": [
                    *[{"type": "image", "image": view} for view in rgb_views],
                    {"type": "text", "text": "Generate CadQuery code for this shape."},
                ],
            },
        ]

        prompt = processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = processor(text=prompt, images=rgb_views, return_tensors="pt").to(model.device)
        output_ids = model.generate(**inputs, max_new_tokens=self._config.max_new_tokens)
        generated_ids = output_ids[:, inputs.input_ids.shape[1] :]
        return processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    def _load(self):
        with self._lock:
            if self._model is None or self._processor is None:
                from transformers import AutoProcessor, Qwen3VLForConditionalGeneration

                self._model = Qwen3VLForConditionalGeneration.from_pretrained(
                    self._config.model_id,
                    torch_dtype="auto",
                    device_map="auto",
                )
                self._processor = AutoProcessor.from_pretrained(self._config.model_id)
            return self._model, self._processor
