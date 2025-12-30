import ast


class CodePreprocessor:
    def __init__(self, code: str):
        self.code = code
        self.tree = ast.parse(code)

    def extract_functions(self):
        functions = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(ast.get_source_segment(self.code, node))
        return functions

    def extract_hotspots(self):
        """
        Heuristic:
        - nested loops
        - pandas apply
        """
        hotspots = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.For):
                if any(isinstance(n, ast.For) for n in ast.walk(node)):
                    hotspots.append(ast.get_source_segment(self.code, node))
        return hotspots

    def full_code(self):
        return self.code
