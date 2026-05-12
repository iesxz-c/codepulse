def compute_health_score(coverage: float, complexity: float, dead_code_count: int, churn_file_count: int) -> float:
    score = (
        0.40 * min(coverage, 100) +
        0.30 * max(0, 100 - (complexity * 10)) +
        0.20 * max(0, 100 - (dead_code_count * 2)) +
        0.10 * max(0, 100 - (churn_file_count * 5))
    )
    return max(0.0, min(100.0, round(score, 2)))
