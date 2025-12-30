import sys
from pipeline.runner import ValidationRunner
from pipeline.error_extractor import extract_critical_issues
from pipeline.code_fixer import CodeFixer

MAX_ITER = 3

code = open(sys.argv[1]).read()

runner = ValidationRunner()
fixer = CodeFixer()

for i in range(MAX_ITER):
    print(f"\n=== ITERATION {i+1} ===")

    result = runner.run(code)
    print("Verdict:", result["verdict"])

    if result["verdict"] == "PASS":
        break

    issues = extract_critical_issues(result)

    if not issues.strip():
        print("No fixable issues.")
        break

    code = fixer.fix(code, issues)

print("\nFINAL CODE:\n")
print(code)
