import re

def extract_critical_issues(report: dict) -> str:
    """
    Extract fixable issues from validator reports.
    Return plain text list for code-fixing agent.
    """

    issues = []

    # Syntax / best-practice issues
    syntax = report.get("syntax", "")
    for line in syntax.splitlines():
        if "[HIGH]" in line or "[MEDIUM]" in line:
            issues.append(line.strip())

    # Logic issues (most important)
    logic = report.get("logic", "")
    for line in logic.splitlines():
        if any(level in line for level in ("CRITICAL", "MAJOR")):
            issues.append(line.strip())

    # Performance issues (optional but useful)
    perf = report.get("performance", "")
    for line in perf.splitlines():
        if any(
            keyword in line.lower()
            for keyword in ("o(", "loop", "inefficient", "vector", "bottleneck")
        ):
            issues.append(line.strip())

    # Remove duplicates & join
    unique = list(dict.fromkeys(issues))

    return "\n".join(unique)
