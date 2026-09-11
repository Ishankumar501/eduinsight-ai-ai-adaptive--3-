"""Step 5 of the demo story: detect a misconception, not just a wrong answer.

A single wrong answer could be a slip. A repeated, confident wrong answer of
the same type is a misconception. This module tells those two apart.
"""

from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class DetectedMisconception:
    name: str
    concept_ids: list
    evidence_question_ids: list = field(default_factory=list)
    evidence_count: int = 0
    avg_confidence: float = 0.0


def detect_misconceptions(answer_records: list, min_evidence: int = 2) -> list:
    """Group misconception-tagged wrong answers by misconception name and
    keep only the ones with enough repeated evidence to call a pattern.
    """
    grouped = defaultdict(list)
    for record in answer_records:
        if record.is_misconception_choice:
            grouped[record.misconception_name].append(record)

    detected = []
    for name, records in grouped.items():
        if len(records) >= min_evidence:
            concept_ids = sorted({r.concept_id for r in records})
            avg_conf = round(sum(r.confidence for r in records) / len(records), 2)
            detected.append(DetectedMisconception(
                name=name,
                concept_ids=concept_ids,
                evidence_question_ids=[r.question_id for r in records],
                evidence_count=len(records),
                avg_confidence=avg_conf,
            ))

    # Strongest, most-confident pattern first — that is the one the system
    # surfaces as "the" misconception in the demo story.
    detected.sort(key=lambda m: (m.evidence_count, m.avg_confidence), reverse=True)
    return detected


def primary_misconception(answer_records: list, min_evidence: int = 2):
    """Return the single highest-priority misconception, or None."""
    detected = detect_misconceptions(answer_records, min_evidence=min_evidence)
    return detected[0] if detected else None
