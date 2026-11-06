# 2026-11-06: initial CLI and Postman collection

## What was done

- uv project `jev-catdog` (Python ≥ 3.12; dependencies `httpx`, `pillow` and `python-dotenv`; `pytest` for development) with five scripts: `cat-detect-text`, `cat-detect-image`, `choice-cat-dog`, `score-cat-dog` and `crop-cat-dog-face`.
- Layered architecture in `src/jev_catdog/`:
  - `jev/`: domain with no I/O. `questions.py` holds `Noul`, `Choice`, `Score` and `Box` with `to_payload()`; `answers.py` holds the typed answers and `parse_answers`; `request.py` defines `JevRequest` with `payload()` and `describe()`; `gateway.py` defines the `JevGateway` port.
  - `infrastructure/`: `TypeSafeGateway` (httpx), `ImagePreparer` (resizes), `ImageCropper` (crops) and `Settings` (reads `.env`).
  - `use_cases/`: one use case per command, with its `QUESTIONS` at the top, plus `ports.py` (`ImageLoader`, `Cropper`, `load_image`).
  - `cli/`: `container.py` (composition root), `presenter.py` (JSON to stdout or stderr) and `commands.py` (argparse).
- `--show-request` adds the request that was sent to the output; `--dry-run` shows it without calling the API.
- 18 network-free tests in `tests/`.
- Postman v3 collection in `postman/collections/Jev CatDog/`, with the five requests, `pm.test` tests and 200 examples taken from real responses. The environment is in `postman/environments/TypeSafe.environment.yaml`, with the key as an empty secret.
- `CLAUDE.md`: Status, Conventions and DSR sections, and verified notes on Jev.

## Decisions and why

- **Native TypeSafe** (`/v1/systemone`): NanoGPT and Portkey accept neither Jev images nor `box`. The key in `.env` (`JEV_API_KEY`) was validated with a real call, and `jev-latest` resolves to `jev-1.14.0`.
- **httpx instead of `typesafe-sdk`**: the SDK does not document `box`, and this keeps the request in plain view.
- **Multipart instead of base64**: the request JSON stays readable, and Postman can use the same shape, with a `request` part and a `photo` part.
- **Resizing up front**: some dataset images (`dogs_01`, `dogs_04`, `dogs_08`, `other_05`) are taller than 1568 px. Since `box` returns fractions, the crop is taken from the full-resolution original.
- **Companion `noul` in `crop-cat-dog-face`**: `box` always returns a box. If `has_face` is below `--threshold` (0.5), the command exits with `face_not_found` and code 1.
- **`score-cat-dog` as a counterexample**: a two-level rubric (cat → dog). `cat_probability` and `dog_probability` come from `probabilities["0"]` and `probabilities["1"]`, and the `note` field recommends `choice`.
- **Probabilities without percentages**: the user asked for a single field between 0 and 1.

## Real verification (jev-1.14.0)

| Command | Input | Result |
|---|---|---|
| `cat-detect-text` | tuna description | `is_cat_probability` 0.86 |
| `cat-detect-image` | `cats/cats_01.jpg` | 0.97 |
| `choice-cat-dog` | `other/other_01.jpg` / `dogs/dogs_02.jpg` | `other` 1.0 / `dog` 1.0 |
| `score-cat-dog` | `dogs/dogs_01.jpg` (1280×1917, resized) / `cats/cats_03.jpg` | `dog` 0.98 / `cat` 0.97 |
| `crop-cat-dog-face` | `dogs/dogs_03.jpg`, `cats/cats_01.jpg` | correct crops in `output/` (checked by eye) |
| `crop-cat-dog-face` | `other/other_03.jpg` | `face_not_found` (`face_probability` 0.09), code 1 |

Postman: `collection lint` with no warnings, and `collection run` with 5/5 requests and 10/10 assertions passing.

## Pending / worth knowing

- The `box` `confidence` is low (0.3–0.65) even when the boxes are good, so it is not used as a filter.
- The crop of the `cats_01` cat slightly clips the tip of one ear; an optional margin could be added.
- When `--show-request` is used without `--dry-run`, the image is prepared twice (once to describe it and once to send it).
- `postman workspace lint` asks for `.postman/` because `postman init` has not been run; that is only needed when linking a cloud workspace.
- The directory is not a git repository yet.
