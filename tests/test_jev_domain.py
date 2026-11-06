"""Jev domain tests: question serialization, the readable request and answer parsing."""

import pytest

from jev_catdog.jev.answers import BoxAnswer, RefusalError, ScoreAnswer, parse_answers
from jev_catdog.jev.questions import Box, Choice, Noul, Score
from jev_catdog.jev.request import ImageAsset, JevRequest


def test_questions_serialize_to_api_shape():
    assert Noul("Is it a cat?").to_payload() == {"type": "noul", "instructions": "Is it a cat?"}
    assert Choice("Which?", {"cat": None}).to_payload()["criteria"] == {"cat": None}
    assert Score("How?", ["low", "high"]).to_payload()["criteria"] == ["low", "high"]
    assert "criteria" not in Box("The face").to_payload()


def test_text_request_has_no_assets():
    payload = JevRequest("a cat", {"q": Noul("Cat?")}).payload("jev-latest")
    assert payload == {
        "model": "jev-latest",
        "state": "a cat",
        "questions": {"q": {"type": "noul", "instructions": "Cat?"}},
    }


def test_image_request_declares_multipart_assets_and_describes_them():
    image = ImageAsset(b"x", "cats_07.jpg", (1280, 1933), (1038, 1568))
    request = JevRequest({"photo": "photo"}, {"q": Noul("Cat?")}, {"photo": image})
    assert request.payload("m")["assets"] == {"photo": {"type": "image", "part": "photo"}}
    assert request.describe("m")["assets"]["photo"]["file"] == "cats_07.jpg 1280x1933 -> 1038x1568"


def test_parse_answers_builds_typed_answers():
    answers = parse_answers({
        "s": {"type": "score", "score": 0.2, "confidence": 0.8, "probabilities": {"0": 0.8, "1": 0.2}},
        "b": {"type": "box", "box": {"top": 0.1, "bottom": 0.9, "left": 0.2, "right": 0.8}, "confidence": 0.5},
    })
    assert answers["s"] == ScoreAnswer(0.2, 0.8, {0: 0.8, 1: 0.2})
    assert answers["b"] == BoxAnswer(0.1, 0.9, 0.2, 0.8, 0.5)


def test_refusal_raises_normalized_error():
    with pytest.raises(RefusalError) as error:
        parse_answers({"q": {"type": "refusal"}})
    assert error.value.code == "refusal"
