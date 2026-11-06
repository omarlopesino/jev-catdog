"""HTTP gateway tests with MockTransport: headers, JSON, multipart and API errors."""

import json

import httpx
import pytest

from jev_catdog.jev.gateway import JevError
from jev_catdog.jev.questions import Noul
from jev_catdog.jev.request import ImageAsset, JevRequest
from jev_catdog.infrastructure.typesafe_gateway import TypeSafeGateway

OK = {"model": "jev-1.14.0", "answers": {"q": {"type": "noul", "noul": 0.9}}}


def _gateway(handler) -> TypeSafeGateway:
    """Gateway pointing at a test URL through a simulated transport, so no network is used."""
    client = httpx.Client(transport=httpx.MockTransport(handler))
    return TypeSafeGateway("secret", "https://jev.test/v1", "jev-latest", client)


def test_text_request_is_json_with_bearer_auth():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Keeps the received request for inspection and replies with a valid noul answer."""
        seen["request"] = request
        return httpx.Response(200, json=OK)

    answers = _gateway(handler).decide(JevRequest("a cat", {"q": Noul("Cat?")}))
    request = seen["request"]
    assert answers["q"].probability == 0.9
    assert str(request.url) == "https://jev.test/v1/systemone"
    assert request.headers["Authorization"] == "Bearer secret"
    assert "TypeSafe-Danger-Zone-Images" not in request.headers
    assert json.loads(request.content)["state"] == "a cat"


def test_image_request_is_multipart_with_danger_zone_header():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Keeps the received request for inspection and replies with a valid noul answer."""
        seen["request"] = request
        return httpx.Response(200, json=OK)

    image = ImageAsset(b"JPEGDATA", "cats_01.jpg", (1280, 853), (1280, 853))
    _gateway(handler).decide(JevRequest({"photo": "photo"}, {"q": Noul("Cat?")}, {"photo": image}))
    request = seen["request"]
    body = request.content
    assert request.headers["TypeSafe-Danger-Zone-Images"] == "true"
    assert request.headers["Content-Type"].startswith("multipart/form-data")
    assert b'name="request"' in body and b'"part": "photo"' in body
    assert b'name="photo"; filename="cats_01.jpg"' in body and b"JPEGDATA" in body


def test_http_error_becomes_api_error():
    gateway = _gateway(lambda request: httpx.Response(400, text="bad image"))
    with pytest.raises(JevError) as error:
        gateway.decide(JevRequest("x", {"q": Noul("?")}))
    assert error.value.code == "api_error"
    assert "bad image" in error.value.message
