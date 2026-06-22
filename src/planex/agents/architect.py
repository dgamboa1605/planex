from __future__ import annotations

from planex.core.spec import ProjectSpec


class ArchitectAgent:
    """Designs the technical structure: file map, components, endpoints, tables.
    Generates the molecular task backlog for the coder agents.

    LLM role: reasoner  (qwen3:14b — planning and reasoning)
    """

    def run(self, spec: ProjectSpec) -> ProjectSpec:
        raise NotImplementedError
