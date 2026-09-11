"""Runs the full 12-step EduInsight demo story from the command line.

    python demo.py

Uses the same modules as the Flask app, with scripted answers standing in
for a real student, so you can see the whole pipeline run in one pass
without clicking through the browser.
"""

import csv
from pathlib import Path

from assessment.diagnostic import DiagnosticSession
from assessment.micro_assessment import get_micro_assessment, score_micro_assessment
from assessment.question_engine import get_diagnostic_set, load_questions
from dashboard.researcher import render_research_summary
from dashboard.teacher import render_teacher_dashboard
from intelligence.intervention import apply_teacher_decision, recommend_intervention
from intelligence.mastery import build_mastery_map
from intelligence.misconception import detect_misconceptions
from knowledge_graph.concepts import load_concepts
from research.anonymizer import anonymize_record, export_csv, export_json
from research.experiment import assign_condition
from research.learning_gain import gain_summary

DATA_DIR = Path(__file__).resolve().parent / "data"
EXPORT_DIR = Path(__file__).resolve().parent / "research" / "exports"


def line(title):
    print(f"\n{'-' * 60}\n{title}\n{'-' * 60}")


# Scripted answers: correct on everything except the two "adding fractions"
# questions (Q5, Q6), which are answered with the denominator-addition
# misconception distractor at high confidence — enough evidence for the
# system to flag a real misconception rather than a slip.
SCRIPTED_ANSWERS = {
    "Q1": ("B", 5), "Q2": ("A", 5),
    "Q3": ("B", 4), "Q4": ("A", 4),
    "Q5": ("B", 4),  # wrong, misconception distractor, confident
    "Q6": ("B", 5),  # wrong, misconception distractor, very confident
    "Q7": ("B", 5),
    "Q8": ("C", 3),
    "Q9": ("A", 4),
    "Q10": ("A", 4),
}


def main():
    concepts = load_concepts()
    questions = get_diagnostic_set(load_questions())
    student_id, student_name = "S100", "Aisha Khan"

    # Step 1
    line("STEP 1 — Student logs in")
    print(f"{student_name} ({student_id}) logged in.")

    # Steps 2-3
    line("STEP 2 & 3 — 10-question diagnostic with confidence ratings")
    diag = DiagnosticSession(student_id, questions)
    for q in questions:
        option, confidence = SCRIPTED_ANSWERS[q.question_id]
        record = diag.answer(q.question_id, option, confidence)
        mark = "correct" if record.correct else "WRONG"
        print(f"  {q.question_id}: chose {option} (confidence {confidence}/5) — {mark}")
    print(f"Diagnostic score: {diag.score() * 100:.0f}%")

    # Step 4
    line("STEP 4 — EduInsight constructs the concept mastery map")
    mastery_map = build_mastery_map(diag.records, concepts)
    for cid, score in mastery_map.items():
        print(f"  {concepts[cid].name}: {score * 100:.0f}%")

    # Step 5
    line("STEP 5 — System detects one misconception")
    misconceptions = detect_misconceptions(diag.records)
    primary = misconceptions[0] if misconceptions else None
    if primary:
        print(f"  Detected: {primary.name} ({primary.evidence_count} pieces of evidence, "
              f"avg confidence {primary.avg_confidence}/5)")
    else:
        print("  No repeated misconception pattern found.")

    # Step 6
    line("STEP 6 — AI recommends an intervention")
    intervention = recommend_intervention(primary, mastery_map, concepts) if primary else None
    if intervention:
        print(f"  {intervention.title} — {intervention.activity_type}, {intervention.est_minutes} min")
        print(f"  {intervention.description}")

    # Step 7
    line("STEP 7 — Teacher accepts or modifies it")
    if intervention:
        apply_teacher_decision(intervention, "accept")
        print(f"  Teacher decision: {intervention.status}")

    # Step 8
    line("STEP 8 — Student completes the intervention")
    if intervention:
        intervention.status = "completed"
        print(f"  Status: {intervention.status}")

    # Step 9
    line("STEP 9 — Micro-assessment")
    post_score = 0.0
    if intervention:
        micro_questions = get_micro_assessment(intervention.concept_ids[0])
        # Scripted: the intervention worked, student now answers correctly
        micro_answers = {q.question_id: q.correct for q in micro_questions}
        post_score = score_micro_assessment(micro_questions, micro_answers)
        print(f"  Micro-assessment score: {post_score * 100:.0f}%")

    # Step 10
    line("STEP 10 — Dashboard calculates learning gain")
    pre_score = diag.score()
    gain = gain_summary(pre_score, post_score) if intervention else None
    if gain:
        print(f"  Pre: {gain['pre_score']*100:.0f}%  Post: {gain['post_score']*100:.0f}%  "
              f"Raw gain: {gain['raw_gain']*100:.0f} pts  Normalized gain (Hake's g): {gain['normalized_gain']}")

    # Step 11
    line("STEP 11 — Teacher sees class-level concept gaps")
    students_mastery = {student_id: mastery_map}
    with open(DATA_DIR / "sample_students.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            students_mastery[row["student_id"]] = {
                cid.replace("_mastery", ""): float(row[cid])
                for cid in row if cid.endswith("_mastery")
            }
    teacher_view = render_teacher_dashboard(students_mastery, concepts)
    print(f"  Class size: {teacher_view['class_size']}")
    for row in teacher_view["concept_gaps"]:
        print(f"  {row['concept']}: class avg {row['class_average']*100:.0f}%, "
              f"{row['students_below_threshold']}/{row['students_assessed']} below target")

    # Step 12
    line("STEP 12 — Research mode exports anonymized evidence")
    if intervention and gain:
        condition = assign_condition(student_id, experiment_id="eduinsight-pilot-1")
        record = anonymize_record(student_id, mastery_map, misconceptions, intervention, gain, condition)
        json_path = export_json([record], str(EXPORT_DIR / "anonymized_export.json"))
        csv_path = export_csv([record], str(EXPORT_DIR / "anonymized_export.csv"))
        summary = render_research_summary([record])
        print(f"  Anonymized ID: {record['anon_id']} (condition: {record['condition']})")
        print(f"  Exported to: {json_path}, {csv_path}")
        print(f"  Summary: {summary}")

    line("Demo complete")


if __name__ == "__main__":
    main()
