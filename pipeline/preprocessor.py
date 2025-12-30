import ast


class CodePreprocessor:
    def __init__(self, code: str):
        self.code = code

        try:
            self.tree = ast.parse(code)
        except SyntaxError as e:
            raise RuntimeError(
                "Invalid Python code detected. "
                "Likely caused by malformed LLM output."
            ) from e

    def extract_functions(self):
        functions = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                segment = ast.get_source_segment(self.code, node)
                if segment:
                    functions.append(segment)
        return functions

    def extract_hotspots(self):
        hotspots = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.For):
                if any(isinstance(n, ast.For) for n in ast.walk(node)):
                    segment = ast.get_source_segment(self.code, node)
                    if segment:
                        hotspots.append(segment)
        return hotspots

    def full_code(self):
        return self.code
