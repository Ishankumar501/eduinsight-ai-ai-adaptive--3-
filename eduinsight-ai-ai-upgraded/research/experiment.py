"""Lightweight cohort/condition tracking for research mode."""

from dataclasses import dataclass


@dataclass
class ExperimentCohort:
    experiment_id: str
    condition: str  # e.g. "ai-intervention" vs "control"
    student_ids: list


def assign_condition(student_id: str, experiment_id: str, split_ratio: float = 0.5) -> str:
    """Deterministic hash-based assignment so the same student always lands
    in the same condition for a given experiment, without storing a lookup table.
    """
    import hashlib
    digest = hashlib.sha256(f"{experiment_id}:{student_id}".encode()).hexdigest()
    bucket = int(digest, 16) % 100
    return "ai-intervention" if bucket < split_ratio * 100 else "control"
