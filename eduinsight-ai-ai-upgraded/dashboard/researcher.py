"""Research-mode summary view over anonymized records."""

from research.statistics import mean, stdev, confidence_interval_95


def render_research_summary(anonymized_records: list) -> dict:
    gains = [r["normalized_gain"] for r in anonymized_records if r.get("normalized_gain") is not None]
    misconception_counts = {}
    for r in anonymized_records:
        for name in r.get("misconceptions_detected", []):
            misconception_counts[name] = misconception_counts.get(name, 0) + 1

    return {
        "n_students": len(anonymized_records),
        "mean_normalized_gain": mean(gains),
        "stdev_normalized_gain": stdev(gains),
        "gain_95_ci": confidence_interval_95(gains),
        "misconception_frequency": misconception_counts,
    }
