"""Step 6 + 7 of the demo story: AI recommends an intervention, teacher
accepts or modifies it.
"""

from dataclasses import dataclass, field

from knowledge_graph.prerequisites import missing_prerequisites

# Each entry describes a short, targeted activity for a known misconception.
INTERVENTION_LIBRARY = {
    "denominator-addition-error": {
        "title": "Common-denominator visual drill",
        "description": (
            "Five fraction-strip problems that force the student to find a "
            "shared denominator before adding, with a visual model showing "
            "why denominators do not add directly."
        ),
        "activity_type": "interactive drill",
        "est_minutes": 12,
    },
    "cross-multiplication-error": {
        "title": "Proportion setup walkthrough",
        "description": (
            "Guided practice that has the student label numerator and "
            "denominator pairs before cross-multiplying, on three worked "
            "proportion problems."
        ),
        "activity_type": "guided worked examples",
        "est_minutes": 10,
    },
}

DEFAULT_INTERVENTION = {
    "title": "Targeted concept review",
    "description": "A short review set focused on the weakest concept from the diagnostic.",
    "activity_type": "review set",
    "est_minutes": 10,
}


@dataclass
class Intervention:
    misconception_name: str
    concept_ids: list
    title: str
    description: str
    activity_type: str
    est_minutes: int
    prerequisite_gaps: list = field(default_factory=list)
    status: str = "recommended"  # recommended -> accepted / modified
    teacher_note: str = ""


def recommend_intervention(detected_misconception, mastery_map: dict, concepts: dict) -> Intervention:
    """Build the AI's recommended intervention for the primary misconception."""
    template = INTERVENTION_LIBRARY.get(detected_misconception.name, DEFAULT_INTERVENTION)

    prereq_gaps = []
    for concept_id in detected_misconception.concept_ids:
        prereq_gaps.extend(missing_prerequisites(concept_id, mastery_map, concepts))

    return Intervention(
        misconception_name=detected_misconception.name,
        concept_ids=detected_misconception.concept_ids,
        title=template["title"],
        description=template["description"],
        activity_type=template["activity_type"],
        est_minutes=template["est_minutes"],
        prerequisite_gaps=sorted(set(prereq_gaps)),
    )


def apply_teacher_decision(intervention: Intervention, decision: str, note: str = "") -> Intervention:
    """Step 7: teacher accepts the AI recommendation as-is, or modifies it.

    decision: "accept" or "modify"
    """
    if decision not in ("accept", "modify"):
        raise ValueError('decision must be "accept" or "modify"')

    if decision == "accept":
        intervention.status = "accepted"
    else:
        intervention.status = "modified"
        if note:
            intervention.description = note
        intervention.teacher_note = note or "Modified by teacher"
    return intervention
