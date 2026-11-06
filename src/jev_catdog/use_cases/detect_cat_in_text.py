"""Example 1, noul with text: probability that a description is about a cat."""

from dataclasses import dataclass

from jev_catdog.jev.gateway import JevGateway
from jev_catdog.jev.questions import Noul
from jev_catdog.jev.request import JevRequest

QUESTIONS = {
    "is_cat": Noul(instructions="Does this description refer to a cat?"),
}


@dataclass(frozen=True)
class CatInTextResult:
    """The analysed description and the probability, between 0 and 1, that it refers to a cat."""

    input: str
    is_cat_probability: float


class DetectCatInText:
    """Asks Jev with noul whether a natural-language description corresponds to a cat."""

    def __init__(self, gateway: JevGateway):
        self._gateway = gateway

    def request_for(self, description: str) -> JevRequest:
        """The description is the state; the noul question is applied directly to it."""
        return JevRequest(state=description, questions=QUESTIONS)

    def execute(self, description: str) -> CatInTextResult:
        """Sends the request and returns the probability that the description is of a cat."""
        answers = self._gateway.decide(self.request_for(description))
        return CatInTextResult(description, answers["is_cat"].probability)
