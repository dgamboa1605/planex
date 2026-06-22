"""Frontend Agent — converts a ProjectSpec into content/site.json.

Strategy: one LLM call per section (atomic context modularization, D-FA spec).
Python assembles the final dict. navbar/footer/theme are deterministic (no LLM).
"""
from __future__ import annotations

import json
import logging
from collections.abc import Callable
from datetime import date
from typing import Any

from planex.core.extractor import extract_code_blocks
from planex.core.spec import ProjectSpec
from planex.llm.config import complete

log = logging.getLogger(__name__)

DEFAULT_PRIMARY_COLOR = "#1D4ED8"
MAX_RETRIES = 2  # aligned with Orchestrator.MAX_QA_RETRIES

# ── Navbar rules (D-FA-01) ──────────────────────────────────────────────────
# Maps navigable section keys → (display label, anchor href).
# hero/features/stats are intentionally absent — they get no nav link.
_NAV_LINKS: dict[str, tuple[str, str]] = {
    "servicios":      ("Servicios",      "#servicios"),
    "casos-de-exito": ("Casos de éxito", "#casos-de-exito"),
    "testimonios":    ("Testimonios",    "#testimonios"),
    "cta-contacto":   ("Contacto",       "#contacto"),
}

# ── Prompt templates ────────────────────────────────────────────────────────
# One per section type. Each asks for ONLY the `data` object in JSON.
# Placeholders filled from _build_ctx(): name, industry, audience, goals, tone.
# Curly braces that appear literally in the JSON example are doubled {{ }}.
_PROMPTS: dict[str, str] = {
    "hero": (
        "Genera el contenido para la sección HERO de una landing page.\n"
        "Empresa: {name} | Industria: {industry} | Tono: {tone}\n"
        "Público: {audience}\n"
        "Objetivos: {goals}\n\n"
        "Responde SOLO con un objeto JSON (sin texto adicional, sin markdown):\n"
        '{{"title": "...", "subtitle": "...", "cta": {{"label": "...", "href": "#contacto"}}}}\n\n'
        "title: 8-12 palabras impactantes en español. subtitle: 1-2 frases de valor. "
        "cta.label: verbo de acción (ej. 'Habla con nosotros')."
    ),
    "servicios": (
        "Genera el contenido para la sección SERVICIOS de una landing page.\n"
        "Empresa: {name} | Industria: {industry} | Tono: {tone}\n"
        "Público: {audience}\n\n"
        "Responde SOLO con un objeto JSON (sin texto adicional, sin markdown):\n"
        '{{"headline": "...", "items": [{{"icon": "emoji", "title": "...", "description": "..."}}]}}\n\n'
        "Exactamente 3-4 servicios relevantes para la industria. "
        "icon: 1 emoji. title: 2-4 palabras. description: 1-2 frases."
    ),
    "features": (
        "Genera el contenido para la sección DIFERENCIADORES de una landing page.\n"
        "Empresa: {name} | Industria: {industry} | Tono: {tone}\n"
        "Público: {audience}\n\n"
        "Responde SOLO con un objeto JSON (sin texto adicional, sin markdown):\n"
        '{{"headline": "...", "items": [{{"title": "...", "description": "..."}}]}}\n\n'
        "Exactamente 4 diferenciadores. title: 2-3 palabras. description: 1-2 frases."
    ),
    "casos-de-exito": (
        "Genera el contenido para la sección CASOS DE ÉXITO de una landing page.\n"
        "Empresa: {name} | Industria: {industry} | Tono: {tone}\n"
        "Público: {audience}\n\n"
        "Responde SOLO con un objeto JSON (sin texto adicional, sin markdown):\n"
        '{{"headline": "...", "items": [{{"name": "...", "description": "..."}}]}}\n\n'
        "Exactamente 3 casos. name: empresa cliente ficticia. "
        "description: resultado concreto en 1 frase (usa cifras)."
    ),
    "testimonios": (
        "Genera el contenido para la sección TESTIMONIOS de una landing page.\n"
        "Empresa: {name} | Industria: {industry} | Tono: {tone}\n"
        "Público: {audience}\n\n"
        "Responde SOLO con un objeto JSON (sin texto adicional, sin markdown):\n"
        '{{"headline": "...", "items": [{{"quote": "...", "author": "...", "role": "..."}}]}}\n\n'
        "Exactamente 3 testimonios. quote: 1-2 frases en primera persona. "
        "author: nombre ficticio. role: cargo y empresa."
    ),
    "stats": (
        "Genera métricas clave para la sección ESTADÍSTICAS de una landing page.\n"
        "Empresa: {name} | Industria: {industry}\n"
        "Público: {audience}\n\n"
        "Responde SOLO con un objeto JSON (sin texto adicional, sin markdown):\n"
        '{{"items": [{{"value": "...", "label": "..."}}]}}\n\n'
        "Exactamente 4 métricas. value: número impactante con símbolo (ej. +50, 10+, 98%). "
        "label: etiqueta corta de 2-4 palabras."
    ),
    "faq": (
        "Genera el contenido para la sección FAQ de una landing page.\n"
        "Empresa: {name} | Industria: {industry} | Tono: {tone}\n"
        "Público: {audience}\n\n"
        "Responde SOLO con un objeto JSON (sin texto adicional, sin markdown):\n"
        '{{"headline": "...", "items": [{{"question": "...", "answer": "..."}}]}}\n\n'
        "Exactamente 4 preguntas reales del público objetivo. "
        "question: duda directa. answer: respuesta clara en 1-3 frases."
    ),
    # showForm is injected from spec.contact_form after generation — not by the LLM.
    "cta-contacto": (
        "Genera el contenido textual para la sección CTA/CONTACTO de una landing page.\n"
        "Empresa: {name} | Industria: {industry} | Tono: {tone}\n"
        "Objetivos: {goals}\n\n"
        "Responde SOLO con un objeto JSON (sin texto adicional, sin markdown):\n"
        '{{"headline": "...", "subtext": "...", "buttonLabel": "...", "buttonHref": "#contacto"}}\n\n'
        "headline: llamada a la acción convincente (6-10 palabras). "
        "subtext: 1 frase motivadora. buttonLabel: texto del botón."
    ),
}

