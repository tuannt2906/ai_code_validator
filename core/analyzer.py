from pathlib import Path
from config import MODEL_SYNTAX, MODEL_PERF, MODEL_LOGIC, PROMPT_DIR, TIMEOUT_CONFIG
from client import OllamaClient
from core.parser import CodeParser

class BaseValidator:
    def __init__(self, client: OllamaClient, model: str, prompt_file: str, timeout: int):
        self.client = client
        self.model = model
        self.timeout = timeout
        self.prompt_template = (PROMPT_DIR / prompt_file).read_text(encoding="utf-8")

    def validate(self, code_snippet: str) -> str:
        prompt = self.prompt_template.replace("{{code}}", code_snippet)
        return self.client.generate(self.model, prompt, timeout=self.timeout)

class SyntaxAudit(BaseValidator):
    def __init__(self, client):
        super().__init__(client, MODEL_SYNTAX, "syntax.txt", TIMEOUT_CONFIG["syntax"])

class PerfAudit(BaseValidator):
    def __init__(self, client):
        super().__init__(client, MODEL_PERF, "performance.txt", TIMEOUT_CONFIG["performance"])

class LogicAudit(BaseValidator):
    def __init__(self, client):
        super().__init__(client, MODEL_LOGIC, "logic.txt", TIMEOUT_CONFIG["logic"])

    def validate(self, code_blocks: list[str]) -> str:
        # Logic cần ghép các khối code lại nhưng không quá dài
        # DeepSeek-R1 cần thấy ngữ cảnh liên kết
        joined_code = "\n\n".join(code_blocks)[:6000] # Cắt giới hạn Token an toàn cho 6GB VRAM
        return super().validate(joined_code)

class ValidationOrchestrator:
    def __init__(self):
        self.client = OllamaClient()
        self.syntax_checker = SyntaxAudit(self.client)
        self.perf_checker = PerfAudit(self.client)
        self.logic_checker = LogicAudit(self.client)

    def run(self, code: str) -> dict:
        parser = CodeParser(code)
        
        # Bước 1: Syntax Check (Nhanh nhất)
        print("🔍 Checking Syntax...")
        # Nếu parser của Python báo lỗi syntax thì báo luôn, đỡ tốn tiền AI
        if not parser.is_valid_syntax():
            return {"syntax": "[HIGH] SyntaxError detected by AST parsing.", "verdict": "FAIL"}

        syntax_report = self.syntax_checker.validate(parser.get_full_code())
        
        # Nếu Syntax lỗi nặng, dừng luôn để tiết kiệm thời gian
        if "HIGH" in syntax_report or "SyntaxError" in syntax_report:
             return {"syntax": syntax_report, "verdict": "FAIL"}

        # Bước 2: Logic & Performance (Chạy tuần tự cho máy 6GB VRAM)
        print("🧠 Checking Logic (DeepSeek-R1)...")
        logic_report = self.logic_checker.validate(parser.get_context_blocks())
        
        print("🚀 Checking Performance...")
        perf_report = self.perf_checker.validate(parser.get_full_code())

        return {
            "syntax": syntax_report,
            "logic": logic_report,
            "performance": perf_report,
            "verdict": "PASS" if "CRITICAL" not in logic_report else "FAIL"
        }