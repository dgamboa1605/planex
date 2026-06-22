# CLAUDE.md — AI Software Factory (planex)

> Este archivo es el contexto persistente del proyecto. Claude Code lo lee automáticamente al inicio de cada sesión. La documentación extendida vive en `docs/`.

## Qué estamos construyendo

Una **AI Software Factory**: una plataforma multi-agente, de uso personal y local-first, que transforma requerimientos de cliente (formulario, texto libre o voz) en proyectos web listos para producción. No reemplaza al desarrollador: **amplifica su productividad** automatizando lo repetitivo mientras el humano controla arquitectura, calidad y despliegue.

- **Foco del MVP:** landing pages y sitios corporativos (proyectos reales de clientes).
- **Autonomía objetivo del MVP:** ~70%. La intervención humana es obligatoria en arquitectura, diseño, revisión final de código y deploy.
- **Timeline:** 6 meses · Owner: Dennis Gamboa.

## Principios fundamentales (no negociables)

1. **Project Spec First** — el `project_spec` (ver `docs/project_spec_schema.json`) es la única fuente de verdad. Los agentes NO se comunican con prompts libres entre sí: leen y enriquecen el spec.
2. **Template First** — el MVP NO genera proyectos desde cero. Flujo: Spec → seleccionar plantilla (boilerplate testeado) → personalizar → generar → revisar. Reduce alucinaciones.
3. **Human in the Loop** — ningún agente hace commit a producción ni deploy sin aprobación humana explícita.
4. **Autonomía incremental** — empezamos con un flujo lineal simple y añadimos ciclos/autonomía por fases.

## Decisiones de stack (CONFIRMADAS)

| Área | Decisión | Nota |
|---|---|---|
| Lenguaje del núcleo | **Python** | Orquestador, agentes, CLI |
| Orquestación | **CrewAI** (MVP) → **LangGraph** (cuando haya ciclos) | La lógica de negocio NO se acopla al framework: vive en módulos Python propios |
| LLM Gateway | **LiteLLM** | Cambiar de modelo local a API = una variable de entorno |
| Interfaz | **CLI** primero → **Dashboard Streamlit** (meta) | CLI valida el motor; arquitectura preparada para envolver en web |
| Persistencia interna | **SQLite** (MVP) → PostgreSQL/pgvector (después) | Clientes, proyectos, versiones del spec |
| AI Runtime | **Ollama** (local-first) | Coste cero de API durante desarrollo |
| Sandbox / infra | **Docker + Docker Compose** | Builds y tests del QA Agent aislados |
| Versionado | **Git / GitHub** | Un repositorio por proyecto generado |
| **Frontend generado** | **Next.js + Tailwind** | SEO/SSG para landing y corporate |
| **Backend generado** | **Next.js + Supabase** (default) | FastAPI reservado como plantilla "Pro" para lógica custom |
| Base de datos generada | **PostgreSQL** (vía Supabase) | — |

## Modelos locales (Ollama) y reparto sugerido

Hardware: **RTX 4070, 12 GB VRAM**. Modelos disponibles: `qwen2.5-coder:14b`, `qwen3:14b`, `deepseek-r1:14b`, `gemma3:12b`, `llama3.1:8b`.

| Rol del agente | Modelo sugerido | Por qué |
|---|---|---|
| Frontend / Backend (generación de código) | **`qwen2.5-coder:14b`** | Especializado en código |
| Analyst / Architect / PM (razonamiento, planificación) | **`qwen3:14b`** o `deepseek-r1:14b` | Razonamiento y estructura |
| Intake (clasificación, extracción de campos) | **`llama3.1:8b`** | Ligero y rápido |

Todo el acceso a modelos pasa por **LiteLLM**, configurado por variables de entorno (`PROVIDER=ollama` en desarrollo) para poder cambiar a Claude/GPT en producción sin tocar código.

## Arquitectura — patrón Orquestador–Trabajador

Línea de ensamblaje secuencial y controlada. El núcleo es el **Project Spec**, no el código.

