"""Step 11 of the demo story: teacher sees class-level concept gaps."""

from collections import defaultdict

from knowledge_graph.concepts import concept_name


def class_concept_gaps(students_mastery: dict, concepts: dict, gap_threshold: float = 0.6) -> list:
    """students_mastery: {student_id: {concept_id: score}}

    Returns concept-level rows sorted so the biggest class-wide gap comes first.
    """
    totals = defaultdict(list)
    for mastery_map in students_mastery.values():
        for cid, score in mastery_map.items():
            totals[cid].append(score)

    rows = []
    for cid, scores in totals.items():
        avg = round(sum(scores) / len(scores), 3)
        below_count = sum(1 for s in scores if s < gap_threshold)
        rows.append({
            "concept_id": cid,
            "concept": concept_name(concepts, cid),
            "class_average": avg,
            "students_below_threshold": below_count,
            "students_assessed": len(scores),
        })

    rows.sort(key=lambda r: r["class_average"])
    return rows


def render_teacher_dashboard(students_mastery: dict, concepts: dict) -> dict:
    return {
        "class_size": len(students_mastery),
        "concept_gaps": class_concept_gaps(students_mastery, concepts),
    }
