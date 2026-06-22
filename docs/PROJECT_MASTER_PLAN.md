# 🏭 AI Software Factory — Plan Maestro

> **Documento maestro y fuente única de verdad.** Consolida los tres documentos de planificación previos en una sola guía viva. Versión 1.0 · Owner: Dennis Gamboa · Timeline MVP: 6 meses.
>
> Versión navegable e imprimible (para humanos): `Documento Maestro - AI Software Factory.dc.html`. Esta versión Markdown es la fuente para Claude Code.

---

## Estado actual del proyecto

**Fase activa:** Fase 0 — Fundaciones y contrato (en curso).

**Checklist de progreso:**

- [x] Confirmar stack y decisiones de arquitectura (4 ADR cerrados).
- [x] Definir `project_spec_schema.json` (básico v0.2).
- [x] Setup de entorno: Ollama 0.30.9 + Docker 29.3.1 + modelos instalados.
- [ ] Crear las 2 plantillas base (boilerplates).
- [ ] Setup del proyecto Python (venv + CrewAI + LiteLLM).
- [ ] Construir el CLI MVP (Spec → clonar plantilla → inyectar contenido).
- [ ] Prueba end-to-end de una landing real.
- [ ] Integrar QA Agent + sandbox Docker.

---

## 1 · Visión y resumen ejecutivo

Construir una **AI Software Factory** de uso personal y alto rendimiento, capaz de transformar requerimientos de cliente en proyectos web listos para producción mediante una arquitectura multi-agente coordinada. El objetivo no es reemplazar al desarrollador, sino **amplificar su productividad** automatizando el trabajo repetitivo mientras el humano mantiene el control de las decisiones estratégicas y de calidad.

Las entradas pueden ser formularios estructurados, instrucciones libres en texto o notas de voz transcritas. Reduce drásticamente los tiempos de análisis, arquitectura, maquetación, codificación, pruebas y despliegue.

- **Foco del MVP:** landing pages y sitios web corporativos — proyectos reales de clientes, eficientes y de calidad.
- **Visión a futuro:** base para una plataforma SaaS escalable (sistemas internos, e-commerce, marketplaces, enterprise).

## 2 · Principios fundamentales

1. **Project Spec First** — la especificación del proyecto es la única fuente de verdad. Los agentes no se comunican con prompts libres entre sí, sino a través de actualizaciones al Project Spec.
2. **Template First** — el MVP no genera proyectos desde cero. Spec → selección de plantilla → personalización → generación → revisión. Reduce alucinaciones y acelera la entrega.
3. **Human in the Loop** — ningún agente despliega a producción por sí solo. Toda acción crítica requiere aprobación humana antes del commit y el deploy.
4. **Autonomía incremental** — objetivo de autonomía del MVP: 70%. La intervención humana sigue siendo obligatoria en arquitectura, diseño, revisión final de código y despliegue.

## 3 · Alcance del producto

**Incluido en el MVP:**
- Landing pages — marketing, lanzamiento de producto, captación de leads.
- Sitios web corporativos — empresas, servicios, consultoras, portafolios.
- Apps con backend — CRUD básico, auth, base de datos (iteración posterior dentro del MVP).

**Excluido del MVP** (fases posteriores): apps móviles, marketplaces, ERP, SaaS complejo, Kubernetes, marketplace de agentes.

Se soportan **2 tipos de plantilla**: Landing/Corporate (estático) y App con backend (CRUD + auth).

## 4 · Decisiones tomadas (ADRs confirmados)

Los tres documentos previos se contradecían en cuatro puntos. Las cuatro decisiones quedaron **confirmadas** (Opción A en cada caso):

### D-01 · Stack backend por defecto → **Next.js + Supabase**
Razón: el MVP son landing pages y sitios corporativos que rara vez necesitan backend pesado. Supabase aporta Postgres + Auth + Storage + API sin escribir backend, menos superficie para errores de los LLM, un solo lenguaje (TS/React). **FastAPI + PostgreSQL** queda como plantilla "Pro / Custom" para clientes con lógica específica, añadible después sin romper nada.

