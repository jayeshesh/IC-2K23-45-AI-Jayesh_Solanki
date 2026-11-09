#!/usr/bin/env python3
"""
Experiment 2: Production System for Rule-Based Decision Making.

Course : Artificial Intelligence Laboratory (IC-703 C)
Lab    : Lab 1 - AI Environment Setup, Production Systems, Water Jug Problem

A production system consists of
    1. Working memory (global database) - the facts known at any moment,
    2. Rule base (set of productions)    - IF <conditions> THEN <actions>,
    3. Control strategy / inference engine that repeats the
       recognise-act cycle:
           MATCH   : find all rules whose conditions are satisfied
                     (the conflict set),
           RESOLVE : choose one rule using a conflict-resolution strategy,
           ACT     : execute the chosen rule's actions (update memory),
       until no rule can fire (quiescence) or a cycle limit is reached.

The generic engine below is demonstrated with a small knowledge base,
"Smart Irrigation Advisor", that decides whether a field should be irrigated
from four observations: soil moisture, air temperature, rain forecast and
crop growth stage.

Conflict-resolution strategy used (in this order):
    a) Refractoriness - a rule fires at most once, and a rule whose actions
                        would not change working memory is not considered.
    b) Priority       - the rule with the higher salience fires first.
    c) Specificity    - the rule with more conditions fires first.
    d) Rule order     - the rule written first in the rule base wins.

Usage examples
--------------
    python exp2_production_system.py                  # 3 built-in scenarios
    python exp2_production_system.py -m 22 -t 38 -r no -s flowering
    python exp2_production_system.py --interactive

Only the Python standard library is used.
"""

import argparse
import operator
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

LINE_WIDTH = 72
EXIT_OK = 0
EXIT_INVALID_INPUT = 2

# Allowed comparison operators for rule conditions.
OPERATORS: Dict[str, Callable[[Any, Any], bool]] = {
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "in": lambda left, right: left in right,
}

Condition = Tuple[str, str, Any]       # (attribute, operator, value)
Action = Tuple[str, Any]               # (attribute, value to assert)

# Valid ranges / values for the input observations.
MOISTURE_RANGE = (0.0, 100.0)          # percent volumetric water content
TEMPERATURE_RANGE = (-20.0, 60.0)      # degree Celsius
RAIN_VALUES = ("yes", "no")
CROP_STAGES = ("seedling", "vegetative", "flowering", "mature")


class ProductionSystemError(Exception):
    """Raised for an invalid rule base or invalid input facts."""


# ---------------------------------------------------------------------------
# Knowledge representation
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Rule:
    """A production rule: IF all conditions hold THEN assert all actions."""

    rule_id: str
    description: str
    conditions: Tuple[Condition, ...]
    actions: Tuple[Action, ...]
    priority: int = 0

    @property
    def specificity(self) -> int:
        """Number of conditions (used for conflict resolution)."""
        return len(self.conditions)

    def matches(self, memory: "WorkingMemory") -> bool:
        """True when every condition is satisfied by working memory."""
        for attribute, op_symbol, value in self.conditions:
            if not memory.contains(attribute):
                return False
            if not OPERATORS[op_symbol](memory.get(attribute), value):
                return False
        return True

    def would_change(self, memory: "WorkingMemory") -> bool:
        """True when firing the rule would add or modify at least one fact."""
        return any(not memory.contains(attr) or memory.get(attr) != value
                   for attr, value in self.actions)

    def as_text(self) -> str:
        """Readable IF ... THEN ... form of the rule."""
        lhs = " AND ".join(f"{a} {op} {_fmt(v)}"
                           for a, op, v in self.conditions)
        rhs = ", ".join(f"{a} = {_fmt(v)}" for a, v in self.actions)
        return f"IF {lhs} THEN {rhs}"


def _fmt(value: Any) -> str:
    """Format a value for rule printing."""
    if isinstance(value, tuple):
        return "{" + ", ".join(str(v) for v in value) + "}"
    return str(value)


