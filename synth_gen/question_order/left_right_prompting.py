import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional


@dataclass(frozen=True)
class Question:
    prompt: str
    answer: int
    num_values: int
    depth: int
    max_val: int
    question_on_right: bool


prompts = [
    (
        "What's the {extremum} value in this set of values: {values}?",
        "Given this set of values: {values} what's the {extremum} value?",
    ),
    (
        "What's the {extremum} value that is {mod_str} in this set of values: {values}?",
        "Given this set of values: {values} what's the {extremum} value that is {mod_str}?",
    ),
]
extra_inst = " Answer with just the value."


class Extremum(Enum):
    MIN = 1
    MAX = 2

    def __str__(self) -> str:
        if self == Extremum.MIN:
            return "minimum"
        else:
            return "maximum"

    @staticmethod
    def get_fn(v):
        if v == Extremum.MIN:
            return min
        else:
            return max


def mod_str(modulus: int) -> str:
    return f"divisible by {modulus}"


def f(extremum: Extremum, modulus: Optional[int], values: list[int], **kwargs):
    if modulus is not None:
        values = [v for v in values if v % modulus == 0]

    efn = Extremum.get_fn(extremum)
    return efn(values)


def reject_q(extremum: str, modulus: Optional[int], values: list[int]):
    """Reject questions where the modulus doesn't change the answer or it selects no
    values."""
    if modulus is None:
        return False

    if len([v for v in values if v % modulus == 0]) == 0:
        return True

    if f(extremum, modulus, values) == f(extremum, None, values):
        return True


def generate_ds():
    MAX_VAL = 100
    questions = []
    for depth in range(2):
        for num_values in range(10, 41, 10):
            for on_right in [False, True]:
                for seed in range(50):
                    random.seed(seed)

                    prompt_template = prompts[depth][int(on_right)]
                    while True:
                        values = [
                            random.randint(10, MAX_VAL) for _ in range(num_values)
                        ]
                        want_max = random.random() > 0.5
                        modulus = None
                        if depth == 1:
                            modulus = random.randint(2, 10)
                        extremum = Extremum.MAX if want_max else Extremum.MIN

                        args = {
                            "extremum": extremum,
                            "modulus": modulus,
                            "mod_str": mod_str(modulus),
                            "values": values,
                        }
                        if not reject_q(extremum, modulus, values):
                            break

                    prompt_str = prompt_template.format(**args) + extra_inst
                    answer = f(**args)
                    questions.append(
                        Question(
                            prompt=prompt_str,
                            answer=answer,
                            num_values=num_values,
                            depth=depth,
                            max_val=MAX_VAL,
                            question_on_right=on_right,
                        )
                    )
    return questions
