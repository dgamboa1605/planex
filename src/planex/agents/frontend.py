from __future__ import annotations

from planex.core.spec import ProjectSpec


class FrontendAgent:
    """Generates UI code (Next.js + Tailwind) one file per interaction.

    LLM role: coder  (qwen2.5-coder:14b — code generation)
    """

    def run(self, spec: ProjectSpec, file_path: str) -> str:
        """Return the generated source code for a single file."""
        raise NotImplementedError