_SEO_PROMPT = (
    "Genera el SEO para una landing page.\n"
    "Empresa: {name} | Industria: {industry}\n"
    "Público: {audience}\n\n"
    "Responde SOLO con un objeto JSON (sin texto adicional, sin markdown):\n"
    '{{"title": "...", "description": "..."}}\n\n'
    "title: máx. 60 caracteres, incluye el nombre de la empresa. "
    "description: 120-160 caracteres sobre el valor para el público."
)

# ── Fallback data ───────────────────────────────────────────────────────────
# Used when a section fails MAX_RETRIES + 1 times. Build never breaks.
_FALLBACKS: dict[str, dict[str, Any]] = {
    "hero": {
        "title": "Soluciones a medida para tu negocio",
        "subtitle": "Transformamos tus procesos para que puedas crecer con confianza.",
        "cta": {"label": "Contáctanos", "href": "#contacto"},
    },
    "servicios": {
        "headline": "Nuestros servicios",
        "items": [
            {"icon": "🔍", "title": "Diagnóstico", "description": "Análisis profundo de tu negocio."},
            {"icon": "⚙️", "title": "Optimización", "description": "Mejora continua de procesos clave."},
            {"icon": "🚀", "title": "Implementación", "description": "Puesta en marcha ágil y eficaz."},
        ],
    },
    "features": {
        "headline": "¿Por qué elegirnos?",
        "items": [
            {"title": "Experiencia probada", "description": "Años de trayectoria en el sector."},
            {"title": "Enfoque personalizado", "description": "Cada cliente es único para nosotros."},
            {"title": "Resultados medibles", "description": "KPIs claros desde el primer día."},
            {"title": "Soporte continuo", "description": "Estamos contigo en cada paso."},
        ],
    },
    "casos-de-exito": {
        "headline": "Casos de éxito",
        "items": [
            {"name": "Cliente A", "description": "Mejora del 20% en eficiencia operativa."},
            {"name": "Cliente B", "description": "Reducción de costes en 3 meses."},
            {"name": "Cliente C", "description": "Digitalización completada con éxito."},
        ],
    },
    "testimonios": {
        "headline": "Lo que dicen nuestros clientes",
        "items": [
            {"quote": "Superaron todas nuestras expectativas.", "author": "Ana García", "role": "CEO"},
            {"quote": "Profesionales y comprometidos con el resultado.", "author": "Luis Martín", "role": "Director"},
            {"quote": "Los recomendaría sin dudarlo.", "author": "María López", "role": "Gerente"},
        ],
    },
    "stats": {
        "items": [
            {"value": "+50", "label": "Proyectos completados"},
            {"value": "5+",  "label": "Años de experiencia"},
            {"value": "95%", "label": "Clientes satisfechos"},
            {"value": "3x",  "label": "ROI medio"},
        ],
    },
    "faq": {
        "headline": "Preguntas frecuentes",
        "items": [
            {"question": "¿Cómo empezamos?", "answer": "Contáctanos para una consulta gratuita sin compromiso."},
            {"question": "¿Cuánto tiempo tarda?", "answer": "Depende del alcance, generalmente entre semanas y meses."},
            {"question": "¿Qué incluye el servicio?", "answer": "Diagnóstico, propuesta, implementación y seguimiento."},
            {"question": "¿Sin compromiso?", "answer": "Sí, la primera consulta es gratuita y sin compromiso."},
        ],
    },
    "cta-contacto": {
        # showForm is always overridden from spec.contact_form — this value is ignored.
        "showForm": True,
        "headline": "¿Listo para dar el siguiente paso?",
        "subtext": "Cuéntanos tu reto y te responderemos en menos de 24 horas.",
        "buttonLabel": "Enviar mensaje",
        "buttonHref": "#contacto",
    },
}

