from llm.ollama_client import call_ollama
from pathlib import Path
from pipeline.code_sanitizer import strip_code_fences


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

        raw_output = call_ollama(self.model, prompt, temperature=0.0)

        clean_code = strip_code_fences(raw_output)

        return clean_code