### D-02 · Orquestación de agentes → **CrewAI (MVP) → LangGraph (después)**
Razón: sintaxis simple, perfecta para el flujo lineal del MVP (PM → Coder). Regla de oro: **la lógica de negocio NO se acopla al framework** — vive en módulos Python propios; el orquestador solo decide *cuándo* llamar a cada módulo. Migrar a LangGraph cuando se necesiten ciclos complejos (QA ↔ Coder) será "reconectar cables".

### D-03 · Frontend de los proyectos generados → **Next.js + Tailwind**
Razón: SEO + SSR + SSG nativos (clave para landing/corporate), cubre estático y dinámico, integra perfecto con Supabase. (Alternativa descartada: React + Vite, sin SSR/SSG → peor SEO.)

### D-04 · Interfaz de la herramienta interna → **CLI primero, Dashboard Streamlit como meta**
Razón: empezar con un CLI Python que valide el "cerebro" (agentes + plantillas + spec) sin construir una segunda app, con la arquitectura preparada para envolverse en web. **Streamlit** es la tecnología elegida para ese dashboard.

**Meta del dashboard (Streamlit) — opciones requeridas:** gestión de clientes y proyectos · formulario de captura del Project Spec · captura de voz (Whisper local) · vista previa del código generado · **punto de aprobación Human-in-the-loop** (aprobar / editar / rechazar con feedback) · seguimiento del progreso por agente · disparo y monitoreo del flujo.

## 5 · Stack tecnológico

### A · Núcleo del sistema (la factoría)

| Componente | Elección | Por qué |
|---|---|---|
| Lenguaje base | Python | Estándar para IA, manejo de archivos y GUIs de datos |
| Orquestador | CrewAI → LangGraph | Lógica desacoplada del framework; migración cuando haya ciclos |
| LLM Gateway | LiteLLM | Cambiar de Ollama a Claude/GPT = una variable de entorno |
| Interfaz | CLI → Dashboard Streamlit | CLI valida el motor; Streamlit es la meta de UI |
| Persistencia interna | SQLite | Tracking local de clientes, proyectos y versiones del spec |
| AI Runtime | Ollama (local) | Coste cero de API, privacidad, iteración rápida en RTX 4070 12GB |
| Modelos locales | qwen2.5-coder:14b · qwen3:14b · deepseek-r1:14b · llama3.1:8b | Coder para código; modelos de razonamiento para planificación; ligero para clasificación |
| Voz (fase 3) | Whisper (local) | Transcripción de notas de voz del cliente |
| Sandbox / infra | Docker · Docker Compose | Ejecución aislada de builds y pruebas del QA Agent |
| Control de versiones | Git / GitHub | Un repositorio por proyecto generado; commits automáticos |

### B · Stack de los proyectos generados (webs de clientes)

| Capa | Elección | Notas |
|---|---|---|
| Frontend | Next.js + Tailwind | React + Tailwind; SEO/SSG para landing y corporate |
| Backend | Next.js + Supabase | Default; FastAPI como plantilla "Pro" para lógica custom |
| Base de datos | PostgreSQL (Supabase / Docker) | Fiabilidad, ACID, escalable; capa gratuita de Supabase |
| Plantilla 1 | Next.js + Tailwind | Landing page / sitio corporativo (estático) |
| Plantilla 2 | Next.js + Tailwind + Supabase | App con backend (CRUD + auth) |
| Plantilla "Pro" (futura) | Next.js + FastAPI | Lógica de negocio muy específica / integraciones pesadas |

## 6 · Arquitectura del sistema

Patrón estricto **Orquestador–Trabajador**: se rechaza la comunicación libre entre agentes. El núcleo no es el código, sino el **Project Spec** centralizado y fuertemente tipado. Una línea de ensamblaje industrial secuencial y controlada.

```
Cliente (formulario / voz)
  └─> Intake Agent ─────────> crea / limpia el PROJECT SPEC (JSON)  ← fuente única de verdad
        └─> Analyst → Architect → PM ──> requerimientos, arquitectura, backlog "molecular"
              └─> Frontend Agent  +  Backend Agent  (implementación en paralelo)
                    └─> QA Agent (build + lint en sandbox Docker, reintenta)
                          └─> ⏸ REVISIÓN HUMANA (aprobar / editar / rechazar con feedback)
                                └─> DevOps Agent → Git commit → Deploy
```

