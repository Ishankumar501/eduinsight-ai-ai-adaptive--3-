import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from assessment.diagnostic import DiagnosticSession
from assessment.question_engine import get_diagnostic_set, load_questions
from intelligence.intervention import recommend_intervention
from intelligence.mastery import build_mastery_map
from intelligence.misconception import detect_misconceptions
from knowledge_graph.concepts import load_concepts
from research.learning_gain import normalized_gain


def _run_scripted_diagnostic():
    concepts = load_concepts()
    questions = get_diagnostic_set(load_questions())
    diag = DiagnosticSession("TEST01", questions)
    answers = {
        "Q1": ("B", 5), "Q2": ("A", 5), "Q3": ("B", 4), "Q4": ("A", 4),
        "Q5": ("B", 4), "Q6": ("B", 5), "Q7": ("B", 5), "Q8": ("C", 3),
        "Q9": ("A", 4), "Q10": ("A", 4),
    }
    for q in questions:
        option, confidence = answers[q.question_id]
        diag.answer(q.question_id, option, confidence)
    return diag, concepts


def test_diagnostic_scores_correctly():
    diag, _ = _run_scripted_diagnostic()
    assert diag.is_complete()
    # 8 of 10 scripted answers are correct (Q5 and Q6 are wrong on purpose)
    assert diag.score() == 0.8


def test_mastery_map_has_all_assessed_concepts():
    diag, concepts = _run_scripted_diagnostic()
    mastery_map = build_mastery_map(diag.records, concepts)
    assert set(mastery_map.keys()) == set(concepts.keys())
    assert mastery_map["C3"] == 0.0  # both C3 questions answered wrong


def test_misconception_is_detected_with_enough_evidence():
    diag, concepts = _run_scripted_diagnostic()
    detected = detect_misconceptions(diag.records)
    assert len(detected) == 1
    assert detected[0].name == "denominator-addition-error"
    assert detected[0].evidence_count == 2


def test_no_misconception_flagged_below_evidence_threshold():
    diag, concepts = _run_scripted_diagnostic()
    # Only keep one piece of evidence for the misconception
    trimmed = [r for r in diag.records if r.question_id != "Q6"]
    detected = detect_misconceptions(trimmed)
    assert detected == []


def test_intervention_is_recommended_for_detected_misconception():
    diag, concepts = _run_scripted_diagnostic()
    mastery_map = build_mastery_map(diag.records, concepts)
    detected = detect_misconceptions(diag.records)
    intervention = recommend_intervention(detected[0], mastery_map, concepts)
    assert intervention.misconception_name == "denominator-addition-error"
    assert intervention.status == "recommended"
    assert intervention.est_minutes > 0


def test_normalized_gain_improves_with_higher_post_score():
    assert normalized_gain(0.5, 1.0) == 1.0
    assert normalized_gain(0.5, 0.5) == 0.0
    assert normalized_gain(1.0, 1.0) == 0.0  # no room left to gain
