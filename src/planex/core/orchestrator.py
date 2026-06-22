from __future__ import annotations

from planex.core.spec import ProjectSpec


class Orchestrator:
    """Runs the agent pipeline for a single Project Spec.

    Phase 0 stub — sequencing logic is implemented in Phase 1.
    Pipeline: Intake → Architect → Frontend + Backend → QA → DevOps.
    """

    MAX_QA_RETRIES = 2

    def __init__(self, spec: ProjectSpec) -> None:
        self.spec = spec

    def run(self) -> None:
        raise NotImplementedError("Pipeline not yet implemented — Phase 1")
