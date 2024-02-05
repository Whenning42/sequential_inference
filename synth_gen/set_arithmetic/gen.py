# Set Arithmetic Benchmark:
#
# Operators:
# - Sample(null, sample_params) used as a start node
# - Map(s, unary_op)
# - Filter(s, pred)
# - Union-Map(s, unary_op)
# - Map-Product(s, binary_op) (all_reduce)
# - Sort-Select(s, index_list) (all_reduce)
# - Sort(s) is terminal node
#
# All non-terminal operators return a set of values.
# Sequential maps or filters could be considered redundant, but we'll allow them for now
# For all operations, we aim to keep the size and quantity of the variables in a desired range 0 < v < 10000, 3 <= |S| <= 15
# We focus on line graphs
# We optionally output subsequence reasoning steps

import random
from dataclasses import dataclass

import synth_gen.set_arithmetic.set_operators as set_operators


@dataclass(frozen=True)
class GenConfig:
    num_samples: int
    start_set_size: int
    min_set_size: int
    max_set_size: int
    min_val: int
    max_val: int
    max_ops: int


class Node:
    pass


@dataclass(frozen=True)
class Question:
    question: str
    answer: str
    reasoning: str
    nodes: list[Node]
    partial_results: list[list[int]]


def sample_node_type():
    return random.choice(
        [
            set_operators.Map,
            set_operators.Filter,
            set_operators.UnionMap,
            set_operators.MapProduct,
            set_operators.SortSelect,
        ]
    )


def reject(set: list[int]):
    return len(set) < 3 or len(set) > 15 or max(set) > 10000 or min(set) < 0


def build_graph(gen_config: GenConfig, num_ops: int) -> Node:
    cur_node = set_operators.Sample(gen_config)

    for i in range(num_ops):
        next_node_type = sample_node_type()
        next_node = next_node_type.generate(cur_node)
        i = 0
        while reject(next_node.values):
            next_node_type = sample_node_type()
            next_node = next_node_type.generate(cur_node)
            i += 1
            if i == 100:
                print("Gen failed")
                break
        cur_node = next_node

    terminal = set_operators.Sort(cur_node)
    return terminal


def formatted_values(values: list[int], node: Node) -> str:
    if isinstance(node, set_operators.Sort):
        open, close = "(", ")"
    else:
        open, close = "{", "}"
    return f"{open}{', '.join(map(str, values))}{close}"


def build_question(terminal: Node) -> Question:
    n = terminal
    nodes = []
    partial_results = []
    while n is not None:
        nodes.append(n)
        partial_results.append(n.values)
        n = n.parent

    nodes = list(reversed(nodes))
    partial_results = list(reversed(partial_results))

    # Prompt format:
    # Given S_0 = {} (Sample)
    #   S_1 = {f(x) forall x in S_0} (Map)
    #   S_2 = {x forall x in S_1 such that p(x) is true} (Filter)
    #   S_3 = S_2 U {f(x) forall x in S_2} (UnionMap)
    #   S_4 = {f(x, y) forall x in S_3, y in S_3} (MapProduct)
    #   OutSeq = sort(S_4)
    # The values in OutSeq are: {

    prompt = f"Given S_0 = {nodes[0].format()}\n"
    parent_name = "S_0"
    reasoning = ""
    for i, node in enumerate(nodes[:-1]):
        if i == 0:
            continue
        node_name = f"S_{i}"
        prompt += f"  {node_name} = {node.format(parent_name)}\n"
        reasoning += f"{node_name} = {formatted_values(partial_results[i], node)}\n"
        parent_name = f"S_{i}"
    prompt += f"The sorted values of {parent_name} are: ("

    return Question(
        question=prompt,
        answer=formatted_values(partial_results[-1], nodes[-1]),
        reasoning=reasoning,
        nodes=nodes,
        partial_results=partial_results,
    )


def generate(gen_config: GenConfig) -> Question:
    num_ops = random.randint(0, gen_config.max_ops)
    terminal = build_graph(gen_config, num_ops)
    return build_question(terminal)


def generate_ds(gen_config: GenConfig) -> list[Question]:
    for i in range(gen_config.num_samples):
        yield generate(gen_config)


config = GenConfig(
    num_samples=100,
    start_set_size=10,
    min_set_size=3,
    max_set_size=20,
    min_val=-10000,
    max_val=10000,
    max_ops=10,
)
ds = list(generate_ds(config))
