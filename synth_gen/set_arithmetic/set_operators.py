import random
from abc import ABC

import synth_gen.set_arithmetic.operators as operators


def order_preserving_unique(values: list[int]) -> list[int]:
    out = []
    vals = set()
    for v in values:
        if v not in vals:
            out.append(v)
            vals.add(v)
    return out


class Node(ABC):
    @staticmethod
    def generate(node):
        pass


class Sample(Node):
    def __init__(self, gen_config):
        self.gen_config = gen_config
        self.parent = None
        self.values = [
            random.randint(
                int(abs(gen_config.min_val) * 0.1), int(gen_config.max_val * 0.9)
            )
            for _ in range(gen_config.start_set_size)
        ]

    def format(self) -> str:
        return f"{self.values}"


class Sort(Node):
    def __init__(self, node):
        self.parent = node

    @staticmethod
    def generate(node):
        return Sort(node)

    @property
    def values(self):
        return sorted(self.parent.values)

    def format(self, parent_name) -> str:
        return f"sort({parent_name})"


class Map(Node):
    def __init__(self, node, unary_op):
        self.parent = node
        self.op = unary_op

    @staticmethod
    def generate(node):
        op = operators.UnaryOp.sample(node.values)
        return Map(node, op)

    @property
    def values(self):
        return order_preserving_unique(map(self.op.fn, self.parent.values))

    def format(self, parent_name) -> str:
        op_name = self.op.format()
        return f"{{{op_name} forall x in {parent_name}}}"


class Filter(Node):
    def __init__(self, node, predicate):
        self.parent = node
        self.predicate = predicate

    @staticmethod
    def generate(node):
        pred = operators.UnaryPredicate.sample(node.values)
        return Filter(node, pred)

    @property
    def values(self):
        return list(filter(self.predicate.fn, self.parent.values))

    def format(self, parent_name) -> str:
        pred = self.predicate.format()
        return f"{{x forall x in {parent_name} such that {pred}}}"


class UnionMap(Node):
    def __init__(self, node, unary_op):
        self.parent = node
        self.op = unary_op

    @staticmethod
    def generate(node):
        op = operators.UnaryOp.sample(node.values)
        return UnionMap(node, op)

    @property
    def values(self):
        mapped = list(map(self.op.fn, self.parent.values))
        return order_preserving_unique(self.parent.values + mapped)

    def format(self, parent_name) -> str:
        op_name = self.op.format()
        return f"{parent_name} U {{{op_name} forall x in {parent_name}}}"


class MapProduct(Node):
    def __init__(self, node, binary_op):
        self.parent = node
        self.op = binary_op

    @staticmethod
    def generate(node):
        op = operators.BinaryOp.sample(node.values)
        return MapProduct(node, op)

    @property
    def values(self):
        return order_preserving_unique(
            [self.op.fn(x, y) for x in self.parent.values for y in self.parent.values]
        )

    def format(self, parent_name) -> str:
        op_name = self.op.format()
        return f"{{{op_name} forall x in {parent_name}, y in {parent_name}}}"


# Should only be used after a sort.
class Select(Node):
    def __init__(self, node, select_indices):
        self.parent = node
        self.select_indices = select_indices

    @staticmethod
    def generate(node):
        select = sorted(random.sample(range(len(node.values)), len(node.values) // 2))
        return Select(node, select)

    @property
    def values(self):
        return [self.parent.values[i] for i in self.select_indices]

    def format(self, parent_name) -> str:
        return f"{{elements {self.select_indices} from {parent_name}}}"


class SortSelect(Node):
    @staticmethod
    def generate(node):
        return Select.generate(Sort.generate(node))
