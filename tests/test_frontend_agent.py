"""Tests for FrontendAgent.

LLM calls are mocked so no Ollama instance is needed.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from planex.agents.frontend import (
    DEFAULT_PRIMARY_COLOR,
    MAX_RETRIES,
    FrontendAgent,
    _FALLBACKS,
    _parse_llm_json,
    _validate_section,
)
from planex.core.spec import ProjectSpec

EXAMPLE_SPEC_PATH = Path(__file__).parents[1] / "docs" / "example.acme-landing.spec.json"

# ── LLM response fixtures ────────────────────────────────────────────────────
# Minimal valid JSON for each section present in example.acme-landing.spec.json:
# sections: hero, servicios, casos-de-exito, testimonios, cta-contacto

_F = {
    "seo": '{"title": "Acme · Consultoría para PYMEs", "description": "Optimizamos procesos."}',
    "hero": (
        '{"title": "Transforma tu empresa", "subtitle": "Expertos en optimización",'
        ' "cta": {"label": "Contáctanos", "href": "#contacto"}}'
    ),
    "servicios": (
        '{"headline": "Servicios", "items": [{"icon": "🔍", "title": "Diagnóstico",'
        ' "description": "Análisis profundo."}]}'
    ),
    "casos-de-exito": (
        '{"headline": "Casos", "items": [{"name": "Cliente A", "description": "Mejora del 20%."}]}'
    ),
    "testimonios": (
        '{"headline": "Testimonios", "items": [{"quote": "Excelente trabajo.",'
        ' "author": "Ana García", "role": "CEO"}]}'
    ),
    "cta-contacto": (
        '{"headline": "Contacto", "subtext": "Escríbenos.",'
        ' "buttonLabel": "Enviar", "buttonHref": "#contacto"}'
    ),
}

# Ordered responses for the example spec: SEO + 5 sections
_HAPPY_PATH_RESPONSES = [
    _F["seo"],
    _F["hero"],
    _F["servicios"],
    _F["casos-de-exito"],
    _F["testimonios"],
    _F["cta-contacto"],
]


def _seq_mock(responses: list[str]):
    """Side-effect callable that yields responses in order."""
    it = iter(responses)
    def _mock(prompt: str, role: str = "coder", **kwargs) -> str:  # noqa: ARG001
        return next(it)
    return _mock


# ── Shared fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def example_spec() -> ProjectSpec:
    return ProjectSpec.from_file(EXAMPLE_SPEC_PATH)


@pytest.fixture
def happy_mock():
    with patch("planex.agents.frontend.complete", side_effect=_seq_mock(_HAPPY_PATH_RESPONSES)):
        yield


# ── Unit tests: _parse_llm_json ──────────────────────────────────────────────

class TestParseLLMJson:
    def test_raw_json(self):
        assert _parse_llm_json('{"key": "val"}') == {"key": "val"}

    def test_json_in_backtick_fence(self):
        result = _parse_llm_json("```json\n{\"a\": 1}\n```")
        assert result == {"a": 1}

    def test_json_embedded_in_prose(self):
        result = _parse_llm_json('Here is the data:\n{"x": 2}\nDone.')
        assert result == {"x": 2}

    def test_raises_on_no_json(self):
        with pytest.raises(ValueError):
            _parse_llm_json("Sorry, I cannot help with that.")

    def test_raises_on_unbalanced(self):
        with pytest.raises(ValueError):
            _parse_llm_json("{no closing brace")


# ── Unit tests: _validate_section ───────────────────────────────────────────

class TestValidateSection:
    def test_hero_valid(self):
        _validate_section("hero", {
            "title": "T", "subtitle": "S",
            "cta": {"label": "L", "href": "#contacto"},
        })

    def test_hero_missing_cta(self):
        with pytest.raises(ValueError, match="cta"):
            _validate_section("hero", {"title": "T", "subtitle": "S"})

    def test_hero_missing_cta_label(self):
        with pytest.raises(ValueError, match="label"):
            _validate_section("hero", {
                "title": "T", "subtitle": "S", "cta": {"href": "#c"},
            })

    def test_items_section_valid(self):
        _validate_section("servicios", {"items": [{"title": "X"}]})

    def test_items_section_empty_list(self):
        with pytest.raises(ValueError, match="non-empty"):
            _validate_section("servicios", {"items": []})

    def test_items_section_missing_items(self):
        with pytest.raises(ValueError, match="items"):
            _validate_section("testimonios", {})

    def test_cta_contacto_passes_without_show_form(self):
        # showForm is injected by Python, not validated here
        _validate_section("cta-contacto", {"headline": "H"})

    def test_rejects_non_dict(self):
        with pytest.raises(ValueError, match="dict"):
            _validate_section("hero", ["list", "not", "dict"])


# ── Integration tests: FrontendAgent.run() happy path ───────────────────────

class TestFrontendAgentHappyPath:
    def test_returns_all_top_level_keys(self, example_spec, happy_mock):
        result = FrontendAgent().run(example_spec)
        assert set(result.keys()) == {"theme", "seo", "navbar", "footer", "sections"}

    def test_theme_primary_color_from_spec(self, example_spec, happy_mock):
        result = FrontendAgent().run(example_spec)
        assert result["theme"]["primaryColor"] == "#1D4ED8"

    def test_seo_has_title_and_description(self, example_spec, happy_mock):
        result = FrontendAgent().run(example_spec)
        assert "title" in result["seo"]
        assert "description" in result["seo"]
        # LLM mock returned Acme in title
        assert "Acme" in result["seo"]["title"]

    def test_navbar_logo_equals_project_name(self, example_spec, happy_mock):
        result = FrontendAgent().run(example_spec)
        assert result["navbar"]["logo"] == "Acme Consulting"

    def test_navbar_links_only_navigable_sections(self, example_spec, happy_mock):
        result = FrontendAgent().run(example_spec)
        hrefs = {link["href"] for link in result["navbar"]["links"]}
        assert "#servicios" in hrefs
        assert "#contacto" in hrefs
        # hero is not navigable
        assert "#hero" not in hrefs
        assert all(href.startswith("#") for href in hrefs)

    def test_footer_copyright_has_year_and_name(self, example_spec, happy_mock):
        result = FrontendAgent().run(example_spec)
        assert "Acme Consulting" in result["footer"]["copyright"]
        assert str(date.today().year) in result["footer"]["copyright"]

    def test_footer_has_legal_links(self, example_spec, happy_mock):
        result = FrontendAgent().run(example_spec)
        hrefs = [link["href"] for link in result["footer"]["links"]]
        assert "/privacidad" in hrefs
        assert "/terminos" in hrefs

    def test_sections_count_matches_spec(self, example_spec, happy_mock):
        result = FrontendAgent().run(example_spec)
        expected = example_spec.data["pages"][0]["sections"]
        assert len(result["sections"]) == len(expected)

    def test_sections_order_matches_spec(self, example_spec, happy_mock):
        result = FrontendAgent().run(example_spec)
        expected = example_spec.data["pages"][0]["sections"]
        for section, expected_type in zip(result["sections"], expected):
            assert section["type"] == expected_type

    def test_each_section_has_type_and_data_dict(self, example_spec, happy_mock):
        result = FrontendAgent().run(example_spec)
        for section in result["sections"]:
            assert "type" in section
            assert isinstance(section["data"], dict)
            assert len(section["data"]) > 0

    def test_contact_form_true_sets_show_form_true(self, example_spec, happy_mock):
        assert example_spec.data.get("contact_form") is True
        result = FrontendAgent().run(example_spec)
        cta = next(s for s in result["sections"] if s["type"] == "cta-contacto")
        assert cta["data"]["showForm"] is True


# ── DoD #3: contact_form:false → showForm:false ──────────────────────────────

class TestContactFormFalse:
    def _make_spec(self, contact_form: bool) -> ProjectSpec:
        return ProjectSpec({
            "meta": {"status": "draft"},
            "project": {"name": "Test Co", "type": "landing"},
            "business": {"industry": "Tech", "target_audience": "Devs"},
            "pages": [{"name": "home", "sections": ["cta-contacto"]}],
            "contact_form": contact_form,
        })

    def test_false_overrides_llm_true(self):
        # LLM returns showForm:true but spec says false → Python wins
        spec = self._make_spec(contact_form=False)
        responses = [
            '{"title": "T", "description": "D"}',  # SEO
            '{"showForm": true, "headline": "H", "subtext": "S",'
            ' "buttonLabel": "Go", "buttonHref": "#contacto"}',  # cta
        ]
        with patch("planex.agents.frontend.complete", side_effect=_seq_mock(responses)):
            result = FrontendAgent().run(spec)
        cta = next(s for s in result["sections"] if s["type"] == "cta-contacto")
        assert cta["data"]["showForm"] is False

    def test_true_is_preserved(self):
        spec = self._make_spec(contact_form=True)
        responses = [
            '{"title": "T", "description": "D"}',
            '{"headline": "H", "subtext": "S", "buttonLabel": "Go", "buttonHref": "#contacto"}',
        ]
        with patch("planex.agents.frontend.complete", side_effect=_seq_mock(responses)):
            result = FrontendAgent().run(spec)
        cta = next(s for s in result["sections"] if s["type"] == "cta-contacto")
        assert cta["data"]["showForm"] is True

    def test_absent_defaults_to_false(self):
        # contact_form key missing from spec
        spec = ProjectSpec({
            "meta": {"status": "draft"},
            "project": {"name": "X", "type": "landing"},
            "business": {"industry": "A", "target_audience": "B"},
            "pages": [{"name": "home", "sections": ["cta-contacto"]}],
        })
        responses = [
            '{"title": "T", "description": "D"}',
            '{"headline": "H", "buttonLabel": "Go", "buttonHref": "#contacto"}',
        ]
        with patch("planex.agents.frontend.complete", side_effect=_seq_mock(responses)):
            result = FrontendAgent().run(spec)
        cta = next(s for s in result["sections"] if s["type"] == "cta-contacto")
        assert cta["data"]["showForm"] is False


# ── DoD #4: fallback on repeated failure ─────────────────────────────────────

class TestFallback:
    def test_hero_falls_back_after_max_retries(self, example_spec):
        """Hero fails MAX_RETRIES+1 times → fallback data returned, no exception."""
        invalid = "not valid json at all"
        responses = (
            [_F["seo"]]
            + [invalid] * (MAX_RETRIES + 1)   # hero: initial + retries
            + [_F["servicios"], _F["casos-de-exito"], _F["testimonios"], _F["cta-contacto"]]
        )
        with patch("planex.agents.frontend.complete", side_effect=_seq_mock(responses)):
            result = FrontendAgent().run(example_spec)
        hero = next(s for s in result["sections"] if s["type"] == "hero")
        assert "title" in hero["data"]
        assert hero["data"] == _FALLBACKS["hero"]

    def test_all_sections_present_when_every_call_fails(self, example_spec):
        """Even if every LLM call fails, all sections are in the output."""
        with patch("planex.agents.frontend.complete", return_value="not json"):
            result = FrontendAgent().run(example_spec)
        expected_types = example_spec.data["pages"][0]["sections"]
        result_types = [s["type"] for s in result["sections"]]
        assert result_types == expected_types

    def test_fallback_sections_are_non_empty_dicts(self, example_spec):
        with patch("planex.agents.frontend.complete", return_value="not json"):
            result = FrontendAgent().run(example_spec)
        for section in result["sections"]:
            assert isinstance(section["data"], dict)
            assert len(section["data"]) > 0

    def test_fallback_cta_respects_contact_form_flag(self, example_spec):
        """Fallback cta-contacto still picks up contact_form from spec."""
        with patch("planex.agents.frontend.complete", return_value="not json"):
            result = FrontendAgent().run(example_spec)
        cta = next(s for s in result["sections"] if s["type"] == "cta-contacto")
        assert cta["data"]["showForm"] is True  # example spec has contact_form:true

    def test_retry_prompt_includes_previous_error(self, example_spec):
        """On retry, the prompt contains the previous error message."""
        captured_prompts: list[str] = []

        def capturing_mock(prompt: str, role: str = "coder", **kwargs) -> str:  # noqa: ARG001
            captured_prompts.append(prompt)
            if len(captured_prompts) == 1:
                return _F["seo"]
            if len(captured_prompts) == 2:
                return "invalid json"
            return _F["hero"]  # succeeds on third call (second section attempt)

        # Only test hero (first section) to keep the mock simple
        spec = ProjectSpec({
            "meta": {"status": "draft"},
            "project": {"name": "X", "type": "landing"},
            "business": {"industry": "A", "target_audience": "B"},
            "pages": [{"name": "home", "sections": ["hero"]}],
        })
        with patch("planex.agents.frontend.complete", side_effect=capturing_mock):
            FrontendAgent().run(spec)

        # The retry prompt (3rd call = index 2) should mention the previous error
        retry_prompt = captured_prompts[2]
        assert "Error del intento anterior" in retry_prompt


# ── DoD #2: branding changes propagate ───────────────────────────────────────

class TestBrandingPropagation:
    def _run_with_color(self, color: str | None) -> dict:
        data: dict = {
            "meta": {"status": "draft"},
            "project": {"name": "X", "type": "landing"},
            "business": {"industry": "A", "target_audience": "B"},
            "pages": [{"name": "home", "sections": ["hero"]}],
        }
        if color is not None:
            data["branding"] = {"primary_color": color}
        spec = ProjectSpec(data)
        responses = [
            '{"title": "T", "description": "D"}',
            '{"title": "H", "subtitle": "S", "cta": {"label": "L", "href": "#contacto"}}',
        ]
        with patch("planex.agents.frontend.complete", side_effect=_seq_mock(responses)):
            return FrontendAgent().run(spec)

    def test_custom_color_used(self):
        result = self._run_with_color("#FF0000")
        assert result["theme"]["primaryColor"] == "#FF0000"

    def test_no_branding_falls_back_to_default(self):
        result = self._run_with_color(None)
        assert result["theme"]["primaryColor"] == DEFAULT_PRIMARY_COLOR

    def test_business_context_changes_seo(self):
        """Different industry → LLM is called with different context (captured in prompt)."""
        prompts: list[str] = []

        def capture(prompt: str, role: str = "coder", **_) -> str:  # noqa: ARG001
            prompts.append(prompt)
            if not prompts or role == "fast":
                return '{"title": "T", "description": "D"}'
            return '{"title": "H", "subtitle": "S", "cta": {"label": "L", "href": "#contacto"}}'

        spec = ProjectSpec({
            "meta": {"status": "draft"},
            "project": {"name": "Biotech Co", "type": "landing"},
            "business": {"industry": "Biotecnología", "target_audience": "Laboratorios"},
            "pages": [{"name": "home", "sections": ["hero"]}],
        })
        with patch("planex.agents.frontend.complete", side_effect=capture):
            FrontendAgent().run(spec)

        seo_prompt = prompts[0]
        assert "Biotecnología" in seo_prompt
        assert "Biotech Co" in seo_prompt