class WorkingMemory:
    """Global database of attribute-value facts with a change history."""

    def __init__(self, initial_facts: Dict[str, Any]) -> None:
        self._facts: Dict[str, Any] = dict(initial_facts)
        self.history: List[Tuple[str, str, Any]] = [
            ("input", key, value) for key, value in initial_facts.items()]

    def contains(self, attribute: str) -> bool:
        """Is the attribute present in memory?"""
        return attribute in self._facts

    def get(self, attribute: str) -> Any:
        """Return the value of an attribute."""
        return self._facts[attribute]

    def assert_fact(self, attribute: str, value: Any, source: str) -> None:
        """Add or update a fact and record which rule produced it."""
        self._facts[attribute] = value
        self.history.append((source, attribute, value))

    def snapshot(self) -> Dict[str, Any]:
        """Copy of all current facts."""
        return dict(self._facts)


@dataclass
class RunResult:
    """Summary of one execution of the production system."""

    fired_rules: List[str] = field(default_factory=list)
    cycles: int = 0
    halt_reason: str = ""
    elapsed_ms: float = 0.0
    rules_tested: int = 0


# ---------------------------------------------------------------------------
# Inference engine
# ---------------------------------------------------------------------------
class ProductionSystem:
    """Forward-chaining production system with conflict resolution."""

    def __init__(self, rules: Sequence[Rule], max_cycles: int = 50) -> None:
        self._validate_rules(rules)
        if max_cycles <= 0:
            raise ProductionSystemError("max_cycles must be positive.")
        self.rules = list(rules)
        self.max_cycles = max_cycles
        self._order = {rule.rule_id: index
                       for index, rule in enumerate(self.rules)}

    @staticmethod
    def _validate_rules(rules: Sequence[Rule]) -> None:
        """Check rule identifiers and operators before running."""
        if not rules:
            raise ProductionSystemError("The rule base is empty.")
        seen = set()
        for rule in rules:
            if rule.rule_id in seen:
                raise ProductionSystemError(
                    f"Duplicate rule id: {rule.rule_id}")
            seen.add(rule.rule_id)
            if not rule.conditions or not rule.actions:
                raise ProductionSystemError(
                    f"Rule {rule.rule_id} needs conditions and actions.")
            for _, op_symbol, _ in rule.conditions:
                if op_symbol not in OPERATORS:
                    raise ProductionSystemError(
                        f"Rule {rule.rule_id}: unknown operator "
                        f"'{op_symbol}'.")

    def conflict_set(self, memory: WorkingMemory,
                     fired: set) -> List[Rule]:
        """MATCH phase: applicable, not yet fired, state-changing rules."""
        return [rule for rule in self.rules
                if rule.rule_id not in fired
                and rule.matches(memory)
                and rule.would_change(memory)]

    def resolve(self, candidates: List[Rule]) -> Rule:
        """RESOLVE phase: priority, then specificity, then rule order."""
        return min(candidates,
                   key=lambda r: (-r.priority, -r.specificity,
                                  self._order[r.rule_id]))

    def run(self, memory: WorkingMemory, trace: bool = True) -> RunResult:
        """Execute recognise-act cycles until quiescence or cycle limit."""
        result = RunResult()
        fired: set = set()
        start = time.perf_counter()
        while True:
            if result.cycles >= self.max_cycles:
                result.halt_reason = (f"cycle limit ({self.max_cycles}) "
                                      f"reached")
                break
            result.rules_tested += len(self.rules)
            candidates = self.conflict_set(memory, fired)
            if not candidates:
                result.halt_reason = "quiescence (conflict set empty)"
                break
            result.cycles += 1
            chosen = self.resolve(candidates)
            # ACT phase
            for attribute, value in chosen.actions:
                memory.assert_fact(attribute, value, chosen.rule_id)
            fired.add(chosen.rule_id)
            result.fired_rules.append(chosen.rule_id)
            if trace:
                ids = ", ".join(r.rule_id for r in candidates)
                changes = ", ".join(f"{a}={_fmt(v)}"
                                    for a, v in chosen.actions)
                print(f"  Cycle {result.cycles:>2} | Conflict set: "
                      f"{{{ids}}}")
                print(f"           | Fired: {chosen.rule_id} "
                      f"(priority {chosen.priority}, specificity "
                      f"{chosen.specificity}) -> {changes}")
        result.elapsed_ms = (time.perf_counter() - start) * 1000.0
        return result