Si QA detecta fallos, bloquea el flujo y devuelve el archivo al programador con el log exacto. Tras 2 intentos fallidos, el orquestador hace `git checkout .` al último estado estable.

## 7 · Sistema multi-agente · roles

- **Intake & Business Analyst** — puerta de entrada. Recibe el formulario o la voz transcrita, limpia ambigüedades, extrae requerimientos funcionales y no funcionales, rellena el esquema inicial del Project Spec.
- **Solution Architect & PM** — diseña la estructura técnica: mapa de archivos físicos, componentes UI, endpoints, tablas y dependencias. Genera el backlog de tareas moleculares.
- **Frontend Agent (Coder UI)** — toma tareas de interfaz secuencialmente. Código modular y documentado en Next.js + Tailwind. Solo capa de cliente.
- **Backend Agent (Coder API)** — modelos de datos, migraciones y lógica de servidor. Endpoints sobre Supabase (o FastAPI en plantilla Pro), con validación de tipos y manejo de excepciones.
- **QA & Tester Agent** — linters, análisis estático y build de prueba en contenedor Docker aislado. Si falla, bloquea el flujo y devuelve el archivo con el log exacto para auto-corrección.
- **DevOps Agent** — `git init`, commits automáticos, `Dockerfile` / `docker-compose` y scripts de despliegue.

## 8 · Project Spec — el contrato central

Contrato de datos compartido por todos los agentes. **Solo el agente dueño de una sección puede modificarla**, todo cambio se versiona y cada modificación crea una nueva revisión. El esquema vive en `project_spec_schema.json` (JSON Schema 2020-12).

Versión actual: **v0.2 (mínima)** — soporta landing/corporate estáticas. Estructura:

```yaml
meta:
  status: draft | approved
project:
  name: "Acme Consulting"
  slug: "acme-landing"          # nombre del repo
  type: landing | corporate     # 'app' (con backend) llega después
business:
  industry: "..."
  target_audience: "..."
  goals: ["captar leads"]
branding:                        # opcional
  primary_color: "#1D4ED8"
  tone: "corporativo"
pages:
  - name: home
    sections: [hero, servicios, testimonios, cta]
contact_form: true | false       # único elemento dinámico del MVP mínimo
```

Campos como `backend.provider`, `deployment` y `template` se reincorporan cuando entremos en apps con backend.

## 9 · Arquitectura de memoria (fase posterior)

Se implementa después del MVP. Da a los agentes memoria persistente y recuperación de conocimiento.

- **Memoria a largo plazo (PostgreSQL):** historial de clientes y proyectos, decisiones tomadas, conversaciones previas.
- **Memoria semántica (pgvector):** embeddings, documentación y conocimiento reutilizable para pipelines RAG.

Flujo: `Query → Embedding → Vector Search → Contexto relevante → Ejecución del agente`.

## 10 · Factores de ingeniería y mitigación de riesgos

Salvaguardas obligatorias para que sea un producto confiable y no un experimento inestable con modelos de 7B–14B:

1. **Modularización atómica de contexto** — prohibido pedir "escribe la app". Se itera la lista de archivos del PM llamando al coder para **un solo archivo por interacción**. El prompt contiene solo el Spec, el archivo base y firmas adyacentes.
2. **Módulo de extracción y persistencia** — script Python que intercepta la respuesta, aísla bloques de código con regex, elimina texto conversacional, valida que no haya cortes abruptos y escribe el archivo con encoding y extensión correctos.
3. **Boilerplates completos obligatorios** — los LLM no generan configs (`next.config`, `tsconfig`…). El orquestador clona un boilerplate testeado; los agentes solo inyectan lógica de negocio.
4. **Sandboxing con Docker** — todo build/test del QA corre en contenedor temporal aislado. Se monta el código en volumen, se capturan logs y se destruye el contenedor.
5. **Versionado y auto-reversión (Git)** — commit automático tras cada archivo que pasa QA. Si tras 2 intentos el LLM no repara el código, `git checkout .` al último estado estable y notificación al usuario.

## 11 · Repositorios y seguridad

**Un repositorio por proyecto** (ej. `client-a-landing`, `client-b-corporate`). Estructura estándar:

