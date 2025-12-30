from llm.ollama_client import call_ollama
from pathlib import Path


class SyntaxValidator:
    def __init__(self):
        self.prompt_template = Path("prompts/syntax.txt").read_text()

    def run(self, code: str) -> str:
        prompt = self.prompt_template.replace("{{code}}", code)
        return call_ollama("qwen2.5-coder:3b", prompt)
