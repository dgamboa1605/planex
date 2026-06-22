from __future__ import annotations

from planex.core.spec import ProjectSpec


class DevOpsAgent:
    """Handles git init, automatic commits, Dockerfile/docker-compose, and deploy scripts.

    Only runs after explicit human approval (Human-in-the-Loop gate).
    """

    def run(self, spec: ProjectSpec, project_dir: str) -> None:
        raise NotImplementedError
