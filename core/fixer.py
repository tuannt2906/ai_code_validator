import json
import re
from config import MODEL_FIXER, PROMPT_DIR, TIMEOUT_CONFIG
from client import OllamaClient

class AutoFixer:
    def __init__(self):
        self.client = OllamaClient()
        self.model = MODEL_FIXER
        self.base_prompt = (PROMPT_DIR / "fix_code.txt").read_text(encoding="utf-8")
        
        self.json_instruction = """
        IMPORTANT: Return ONLY a valid JSON object with the following structure. Do not use Markdown block.
        {
            "code": "THE_FULL_FIXED_CODE_HERE"
        }
        """

    def _parse_json(self, text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        try:
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            
            match = re.search(r"(\{.*\})", text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
                
        except json.JSONDecodeError:
            pass
            
        print("❌ Could not extract JSON from AI response.")
        return {}

    def apply_fix(self, code: str, issues: str) -> str:
        full_prompt = f"{self.base_prompt}\n{self.json_instruction}".replace("{{code}}", code).replace("{{issues}}", issues)
        
        print("🔧 Attempting to fix code (JSON Mode)...")
        response = self.client.generate(self.model, full_prompt, timeout=TIMEOUT_CONFIG["fix"] + 60)
        
        fix_data = self._parse_json(response)
        
        if fix_data and "code" in fix_data:
             return fix_data["code"]
        
        return code