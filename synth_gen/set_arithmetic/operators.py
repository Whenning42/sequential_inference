import math
import random
from typing import Optional


class Add:
    def __init__(self, r: Optional[int] = None):
        self.r = r
        if r is None:
            self.fn = lambda x, y: x + y
        else:
            self.fn = lambda x, r=r: x + r

    @staticmethod
    def sample_unary(values: list[int]):
        k = random.randint(-100, 100)
        return Add(k)

    def format(self) -> str:
        if self.r is None:
            return "x + y"
        else:
            return f"x + {self.r}"


class Mul:
    def __init__(self, r: Optional[int] = None):
        self.r = r
        if r is None:
            self.fn = lambda x, y: x * y
        else:
            self.fn = lambda x, r=r: x * r

    @staticmethod
    def sample_unary(values: list[int]):
        k = random.randint(-50, 50)
        return Mul(k)

    def format(self) -> str:
        if self.r is None:
            return "x * y"
        else:
            return f"x * {self.r}"


class Exp:
    def __init__(self, r: Optional[int] = None):
        self.r = r
        if r is None:
            self.fn = lambda x, y: x**y
        else:
            self.fn = lambda x: x**r

    @staticmethod
    def sample_unary(values: list[int]):
        k = random.randint(2, 5)
        return Exp(k)

    def format(self) -> str:
        if self.r is None:
            return "x^y"
        else:
            return f"x^{self.r}"


class IntDiv:
    def __init__(self, r: Optional[int] = None):
        self.r = r
        if r is None:
            self.fn = lambda x, y: x // y
        else:
            self.fn = lambda x: x // r

    @staticmethod
    def sample_unary(values: list[int]):
        k = 0
        while k == 0 or k == 1:
            k = random.randint(-30, 30)
        return IntDiv(k)

    def format(self) -> str:
        if self.r is None:
            return "floor(x / y)"
        else:
            return f"floor(x / {self.r})"


class IntRoot:
    def __init__(self, r: Optional[int] = None):
        self.r = r
        if r is None:
            self.fn = lambda x, y: math.floor(x ** (1 / y))
        else:
            self.fn = lambda x, r=r: math.floor(math.copysign(abs(x) ** (1 / r), x))

    @staticmethod
    def sample_unary(values: list[int]):
        # TODO: Handle negative values
        k = random.choice([3, 5])
        return IntRoot(k)

    def format(self) -> str:
        if self.r is None:
            return "floor(x^(1/y))"
        else:
            return f"floor(x^(1/{self.r}))"


class Mod:
    def __init__(self, r: Optional[int] = None):
        self.r = r
        if r is None:
            self.fn = lambda x, y: x % y
        else:
            self.fn = lambda x, r=r: x % r

    @staticmethod
    def sample_unary(values: list[int]):
        k = random.randint(2, 100)
        return Mod(k)

    def format(self) -> str:
        if self.r is None:
            return "x % y"
        else:
            return f"x % {self.r}"


class UnaryOp:
    @staticmethod
    def sample(values: list[int]):
        cls = random.choice([Add, Mul, Exp, IntDiv, IntRoot, Mod])
        return cls.sample_unary(values)


class BinaryOp:
    @staticmethod
    def sample(values: list[int]):
        # TODO: Safe binary int div, int root, and mod?
        cls = random.choice([Add, Mul])
        return cls()


class Comparison:
    def __init__(self, r: int, dir: str):
        self.r = r
        self.dir = dir
        if dir == "lt":
            self.fn = lambda x, r=r: x < r
        else:
            self.fn = lambda x, r=r: x > r

    @staticmethod
    def sample_unary(set: list[int]):
        k = random.randint(min(set), max(set))
        dir = random.choice(["lt", "gt"])
        return Comparison(k, dir)

    def format(self) -> str:
        dir_str = "<" if self.dir == "lt" else ">"
        if self.r is None:
            return "x {dir_str} y"
        else:
            return f"x {dir_str} {self.r}"


class IsMod:
    def __init__(self, k: int, j: int):
        self.k = k
        self.j = j
        self.fn = lambda x, k=k, j=j: x % k == j

    @staticmethod
    def sample_unary(set: list[int]):
        k = random.randint(2, 100)
        j = random.randint(0, k)
        return IsMod(k, j)

    def format(self) -> str:
        return f"x % {self.k} == {self.j}"


class UnaryPredicate:
    @staticmethod
    def sample(values: list[int]):
        cls = random.choice([Comparison, IsMod])
        return cls.sample_unary(values)
