import subprocess
import threading
from typing import Optional

# Global lock to prevent concurrent Ollama calls (VRAM safety)
OLLAMA_LOCK = threading.Lock()

# Absolute path to ollama.exe (Windows-safe)
OLLAMA_PATH = r"C:\Users\nguye\AppData\Local\Programs\Ollama\ollama.exe"


def call_ollama(
    model: str,
    prompt: str,
    temperature: float = 0.0,
    timeout: Optional[int] = None
) -> str:
    """
    Call Ollama model safely on Windows.

    - Uses absolute ollama.exe path
    - Serializes calls via global lock
    - Disables keepalive to free VRAM
    """

    cmd = [
        OLLAMA_PATH,
        "run",
        model,
        "--keepalive", "0",
        prompt
    ]

    with OLLAMA_LOCK:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout
        )

    if result.returncode != 0:
        raise RuntimeError(
            f"Ollama call failed:\n{result.stderr}"
        )

    output = result.stdout.strip()

    if not output:
        raise RuntimeError("Empty response from Ollama")

    return output
