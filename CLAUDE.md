# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

Usage examples of Jev's question types (`noul`, `score`, `choice`) and of `box`, applied to cats and dogs.

The examples form a progression, each building on the previous one:

1. **`noul` with text**: given a description, the probability that the animal is a cat.
2. **`noul` with an image**: the same question, asked about an image.
3. **`choice` with an image**: decide whether it is a dog or a cat.
4. **`score` with an image**: rate on a scale from cat to dog. This is a deliberate counterexample: it shows that `choice` fits unordered categories better.
5. **`box`**: locate and crop only the animal's face.

## Status

Python CLI managed with uv. All five examples are implemented and verified against the real API.

- Commands: `uv run cat-detect-text "<description>"`, `uv run cat-detect-image <img>`, `uv run choice-cat-dog <img>`, `uv run score-cat-dog <img>`, `uv run crop-cat-dog-face <img> [--out PATH] [--threshold 0.5]`. All accept `--verbose` (`-v`), `--dry-run` and `--format json|image` (`--card PATH` for where the PNG card goes).
- Tests: `uv run pytest`, no network (gateway faked with `httpx.MockTransport` and `FakeGateway` in `tests/conftest.py`).
- Configuration: `JEV_API_KEY` in `.env` (loaded with python-dotenv; never printed or committed). `JEV_BASE_URL` and `JEV_MODEL` are optional.
- Postman: v3 collection in `postman/collections/Jev CatDog/` and environment `postman/environments/TypeSafe.environment.yaml`. Lint with `postman collection lint "postman/collections/Jev CatDog"`. Run it from the repository root with `postman collection run "postman/collections/Jev CatDog" -e postman/environments/TypeSafe.environment.yaml --env-var jev_api_key=... --working-dir .`.
- Image cards: `infrastructure/card_canvas.py` holds the Pillow primitives and fixed 1200×630 geometry (drawn at 2×), `infrastructure/card_renderer.py` one layout per result type. The design lives in the Design canvas https://claude.ai/artifact/LyKmSv7FMwZcjBPZgkuYhE.
- Layered architecture: `cli` → `use_cases` → `jev` (domain and `JevGateway` port) ← `infrastructure` (httpx, Pillow, settings). Only `cli/container.py` knows the concrete implementations.

## Conventions

- Every module, class and public function has a 10–20 word docstring saying what it does and why it exists. Inline comments appear only where the reason is not obvious.
- Each use case declares its questions at the top of its file, in the `QUESTIONS` constant, so the request sent to Jev reads at a glance.
- Output is JSON with `snake_case` English keys, and all its text (`message`, `note`…) is in English too, because it will be used in an English article. Probabilities are a single number between 0 and 1, never duplicated as percentages. Errors go to stderr as `{"error", "message", ...}` with exit code 1.
- Everything is written in English: code, docstrings and comments, `--help` text, tests, the Postman collection, and documentation (this file, `README.md` and `.agents/log/`).

## DSR-001: Record technical progress

After every development, record the technical progress in `.agents/log/YYYY-MM-DD-<topic>.md` without waiting to be asked: what was done, the decisions and why, and what is still pending.

## Notes on Jev

- `noul`, `choice` and `score` are question types inside a single request, not separate endpoints: `noul` returns the probability that a yes/no statement is true, `choice` picks an option with a probability for each one, and `score` gives an expected value over an ordered rubric.
- Provider: the native TypeSafe API, `POST https://api.typesafe.ai/v1/systemone` with `Authorization: Bearer`. It is the only provider that accepts images with Jev and supports `box`. `jev-latest` resolves to `jev-1.14.0`.
- Images: multipart with a `request` part (the JSON) and one part per image, declared in `assets` as `{"type": "image", "part": "photo"}` and referenced from `state`. Requires the `TypeSafe-Danger-Zone-Images: true` header. Limits: each side between 280 and 1568 px and at most 2,458,624 pixels in total; `ImagePreparer` shrinks images that exceed them.
- `box` (verified): the question only takes `instructions`. The answer is `{"type": "box", "box": {"top", "bottom", "left", "right"}, "confidence"}`, as fractions from the top-left corner. It always returns a box, so a companion `noul` is asked alongside it to tell whether the target exists.
