import re


def strip_code_fences(text: str) -> str:
    """
    Remove markdown code fences from LLM output.
    Handles:
    ```python
    code
    ```
    or
    ```
    code
    ```
    """
    if not text:
        return text

    text = text.strip()

    # Remove opening fence ``` or ```python
    text = re.sub(r"^```[a-zA-Z]*\n", "", text)

    # Remove closing fence ```
    text = re.sub(r"\n```$", "", text)

    return text.strip()
