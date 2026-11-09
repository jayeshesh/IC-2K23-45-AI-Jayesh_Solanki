#!/usr/bin/env python3
"""
Experiment 3: Water Jug Problem solved as a Production System.

Course : Artificial Intelligence Laboratory (IC-703 C)
Lab    : Lab 1 - AI Environment Setup, Production Systems, Water Jug Problem

Problem
-------
Two jugs of capacity A and B litres (with no measuring marks) and an
unlimited water supply are available. Starting with both jugs empty, obtain
exactly T litres of water in the required jug (Jug A, Jug B or either jug).

Approach
--------
The problem is formulated as a state space and solved as a production system:

    * Global database : the current state (x, y), where x and y are the
                        litres of water in Jug A and Jug B respectively.
    * Production rules: R1 - R8, each of the form IF <condition> THEN <state>.
    * Control strategy: systematic, breadth-wise application of every
                        applicable rule, with a record of already generated
                        states so that no state is processed twice. This
                        guarantees a solution with the minimum number of rule
                        applications.

Usage examples
--------------
    python Experiment2.py                      # classic 4-3-2 problem
    python Experiment2.py --trace              # show rule matching trace
    python Experiment2.py -a 5 -b 3 -t 4 -g ANY
    python Experiment2.py --interactive        # read inputs from keyboard
    python Experiment2.py --benchmark          # performance table

Only the Python standard library is used.
"""

import argparse
import sys
import time
from collections import deque
from dataclasses import dataclass
from math import gcd
from typing import Callable, Dict, List, Optional, Sequence, Tuple

State = Tuple[int, int]

MAX_CAPACITY = 1000          # upper bound keeps the state space tractable
VALID_GOAL_JUGS = ("A", "B", "ANY")
LINE_WIDTH = 72

# Exit codes returned by main()
EXIT_SOLVED = 0
EXIT_NO_SOLUTION = 1
EXIT_INVALID_INPUT = 2


class WaterJugInputError(ValueError):
    """Raised when the water jug problem parameters are invalid."""


# ---------------------------------------------------------------------------
# Production rules
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ProductionRule:
    """A single production rule: IF condition(state) THEN action(state).

    Both callables receive (x, y, cap_a, cap_b) so that the same rule base
    works for any pair of jug capacities.
    """

    rule_id: str
    name: str
    condition_text: str
    action_text: str
    condition: Callable[[int, int, int, int], bool]
    action: Callable[[int, int, int, int], State]

    def is_applicable(self, state: State, cap_a: int, cap_b: int) -> bool:
        """Return True if the rule's left-hand side matches the state."""
        x, y = state
        return self.condition(x, y, cap_a, cap_b)

    def apply(self, state: State, cap_a: int, cap_b: int) -> State:
        """Return the new state produced by the rule's right-hand side."""
        x, y = state
        return self.action(x, y, cap_a, cap_b)


def build_rule_base() -> List[ProductionRule]:
    """Create the eight production rules of the water jug problem.

    The pouring rules are split into "until the other jug is full" and
    "pour everything" so that every rule has a precise, non-overlapping
    condition.
    """
    return [
        ProductionRule(
            "R1", "Fill Jug A", "x < A", "(A, y)",
            lambda x, y, a, b: x < a,
            lambda x, y, a, b: (a, y)),
        ProductionRule(
            "R2", "Fill Jug B", "y < B", "(x, B)",
            lambda x, y, a, b: y < b,
            lambda x, y, a, b: (x, b)),
        ProductionRule(
            "R3", "Empty Jug A", "x > 0", "(0, y)",
            lambda x, y, a, b: x > 0,
            lambda x, y, a, b: (0, y)),
        ProductionRule(
            "R4", "Empty Jug B", "y > 0", "(x, 0)",
            lambda x, y, a, b: y > 0,
            lambda x, y, a, b: (x, 0)),
        ProductionRule(
            "R5", "Pour A into B until B is full",
            "x > 0 and y < B and x + y >= B", "(x - (B - y), B)",
            lambda x, y, a, b: x > 0 and y < b and x + y >= b,
            lambda x, y, a, b: (x - (b - y), b)),
        ProductionRule(
            "R6", "Pour B into A until A is full",
            "y > 0 and x < A and x + y >= A", "(A, y - (A - x))",
            lambda x, y, a, b: y > 0 and x < a and x + y >= a,
            lambda x, y, a, b: (a, y - (a - x))),
        ProductionRule(
            "R7", "Pour all water of A into B",
            "x > 0 and x + y < B", "(0, x + y)",
            lambda x, y, a, b: x > 0 and x + y < b,
            lambda x, y, a, b: (0, x + y)),
        ProductionRule(
            "R8", "Pour all water of B into A",
            "y > 0 and x + y < A", "(x + y, 0)",
            lambda x, y, a, b: y > 0 and x + y < a,
            lambda x, y, a, b: (x + y, 0)),
    ]


