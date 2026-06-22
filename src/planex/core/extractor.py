from __future__ import annotations

import re

_FENCE_RE = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)


def extract_code_blocks(text: str) -> list[tuple[str, str]]:
    """Return all fenced code blocks as (language, code) pairs."""
    return [(lang or "", code.rstrip()) for lang, code in _FENCE_RE.findall(text)]


def extract_single_file(text: str) -> str:
    """Extract the first non-empty code block from an LLM response.

    Raises ValueError if none found or the block is empty — the caller
    should treat this as a QA failure and retry.
    """
    blocks = extract_code_blocks(text)
    if not blocks:
        raise ValueError("No fenced code block found in LLM response")
    _, code = blocks[0]
    if not code.strip():
        raise ValueError("Empty code block in LLM response")
    return code