# ── Validators ──────────────────────────────────────────────────────────────

def _check_nonempty_items(data: dict[str, Any]) -> None:
    items = data.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("'items' must be a non-empty list")


def _validate_hero(data: dict[str, Any]) -> None:
    for key in ("title", "subtitle", "cta"):
        if key not in data:
            raise ValueError(f"hero.data missing required key: '{key}'")
    if not isinstance(data.get("cta"), dict):
        raise ValueError("hero.data.cta must be a dict")
    for sub in ("label", "href"):
        if sub not in data["cta"]:
            raise ValueError(f"hero.data.cta missing '{sub}'")


_VALIDATORS: dict[str, Callable[[dict[str, Any]], None]] = {
    "hero":           _validate_hero,
    "servicios":      _check_nonempty_items,
    "features":       _check_nonempty_items,
    "casos-de-exito": _check_nonempty_items,
    "testimonios":    _check_nonempty_items,
    "stats":          _check_nonempty_items,
    "faq":            _check_nonempty_items,
    "cta-contacto":   lambda _: None,  # showForm injected by Python; no LLM validation needed
}


def _validate_section(section_type: str, data: Any) -> None:
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict for section data, got {type(data).__name__}")
    check = _VALIDATORS.get(section_type)
    if check:
        check(data)


# ── JSON extraction ─────────────────────────────────────────────────────────

def _parse_llm_json(response: str) -> Any:
    """Extract and parse the first JSON object from an LLM response.

    Handles ```json fenced blocks, plain ``` fenced blocks, and raw inline JSON.
    Raises ValueError if no valid JSON object is found.
    """
    # Try fenced code blocks first (most reliable when the model follows instructions)
    for _, code in extract_code_blocks(response):
        stripped = code.strip()
        if stripped:
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                continue

    # Fall back: find the first balanced { … } span in the raw text
    text = response.strip()
    start = text.find("{")
    if start < 0:
        raise ValueError("No JSON object found in LLM response")

    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError as exc:
                    raise ValueError(f"JSON parse error: {exc}") from exc

    raise ValueError("Unbalanced braces in LLM response — likely truncated output")


def _build_ctx(spec: ProjectSpec) -> dict[str, str]:
    """Flatten spec fields into prompt-injection context."""
    biz = spec.data.get("business", {})
    return {
        "name":     spec.name,
        "industry": biz.get("industry", ""),
        "audience": biz.get("target_audience", ""),
        "goals":    ", ".join(biz.get("goals", [])),
        "tone":     spec.data.get("branding", {}).get("tone", "profesional"),
    }


# ── Agent ───────────────────────────────────────────────────────────────────

