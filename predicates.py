import random
from abc import ABC
from typing import Any, NewType, Optional, Union

import sets

letter = NewType("letter", str)


def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return str(n) + suffix


def letter_w_article(letter: str):
    if letter in "aeiou":
        return f"an '{letter}'"
    return f"a '{letter}'"


class Predicate(ABC):
    @staticmethod
    def out_type() -> Any:
        raise NotImplementedError

    @staticmethod
    def prompt(query) -> str:
        raise NotImplementedError

    @staticmethod
    def eval(query, set) -> Union[list[str], str, letter]:
        raise NotImplementedError

    @staticmethod
    def domain(set) -> list[Any]:
        raise NotImplementedError

    @staticmethod
    def is_terminal():
        return False


class SelectList(Predicate):
    # U, (prompt_i) -> list
    @staticmethod
    def out_type():
        return list[str]

    def __init__(
        self,
        set_prompts: list[str],
        set_values: list[list[str]],
        selection: Optional[int],
    ):
        if selection is None:
            selection = random.randint(0, len(set_prompts))
        self.prompt = set_prompts[selection]
        self.vals = set_values[selection]

    @staticmethod
    def prompt(i: int) -> str:
        return sets.set_prompts[i]

    @staticmethod
    def eval(none_val, i: int) -> list[str]:
        return sets.set_values[i]

    @staticmethod
    def domain(none_val) -> list[int]:
        return list(range(0, len(sets.set_prompts)))


class SelectLetter(Predicate):
    # str, (n) -> letter
    @staticmethod
    def out_type():
        return letter

    @staticmethod
    def prompt(n: int) -> str:
        return f"the {ordinal(n)} letter of: "

    @staticmethod
    def eval(val: str, n: int) -> letter:
        return val[n - 1]

    @staticmethod
    def domain(val: str) -> list[int]:
        return list(range(1, len(val) + 1))


class SelectItem(Predicate):
    # Note: We use 1-indexing since we're doing list item counting.
    # list, (n) -> str
    @staticmethod
    def out_type():
        return str

    @staticmethod
    def prompt(n: int) -> str:
        return f"the {ordinal(n)} item of: "

    @staticmethod
    def eval(val: list[str], n: int) -> str:
        return val[n - 1]

    @staticmethod
    def domain(val: list[str]) -> int:
        return list(range(1, len(val) + 1))


class SelectWithLength(Predicate):
    # list, (n) -> list
    @staticmethod
    def out_type():
        return list[str]

    @staticmethod
    def prompt(n: int) -> str:
        return f"the string(s) whose length (including spaces) is {n} in: "

    @staticmethod
    def eval(val: list[str], n: int) -> Union[list[str], str]:
        vals = [v for v in val if len(v) == n]
        if len(vals) == 1:
            return vals[0]
        return vals

    @staticmethod
    def domain(val: list[str]) -> list[int]:
        return list(set(map(len, val)))


def list_get(l, i):
    if i >= 0 and i < len(l):
        return l[i]
    return None


class SelectWithLetterAtPos(Predicate):
    # list, (letter, i) -> list
    @staticmethod
    def out_type():
        return list[str]

    @staticmethod
    def prompt(letter_and_pos: tuple[str, int]) -> str:
        letter, i = letter_and_pos
        return (
            f"the item(s) whose {ordinal(i)} letter (including spaces) is "
            f"{letter_w_article(letter)} from: "
        )

    @staticmethod
    def eval(val: list[str], letter_and_pos: tuple[str, int]) -> Union[list[str], str]:
        letter, i = letter_and_pos
        vals = [v for v in val if list_get(v, i - 1) == letter]
        if len(vals) == 1:
            return vals[0]
        return vals

    @staticmethod
    def domain(val: list[str]) -> list[tuple[str, int]]:
        options = set()
        for v in val:
            for i, letter in enumerate(v):
                if letter == " ":
                    continue
                options.add((letter, i + 1))
        return list(options)


class SelectLength(Predicate):
    # str, () -> n
    @staticmethod
    def out_type():
        return int

    @staticmethod
    def prompt(none_arg: None) -> str:
        return "the number of letters in: "

    @staticmethod
    def eval(val: str, none_arg: None) -> int:
        return len(val)

    @staticmethod
    def domain(val: str) -> list[None]:
        return [None]


class Terminate(Predicate):
    @staticmethod
    def out_type():
        return None

    @staticmethod
    def prompt(none_arg: None) -> str:
        return ""

    @staticmethod
    def eval(val: str, none_arg: None) -> None:
        return val

    @staticmethod
    def domain(val: str) -> list[None]:
        return [None]

    @staticmethod
    def is_terminal():
        return True


# Walk Grammar:
#   U:      SelList(n):List
#   List:   SelItem(n):Item | SelWithLength(n):List | SelWithLetterAtPos(n, L):List
#   Item:   End | SelLetter(n):Letter
#   Letter: End
