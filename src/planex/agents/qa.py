from __future__ import annotations

from dataclasses import dataclass


@dataclass
class QAResult:
    passed: bool
    log: str


class QAAgent:
    """Runs lint + build inside an isolated Docker container.

    Returns QAResult. On failure the orchestrator retries up to MAX_QA_RETRIES
    times; after that it rolls back via git checkout.
    """

    def run(self, project_dir: str) -> QAResult:
        raise NotImplementedError
