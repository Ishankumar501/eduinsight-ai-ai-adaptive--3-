import csv
from pathlib import Path

from flask import Blueprint, redirect, render_template, request, url_for

from dashboard.teacher import render_teacher_dashboard
from intelligence.intervention import apply_teacher_decision
from knowledge_graph.concepts import load_concepts

teacher_bp = Blueprint("teacher", __name__)

CONCEPTS = load_concepts()
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _store():
    from app import STORE
    return STORE


def _sample_class_mastery() -> dict:
    """Pre-recorded classmates so the class dashboard has more than one
    student in it without every classmate running the live diagnostic."""
    students = {}
    with open(DATA_DIR / "sample_students.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mastery = {
                cid.replace("_mastery", ""): float(row[cid])
                for cid in row if cid.endswith("_mastery")
            }
            students[row["student_id"]] = mastery
    return students


@teacher_bp.route("/review/<student_id>", methods=["GET", "POST"])
def review_intervention(student_id):
    """Step 7: teacher reviews the AI-recommended intervention and accepts
    or modifies it before the student sees it."""
    store = _store()
    intervention = store["interventions"].get(student_id)
    if not intervention:
        return "No pending intervention for this student.", 404

    if request.method == "POST":
        decision = request.form["decision"]
        note = request.form.get("note", "")
        apply_teacher_decision(intervention, decision, note)
        return redirect(url_for("teacher.dashboard"))

    return render_template("teacher_review.html", student_id=student_id, intervention=intervention)


@teacher_bp.route("/dashboard")
def dashboard():
    """Step 11: teacher sees class-level concept gaps."""
    students_mastery = _sample_class_mastery()
    students_mastery.update(_store()["mastery_maps"])  # live demo student(s) join the roster
    data = render_teacher_dashboard(students_mastery, CONCEPTS)
    return render_template("teacher_dashboard.html", data=data)
