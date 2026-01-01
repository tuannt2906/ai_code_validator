import os
from pathlib import Path

MODEL_SYNTAX = "qwen2.5-coder:3b"
MODEL_PERF = "qwen2.5-coder:7b"
MODEL_LOGIC = "deepseek-r1:7b"
MODEL_FIXER = "qwen2.5-coder:7b"

OLLAMA_API_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434/api/generate")

BASE_DIR = Path(__file__).parent
PROMPT_DIR = BASE_DIR / "prompts"

TIMEOUT_CONFIG = {
    "syntax": 30,
    "performance": 120,
    "logic": 480,
    "fix": 240
}