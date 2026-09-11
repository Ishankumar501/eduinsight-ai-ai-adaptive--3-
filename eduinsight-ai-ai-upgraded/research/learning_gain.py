"""Step 10 of the demo story: dashboard calculates learning gain.

Uses normalized gain (Hake's g), the standard measure in education
research for comparing pre/post scores regardless of starting point.
"""


def normalized_gain(pre_score: float, post_score: float) -> float:
    """Hake's normalized gain: (post - pre) / (1 - pre).

    Returns a value roughly between -1 and 1. Returns 0.0 for a student who
    already scored 1.0 pre-assessment, since there is no room left to gain.
    """
    if pre_score >= 1.0:
        return 0.0
    gain = (post_score - pre_score) / (1 - pre_score)
    return round(gain, 3)


def raw_gain(pre_score: float, post_score: float) -> float:
    return round(post_score - pre_score, 3)


def gain_summary(pre_score: float, post_score: float) -> dict:
    return {
        "pre_score": pre_score,
        "post_score": post_score,
        "raw_gain": raw_gain(pre_score, post_score),
        "normalized_gain": normalized_gain(pre_score, post_score),
    }
