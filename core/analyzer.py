import json
import subprocess
import sys
from client import OllamaClient
from config import MODEL_PERF, MODEL_LOGIC, TIMEOUT_CONFIG, PROMPT_DIR
from core.parser import CodeParser

# --- HÀM FORMAT GIÚP HIỂN THỊ ĐẸP ---
def format_ruff_errors(errors: list) -> str:
    """Chuyển đổi JSON của Ruff sang dạng text gạch đầu dòng"""
    if not errors: return "✅ PASS (Clean Code)"
    
    lines = []
    for e in errors:
        # Lấy thông tin lỗi
        row = e.get("location", {}).get("row", "?")
        code = e.get("code", "ERR")
        msg = e.get("message", "Unknown Error")
        
        # Tạo icon mức độ
        icon = "⛔" if code.startswith(("E9", "F")) else "⚠️"
        
        # Format: ⛔ [Line 10] F541: f-string is missing placeholders
        lines.append(f"{icon} [Line {row}] {code}: {msg}")
        
    return "\n".join(lines)

class StaticAnalyzer:
    def run(self, file_path: str) -> list:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "ruff", "check", file_path, "--output-format=json", "--select=E,F,W,B"],
                capture_output=True,
                text=True
            )
            if result.stdout:
                return json.loads(result.stdout)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        return []

class BaseValidator:
    def __init__(self, client: OllamaClient, model: str, prompt_file: str, timeout: int):
        self.client = client
        self.model = model
        self.timeout = timeout
        self.prompt_template = (PROMPT_DIR / prompt_file).read_text(encoding="utf-8")

    def validate(self, code_snippet: str) -> str:
        prompt = self.prompt_template.replace("{{code}}", code_snippet)
        return self.client.generate(self.model, prompt, timeout=self.timeout)

class PerfAudit(BaseValidator):
    def __init__(self, client):
        super().__init__(client, MODEL_PERF, "performance.txt", TIMEOUT_CONFIG["performance"])

class LogicAudit(BaseValidator):
    def __init__(self, client):
        super().__init__(client, MODEL_LOGIC, "logic.txt", TIMEOUT_CONFIG["logic"])

    def validate(self, code_blocks: list[str]) -> str:
        joined_code = "\n\n".join(code_blocks)[:6000]
        return super().validate(joined_code)

class ValidationOrchestrator:
    def __init__(self):
        self.client = OllamaClient()
        self.static_checker = StaticAnalyzer()
        self.perf_checker = PerfAudit(self.client)
        self.logic_checker = LogicAudit(self.client)

    def run(self, code: str, file_path: str) -> dict:
        parser = CodeParser(code)
        
        # 1. STATIC ANALYSIS
        static_errors = self.static_checker.run(file_path)
        formatted_syntax = format_ruff_errors(static_errors)
        
        # Kiểm tra lỗi nghiêm trọng
        critical_static = [e for e in static_errors if e.get("code", "").startswith(("E9", "F"))]
        
        if critical_static:
            return {
                "syntax": formatted_syntax, # Đã format đẹp
                "logic": "🚫 Skipped due to critical syntax errors.",
                "performance": "🚫 Skipped due to critical syntax errors.",
                "verdict": "FAIL"
            }

        # 2. Logic Audit
        print("🧠 Checking Logic (DeepSeek-R1)...")
        logic_report = self.logic_checker.validate(parser.get_context_blocks())
        
        # 3. Performance Audit
        print("🚀 Checking Performance...")
        perf_report = self.perf_checker.validate(parser.get_full_code())

        return {
            "syntax": formatted_syntax,
            "logic": logic_report,
            "performance": perf_report,
            "verdict": "PASS" if "CRITICAL" not in logic_report else "FAIL"
        }