# ---------------------------------------------------------------------------
# Domain knowledge base: Smart Irrigation Advisor
# ---------------------------------------------------------------------------
def build_irrigation_rules() -> List[Rule]:
    """Rule base. Priorities: 30 = classify, 20 = infer, 10 = decide,
    5 = advisory."""
    return [
        Rule("R01", "Soil is dry",
             (("soil_moisture", "<", 30),),
             (("soil_status", "dry"),), 30),
        Rule("R02", "Soil moisture is optimal",
             (("soil_moisture", ">=", 30), ("soil_moisture", "<=", 60)),
             (("soil_status", "optimal"),), 30),
        Rule("R03", "Soil is wet",
             (("soil_moisture", ">", 60),),
             (("soil_status", "wet"),), 30),
        Rule("R04", "Crop is under heat stress",
             (("temperature", ">=", 35),),
             (("heat_stress", "yes"),), 30),
        Rule("R05", "No heat stress",
             (("temperature", "<", 35),),
             (("heat_stress", "no"),), 30),
        Rule("R06", "Dry soil and heat stress",
             (("soil_status", "==", "dry"), ("heat_stress", "==", "yes")),
             (("water_need", "high"),), 20),
        Rule("R07", "Dry soil without heat stress",
             (("soil_status", "==", "dry"), ("heat_stress", "==", "no")),
             (("water_need", "medium"),), 20),
        Rule("R08", "Optimal soil at sensitive flowering stage",
             (("soil_status", "==", "optimal"),
              ("crop_stage", "==", "flowering")),
             (("water_need", "medium"),), 20),
        Rule("R09", "Optimal soil at other stages",
             (("soil_status", "==", "optimal"),
              ("crop_stage", "!=", "flowering")),
             (("water_need", "low"),), 20),
        Rule("R10", "Wet soil needs no water",
             (("soil_status", "==", "wet"),),
             (("water_need", "none"),), 20),
        Rule("R11", "High need: irrigate immediately",
             (("water_need", "==", "high"),),
             (("decision", "IRRIGATE_NOW"), ("duration_min", 40)), 10),
        Rule("R12", "Medium need and no rain expected",
             (("water_need", "==", "medium"), ("rain_forecast", "==", "no")),
             (("decision", "IRRIGATE_NOW"), ("duration_min", 20)), 10),
        Rule("R13", "Medium need but rain expected",
             (("water_need", "==", "medium"),
              ("rain_forecast", "==", "yes")),
             (("decision", "POSTPONE"), ("duration_min", 0)), 10),
        Rule("R14", "Low or no need",
             (("water_need", "in", ("low", "none")),),
             (("decision", "NO_IRRIGATION"), ("duration_min", 0)), 10),
        Rule("R15", "Waterlogging risk",
             (("soil_moisture", ">", 85),),
             (("drainage_alert", "CHECK_FIELD_DRAINAGE"),), 5),
        Rule("R16", "Seedlings under heat stress",
             (("heat_stress", "==", "yes"), ("crop_stage", "==", "seedling")),
             (("shade_advice", "USE_SHADE_NET"),), 5),
    ]


def validate_observations(moisture: Any, temperature: Any, rain: Any,
                          stage: Any) -> Dict[str, Any]:
    """Validate raw observations and return the initial working memory."""
    try:
        moisture = float(moisture)
        temperature = float(temperature)
    except (TypeError, ValueError) as exc:
        raise ProductionSystemError(
            "Soil moisture and temperature must be numbers.") from exc
    if not MOISTURE_RANGE[0] <= moisture <= MOISTURE_RANGE[1]:
        raise ProductionSystemError(
            f"Soil moisture must be in {MOISTURE_RANGE[0]:g}-"
            f"{MOISTURE_RANGE[1]:g} %, got {moisture:g}.")
    if not TEMPERATURE_RANGE[0] <= temperature <= TEMPERATURE_RANGE[1]:
        raise ProductionSystemError(
            f"Temperature must be in {TEMPERATURE_RANGE[0]:g} to "
            f"{TEMPERATURE_RANGE[1]:g} C, got {temperature:g}.")
    rain = str(rain).strip().lower()
    if rain not in RAIN_VALUES:
        raise ProductionSystemError(
            f"Rain forecast must be one of {RAIN_VALUES}, got {rain!r}.")
    stage = str(stage).strip().lower()
    if stage not in CROP_STAGES:
        raise ProductionSystemError(
            f"Crop stage must be one of {CROP_STAGES}, got {stage!r}.")
    return {"soil_moisture": moisture, "temperature": temperature,
            "rain_forecast": rain, "crop_stage": stage}


# ---------------------------------------------------------------------------
# Presentation
# ---------------------------------------------------------------------------
def print_rule_base(rules: Sequence[Rule]) -> None:
    """Print every production rule."""
    print("Rule base (priority shown in brackets)")
    for rule in rules:
        print(f"  {rule.rule_id} [{rule.priority:>2}] {rule.as_text()}")
    print()


