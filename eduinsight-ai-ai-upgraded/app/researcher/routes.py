from pathlib import Path

from flask import Blueprint, render_template

from dashboard.researcher import render_research_summary
from research.anonymizer import anonymize_record, export_csv, export_json
from research.experiment import assign_condition

researcher_bp = Blueprint("researcher", __name__)

EXPORT_DIR = Path(__file__).resolve().parent.parent.parent / "research" / "exports"


def _store():
    from app import STORE
    return STORE


@researcher_bp.route("/export")
def export():
    """Step 12: research mode exports anonymized evidence for every student
    who has completed the full flow (has a post micro-assessment score)."""
    store = _store()
    records = []
    for student_id, gain in store["learning_gains"].items():
        if "post_score" not in gain:
            continue
        mastery_map = store["mastery_maps"].get(student_id, {})
        misconceptions = store["misconceptions"].get(student_id, [])
        intervention = store["interventions"].get(student_id)
        condition = assign_condition(student_id, experiment_id="eduinsight-pilot-1")
        records.append(anonymize_record(student_id, mastery_map, misconceptions, intervention, gain, condition))

    json_path = export_json(records, str(EXPORT_DIR / "anonymized_export.json"))
    csv_path = export_csv(records, str(EXPORT_DIR / "anonymized_export.csv"))
    summary = render_research_summary(records)

    return render_template(
        "researcher_export.html",
        records=records,
        summary=summary,
        json_path=json_path,
        csv_path=csv_path,
    )
