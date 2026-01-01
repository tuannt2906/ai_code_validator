import ast

class CodeParser:
    def __init__(self, code: str):
        self.code = code
        try:
            self.tree = ast.parse(code)
        except SyntaxError:
            self.tree = None # Đánh dấu code lỗi nặng ngay từ đầu

    def is_valid_syntax(self) -> bool:
        return self.tree is not None

    def get_context_blocks(self) -> list[str]:
        """
        Lấy các khối code quan trọng: Hàm, Class, và Async Hàm.
        Bỏ qua các import đơn giản để tiết kiệm token cho LLM.
        """
        if not self.tree:
            return [self.code] # Nếu lỗi syntax, trả về nguyên cục để model sửa

        blocks = []
        for node in self.tree.body:
            # Lấy Function, AsyncFunction, Class
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                segment = ast.get_source_segment(self.code, node)
                if segment:
                    blocks.append(segment)
            # Lấy khối Main (if __name__ == "__main__":)
            elif isinstance(node, ast.If) and self._is_main_block(node):
                segment = ast.get_source_segment(self.code, node)
                if segment:
                    blocks.append(segment)
        
        # Nếu file quá ngắn hoặc không có hàm/class (script đơn), trả về toàn bộ
        if not blocks:
            return [self.code]
        return blocks

    def _is_main_block(self, node: ast.If) -> bool:
        # Check đơn giản cho block __main__
        try:
            return (isinstance(node.test, ast.Compare) and 
                    node.test.left.id == "__name__" and 
                    node.test.comparators[0].s == "__main__")
        except AttributeError:
            return False

    def get_full_code(self) -> str:
        return self.code