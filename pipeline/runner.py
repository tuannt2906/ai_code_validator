from pipeline.preprocessor import CodePreprocessor
from pipeline.validator_syntax import SyntaxValidator
from pipeline.validator_logic import LogicValidator
from pipeline.validator_performance import PerformanceValidator
from pipeline.aggregator import aggregate


class ValidationRunner:
    def __init__(self):
        self.syntax = SyntaxValidator()
        self.logic = LogicValidator()
        self.perf = PerformanceValidator()

    def run(self, code: str) -> dict:
        pre = CodePreprocessor(code)

        syntax_report = self.syntax.run(pre.full_code())

        logic_report = ""
        perf_report = ""

        if "HIGH" not in syntax_report:
            logic_report = self.logic.run(pre.extract_functions())
            perf_report = self.perf.run(pre.extract_hotspots())

        return aggregate(syntax_report, logic_report, perf_report)
