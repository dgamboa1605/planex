from __future__ import annotations

from planex.core.spec import ProjectSpec


class IntakeAgent:
    """Gate agent. Receives raw client input, extracts requirements, fills the initial spec.

    LLM role: fast  (llama3.1:8b — lightweight classification/extraction)
    """

    def run(self, raw_input: str, spec: ProjectSpec) -> ProjectSpec:
        raise NotImplementedError
