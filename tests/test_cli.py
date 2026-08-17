from pathlib import Path

from repoready.cli import build_report, extract_commands


def test_extract_commands():
    text = """# Demo\n```bash\n$ python -m pytest\nnpm run build\n```\n"""
    assert extract_commands(text) == ["python -m pytest", "npm run build"]


def test_report_detects_missing_project_files(tmp_path: Path):
    (tmp_path / "README.md").write_text("# Demo\n\n```bash\npython -m pytest\n```\n", encoding="utf-8")
    report = build_report(tmp_path)
    names = {check.name for check in report.checks}
    assert "README" in names
    assert report.score < 100
    assert report.next_steps


def test_report_passes_project_files(tmp_path: Path):
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("MIT", encoding="utf-8")
    (tmp_path / "CONTRIBUTING.md").write_text("Contribute", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / ".github/workflows").mkdir(parents=True)
    (tmp_path / ".github/workflows/test.yml").write_text("name: test", encoding="utf-8")
    report = build_report(tmp_path)
    assert all(check.status in {"pass", "warn"} for check in report.checks)
