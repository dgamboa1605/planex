"""Orchestrator — Phase 1 MVP pipeline.

Steps:
  1. Assert spec is approved.
  2. Clone templates/landing/ → output/<slug>/ (excludes node_modules, .next).
  3. FrontendAgent: generate content dict from spec.
  4. Write content/site.json into the cloned directory.
  5. Return the output Path.
"""
from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path

from planex.agents.frontend import FrontendAgent
from planex.core.spec import ProjectSpec

log = logging.getLogger(__name__)

# Default template: resolved relative to this file (works in dev; override via constructor).
_TEMPLATE_LANDING = Path(__file__).parents[3] / "templates" / "landing"

# Directories and patterns excluded from the template clone.
_IGNORE = shutil.ignore_patterns("node_modules", ".next", "*.tsbuildinfo", ".env")


class Orchestrator:
    """Runs the MVP pipeline for a single Project Spec.

    Phase 1: Spec → clone template → FrontendAgent → write site.json.
    Future phases add Architect, Backend, QA, DevOps agents here.
    """

    MAX_QA_RETRIES = 2

    def __init__(
        self,
        spec: ProjectSpec,
        *,
        template_dir: Path | None = None,
        output_root: Path | None = None,
    ) -> None:
        self.spec = spec
        self.template_dir = template_dir or _TEMPLATE_LANDING
        self.output_root = output_root or Path.cwd() / "output"

    # ── Public API ────────────────────────────────────────────────────────────

    def run(self) -> Path:
        """Execute the pipeline; return the absolute output directory path."""
        self._assert_approved()
        output_dir = self._clone_template()
        site_json = self._generate_content()
        self._write_site_json(output_dir, site_json)
        log.info("Pipeline complete → %s", output_dir)
        return output_dir

    # ── Steps ─────────────────────────────────────────────────────────────────

    def _assert_approved(self) -> None:
        if not self.spec.is_approved():
            raise ValueError(
                f"Spec '{self.spec.slug}' must be approved before running "
                f"(current status: '{self.spec.status}'). "
                "Set meta.status to 'approved' in the spec file."
            )

    def _clone_template(self) -> Path:
        """Copy the template tree to output/<slug>/, skipping runtime artifacts."""
        if not self.template_dir.exists():
            raise FileNotFoundError(
                f"Landing template not found: {self.template_dir}\n"
                "Run 'npm install' inside templates/landing/ or set template_dir."
            )
        output_dir = self.output_root / self.spec.slug
        log.info("Cloning template %s → %s", self.template_dir, output_dir)
        shutil.copytree(
            self.template_dir,
            output_dir,
            ignore=_IGNORE,
            dirs_exist_ok=True,
        )
        return output_dir

    def _generate_content(self) -> dict:
        """Run FrontendAgent to produce the site.json dict."""
        log.info("FrontendAgent: generating content for '%s'", self.spec.slug)
        return FrontendAgent().run(self.spec)

    def _write_site_json(self, output_dir: Path, content: dict) -> None:
        """Serialize content dict to <output>/content/site.json."""
        dest = output_dir / "content" / "site.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        log.info("Written: %s", dest)
