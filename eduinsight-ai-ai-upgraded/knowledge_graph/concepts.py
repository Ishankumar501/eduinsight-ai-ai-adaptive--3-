"""Load and represent the concept graph used by EduInsight."""

import csv
from dataclasses import dataclass, field
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass
class Concept:
    concept_id: str
    name: str
    prerequisites: list = field(default_factory=list)
    description: str = ""


def load_concepts(path: str = None) -> dict:
    """Return {concept_id: Concept} loaded from concepts.csv."""
    path = path or (DATA_DIR / "concepts.csv")
    concepts = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            prereqs = [p for p in row["prerequisite_ids"].split("|") if p]
            concepts[row["concept_id"]] = Concept(
                concept_id=row["concept_id"],
                name=row["concept_name"],
                prerequisites=prereqs,
                description=row["description"],
            )
    return concepts


def concept_name(concepts: dict, concept_id: str) -> str:
    c = concepts.get(concept_id)
    return c.name if c else concept_id
