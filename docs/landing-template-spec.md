# Plantilla base — Landing / Corporate

> Especificación del boilerplate que el orquestador clona por proyecto (Principio **Template First**). Destino sugerido en el repo: `templates/landing/` (el boilerplate en sí) + este doc en `docs/`.

## Stack

- **Next.js 14** (App Router) + **TypeScript**
- **Tailwind CSS** (tema vía variable CSS `--color-primary`)
- Sin backend propio: la única parte dinámica es el formulario de contacto, que reenvía a un servicio externo configurable.

## Modelo de inyección (clave)

Híbrido **content-first**. Las secciones son componentes genéricos, pre-construidos y testeados. El Frontend Agent **NO escribe JSX de bajo nivel ni configuración**; solo produce un archivo de contenido. Con modelos locales de 14B esto minimiza alucinaciones y respeta la salvaguarda "boilerplates completos obligatorios".

| 🔒 LOCKED (parte del boilerplate, el agente no lo toca) | ✏️ INJECT (lo que el agente genera) |
|---|---|
| `next.config.js`, `tsconfig.json`, `tailwind.config.ts`, `package.json` | `content/site.json` — textos y datos |
| Componentes de sección (`.tsx`) | Orden y selección de secciones |
| Layout raíz, `ui/`, utilidades, routing | `theme.primaryColor` (de `branding.primary_color`) |
| `SectionRenderer`, loaders, tipos | Metadatos SEO (title, description) |
| `api/contact/route.ts` | Flag de formulario de contacto (on/off) |

En el MVP, el agente toca **un solo archivo**: `content/site.json`.

## Árbol de archivos

```
landing-template/
├── app/
│   ├── layout.tsx              # 🔒 layout raíz, fuentes, metadata base
│   ├── page.tsx                # compone secciones según content.json
│   ├── globals.css             # 🔒 Tailwind + --color-primary (variable)
│   └── api/contact/route.ts    # 🔒 handler del form → servicio externo
├── components/
│   ├── sections/               # 🔒 LIBRERÍA de bloques
│   │   ├── Navbar.tsx
│   │   ├── Hero.tsx
│   │   ├── Services.tsx
│   │   ├── Features.tsx
│   │   ├── CaseStudies.tsx
│   │   ├── Testimonials.tsx
│   │   ├── Stats.tsx
│   │   ├── FAQ.tsx
│   │   ├── CTA.tsx
│   │   ├── Contact.tsx
│   │   └── Footer.tsx
│   ├── ui/                     # 🔒 Button, Container, Section…
│   └── SectionRenderer.tsx     # 🔒 mapea nombre de sección → componente
├── content/
│   └── site.json               # ✏️ ÚNICO archivo que el agente llena
├── lib/
│   ├── content.ts              # 🔒 tipos + loader de site.json
│   └── sections.ts             # 🔒 registro de secciones disponibles
├── public/                     # imágenes / logo (placeholders)
├── tailwind.config.ts          # 🔒
├── tsconfig.json               # 🔒
├── next.config.js              # 🔒
├── package.json                # 🔒
└── .env.example                # CONTACT_ENDPOINT, etc.
```

## Librería de secciones

Cada valor de `pages[].sections` en el Project Spec mapea a un componente. El Architect elige cuáles y en qué orden; el Frontend llena su `data`.

| key (en el spec) | Componente | Propósito |
|---|---|---|
| `navbar` | Navbar | Navegación + logo (siempre presente) |
| `hero` | Hero | Titular, subtítulo, CTA principal |
| `servicios` | Services | Grid de servicios / oferta |
| `features` | Features | Beneficios / diferenciadores |
| `casos-de-exito` | CaseStudies | Casos, portafolio o logos de clientes |
| `testimonios` | Testimonials | Citas de clientes |
| `stats` | Stats | Métricas / números destacados |
| `faq` | FAQ | Preguntas frecuentes (acordeón) |
| `cta-contacto` | Contact | Formulario (si `contact_form: true`) o CTA |
| `footer` | Footer | Pie con enlaces y datos (siempre presente) |

`navbar` y `footer` se montan siempre aunque no estén listados explícitamente.

## Del Project Spec a `content/site.json`

El Frontend Agent transforma el spec en el archivo de contenido:

**Entrada (Project Spec):**
```json
{
  "project": { "name": "Acme", "type": "landing" },
  "branding": { "primary_color": "#1D4ED8" },
  "pages": [{ "name": "home", "sections": ["hero", "servicios", "testimonios", "cta-contacto"] }],
  "contact_form": true
}
```

**Salida (`content/site.json`):**
```json
{
  "theme": { "primaryColor": "#1D4ED8" },
  "seo": { "title": "Acme · ...", "description": "..." },
  "sections": [
    { "type": "hero", "data": { "title": "...", "subtitle": "...", "cta": { "label": "...", "href": "#contacto" } } },
    { "type": "servicios", "data": { "items": [ ... ] } },
    { "type": "testimonios", "data": { "items": [ ... ] } },
    { "type": "cta-contacto", "data": { "showForm": true } }
  ]
}
```

**Flujo de render:** `page.tsx` lee `site.json` → `SectionRenderer` recorre `sections[]` y monta cada componente con su `data`. Añadir una sección = añadir un objeto al array; nunca se toca JSX.

## Decisiones de la plantilla (CONFIRMADAS)

- **T-01 · TypeScript (no JavaScript)** ✅ — los tipos en `content.ts` hacen que un `site.json` mal formado falle en build (lo detecta el QA Agent) en vez de romper en runtime. Red de seguridad con modelos pequeños.
- **T-02 · Tema por variable CSS `--color-primary`** ✅ — el agente inyecta un hex; Tailwind lo consume como color `primary`. Cambiar branding = cambiar una variable.
- **T-03 · Formulario vía servicio externo** ✅ — coherente con el schema mínimo ("sin backend propio"). `route.ts` reenvía a `CONTACT_ENDPOINT` (Resend/Formspree). Landing 100% estática + un punto dinámico.
- **T-04 · Imágenes con placeholder** ✅ — el boilerplate trae placeholders en `public/`; el humano sube los assets reales en la revisión. Evita que el modelo invente imágenes.

> Librería congelada en **10 secciones** para el MVP. Se añadirán más (ej. `pricing`, `equipo`, `blog`) cuando un proyecto real lo requiera.

## Criterio de "terminado" (Definition of Done) del boilerplate

1. `npm install && npm run build` pasa limpio (sin contenido del agente).
2. `npm run dev` renderiza todas las secciones con datos de ejemplo.
3. `npm run lint` (ruff equivalente: ESLint) pasa.
4. Cambiar `theme.primaryColor` en `site.json` re-colorea todo el sitio.
5. `contact_form: false` oculta el formulario sin romper el layout.