def run_scenario(title: str, facts: Dict[str, Any],
                 rules: Sequence[Rule]) -> RunResult:
    """Run the production system on one set of input facts."""
    print("-" * LINE_WIDTH)
    print(f" {title}")
    print("-" * LINE_WIDTH)
    print("Initial working memory: " + ", ".join(
        f"{k}={_fmt(v)}" for k, v in facts.items()))
    memory = WorkingMemory(facts)
    engine = ProductionSystem(rules)
    result = engine.run(memory, trace=True)

    final = memory.snapshot()
    derived = {k: v for k, v in final.items() if k not in facts}
    print(f"Halted after {result.cycles} cycles: {result.halt_reason}")
    print("Derived facts         : " + ", ".join(
        f"{k}={_fmt(v)}" for k, v in derived.items()))
    duration = final.get("duration_min", 0)
    print(f"DECISION              : {final.get('decision', 'UNDETERMINED')}"
          f" (duration {duration} min)")
    advisories = [final[k] for k in ("drainage_alert", "shade_advice")
                  if k in final]
    print(f"Advisories            : {', '.join(advisories) or 'none'}")
    print("Explanation (why)     : " + " -> ".join(result.fired_rules))
    print(f"Rule match attempts   : {result.rules_tested}   "
          f"Execution time: {result.elapsed_ms:.3f} ms")
    print()
    return result


DEFAULT_SCENARIOS = [
    ("Scenario 1: Hot day, dry soil, flowering crop",
     (22, 38, "no", "flowering")),
    ("Scenario 2: Moderate moisture, rain expected, flowering crop",
     (45, 30, "yes", "flowering")),
    ("Scenario 3: Waterlogged field, heat wave, seedlings",
     (90, 36, "no", "seedling")),
]


def build_parser() -> argparse.ArgumentParser:
    """Command-line interface definition."""
    parser = argparse.ArgumentParser(
        description="Production system demo: Smart Irrigation Advisor.")
    parser.add_argument("-m", "--moisture", type=float,
                        help="soil moisture in percent (0-100)")
    parser.add_argument("-t", "--temperature", type=float,
                        help="air temperature in degree Celsius")
    parser.add_argument("-r", "--rain", help="rain forecast: yes / no")
    parser.add_argument("-s", "--stage",
                        help="crop stage: " + ", ".join(CROP_STAGES))
    parser.add_argument("--interactive", action="store_true",
                        help="read the observations from the keyboard")
    return parser


def read_interactive() -> Dict[str, Any]:
    """Prompt for observations; re-prompt up to three times on error."""
    for attempt in range(1, 4):
        try:
            return validate_observations(
                input("Soil moisture (%)            : "),
                input("Air temperature (C)          : "),
                input("Rain forecast (yes/no)       : "),
                input(f"Crop stage {CROP_STAGES}: "))
        except ProductionSystemError as exc:
            print(f"  Invalid input ({attempt}/3): {exc}")
    raise ProductionSystemError("Too many invalid attempts.")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Program entry point; returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    rules = build_irrigation_rules()
    custom = [args.moisture, args.temperature, args.rain, args.stage]
    try:
        if args.interactive:
            scenarios = [("User scenario", read_interactive())]
        elif any(value is not None for value in custom):
            if any(value is None for value in custom):
                raise ProductionSystemError(
                    "Provide all of --moisture, --temperature, --rain "
                    "and --stage (or none of them).")
            scenarios = [("User scenario", validate_observations(*custom))]
        else:
            scenarios = [(title, validate_observations(*values))
                         for title, values in DEFAULT_SCENARIOS]

        print("=" * LINE_WIDTH)
        print(" EXPERIMENT 2 : PRODUCTION SYSTEM - SMART IRRIGATION ADVISOR")
        print("=" * LINE_WIDTH)
        print("Conflict resolution: refractoriness > priority > "
              "specificity > rule order")
        print()
        print_rule_base(rules)
        for title, facts in scenarios:
            run_scenario(title, facts, rules)
        return EXIT_OK
    except ProductionSystemError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return EXIT_INVALID_INPUT
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled by the user.", file=sys.stderr)
        return EXIT_INVALID_INPUT


if __name__ == "__main__":
    sys.exit(main())
