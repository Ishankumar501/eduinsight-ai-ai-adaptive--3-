"""Small dependency-free statistics helpers for the research export."""

import math


def mean(values: list) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


def stdev(values: list) -> float:
    if len(values) < 2:
        return 0.0
    m = mean(values)
    variance = sum((v - m) ** 2 for v in values) / (len(values) - 1)
    return round(math.sqrt(variance), 4)


def cohens_d(group_a: list, group_b: list) -> float:
    """Effect size between two groups, e.g. AI-intervention vs control."""
    if not group_a or not group_b:
        return 0.0
    pooled_sd = math.sqrt(((stdev(group_a) ** 2) + (stdev(group_b) ** 2)) / 2)
    if pooled_sd == 0:
        return 0.0
    return round((mean(group_a) - mean(group_b)) / pooled_sd, 4)


def confidence_interval_95(values: list) -> tuple:
    """Approximate 95% CI on the mean using a normal approximation."""
    if len(values) < 2:
        return (mean(values), mean(values))
    m = mean(values)
    margin = 1.96 * (stdev(values) / math.sqrt(len(values)))
    return (round(m - margin, 4), round(m + margin, 4))
