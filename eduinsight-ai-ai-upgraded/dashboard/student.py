"""Data shaping for the student-facing dashboard view."""

from knowledge_graph.concepts import concept_name


def render_student_dashboard(student_id: str, mastery_map: dict, concepts: dict,
                              misconceptions: list, intervention, learning_gain: dict = None) -> dict:
    return {
        "student_id": student_id,
        "mastery": [
            {"concept": concept_name(concepts, cid), "score": score}
            for cid, score in sorted(mastery_map.items(), key=lambda kv: kv[1])
        ],
        "misconceptions": [
            {
                "name": m.name,
                "concepts": [concept_name(concepts, c) for c in m.concept_ids],
                "evidence_count": m.evidence_count,
            }
            for m in misconceptions
        ],
        "intervention": {
            "title": intervention.title,
            "description": intervention.description,
            "activity_type": intervention.activity_type,
            "est_minutes": intervention.est_minutes,
            "status": intervention.status,
        } if intervention else None,
        "learning_gain": learning_gain,
    }
