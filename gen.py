import random
from typing import Any, Optional

import predicates

# We generate questions via a random walk through the predicate types allowed by this
# grammar:
#   Start:  SelList(n):List
#   List:   SelItem(n):Item | SelWithLength(n):List/Item | SelWithLetterAtPos(n, L):List/Item
#   Item:   End | SelLetter(n):Letter | SelLength(n):Int
#   Int:    End
#   Letter: End
#
# Additionally, SelLength shouldn't follow SelWithLength.

grammar = {
    None: [predicates.SelectList],
    list[str]: [
        predicates.SelectItem,
        predicates.SelectWithLength,
        predicates.SelectWithLetterAtPos,
    ],
    str: [predicates.Terminate, predicates.SelectLetter, predicates.SelectLength],
    int: [predicates.Terminate],
    predicates.letter: [predicates.Terminate],
}


class Node:
    def __init__(self, predicate: predicates.Predicate, parent: Optional[Any]):
        self.parent = parent
        self.predicate = predicate
        self.domain = predicate.domain(self.parent_value())
        self.query = random.choice(self.domain)
        self.prompt = predicate.prompt(self.query)
        self.value = predicate.eval(self.parent_value(), self.query)

    @property
    def terminal(self) -> bool:
        return self.predicate.is_terminal()

    def parent_value(self) -> Any:
        if self.parent is None:
            return None
        return self.parent.value

    def full_answer(self) -> str:
        if self.terminal:
            return self.parent.full_answer()
        if self.parent is None:
            return f"{self.value}"
        return f"{self.value} | " + self.parent.full_answer()

    def full_prompt(self) -> str:
        if self.parent is None:
            return self.prompt
        return self.prompt + self.parent.full_prompt()


def Allowlist(n: Node, parent: Node):
    if n.predicate == predicates.Terminate:
        return True
    if n.value == parent.value:
        return False

    if (
        n.predicate == predicates.SelectLength
        and parent.predicate == predicates.SelectWithLength
    ):
        return False
    return True


def StepFrom(n: Node):
    out_type = n.predicate.out_type()
    if out_type == list[str] and not isinstance(n.value, list):
        out_type = str
    options = grammar[out_type]
    for retries in range(20):
        next_pred = random.choice(options)
        next_node = Node(next_pred, n)
        if Allowlist(next_node, n):
            break
    return next_node


def walk():
    # p0 = predicates.SelectList()

    for i in range(20):
        random.seed(i)
        n = Node(predicates.SelectList, None)
        while not n.terminal:
            n = StepFrom(n)
        # print("Question Number:", i)
        print("Q: What is", n.full_prompt(), "?")
        print("A:", n.value)
        print("Reasoning:", n.full_answer())
        print()


if __name__ == "__main__":
    walk()
