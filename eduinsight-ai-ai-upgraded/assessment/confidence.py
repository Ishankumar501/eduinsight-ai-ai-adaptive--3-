"""Confidence rating captured after each diagnostic answer.

Students rate confidence on a 1-5 scale:
  1 = Just guessing   3 = Somewhat sure   5 = Certain
"""

CONFIDENCE_LABELS = {
    1: "Just guessing",
    2: "Not very sure",
    3: "Somewhat sure",
    4: "Fairly confident",
    5: "Certain",
}


def valid_confidence(level) -> int:
    level = int(level)
    if level not in CONFIDENCE_LABELS:
        raise ValueError("Confidence must be an integer from 1 to 5")
    return level


def calibration_score(answer_records: list) -> float:
    """Return a 0-1 calibration score comparing confidence to correctness.

    Built like a simplified Brier score: for every answer we compare the
    normalized confidence (0-1) against correctness (1 or 0), average the
    squared error, then flip it so 1.0 means perfectly calibrated and 0.0
    means confidence and correctness never lined up.
    """
    if not answer_records:
        return 0.0
    total_error = 0.0
    for record in answer_records:
        normalized_confidence = (record.confidence - 1) / 4  # 1-5 -> 0-1
        actual = 1.0 if record.correct else 0.0
        total_error += (normalized_confidence - actual) ** 2
    mean_error = total_error / len(answer_records)
    return round(1 - mean_error, 3)


def overconfidence_flags(answer_records: list, confidence_threshold: int = 4) -> list:
    """Return records where the student was confident but wrong.

    This is the core signal the risk model uses: high confidence plus an
    incorrect answer usually means a misconception rather than a gap.
    """
    return [
        r for r in answer_records
        if not r.correct and r.confidence >= confidence_threshold
    ]
