import re

def extract_critical_issues(report: dict) -> str:
    issues = []

    if report["syntax"]:
        issues += re.findall(r"\[(HIGH|MEDIUM)\].*", report["syntax"])

    if report["logic"]:
        issues += re.findall(r"(CRITICAL|MAJOR).*", report["logic"])

    if report["performance"]:
        issues += re.findall(r"O\(.*?\)|inefficient|bottleneck", report["performance"], re.I)

    return "\n".join(set(issues))
