"""Combine mastery scores and confidence patterns into risk flags.

Feeds the teacher dashboard and the intervention engine's prioritization.
"""

from dataclasses import dataclass

from assessment.confidence import overconfidence_flags


@dataclass
class RiskFlag:
    concept_id: str
    reason: str
    severity: str  # "low", "medium", "high"


def compute_risk_flags(mastery_map: dict, answer_records: list,
                        low_mastery_threshold: float = 0.5) -> list:
    flags = []

    for concept_id, score in mastery_map.items():
        if score <= low_mastery_threshold:
            flags.append(RiskFlag(
                concept_id=concept_id,
                reason=f"Mastery at {int(score * 100)}%, below the {int(low_mastery_threshold * 100)}% target",
                severity="high" if score < 0.3 else "medium",
            ))

    overconfident = overconfidence_flags(answer_records)
    concepts_hit = {}
    for record in overconfident:
        concepts_hit.setdefault(record.concept_id, 0)
        concepts_hit[record.concept_id] += 1

    for concept_id, count in concepts_hit.items():
        flags.append(RiskFlag(
            concept_id=concept_id,
            reason=f"Answered confidently but incorrectly {count} time(s) — likely misconception, not a knowledge gap",
            severity="high",
        ))

    return flags
