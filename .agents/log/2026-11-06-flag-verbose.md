# 2026-11-06: `--show-request` renamed to `--verbose`

## What was done

- In `src/jev_catdog/cli/commands.py`, the shared `--show-request` option is renamed to `--verbose`, with the short alias `-v`. It behaves as before: it adds the request sent to Jev to the JSON output, under the `request` key.
- `CLAUDE.md` (Status) is updated with the new name.

## Decisions and why

- A rename requested by the user, with no change in behaviour. `--show-request` no longer exists and no alias is kept, because there are no external users depending on it yet.
- The previous log entry is left untouched, because it records the state at that time.

## Verification

- `uv run pytest`: 18 pass.
- `uv run cat-detect-text "Ladra y mueve la cola" -v` includes `request` in the output.
