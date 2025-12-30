import subprocess

OLLAMA_PATH = r"C:\Users\nguye\AppData\Local\Programs\Ollama\ollama.exe"

def call_ollama(model: str, prompt: str, temperature=0.0) -> str:
    cmd = [
        OLLAMA_PATH,
        "run",
        model,
        prompt
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return result.stdout.strip()
