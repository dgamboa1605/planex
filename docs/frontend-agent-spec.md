# Frontend Agent — Spec → `content/site.json`

> Primer agente "productivo" del MVP. Convierte un Project Spec validado en el `content/site.json` que consume la plantilla landing. Destino en el repo: `src/planex/agents/frontend.py` (reemplaza el stub actual).

## Contrato

- **Entrada:** un `ProjectSpec` validado (`planex.core.spec.ProjectSpec`).
- **Salida:** un dict que serializa a `content/site.json` y valida contra los tipos de `templates/landing/lib/content.ts` (`SiteContent`).
- **Modelo:** `qwen2.5-coder:14b` (rol `coder`) para el contenido de secciones; `llama3.1:8b` (rol `fast`) para el SEO. Vía `planex.llm.config.complete(prompt, role=...)`.

## Estrategia anti-alucinación: una sección por llamada

NO se pide el JSON entero de golpe. Por cada entrada de `pages[0].sections` se hace **una llamada enfocada** que devuelve **solo el objeto `data`** de esa sección. El código Python ensambla el `site.json` final. (Salvaguarda "modularización atómica de contexto".)

```
build_site_json(spec):
    theme   = { "primaryColor": spec.branding.primary_color or DEFAULT }
    seo     = generate_seo(spec)                 # 1 llamada al modelo `fast`
    navbar  = build_navbar(spec, sections)       # POR REGLAS (sin LLM)
    footer  = build_footer(spec)                 # POR REGLAS (sin LLM)
    sections = []
    for name in spec.pages[0].sections:
        data = generate_section(name, spec)      # 1 llamada `coder` por sección
        data = validate_or_retry(name, data)     # máx. 2 reintentos
        sections.append({ "type": name, "data": data })
    return { theme, seo, navbar, footer, sections }
```

## Decisiones confirmadas

- **D-FA-01 · navbar y footer POR REGLAS (sin LLM).** Deterministas, no necesitan creatividad.
  - `navbar.logo` = `spec.project.name`.
  - `navbar.links` = un link por sección "navegable" presente (servicios → `#servicios`, casos-de-exito → `#casos-de-exito`, testimonios → `#testimonios`, cta-contacto → `#contacto`). Se omiten hero/stats/features del nav.
  - `footer.copyright` = `© {año} {project.name}. Todos los derechos reservados.`
  - `footer.links` = legales por defecto (privacidad, términos).
- **D-FA-02 · SEO con una mini-llamada al modelo `fast`.** `generate_seo(spec)` pide a `llama3.1:8b` un `{ "title", "description" }` a partir de `business.industry`, `target_audience` y `project.name`. Fallback determinista si la respuesta no parsea.

## Generación de una sección

`generate_section(name, spec)`:
1. Toma el **prompt template** de esa sección (uno por tipo: hero, servicios, features, casos-de-exito, testimonios, stats, faq, cta-contacto).
2. Inyecta el contexto de negocio del spec (industry, audience, goals, name).
3. Pide al modelo `coder` **solo el objeto `data`** en JSON, sin texto alrededor.
4. Pasa la respuesta por `planex.core.extractor` (aísla el bloque, limpia texto conversacional).
5. `json.loads` + validación de forma.

Para `cta-contacto`, `data.showForm` = valor de `spec.contact_form`.

## Validación y reintentos

- Cada `data` se valida contra la forma esperada de su tipo (claves requeridas presentes, `items` es lista no vacía donde aplique).
- Si falla parse o validación → **reintento** (máx. 2, alineado con `Orchestrator.MAX_QA_RETRIES`). El prompt de reintento incluye el error.
- Tras 2 fallos → **fallback** a un `data` de ejemplo mínimo para esa sección (el sitio nunca queda roto; se marca para revisión humana).

## Definition of Done

1. `FrontendAgent().run(spec)` devuelve un dict que, escrito como `content/site.json`, hace `npm run build` pasar en la plantilla.
2. Cambiar `business`/`branding` en el spec cambia el contenido y el color del sitio generado.
3. `contact_form: false` produce `cta-contacto.data.showForm = false`.
4. Una sección que falla 2 veces cae al fallback sin romper el build.
5. Test unitario con el `example.acme-landing.spec.json` (mock del LLM) que verifica la forma del `site.json`.
