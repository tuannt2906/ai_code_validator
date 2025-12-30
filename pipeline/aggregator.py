def aggregate(syntax_report, logic_report, perf_report):
    score = 0
    if "HIGH" in syntax_report:
        score -= 30
    if "CRITICAL" in logic_report:
        score -= 50
    if "MAJOR" in logic_report:
        score -= 20

    if score <= -50:
        verdict = "FAIL"
    elif score <= -20:
        verdict = "WARN"
    else:
        verdict = "PASS"

    return {
        "verdict": verdict,
        "score": score,
        "syntax": syntax_report,
        "logic": logic_report,
        "performance": perf_report
    }
