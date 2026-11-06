# 2026-11-06: code, help and Postman collection in English

## What was done

- Translated to English across `src/` and `tests/`: every docstring and inline comment, the argparse `--help` text, and the test input strings.
- Translated the Postman collection: request names and descriptions, the image header description, the `pm.test` names, the example names, the collection definition and the environment description.
- The Postman text request (`01-cat-detect-text`) now sends the same English description as the README, and its saved example was recaptured from a real call (`noul` 0.88).
- `CLAUDE.md`: the language convention now covers everything (code, help, tests, Postman and documentation).

## Decisions and why

- The project will appear in an English article, so nothing user-visible or reader-visible stays in Spanish.
- Docstrings were kept within the 10–20 word convention; one translation came out at 9 words and was lengthened.
- The README shows 0.89 for example 1 and the Postman example 0.88: both are real responses, and Jev's output varies slightly between calls.

## Verification

- `uv run pytest`: 18 pass.
- Search for Spanish accented characters in `src`, `tests`, `postman`, `README.md` and `CLAUDE.md`: none left.
- `postman collection lint` and `environment lint`: no issues. `postman collection run`: 5/5 requests and 10/10 assertions pass.
