from llm.ollama_client import call_ollama
from pathlib import Path

class CodeFixer:
    def __init__(self, model="qwen2.5-coder:7b"):
        self.prompt_template = Path("prompts/fix_code.txt").read_text()
        self.model = model

    def fix(self, code: str, issues: str) -> str:
        prompt = (
            self.prompt_template
            .replace("{{issues}}", issues)
            .replace("{{code}}", code)
        )
        return call_ollama(self.model, prompt, temperature=0.0)
