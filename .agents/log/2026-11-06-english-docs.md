# 2026-11-06: documentation in English and README

## What was done

- `CLAUDE.md` translated to English, with a new convention: documentation (`CLAUDE.md`, `README.md`, `.agents/log/`) is written in English.
- The existing log entries were translated, and their files renamed to English (`initial-cli`, `json-in-english`; `flag-verbose` keeps its name).
- New `README.md`: setup, the five commands with real outputs, `--verbose` / `--dry-run`, Postman, architecture and tests. `pyproject.toml` now points `readme` to it and has an English `description`.

## Decisions and why

- The user will publish an English article, so all of the project's prose is now in English.
- The outputs in the README are real results from `jev-1.14.0`. The example 1 description was translated to English and run again (0.89), instead of reusing the Spanish run's 0.86.
- The argparse help (`--help`) and the docstrings remain in Spanish; this change did not cover them.

## Verification

- `uv run pytest`: 18 pass.