```
frontend/
backend/
infrastructure/
docs/
project-spec/
tests/
```

**Modelo de seguridad:** los secretos nunca se guardan en los repositorios. Uso de `.env`, variables de entorno y gestión de secretos. A futuro: integración con Vault.

## 12 · Estrategia de costes — Local First

Enfoque híbrido en dos fases a través de una capa de abstracción única (LiteLLM):

- **Fase inicial · desarrollo y MVP:** 100% LLMs locales (Ollama). Modelos en la RTX 4070 12GB. Elimina el coste de APIs comerciales durante construcción, pruebas de prompts y validación.
- **Fase producción · escalabilidad (híbrido):** alta complejidad (arquitectura, bugs difíciles, refactor) → Claude 3.5 Sonnet / GPT-4o, pagado por ingresos del cliente. Rutina (extracción, clasificación, copywriting) → sigue en local para optimizar márgenes.

## 13 · Hoja de ruta

- **Fase 0 · Mes 1 — Fundaciones y contrato:** definir `project_spec_schema.json`. Setup de Ollama + modelos. Entorno Docker, Python, PostgreSQL.
- **Fase 1 · Mes 2 — Generador guiado por plantillas (MVP):** sistema del Project Spec, formularios e Intake Agent. CLI + clonación de boilerplate + inyección básica de contenido. Resultado: carpeta con código estático funcional.
- **Fase 2 · Meses 3–5 — Multi-agente autónomo:** Analyst y Architect Agents. Template engine (landing + corporate). Frontend y Backend Agents. Integración del QA Agent con Docker y bucle de auto-corrección.
- **Mes 6 — QA + Release del MVP:** testing interno y primeros proyectos reales de clientes.
- **Fase 3+ — Voz, híbrido de pago y SaaS:** Whisper + parser de requerimientos. Activación de LiteLLM para APIs de pago. Después: generación SaaS, pagos, multi-idioma, marketplace de agentes, plataforma enterprise.

## 14 · Registro de decisiones (ADRs)

| # | Decisión | Estado |
|---|---|---|
| ADR-001 | Next.js en lugar de solo React | ✅ Confirmado · Next.js |
| ADR-002 | Backend por defecto (Next.js + Supabase; FastAPI = plantilla Pro) | ✅ Confirmado · Supabase |
| ADR-003 | PostgreSQL como base de datos principal | ✅ Confirmado |
| ADR-004 | pgvector para memoria semántica | ✅ Confirmado (fase posterior) |
| ADR-005 | Orquestación: CrewAI (MVP) → LangGraph (cuando haya ciclos) | ✅ Confirmado |
| ADR-006 | Un repositorio por proyecto de cliente | ✅ Confirmado |
| ADR-007 | Estrategia Template-First | ✅ Confirmado |
| ADR-008 | Aprobación humana antes del despliegue | ✅ Confirmado |
| ADR-009 | Ejecución local-first con Ollama | ✅ Confirmado |
| ADR-010 | Autonomía objetivo del 70% en el MVP | ✅ Confirmado |
| ADR-011 | Interfaz CLI primero, dashboard Streamlit como meta | ✅ Confirmado |

## 15 · Próximos pasos

1. Validar/aprobar el `project_spec_schema.json` v0.2 (`meta.status: approved`).
2. Definir el contenido de la **plantilla base de landing** (estructura de archivos del boilerplate Next.js + Tailwind).
3. Levantar el esqueleto del proyecto Python: estructura de carpetas, dependencias, config de LiteLLM apuntando a Ollama.
4. Construir el CLI MVP: leer spec → validar contra el schema → clonar boilerplate → inyectar contenido básico.

### Bitácora de sesiones

| Fecha | Sesión / Foco | Resultado · decisiones |
|---|---|---|
| — | Consolidación de documentación | Tres documentos unificados. 4 decisiones de stack confirmadas (Next.js + Supabase, CrewAI→LangGraph, Next.js, CLI→Streamlit) y promovidas a ADR. |
| 17 jun 2026 | Arranque Fase 0 · Project Spec básico | `project_spec_schema.json` v0.2 mínimo definido. Entorno local (Ollama + Docker + modelos) completado. Handoff a Claude Code preparado. |
