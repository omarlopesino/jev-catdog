# 2026-11-06: `--format image` summary cards

## What was done

- Every command accepts `--format json|image` (default `json`) and `--card PATH`. With `image`, the result is drawn as a 1200×630 PNG card (rendered at 2400×1260) and stdout prints `{"card": path}`, plus `request` with `--verbose`.
- `infrastructure/card_canvas.py`: Pillow primitives (header, photo with object-fit cover and rounded corners, colour tile with centred text, quote, red X panel, caption) over one fixed geometry: 56 px padding, 96 px header, 394 px content row.
- `infrastructure/card_renderer.py`: one layout per result type, plus `render_failure` for `face_not_found`. `Container.cards` exposes it.
- Fonts bundled in `infrastructure/fonts/` with their OFL licences: Bricolage Grotesque, Instrument Sans (variable fonts), Instrument Serif Italic and IBM Plex Mono Medium.
- `tests/test_cards.py`: card size, traffic-light and class colours, long-quote fitting, and the not-found card.

## Decisions and why

- The layouts follow the Design canvas (https://claude.ai/artifact/LyKmSv7FMwZcjBPZgkuYhE). Every panel fills the same 394 px row so photos and tiles share top and bottom edges.
- The renderer lives in `infrastructure` and imports the use-case result types: adapters may depend on the use-case layer, and `cli` still only reaches it through the container.
- Noul tiles use a traffic light (green ≥ 0.75, orange ≥ 0.40, red below). choice and score use fixed class colours (cat blue, dog orange, other grey) so they are not read as good or bad.
- `face_not_found` keeps exit code 1 and its stderr JSON, as in JSON mode, but also saves the red-X card and adds `card` to the error.
- Long descriptions shrink from 40 to 24 px and are then cut with an ellipsis; numbers in tiles shrink until they fit, so 100% never spills out.

## Verification

- `uv run pytest`: 26 pass.
- Against the real API, all five commands with `--format image` produced cards, and `crop-cat-dog-face data/other/other_03.jpg` produced the red-X card (face probability 0.11) with exit code 1.

## Pending

- Captions and labels are English-only and the card size is fixed; no option yet for other sizes or a dark theme.