# ---------------------------------------------------------------------------
# Problem definition and validation
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class WaterJugProblem:
    """Formal description of one water jug problem instance."""

    cap_a: int
    cap_b: int
    target: int
    goal_jug: str = "A"

    @property
    def initial_state(self) -> State:
        """Both jugs are empty at the start."""
        return (0, 0)

    def is_goal(self, state: State) -> bool:
        """Goal test: the required jug holds exactly `target` litres."""
        x, y = state
        if self.goal_jug == "A":
            return x == self.target
        if self.goal_jug == "B":
            return y == self.target
        return self.target in (x, y)

    def goal_description(self) -> str:
        """Human readable description of the goal state set."""
        if self.goal_jug == "A":
            return (f"({self.target}, y) for any y in "
                    f"[0, {self.cap_b}]")
        if self.goal_jug == "B":
            return (f"(x, {self.target}) for any x in "
                    f"[0, {self.cap_a}]")
        return (f"({self.target}, y) or (x, {self.target}) "
                f"- target in either jug")


def validate_parameters(cap_a: int, cap_b: int, target: int,
                        goal_jug: str) -> WaterJugProblem:
    """Validate raw parameters and return a WaterJugProblem.

    Raises:
        WaterJugInputError: if any parameter is out of range or invalid.
    """
    for label, value in (("Capacity of Jug A", cap_a),
                         ("Capacity of Jug B", cap_b),
                         ("Target quantity", target)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise WaterJugInputError(f"{label} must be an integer, "
                                     f"got {value!r}.")
        if not 1 <= value <= MAX_CAPACITY:
            raise WaterJugInputError(f"{label} must be between 1 and "
                                     f"{MAX_CAPACITY}, got {value}.")

    goal_jug = str(goal_jug).strip().upper()
    if goal_jug not in VALID_GOAL_JUGS:
        raise WaterJugInputError(f"Goal jug must be one of "
                                 f"{', '.join(VALID_GOAL_JUGS)}, "
                                 f"got {goal_jug!r}.")

    limit = {"A": cap_a, "B": cap_b, "ANY": max(cap_a, cap_b)}[goal_jug]
    if target > limit:
        raise WaterJugInputError(
            f"Target {target} L cannot be held by the selected jug(s); "
            f"maximum possible is {limit} L.")
    return WaterJugProblem(cap_a, cap_b, target, goal_jug)


def solvability_check(problem: WaterJugProblem) -> Tuple[bool, str]:
    """Necessary condition from Bezout's identity: gcd(A, B) divides T."""
    divisor = gcd(problem.cap_a, problem.cap_b)
    if problem.target % divisor == 0:
        return True, (f"gcd({problem.cap_a}, {problem.cap_b}) = {divisor} "
                      f"divides {problem.target} -> solvable")
    return False, (f"gcd({problem.cap_a}, {problem.cap_b}) = {divisor} "
                   f"does not divide {problem.target} -> NOT solvable")


# ---------------------------------------------------------------------------
# Control strategy (systematic breadth-wise rule application)
# ---------------------------------------------------------------------------
@dataclass
class SearchResult:
    """Outcome and statistics of one production-system run."""

    found: bool
    path: List[Tuple[Optional[ProductionRule], State]]
    states_expanded: int
    states_generated: int
    max_open_size: int
    elapsed_ms: float
    trace: List[str]
    # Search tree: generated state -> (parent state, rule id that made it)
    tree: Dict[State, Tuple[Optional[State], Optional[str]]]


def solve(problem: WaterJugProblem, rules: Sequence[ProductionRule],
          record_trace: bool = False) -> SearchResult:
    """Apply the production rules systematically until a goal is reached.

    OPEN   : FIFO queue of states whose rules have not yet been applied.
    parent : maps every generated state to (previous state, rule used);
             it doubles as the CLOSED record that prevents repetition.
    """
    cap_a, cap_b = problem.cap_a, problem.cap_b
    start = problem.initial_state
    parent: Dict[State, Tuple[Optional[State], Optional[ProductionRule]]] = {
        start: (None, None)}
    open_list: deque = deque([start])
    expanded, generated, max_open = 0, 1, 1
    trace: List[str] = []
    goal: Optional[State] = start if problem.is_goal(start) else None

    timer_start = time.perf_counter()
    while open_list and goal is None:
        state = open_list.popleft()
        expanded += 1
        fired: List[str] = []
        for rule in rules:
            if not rule.is_applicable(state, cap_a, cap_b):
                continue
            new_state = rule.apply(state, cap_a, cap_b)
            generated += 1
            if new_state in parent:            # already generated earlier
                fired.append(f"{rule.rule_id}:{new_state}*")
                continue
            parent[new_state] = (state, rule)
            fired.append(f"{rule.rule_id}:{new_state}")
            if problem.is_goal(new_state):
                goal = new_state
                break
            open_list.append(new_state)
        max_open = max(max_open, len(open_list))
        if record_trace:
            trace.append(f"[{expanded:>2}] Expand {state} -> "
                         + "  ".join(fired))
    elapsed_ms = (time.perf_counter() - timer_start) * 1000.0

    path: List[Tuple[Optional[ProductionRule], State]] = []
    if goal is not None:
        node: Optional[State] = goal
        while node is not None:
            previous, rule = parent[node]
            path.append((rule, node))
            node = previous
        path.reverse()

    tree = {state: (prev, rule.rule_id if rule else None)
            for state, (prev, rule) in parent.items()}
    return SearchResult(goal is not None, path, expanded, generated,
                        max_open, elapsed_ms, trace, tree)


def explore_state_space(
        problem: WaterJugProblem, rules: Sequence[ProductionRule]
) -> Dict[State, List[Tuple[str, State]]]:
    """Return every state reachable from (0, 0) with its rule transitions."""
    cap_a, cap_b = problem.cap_a, problem.cap_b
    graph: Dict[State, List[Tuple[str, State]]] = {}
    pending = deque([problem.initial_state])
    while pending:
        state = pending.popleft()
        if state in graph:
            continue
        graph[state] = []
        for rule in rules:
            if rule.is_applicable(state, cap_a, cap_b):
                new_state = rule.apply(state, cap_a, cap_b)
                graph[state].append((rule.rule_id, new_state))
                if new_state not in graph:
                    pending.append(new_state)
    return graph


# ---------------------------------------------------------------------------
# Presentation helpers
# ---------------------------------------------------------------------------
def print_header(title: str) -> None:
    """Print a section banner."""
    print("=" * LINE_WIDTH)
    print(f" {title}")
    print("=" * LINE_WIDTH)


def print_formulation(problem: WaterJugProblem, solvable_msg: str) -> None:
    """Print the state-space formulation of the problem."""
    total_states = (problem.cap_a + 1) * (problem.cap_b + 1)
    print("Problem formulation")
    print(f"  Jug A capacity      : {problem.cap_a} litres")
    print(f"  Jug B capacity      : {problem.cap_b} litres")
    jug = "either jug" if problem.goal_jug == "ANY" else \
        f"Jug {problem.goal_jug}"
    print(f"  Target              : {problem.target} litres in {jug}")
    print("  State               : (x, y) = litres in (Jug A, Jug B)")
    print(f"  State space         : {{(x, y) | 0 <= x <= {problem.cap_a}, "
          f"0 <= y <= {problem.cap_b}}}  ({total_states} states)")
    print(f"  Initial state       : {problem.initial_state}")
    print(f"  Goal state(s)       : {problem.goal_description()}")
    print(f"  Solvability check   : {solvable_msg}")
    print()


def print_rules(rules: Sequence[ProductionRule]) -> None:
    """Print the production rule base as a table."""
    print("Production rules (IF condition THEN new state)")
    print(f"  {'Rule':<5}{'Name':<32}{'Condition':<33}New state")
    print("  " + "-" * (LINE_WIDTH - 2))
    for rule in rules:
        print(f"  {rule.rule_id:<5}{rule.name:<32}"
              f"{rule.condition_text:<33}{rule.action_text}")
    print()


def print_solution(result: SearchResult) -> None:
    """Print the solution path step by step."""
    print("Solution path")
    print(f"  {'Step':<6}{'Rule':<6}{'Action':<34}State (x, y)")
    print("  " + "-" * (LINE_WIDTH - 2))
    for step, (rule, state) in enumerate(result.path):
        rule_id = rule.rule_id if rule else "-"
        action = rule.name if rule else "Initial state"
        print(f"  {step:<6}{rule_id:<6}{action:<34}{state}")
    print()


def print_performance(result: SearchResult, reachable: int) -> None:
    """Print search statistics and execution time."""
    print("Performance analysis")
    steps = len(result.path) - 1 if result.found else "-"
    print(f"  Solution length (rule applications) : {steps}")
    print(f"  States expanded                     : {result.states_expanded}")
    print(f"  States generated (incl. repeats)    : "
          f"{result.states_generated}")
    print(f"  Maximum OPEN list size              : {result.max_open_size}")
    print(f"  States reachable from (0, 0)        : {reachable}")
    print(f"  Execution time                      : "
          f"{result.elapsed_ms:.3f} ms")
    print()


def run_experiment(problem: WaterJugProblem, show_trace: bool) -> int:
    """Formulate, solve and report one problem instance."""
    rules = build_rule_base()
    solvable, message = solvability_check(problem)

    print_header("EXPERIMENT 3 : WATER JUG PROBLEM AS A PRODUCTION SYSTEM")
    print_formulation(problem, message)
    print_rules(rules)

    if not solvable:
        print("Result: The target cannot be measured with these jugs.")
        print("        The rule base was not executed (necessary "
              "condition failed).")
        return EXIT_NO_SOLUTION

    result = solve(problem, rules, record_trace=show_trace)
    reachable = len(explore_state_space(problem, rules))

    if show_trace:
        print("Rule-application trace "
              "(control strategy: breadth-wise, no repeated states)")
        print("  Format: RuleId:(new state); '*' = state already generated")
        for line in result.trace:
            print("  " + line)
        print()

    if result.found:
        print_solution(result)
    print_performance(result, reachable)

    if result.found:
        final = result.path[-1][1]
        print(f"Result: GOAL REACHED - final state {final} contains "
              f"{problem.target} L in the required jug after "
              f"{len(result.path) - 1} rule applications.")
        return EXIT_SOLVED
    print("Result: All reachable states were examined; goal not reachable.")
    return EXIT_NO_SOLUTION


def run_benchmark() -> int:
    """Solve several instances and tabulate the performance metrics."""
    cases = [(4, 3, 2, "A"), (4, 3, 2, "ANY"), (5, 3, 4, "A"),
             (8, 5, 6, "ANY"), (9, 4, 6, "A"), (7, 5, 1, "B"),
             (12, 7, 9, "ANY"), (6, 4, 3, "ANY")]
    rules = build_rule_base()
    print_header("EXPERIMENT 3 : WATER JUG PRODUCTION SYSTEM - BENCHMARK")
    print(f"  {'A':>3} {'B':>3} {'T':>3} {'Jug':<4} {'Solvable':<9}"
          f"{'Steps':>6}{'Expanded':>10}{'Generated':>11}"
          f"{'Reachable':>11}{'Time (ms)':>11}")
    print("  " + "-" * (LINE_WIDTH - 2))
    for cap_a, cap_b, target, jug in cases:
        problem = validate_parameters(cap_a, cap_b, target, jug)
        solvable, _ = solvability_check(problem)
        reachable = len(explore_state_space(problem, rules))
        if solvable:
            result = solve(problem, rules)
            steps = str(len(result.path) - 1) if result.found else "-"
            row = (f"{steps:>6}{result.states_expanded:>10}"
                   f"{result.states_generated:>11}{reachable:>11}"
                   f"{result.elapsed_ms:>11.3f}")
        else:
            row = f"{'-':>6}{'-':>10}{'-':>11}{reachable:>11}{'-':>11}"
        print(f"  {cap_a:>3} {cap_b:>3} {target:>3} {jug:<4} "
              f"{'Yes' if solvable else 'No':<9}{row}")
    print()
    print("Note: execution times depend on the machine and vary between runs.")
    return EXIT_SOLVED


# ---------------------------------------------------------------------------
# Input handling
# ---------------------------------------------------------------------------
def positive_int(text: str) -> int:
    """argparse type: a strictly positive integer."""
    try:
        value = int(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"'{text}' is not a valid integer") from exc
    if value <= 0:
        raise argparse.ArgumentTypeError(f"{value} must be greater than 0")
    return value


def prompt_int(label: str, attempts: int = 3) -> int:
    """Read a positive integer from the keyboard with retries."""
    for _ in range(attempts):
        raw = input(f"{label}: ").strip()
        try:
            return positive_int(raw)
        except argparse.ArgumentTypeError as exc:
            print(f"  Invalid input: {exc}. Please try again.")
    raise WaterJugInputError(f"Too many invalid attempts for '{label}'.")


def read_interactive() -> Tuple[int, int, int, str]:
    """Collect all problem parameters interactively."""
    cap_a = prompt_int("Enter capacity of Jug A (litres)")
    cap_b = prompt_int("Enter capacity of Jug B (litres)")
    target = prompt_int("Enter target quantity (litres)")
    goal = input("Target required in which jug? [A/B/ANY] (default A): ")
    return cap_a, cap_b, target, goal.strip() or "A"


def build_parser() -> argparse.ArgumentParser:
    """Command-line interface definition."""
    parser = argparse.ArgumentParser(
        description="Water Jug Problem solved as a production system.")
    parser.add_argument("-a", "--cap-a", type=positive_int, default=4,
                        help="capacity of Jug A in litres (default 4)")
    parser.add_argument("-b", "--cap-b", type=positive_int, default=3,
                        help="capacity of Jug B in litres (default 3)")
    parser.add_argument("-t", "--target", type=positive_int, default=2,
                        help="litres to be measured (default 2)")
    parser.add_argument("-g", "--goal-jug", default="A",
                        type=str.upper, choices=VALID_GOAL_JUGS,
                        help="jug that must hold the target (default A)")
    parser.add_argument("--trace", action="store_true",
                        help="print the rule-application trace")
    parser.add_argument("--interactive", action="store_true",
                        help="read the parameters from the keyboard")
    parser.add_argument("--benchmark", action="store_true",
                        help="solve several instances and print metrics")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Program entry point; returns a process exit code."""
    args = build_parser().parse_args(argv)
    try:
        if args.benchmark:
            return run_benchmark()
        if args.interactive:
            cap_a, cap_b, target, goal = read_interactive()
        else:
            cap_a, cap_b, target, goal = (args.cap_a, args.cap_b,
                                          args.target, args.goal_jug)
        problem = validate_parameters(cap_a, cap_b, target, goal)
        return run_experiment(problem, args.trace)
    except WaterJugInputError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return EXIT_INVALID_INPUT
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled by the user.", file=sys.stderr)
        return EXIT_INVALID_INPUT


if __name__ == "__main__":
    sys.exit(main())
