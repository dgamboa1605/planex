"""Tests for Orchestrator.run().

FrontendAgent.run() is mocked so no Ollama instance is needed.
The template clone uses the real templates/landing/ tree (node_modules excluded).
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from planex.core.orchestrator import Orchestrator
from planex.core.spec import ProjectSpec

# ── Paths ────────────────────────────────────────────────────────────────────

_PROJECT_ROOT = Path(__file__).parents[1]
EXAMPLE_SPEC_PATH = _PROJECT_ROOT / "docs" / "example.acme-landing.spec.json"
TEMPLATE_DIR = _PROJECT_ROOT / "templates" / "landing"

# Minimal valid site.json returned by the mocked FrontendAgent
MOCK_SITE_JSON: dict = {
    "theme": {"primaryColor": "#1D4ED8"},
    "seo": {"title": "Acme · Test", "description": "Test description."},
    "navbar": {"logo": "Acme Consulting", "links": [{"label": "Contacto", "href": "#contacto"}]},
    "footer": {
        "copyright": "© 2024 Acme Consulting. Todos los derechos reservados.",
        "links": [{"label": "Privacidad", "href": "/privacidad"}],
    },
    "sections": [
        {
            "type": "hero",
            "data": {
                "title": "Transforma tu empresa",
                "subtitle": "Expertos en optimización.",
                "cta": {"label": "Contáctanos", "href": "#contacto"},
            },
        }
    ],
}


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def approved_spec() -> ProjectSpec:
    """Load the example spec and override status to 'approved'."""
    spec = ProjectSpec.from_file(EXAMPLE_SPEC_PATH)
    spec.data["meta"]["status"] = "approved"
    return spec


@pytest.fixture
def mock_frontend():
    """Patch FrontendAgent so no LLM call is made."""
    with patch("planex.core.orchestrator.FrontendAgent") as MockAgent:
        MockAgent.return_value.run.return_value = MOCK_SITE_JSON
        yield MockAgent


# ── Tests ─────────────────────────────────────────────────────────────────────


class TestOrchestratorRun:
    def _orch(self, spec, tmp_path) -> Orchestrator:
        return Orchestrator(spec, template_dir=TEMPLATE_DIR, output_root=tmp_path)

    # ── Output directory ──────────────────────────────────────────────────────

    def test_creates_output_directory(self, approved_spec, tmp_path, mock_frontend):
        output_dir = self._orch(approved_spec, tmp_path).run()
        assert output_dir.is_dir()

    def test_output_directory_name_is_slug(self, approved_spec, tmp_path, mock_frontend):
        output_dir = self._orch(approved_spec, tmp_path).run()
        assert output_dir.name == "acme-landing"

    def test_run_returns_path(self, approved_spec, tmp_path, mock_frontend):
        result = self._orch(approved_spec, tmp_path).run()
        assert isinstance(result, Path)

    # ── Template clone ────────────────────────────────────────────────────────

    def test_clones_package_json(self, approved_spec, tmp_path, mock_frontend):
        output_dir = self._orch(approved_spec, tmp_path).run()
        assert (output_dir / "package.json").exists()

    def test_clones_app_layout(self, approved_spec, tmp_path, mock_frontend):
        output_dir = self._orch(approved_spec, tmp_path).run()
        assert (output_dir / "app" / "layout.tsx").exists()

    def test_node_modules_not_copied(self, approved_spec, tmp_path, mock_frontend):
        output_dir = self._orch(approved_spec, tmp_path).run()
        assert not (output_dir / "node_modules").exists()

    def test_dot_next_not_copied(self, approved_spec, tmp_path, mock_frontend):
        output_dir = self._orch(approved_spec, tmp_path).run()
        assert not (output_dir / ".next").exists()

    # ── site.json ─────────────────────────────────────────────────────────────

    def test_site_json_exists(self, approved_spec, tmp_path, mock_frontend):
        output_dir = self._orch(approved_spec, tmp_path).run()
        assert (output_dir / "content" / "site.json").exists()

    def test_site_json_is_valid_json(self, approved_spec, tmp_path, mock_frontend):
        output_dir = self._orch(approved_spec, tmp_path).run()
        raw = (output_dir / "content" / "site.json").read_text(encoding="utf-8")
        parsed = json.loads(raw)
        assert isinstance(parsed, dict)

    def test_site_json_has_all_top_level_keys(self, approved_spec, tmp_path, mock_frontend):
        output_dir = self._orch(approved_spec, tmp_path).run()
        data = json.loads((output_dir / "content" / "site.json").read_text())
        assert set(data.keys()) == {"theme", "seo", "navbar", "footer", "sections"}

    def test_site_json_content_matches_frontend_agent_output(
        self, approved_spec, tmp_path, mock_frontend
    ):
        output_dir = self._orch(approved_spec, tmp_path).run()
        data = json.loads((output_dir / "content" / "site.json").read_text())
        assert data["theme"]["primaryColor"] == MOCK_SITE_JSON["theme"]["primaryColor"]
        assert data["navbar"]["logo"] == MOCK_SITE_JSON["navbar"]["logo"]

    def test_idempotent_second_run_succeeds(self, approved_spec, tmp_path, mock_frontend):
        """Running twice does not raise (dirs_exist_ok=True)."""
        orch = self._orch(approved_spec, tmp_path)
        orch.run()
        orch.run()  # should not raise

    # ── Error cases ───────────────────────────────────────────────────────────

    def test_raises_value_error_if_spec_not_approved(self, tmp_path):
        spec = ProjectSpec.from_file(EXAMPLE_SPEC_PATH)  # status: draft
        orch = Orchestrator(spec, template_dir=TEMPLATE_DIR, output_root=tmp_path)
        with pytest.raises(ValueError, match="approved"):
            orch.run()

    def test_raises_file_not_found_if_template_missing(self, approved_spec, tmp_path, mock_frontend):
        orch = Orchestrator(
            approved_spec,
            template_dir=Path("/nonexistent/template"),
            output_root=tmp_path,
        )
        with pytest.raises(FileNotFoundError):
            orch.run()

    def test_frontend_agent_called_with_spec(self, approved_spec, tmp_path, mock_frontend):
        self._orch(approved_spec, tmp_path).run()
        mock_frontend.return_value.run.assert_called_once_with(approved_spec)
