from config import MODEL_FIXER, PROMPT_DIR, TIMEOUT_CONFIG
from client import OllamaClient
import re

class AutoFixer:
    def __init__(self):
        self.client = OllamaClient()
        self.prompt = (PROMPT_DIR / "fix_code.txt").read_text(encoding="utf-8")

    def apply_fix(self, code: str, issues: str) -> str:
        full_prompt = self.prompt.replace("{{code}}", code).replace("{{issues}}", issues)
        print("🔧 Attempting to fix code...")
        raw_output = self.client.generate(MODEL_FIXER, full_prompt, timeout=TIMEOUT_CONFIG["fix"])
        return self._clean_markdown(raw_output)

    def _clean_markdown(self, text: str) -> str:
        # Regex mạnh mẽ hơn để bắt block code
        pattern = r"```(?:python)?\n(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip() # Fallback nếu model quên markdown