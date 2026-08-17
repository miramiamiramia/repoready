# RepoReady

> Verify whether a repository is genuinely ready for new contributors.

RepoReady is a small, safe CLI that inspects an open-source project and produces an onboarding report. It checks whether the repository has the basics a first-time contributor needs: a readable README, a license, contribution guidance, CI, tests, and documented commands.

Unlike a README generator, RepoReady focuses on **verification**. It turns a repository's current state into a concrete score and a list of next steps. Optional command execution is disabled by default and only runs an explicit allow-list of common test and build commands.

## Quick start

```bash
python -m pip install -e .
repoready /path/to/repository
```

Write a Markdown report:

```bash
repoready . --output repoready-report.md
```

Write machine-readable JSON:

```bash
repoready . --format json --output repoready-report.json
```

Run safe test/build commands found in README code blocks:

```bash
repoready . --run
```

`--run` is opt-in. RepoReady never executes arbitrary README commands; it only considers common test/build prefixes such as `pytest`, `npm test`, `cargo test`, and `go test`.

## What it checks

| Area | Example signal |
|---|---|
| Documentation | A README exists and contains copy-paste commands |
| Licensing | An open-source license file exists |
| Contribution | Contributors have a dedicated guide |
| Automation | GitHub Actions workflows are present |
| Quality | A test directory is present |
| Verification | Optional allow-listed tests/builds can be run |

## Why this exists

Many projects are easy to discover but difficult to join. Setup instructions go stale, tests are hidden, and first-time contributors cannot tell whether an issue is actionable. RepoReady is designed as a lightweight health check that maintainers can run locally or in CI before inviting more contributors.

## Development

```bash
python -m pytest
python -m repoready.cli .
```

The project is intentionally dependency-light and uses only the Python standard library at runtime.

## Roadmap

The first release is deliberately small. Planned extensions include a GitHub Action, a `RepoReady` badge, Docker-based clean-room verification, issue reproducibility scoring, and bilingual reports in English, French, and Arabic. These features will be added only with explicit, reviewable configuration and safe defaults.

## Contributing

Bug reports, test cases, and ideas are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. RepoReady should remain transparent, local-first, and safe for untrusted repositories.

## License

MIT. See [LICENSE](LICENSE).
