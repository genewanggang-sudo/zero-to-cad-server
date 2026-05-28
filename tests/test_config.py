from pathlib import Path

from zero_to_cad_server.config import load_settings


def test_load_settings_uses_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("ZERO_TO_CAD_MODEL_ID", "local/model")
    monkeypatch.setenv("ZERO_TO_CAD_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("ZERO_TO_CAD_MAX_NEW_TOKENS", "128")
    monkeypatch.setenv("ZERO_TO_CAD_EXPORT_TIMEOUT_SECONDS", "30")

    settings = load_settings()

    assert settings.model_id == "local/model"
    assert settings.data_dir == Path(tmp_path).resolve()
    assert settings.max_new_tokens == 128
    assert settings.export_timeout_seconds == 30
