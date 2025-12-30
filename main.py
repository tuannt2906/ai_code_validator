import sys
from pipeline.runner import ValidationRunner

code = open(sys.argv[1]).read()

runner = ValidationRunner()
result = runner.run(code)

print(result)