class FrontendAgent:
    """Converts a validated ProjectSpec into the content/site.json dict.

    Atomic modularization: one LLM call per section.
    navbar, footer, theme, and showForm are deterministic (no LLM).
    """

    def run(self, spec: ProjectSpec) -> dict[str, Any]:
        """Return the site.json dict ready to be written to content/site.json."""
        pages = spec.data.get("pages", [])
        section_names: list[str] = pages[0].get("sections", []) if pages else []

        return {
            "theme":    self._build_theme(spec),
            "seo":      self._generate_seo(spec),
            "navbar":   self._build_navbar(spec, section_names),
            "footer":   self._build_footer(spec),
            "sections": [
                {"type": name, "data": self._generate_with_retry(name, spec)}
                for name in section_names
            ],
        }

    # ── Deterministic builders (D-FA-01) ─────────────────────────────────────

    def _build_theme(self, spec: ProjectSpec) -> dict[str, str]:
        color = (
            spec.data.get("branding", {}).get("primary_color")
            or DEFAULT_PRIMARY_COLOR
        )
        return {"primaryColor": color}

    def _build_navbar(
        self, spec: ProjectSpec, section_names: list[str]
    ) -> dict[str, Any]:
        links = [
            {"label": label, "href": href}
            for name in section_names
            if name in _NAV_LINKS
            for label, href in (_NAV_LINKS[name],)
        ]
        return {"logo": spec.name, "links": links}

    def _build_footer(self, spec: ProjectSpec) -> dict[str, Any]:
        year = date.today().year
        return {
            "copyright": f"© {year} {spec.name}. Todos los derechos reservados.",
            "links": [
                {"label": "Política de privacidad", "href": "/privacidad"},
                {"label": "Términos", "href": "/terminos"},
            ],
        }

    # ── LLM-backed builders ───────────────────────────────────────────────────

    def _generate_seo(self, spec: ProjectSpec) -> dict[str, str]:
        """One fast-model call for SEO; deterministic fallback on any failure."""
        ctx = _build_ctx(spec)
        try:
            raw = complete(_SEO_PROMPT.format(**ctx), role="fast")
            seo = _parse_llm_json(raw)
            if isinstance(seo, dict) and "title" in seo and "description" in seo:
                return {"title": str(seo["title"]), "description": str(seo["description"])}
            raise ValueError(f"Unexpected SEO shape: {seo}")
        except Exception as exc:  # noqa: BLE001
            log.warning("SEO generation failed (%s), using deterministic fallback.", exc)

        biz = spec.data.get("business", {})
        desc_parts = [biz.get("target_audience", ""), ", ".join(biz.get("goals", []))]
        return {
            "title": f"{spec.name} · {biz.get('industry', 'Empresa')}",
            "description": ". ".join(p for p in desc_parts if p),
        }

    def _generate_with_retry(
        self, name: str, spec: ProjectSpec
    ) -> dict[str, Any]:
        """Call the LLM for one section, retry up to MAX_RETRIES times, then fall back."""
        last_error: str | None = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                data = self._call_llm(name, spec, prev_error=last_error)
                _validate_section(name, data)
                if name == "cta-contacto":
                    data["showForm"] = bool(spec.data.get("contact_form", False))
                return data
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                log.warning(
                    "Section '%s' attempt %d/%d failed: %s",
                    name, attempt + 1, MAX_RETRIES + 1, last_error,
                )

        log.error(
            "Section '%s' fell back to static default after %d failed attempts.",
            name, MAX_RETRIES + 1,
        )
        fallback = dict(_FALLBACKS.get(name, {}))
        if name == "cta-contacto":
            fallback["showForm"] = bool(spec.data.get("contact_form", False))
        return fallback

    def _call_llm(
        self,
        name: str,
        spec: ProjectSpec,
        prev_error: str | None = None,
    ) -> dict[str, Any]:
        prompt_tmpl = _PROMPTS.get(name)
        if prompt_tmpl is None:
            raise ValueError(f"No prompt template for section type: '{name}'")
        ctx = _build_ctx(spec)
        prompt = prompt_tmpl.format(**ctx)
        if prev_error:
            prompt += f"\n\nError del intento anterior: {prev_error}\nCorrige el JSON y devuelve solo el objeto."
        raw = complete(prompt, role="coder")
        return _parse_llm_json(raw)
