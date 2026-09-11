"""Step 4 of the demo story: build the concept mastery map."""

from collections import defaultdict


def build_mastery_map(answer_records: list, concepts: dict) -> dict:
    """Return {concept_id: mastery_score} where mastery is the fraction of
    correct answers per concept, 0.0-1.0.

    Concepts the diagnostic never touched are left out of the map; callers
    should treat a missing concept as "not yet assessed" rather than 0.
    """
    by_concept = defaultdict(list)
    for record in answer_records:
        by_concept[record.concept_id].append(record.correct)

    mastery_map = {}
    for concept_id in concepts:
        if concept_id in by_concept:
            answers = by_concept[concept_id]
            mastery_map[concept_id] = round(sum(answers) / len(answers), 3)
    return mastery_map


def weakest_concepts(mastery_map: dict, threshold: float = 0.6) -> list:
    """Return concept_ids at or below the mastery threshold, weakest first."""
    below = [(cid, score) for cid, score in mastery_map.items() if score <= threshold]
    below.sort(key=lambda pair: pair[1])
    return [cid for cid, _ in below]