```
Cliente (formulario / voz)
  └─> Intake Agent ─────────> crea / limpia el PROJECT SPEC (JSON)  ← fuente única de verdad
        └─> Analyst → Architect → PM ──> requerimientos, arquitectura, backlog "molecular"
              └─> Frontend Agent  +  Backend Agent  (implementación)
                    └─> QA Agent (build + lint en sandbox Docker, reintenta)
                          └─> ⏸ REVISIÓN HUMANA (aprobar / editar / rechazar)
                                └─> DevOps Agent → Git commit → Deploy
```

Si QA falla, devuelve el archivo al coder con el log exacto. Tras **2 intentos** fallidos, el orquestador hace `git checkout .` al último estado estable y avisa al humano.

## Agentes (roles)

- **Intake & Business Analyst** — recibe la entrada, limpia ambigüedades, rellena el spec inicial.
- **Solution Architect & PM** — diseña estructura técnica (archivos, componentes, endpoints, tablas) y genera el backlog de tareas moleculares.
- **Frontend Agent** — código de UI en Next.js + Tailwind. Solo capa de cliente.
- **Backend Agent** — modelos, migraciones y lógica de servidor (Supabase; FastAPI en plantilla Pro).
- **QA & Tester Agent** — linters, análisis estático y build de prueba en Docker aislado.
- **DevOps Agent** — `git init`, commits, `Dockerfile`/`docker-compose`, scripts de deploy.

## Reglas de ingeniería críticas (salvaguardas)

1. **Modularización atómica** — prohibido pedir "escribe la app". Se genera **un archivo por interacción**; el prompt solo lleva el spec, el archivo base y firmas adyacentes.
2. **Módulo de extracción/persistencia** — script que aísla bloques de código con regex, elimina texto conversacional, valida que no haya cortes y escribe el archivo con extensión/encoding correctos.
3. **Boilerplates completos obligatorios** — los LLM NO generan configs (`next.config`, `tsconfig`…). El orquestador clona un boilerplate testeado; los agentes solo inyectan lógica.
4. **Sandboxing con Docker** — todo build/test corre en contenedor temporal aislado; se capturan logs y se destruye.
5. **Versionado y auto-reversión** — commit automático tras cada archivo que pasa QA; `git checkout .` tras 2 fallos.

## Estado actual del proyecto

- **Fase 0 — Fundaciones** (en curso).
  - ✅ Stack y decisiones confirmadas (ver tabla arriba).
  - ✅ `project_spec_schema.json` v0.2 (mínimo) definido — ver `docs/`.
  - ✅ Entorno local: Ollama + Docker + modelos instalados.
  - ⬜ Crear las 2 plantillas base (boilerplates).
  - ⬜ Setup del proyecto Python (venv + CrewAI + LiteLLM).
  - ⬜ Construir el CLI MVP (Spec → clonar plantilla → inyectar contenido).
  - ⬜ Prueba end-to-end de una landing real.
  - ⬜ Integrar QA Agent + sandbox Docker.

## Próximos pasos inmediatos

1. Validar/aprobar el `project_spec_schema.json` v0.2 (`meta.status: approved`).
2. Definir el contenido de la **plantilla base de landing** (estructura de archivos del boilerplate Next.js + Tailwind).
3. Levantar el esqueleto del proyecto Python: estructura de carpetas, `pyproject`/`requirements`, config de LiteLLM apuntando a Ollama.
4. Construir el CLI MVP que recorre: leer spec → validar contra el schema → clonar boilerplate → inyectar contenido básico.

## Convenciones

- Lógica de negocio (prompts, manejo del spec, archivos, llamadas LLM) en **módulos Python propios**, desacoplada del framework de orquestación.
- Toda configuración por **variables de entorno** (`.env`, nunca secretos en el repo).
- Un **repositorio por proyecto de cliente** generado, con estructura estándar: `frontend/`, `backend/`, `infrastructure/`, `docs/`, `project-spec/`, `tests/`.
- El spec se **versiona**: cada cambio crea una revisión; solo el agente dueño de una sección la modifica.

## Documentación de referencia

- `docs/PROJECT_MASTER_PLAN.md` — plan maestro completo (visión, alcance, roadmap, ADRs, riesgos, costes).
- `docs/project_spec_schema.json` — el contrato (JSON Schema 2020-12), versión mínima v0.2.
- `docs/example.acme-landing.spec.json` — ejemplo de un spec lleno.
