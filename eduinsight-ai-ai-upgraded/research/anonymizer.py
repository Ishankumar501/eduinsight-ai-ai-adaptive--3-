"""Step 12 of the demo story: research mode exports anonymized evidence."""

import csv
import hashlib
import json
from pathlib import Path

SALT = "eduinsight-research-salt-v1"  # fixed salt keeps hashed IDs stable across exports


def anonymize_student_id(student_id: str) -> str:
    return hashlib.sha256(f"{SALT}:{student_id}".encode()).hexdigest()[:12]


def anonymize_record(student_id: str, mastery_map: dict, misconceptions: list,
                      intervention, learning_gain: dict, condition: str = "") -> dict:
    """Strip all direct identifiers and keep only fields needed for analysis."""
    return {
        "anon_id": anonymize_student_id(student_id),
        "condition": condition,
        "mastery": mastery_map,
        "misconceptions_detected": [m.name for m in misconceptions],
        "intervention_type": intervention.activity_type if intervention else None,
        "intervention_status": intervention.status if intervention else None,
        "pre_score": learning_gain.get("pre_score"),
        "post_score": learning_gain.get("post_score"),
        "normalized_gain": learning_gain.get("normalized_gain"),
    }


def export_json(records: list, path: str) -> str:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    return path


def export_csv(records: list, path: str) -> str:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    if not records:
        return path
    flat_records = []
    for r in records:
        flat = {k: v for k, v in r.items() if k != "mastery"}
        for cid, score in r.get("mastery", {}).items():
            flat[f"mastery_{cid}"] = score
        flat_records.append(flat)
    fieldnames = sorted({key for r in flat_records for key in r})
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flat_records)
    return path
