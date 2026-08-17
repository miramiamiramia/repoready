"""RepoReady: verify whether a repository is ready for new contributors."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class Check:
    name: str
    status: str
    details: str


@dataclass
class Report:
    repository: str
    score: int
    checks: list[Check]
    commands_found: list[str]
    next_steps: list[str]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["checks"] = [asdict(c) for c in self.checks]
        return data


def readme_path(root: Path) -> Path | None:
    for name in ("README.md", "README.rst", "README.txt", "README"):
        candidate = root / name
        if candidate.is_file():
            return candidate
    return None


def extract_commands(text: str) -> list[str]:
    commands: list[str] = []
    in_block = False
    language = ""
    for line in text.splitlines():
        fence = re.match(r"^\s*```(\w*)\s*$", line)
        if fence:
            if in_block:
                in_block = False
                language = ""
            else:
                in_block = True
                language = fence.group(1).lower()
            continue
        if in_block and language in {"", "bash", "sh", "shell", "console", "zsh"}:
            value = line.strip()
            value = re.sub(r"^\$\s*", "", value)
            if value and not value.startswith(("#", ">")):
                commands.append(value)
    return commands[:50]


def detect_files(root: Path) -> list[Check]:
    checks: list[Check] = []
    readme = readme_path(root)
    checks.append(Check("README", "pass" if readme else "fail", "README file found." if readme else "No README file found."))
    has_license = any((root / name).is_file() for name in ("LICENSE", "LICENSE.md", "COPYING"))
    checks.append(Check("License", "pass" if has_license else "warn", "License file found." if has_license else "Add an open-source license."))
    has_contrib = any((root / name).is_file() for name in ("CONTRIBUTING.md", ".github/CONTRIBUTING.md"))
    checks.append(Check("Contribution guide", "pass" if has_contrib else "warn", "Contribution guide found." if has_contrib else "Add CONTRIBUTING.md for new contributors."))
    has_ci = (root / ".github/workflows").is_dir() and any((root / ".github/workflows").glob("*.y*ml"))
    checks.append(Check("CI", "pass" if has_ci else "warn", "GitHub Actions workflow found." if has_ci else "Add CI to show that checks run automatically."))
    has_tests = any((root / name).is_dir() for name in ("tests", "test", "spec"))
    checks.append(Check("Tests", "pass" if has_tests else "warn", "Test directory found." if has_tests else "Add a test directory and a quick-start test."))
    return checks


def verify_commands(root: Path, commands: Iterable[str], run: bool = False) -> list[Check]:
    checks: list[Check] = []
    safe_prefixes = ("python -m pytest", "pytest", "npm test", "pnpm test", "yarn test", "npm run build", "pnpm build", "cargo test", "go test")
    for command in commands:
        if not run:
            continue
        if not command.startswith(safe_prefixes):
            continue
        try:
            result = subprocess.run(command, cwd=root, shell=True, text=True, capture_output=True, timeout=120)
            status = "pass" if result.returncode == 0 else "fail"
            output = (result.stdout or result.stderr).strip().splitlines()
            details = output[-1][:240] if output else f"Exit code {result.returncode}."
        except subprocess.TimeoutExpired:
            status, details = "fail", "Command timed out after 120 seconds."
        checks.append(Check(f"Command: {command}", status, details))
    return checks


def build_report(root: Path, run: bool = False) -> Report:
    root = root.resolve()
    readme = readme_path(root)
    commands = extract_commands(readme.read_text(encoding="utf-8", errors="replace")) if readme else []
    checks = detect_files(root)
    checks.extend(verify_commands(root, commands, run=run))
    points = {"pass": 1, "warn": 0, "fail": -1}
    score = round(max(0, min(100, 70 + sum(points[c.status] for c in checks) * 6)))
    next_steps = [c.details for c in checks if c.status != "pass"]
    if not commands:
        next_steps.append("Document at least one copy-paste setup or test command in README.")
    return Report(root.name, score, checks, commands, next_steps)


def markdown(report: Report) -> str:
    lines = [f"# RepoReady report: `{report.repository}`", "", f"**Onboarding score:** `{report.score}/100`", "", "| Check | Status | Details |", "|---|---|---|"]
    icons = {"pass": "PASS", "warn": "WARN", "fail": "FAIL"}
    lines.extend(f"| {c.name} | {icons.get(c.status, c.status.upper())} | {c.details.replace('|', '/')} |" for c in report.checks)
    lines += ["", "## Commands found", ""]
    lines += [f"- `{cmd}`" for cmd in report.commands_found] or ["No shell commands were found in README code blocks."]
    lines += ["", "## Next steps", ""]
    lines += [f"- {step}" for step in report.next_steps] or ["No immediate blockers detected."]
    lines += ["", "Generated by [RepoReady](https://github.com/repoready/repoready)."]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify whether a repository is ready for new contributors.")
    parser.add_argument("path", nargs="?", default=".", help="Repository path")
    parser.add_argument("--run", action="store_true", help="Run allow-listed test/build commands found in README")
    parser.add_argument("--format", choices=("md", "json"), default="md")
    parser.add_argument("--output", help="Write report to a file instead of stdout")
    args = parser.parse_args(argv)
    report = build_report(Path(args.path), run=args.run)
    content = json.dumps(report.to_dict(), indent=2) if args.format == "json" else markdown(report)
    if args.output:
        Path(args.output).write_text(content + ("\n" if args.format == "json" else ""), encoding="utf-8")
    else:
        print(content)
    return 0 if all(c.status != "fail" for c in report.checks) else 2


if __name__ == "__main__":
    sys.exit(main())
