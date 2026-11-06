"""HTTP gateway to the native TypeSafe API: JSON for text, multipart when there are images."""

import json

import httpx

from jev_catdog.jev.answers import Answer, parse_answers
from jev_catdog.jev.gateway import JevError
from jev_catdog.jev.request import JevRequest

USER_AGENT = "jev-catdog/0.1"
TIMEOUT_SECONDS = 60.0


class TypeSafeGateway:
    """Implements JevGateway with POST /systemone; turns HTTP errors into readable JevError instances."""

    def __init__(self, api_key: str, base_url: str, model: str, client: httpx.Client | None = None):
        self.model = model
        self._url = f"{base_url}/systemone"
        self._headers = {"Authorization": f"Bearer {api_key}", "User-Agent": USER_AGENT}
        self._client = client or httpx.Client(timeout=TIMEOUT_SECONDS)

    def decide(self, request: JevRequest) -> dict[str, Answer]:
        """Sends the request, checks the HTTP status and returns the answers already typed."""
        try:
            response = self._post(request)
        except httpx.HTTPError as error:
            raise JevError("api_unreachable", f"Could not reach TypeSafe: {error}") from error
        if response.status_code != 200:
            raise JevError("api_error", f"TypeSafe responded {response.status_code}: {response.text}")
        return parse_answers(response.json()["answers"])

    def _post(self, request: JevRequest) -> httpx.Response:
        """Uses JSON when there are no images; with images, multipart plus the header enabling them."""
        payload = request.payload(self.model)
        if not request.images:
            return self._client.post(self._url, headers=self._headers, json=payload)
        files = {"request": (None, json.dumps(payload), "application/json")}
        for name, image in request.images.items():
            files[name] = (image.source, image.data, "image/jpeg")
        # TypeSafe rejects images with a 400 if this experimental-feature header is missing.
        headers = {**self._headers, "TypeSafe-Danger-Zone-Images": "true"}
        return self._client.post(self._url, headers=headers, files=files)
