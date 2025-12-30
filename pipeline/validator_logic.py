from llm.ollama_client import call_ollama
from pathlib import Path


class LogicValidator:
    def __init__(self):
        self.prompt_template = Path("prompts/logic.txt").read_text()

    def run(self, code_blocks: list[str]) -> str:
        joined = "\n\n".join(code_blocks)
        prompt = self.prompt_template.replace("{{code}}", joined)
        return call_ollama("deepseek-r1:7b", prompt)
