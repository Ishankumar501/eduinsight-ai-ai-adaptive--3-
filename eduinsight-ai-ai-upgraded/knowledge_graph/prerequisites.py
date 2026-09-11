"""Utilities for reasoning over concept prerequisites."""


def missing_prerequisites(concept_id: str, mastery_map: dict, concepts: dict,
                           threshold: float = 0.6) -> list:
    """Return prerequisite concept_ids that are below the mastery threshold.

    Used by the intervention engine to decide whether a student needs to
    revisit an earlier concept before the flagged one will make sense.
    """
    concept = concepts.get(concept_id)
    if not concept:
        return []
    gaps = []
    for prereq_id in concept.prerequisites:
        score = mastery_map.get(prereq_id, 0.0)
        if score < threshold:
            gaps.append(prereq_id)
    return gaps


def topological_order(concepts: dict) -> list:
    """Return concept_ids ordered so prerequisites always come first."""
    visited, order = set(), []

    def visit(cid):
        if cid in visited or cid not in concepts:
            return
        visited.add(cid)
        for prereq in concepts[cid].prerequisites:
            visit(prereq)
        order.append(cid)

    for cid in concepts:
        visit(cid)
    return order
