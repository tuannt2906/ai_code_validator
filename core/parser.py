# core/parser.py
import ast

class CodeParser:
    def __init__(self, code: str):
        self.code = code
        try:
            self.tree = ast.parse(code)
        except SyntaxError:
            self.tree = None

    def is_valid_syntax(self) -> bool:
        return self.tree is not None

    def get_full_code(self) -> str:
        return self.code

    def get_context_blocks(self) -> list[str]:
        if not self.tree:
            return [self.code]

        blocks = []
        for node in self.tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                segment = ast.get_source_segment(self.code, node)
                if segment: blocks.append(segment)
            elif isinstance(node, ast.If) and self._is_main_block(node):
                segment = ast.get_source_segment(self.code, node)
                if segment: blocks.append(segment)
        
        if not blocks: return [self.code]
        return blocks

    def _is_main_block(self, node: ast.If) -> bool:
        try:
            return (isinstance(node.test, ast.Compare) and 
                    node.test.left.id == "__name__" and 
                    node.test.comparators[0].s == "__main__")
        except AttributeError:
            return False

    # --- HÀM MỚI: TẠO SKELETON CODE ---
    def get_skeleton(self) -> str:
        """
        Trả về khung sườn code: Giữ lại Class/Function definitions nhưng ẩn nội dung.
        Giúp AI hiểu ngữ cảnh toàn cục (Global Context) khi check project lớn.
        """
        if not self.tree: return self.code
        
        lines = self.code.splitlines()
        skeleton = []
        
        for node in self.tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # Lấy dòng definition (ví dụ: def my_func(a, b):)
                start_line = node.lineno - 1
                # Chỉ lấy dòng đầu tiên của definition
                skeleton.append(lines[start_line])
                skeleton.append("    # ... implementation hidden ...")
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                # Giữ nguyên import
                skeleton.append(ast.get_source_segment(self.code, node))
            else:
                # Các biến global
                skeleton.append(ast.get_source_segment(self.code, node))
                
        return "\n".join(filter(None, skeleton))