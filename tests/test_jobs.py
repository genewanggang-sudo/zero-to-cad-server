from zero_to_cad_server.jobs import JobManager


class StubModel:
    def generate_cadquery(self, views):
        return "result = cq.Workplane('XY').box(1, 1, 1)"


def test_artifact_path_rejects_path_traversal(tmp_path):
    manager = JobManager(
        data_dir=tmp_path,
        model=StubModel(),
        export_timeout_seconds=1,
    )
    job_dir = tmp_path / "jobs" / "job-1"
    job_dir.mkdir(parents=True)
    (job_dir / "output.step").write_text("step", encoding="utf-8")

    assert manager.artifact_path("job-1", "output.step") == job_dir / "output.step"
    assert manager.artifact_path("job-1", "../outside.step") is None


def test_get_returns_none_for_unknown_job(tmp_path):
    manager = JobManager(
        data_dir=tmp_path,
        model=StubModel(),
        export_timeout_seconds=1,
    )

    assert manager.get("missing") is None
