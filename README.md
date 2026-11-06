# jev-catdog

Console examples of [Jev](https://docs.typesafe.ai/) (TypeSafe) applied to cats and dogs. Each command shows one question type: `noul`, `choice`, `score` or `box`, and prints JSON.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and a TypeSafe API key.

```sh
echo 'JEV_API_KEY=your-key' > .env
uv sync
```

Optional variables: `JEV_MODEL` (default `jev-latest`; `box` needs `jev-1.14` or later) and `JEV_BASE_URL` (default `https://api.typesafe.ai/v1`).

## Commands

The examples build on each other. The images come from the dataset in `data/` (see `data/CREDITS.md`).

### 1. Is the description about a cat? (`noul`, text)

```sh
uv run cat-detect-text "It looks like a tiger but smaller. When I open a can of tuna it comes running and meows."
```

```json
{
  "input": "It looks like a tiger but smaller. When I open a can of tuna it comes running and meows.",
  "is_cat_probability": 0.89
}
```

### 2. Is there a cat in the image? (`noul`, image)

```sh
uv run cat-detect-image ./data/cats/cats_01.jpg
```

```json
{ "image": "data/cats/cats_01.jpg", "is_cat_probability": 0.97 }
```

### 3. Cat, dog or something else? (`choice`)

```sh
uv run choice-cat-dog ./data/dogs/dogs_02.jpg
```

```json
{
  "image": "data/dogs/dogs_02.jpg",
  "choice": "dog",
  "confidence": 1.0,
  "probabilities": { "cat": 0.0, "dog": 1.0, "other": 0.0 }
}
```

### 4. Where on the cat-to-dog scale? (`score`, a counterexample)

```sh
uv run score-cat-dog ./data/dogs/dogs_01.jpg
```

```json
{
  "image": "data/dogs/dogs_01.jpg",
  "score": 0.98,
  "confidence": 0.96,
  "cat_probability": 0.02,
  "dog_probability": 0.98,
  "note": "Score assumes ordered levels; for unordered categories such as cat or dog, choice is a better fit."
}
```

`score` is meant for ordered rubrics. Cat and dog have no order, which is why `choice` is the better tool here.

### 5. Crop the animal's face (`box`)

```sh
uv run crop-cat-dog-face ./data/dogs/dogs_03.jpg
```

```json
{
  "image": "data/dogs/dogs_03.jpg",
  "face_found": true,
  "face_probability": 0.95,
  "confidence": 0.4,
  "box": { "top": 0.22, "bottom": 0.73, "left": 0.07, "right": 0.88 },
  "output": "output/dogs_03_face.jpg"
}
```

`box` always returns a box, even when there is nothing to find, so the same request also asks a `noul` ("Is the face of a cat or a dog visible?"). Below `--threshold` (default 0.5) the command fails instead of cropping:

```json
{
  "error": "face_not_found",
  "message": "No cat or dog face was found in the image.",
  "image": "data/other/other_03.jpg",
  "face_probability": 0.09
}
```

Use `--out PATH` to choose where the crop is saved.

## Image cards

Every command also accepts `--format image`, which saves a 1200×630 PNG card summarising the result (drawn at 2× for sharp text) and prints its path:

```sh
uv run choice-cat-dog ./data/dogs/dogs_02.jpg --format image
```

```json
{ "card": "output/dogs_02_choice-cat-dog.png" }
```

The card goes to `output/<image name>_<command>.png` (`text_cat-detect-text.png` for the text command); `--card PATH` picks another path. The noul cards colour the probability green from 75%, orange from 40% and red below. When `crop-cat-dog-face` finds no face, it still saves a card with a red X, adds its path to the error under `card` and exits with code 1. The fonts (Bricolage Grotesque, Instrument Sans, Instrument Serif and IBM Plex Mono, all under the SIL Open Font License) ship in `src/jev_catdog/infrastructure/fonts/`.

## Seeing the request sent to Jev

Every command accepts:

- `--verbose` / `-v`: adds the exact request sent to Jev to the output, under `request`.
- `--dry-run`: prints the request without calling the API.

```sh
uv run cat-detect-image ./data/cats/cats_01.jpg --dry-run
```

```json
{
  "request": {
    "model": "jev-latest",
    "state": { "photo": "photo" },
    "questions": {
      "is_cat": { "type": "noul", "instructions": "Is there a cat in `photo`?" }
    },
    "assets": {
      "photo": { "type": "image", "part": "photo", "file": "cats_01.jpg 1280x903 -> 1280x903" }
    }
  }
}
```

Images are sent as multipart: a `request` part with the JSON above and a `photo` part with the image. Images larger than Jev's limits (1568 px per side) are shrunk before sending; crops are always taken from the original.

Errors go to stderr as `{"error": "...", "message": "..."}` with exit code 1.

## Postman

The same five requests live in a Postman collection, with tests and saved real responses:

```sh
postman collection run "postman/collections/Jev CatDog" \
  -e postman/environments/TypeSafe.environment.yaml \
  --env-var jev_api_key=your-key --working-dir .
```

Run it from the repository root so the image paths under `data/` resolve.

## Architecture

```
src/jev_catdog/
  jev/             domain: questions, answers, request, JevGateway port (no I/O)
  use_cases/       one per command; each declares its QUESTIONS at the top
  infrastructure/  TypeSafe HTTP gateway, image preparer and cropper, settings, card renderer
  cli/             argparse commands, JSON presenter, composition root
```

Dependencies point inwards: use cases only know the `JevGateway` interface, and `cli/container.py` is the only place that builds the concrete implementations.

## Tests

```sh
uv run pytest
```

The tests use no network: the HTTP layer is faked with `httpx.MockTransport` and the use cases with a `FakeGateway`.
