#!/usr/bin/env python3
"""Lab 4: Knowledge Representation and Logical Reasoning.

Covers predicate facts, production rules, semantic networks, frames,
conceptual dependency and simple forward-chaining inference.
"""

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Set, Tuple
import argparse

Fact = Tuple[str, ...]


def show_fact(fact: Fact) -> str:
    """Format a tuple as a readable predicate expression."""
    predicate, *arguments = fact
    return f"{predicate}({', '.join(arguments)})"


@dataclass
class Rule:
    """A production rule with a name and a conclusion generator."""
    name: str
    conclusion: Callable[[Set[Fact]], Iterable[Fact]]


class KnowledgeBase:
    """Store predicate facts and infer new facts using production rules."""

    def __init__(self) -> None:
        self.facts: Set[Fact] = set()
        self.rules: List[Rule] = []

    def add_fact(self, *fact: str) -> None:
        if not fact or not all(isinstance(part, str) and part for part in fact):
            raise ValueError("A fact must contain a predicate and non-empty string arguments.")
        self.facts.add(tuple(fact))

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)

    def infer(self, max_rounds: int = 20) -> List[Fact]:
        """Apply rules until no new facts are produced or the limit is reached."""
        inferred: List[Fact] = []
        for _ in range(max_rounds):
            new_facts: Set[Fact] = set()
            for rule in self.rules:
                new_facts.update(rule.conclusion(self.facts))
            new_facts.difference_update(self.facts)
            if not new_facts:
                break
            self.facts.update(new_facts)
            inferred.extend(sorted(new_facts))
        return inferred


def build_university_rules(kb: KnowledgeBase) -> None:
    """Add rules for deriving university relationships."""
    def student_enrolments(facts: Set[Fact]) -> Iterable[Fact]:
        for student in facts:
            if student[0] == "Student":
                name = student[1]
                for enrolment in facts:
                    if enrolment[0] == "EnrolledIn" and enrolment[1] == name:
                        yield ("LearnerOf", name, enrolment[2])

    def learner_institute(facts: Set[Fact]) -> Iterable[Fact]:
        for learner in facts:
            if learner[0] == "LearnerOf":
                name, course = learner[1], learner[2]
                for offer in facts:
                    if offer[0] == "Offers" and offer[2] == course:
                        yield ("StudiesAt", name, offer[1])

    kb.add_rule(Rule("R1: Student + EnrolledIn -> LearnerOf", student_enrolments))
    kb.add_rule(Rule("R2: LearnerOf + Offers -> StudiesAt", learner_institute))


def build_medical_rules(kb: KnowledgeBase) -> None:
    """Add illustrative symptom rules. These are not medical diagnoses."""
    def possible_flu(facts: Set[Fact]) -> Iterable[Fact]:
        fever_people = {fact[1] for fact in facts if fact[0] == "Fever"}
        cough_people = {fact[1] for fact in facts if fact[0] == "Cough"}
        for person in fever_people & cough_people:
            yield ("PossibleFlu", person)

    def rest_advice(facts: Set[Fact]) -> Iterable[Fact]:
        possible = {fact[1] for fact in facts if fact[0] == "PossibleFlu"}
        fatigue = {fact[1] for fact in facts if fact[0] == "Fatigue"}
        for person in possible & fatigue:
            yield ("SuggestRestAndConsultation", person)

    kb.add_rule(Rule("R3: Fever + Cough -> PossibleFlu", possible_flu))
    kb.add_rule(Rule("R4: PossibleFlu + Fatigue -> SuggestRestAndConsultation", rest_advice))


def university_example() -> KnowledgeBase:
    kb = KnowledgeBase()
    kb.add_fact("Student", "Aarav")
    kb.add_fact("EnrolledIn", "Aarav", "MCA")
    kb.add_fact("Offers", "IIPS DAVV", "MCA")
    build_university_rules(kb)
    return kb


def medical_example() -> KnowledgeBase:
    kb = KnowledgeBase()
    kb.add_fact("Fever", "PatientA")
    kb.add_fact("Cough", "PatientA")
    kb.add_fact("Fatigue", "PatientA")
    build_medical_rules(kb)
    return kb


def show_semantic_network() -> None:
    """Print a small semantic network as subject-relation-object triples."""
    links = [
        ("Aarav", "instance-of", "Student"),
        ("Aarav", "enrolled-in", "MCA"),
        ("MCA", "offered-by", "IIPS DAVV"),
        ("IIPS DAVV", "part-of", "DAVV"),
        ("Student", "is-a", "Person"),
    ]
    print("Semantic network (subject --relation--> object):")
    for subject, relation, obj in links:
        print(f"  {subject} --{relation}--> {obj}")


def show_frames() -> None:
    """Demonstrate frame representation using dictionaries."""
    student_frame: Dict[str, object] = {
        "Frame": "Student", "Name": "Aarav", "Programme": "MCA",
        "Institute": "IIPS DAVV", "Year": 1, "Status": "Enrolled",
    }
    course_frame: Dict[str, object] = {
        "Frame": "Course", "Name": "MCA", "Duration": "4 years",
        "Department": "Computer Applications",
    }
    print("Student frame:")
    for slot, value in student_frame.items():
        print(f"  {slot}: {value}")
    print("Course frame:")
    for slot, value in course_frame.items():
        print(f"  {slot}: {value}")


def show_conceptual_dependency() -> None:
    """Represent a simple transfer action using an ATRANS relation."""
    action = {
        "Primitive": "ATRANS (transfer of possession)",
        "Actor": "John", "Object": "Book", "From": "John", "To": "Mary",
    }
    print("Conceptual dependency example: John gives a book to Mary")
    print("  " + "; ".join(f"{key}={value}" for key, value in action.items()))


def run_inference(title: str, kb: KnowledgeBase) -> None:
    print(f"\n{title}")
    print("Initial facts:")
    initial = sorted(kb.facts)
    for fact in initial:
        print(f"  {show_fact(fact)}")
    inferred = kb.infer()
    print("Inferred facts:")
    if inferred:
        for fact in inferred:
            print(f"  {show_fact(fact)}")
    else:
        print("  No new facts inferred.")
    print("Final knowledge base:")
    for fact in sorted(kb.facts):
        print(f"  {show_fact(fact)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Lab 4 Knowledge Representation examples")
    parser.add_argument("--example", choices=("all", "university", "medical"), default="all")
    args = parser.parse_args()

    print("=" * 68)
    print("LAB 4: KNOWLEDGE REPRESENTATION & LOGICAL REASONING")
    print("=" * 68)
    print("\n1. PREDICATE REPRESENTATION AND UNIVERSITY KNOWLEDGE BASE")
    if args.example in ("all", "university"):
        run_inference("University knowledge base", university_example())
    if args.example == "all":
        print("\n2. SEMANTIC NETWORK CONSTRUCTION")
        show_semantic_network()
        print("\n3. FRAME REPRESENTATION")
        show_frames()
        print("\n4. CONCEPTUAL DEPENDENCY")
        show_conceptual_dependency()
    if args.example in ("all", "medical"):
        print("\n5. RULE-BASED MEDICAL KNOWLEDGE REPRESENTATION")
        print("Note: This is a classroom rule demonstration, not medical advice.")
        run_inference("Medical example", medical_example())
    print("\n" + "=" * 68)
    print("LAB 4 COMPLETED")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
