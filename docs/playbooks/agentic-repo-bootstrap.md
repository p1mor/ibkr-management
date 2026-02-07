# Guia Reutilizable: Infraestructura Inicial Moderna (Agent-First)

## Objetivo
Framework base minimalista para cualquier repo:
- consistente para humanos y agentes
- simple en fase inicial
- escalable sin romper lo existente
- basado en fuentes oficiales y verificables

Aplica a trading, salud/FHIR, data y otros dominios.

## Criterio de curacion (aplicado a la propuesta externa)
Se adopta:
- marco de 5 capas para evitar deriva
- boundaries explicitos (`Always`, `Ask first`, `Never`)
- checklist de bootstrap corto y verificable

Se ajusta:
- priorizar solo fuentes oficiales en la guia base
- mantener `specs/` separada de arquitectura (en este repo ya es parte del flujo)
- dejar `CLAUDE.md` como opcional, no obligatorio

Se descarta:
- claims no verificables sin fuente primaria
- crecimiento de estructura antes de necesitarlo

## Marco mental (5 capas)
1. Direccion: problema, fase y limites (`AGENTS.md`).
2. Arquitectura: estado real hoy (`docs/architecture/overview.md`).
3. Contrato de cambio: in/out por iteracion (`specs/*.md`).
4. Calidad automatica: checks minimos recurrentes (`.github/workflows/ci.yml`).
5. Consistencia de tooling: una fuente de verdad para herramientas (`pyproject.toml`).

Si falta una capa, aparece friccion operativa.

## Estructura minima recomendada
```text
repo/
├── AGENTS.md
├── CLAUDE.md                    # opcional (si usas Claude Code)
├── pyproject.toml
├── .github/
│   ├── copilot-instructions.md
│   └── workflows/ci.yml
├── docs/
│   └── architecture/overview.md
├── specs/
│   └── 001-foundation.md
└── tests/
    └── test_smoke.py
```

## Orquestacion de archivos (por que existe cada uno)
- `AGENTS.md`: contrato operativo canonic (rol, comandos, boundaries, seguridad).
- `docs/architecture/overview.md`: foto actual del sistema, sin aspiracional.
- `specs/*.md`: acuerdo de alcance por iteracion (in-scope/out-of-scope/aceptacion).
- `pyproject.toml`: configuracion de tooling y calidad en un solo lugar.
- `.github/workflows/ci.yml`: ejecuta checks automaticos en push/PR.
- `tests/test_smoke.py`: red minima contra regresiones basicas.
- `CLAUDE.md`: memoria de proyecto para Claude Code (si aplica).
- `.github/copilot-instructions.md`: contexto minimo para Copilot y enlace a `AGENTS.md`.

## Checklist de bootstrap (30-60 min)
1. Definir fase actual (`foundation`, `growth`, `scale`).
2. Crear `AGENTS.md` con comandos ejecutables y boundaries claros.
3. Documentar arquitectura real en `docs/architecture/overview.md`.
4. Crear una spec minima de la iteracion en `specs/`.
5. Configurar `pyproject.toml` (lint, test, tipado segun necesidad real).
6. Agregar `tests/test_smoke.py`.
7. Configurar `ci.yml` con instalacion, checks y tests.

## Prompt reutilizable para agentes
Usa esta plantilla al iniciar trabajo en cualquier repo:

```text
Objetivo: disenar/ajustar infraestructura base sin sobre-ingenieria.

1) Lee primero:
   - AGENTS.md
   - docs/architecture/overview.md
   - specs activas

2) Verifica practicas actuales en fuentes oficiales:
   - AGENTS.md spec
   - GitHub Copilot instructions/agents
   - GitHub Actions workflow syntax + security hardening
   - Claude Code memory (si aplica)
   - estandares de dominio (FHIR, etc.) si aplica

3) Propone solo MVP escalable:
   - que agregas ahora
   - que dejas explicitamente fuera
   - tradeoffs y riesgos

4) Entrega:
   - plan por fases
   - diff concreto por archivo
   - checks para validar (local + CI)
   - links oficiales consultados
```

## Politica de actualizacion continua
- Cadencia: mensual o cuando cambie una fase.
- Regla: priorizar fuentes oficiales; secundarias solo como contexto.
- Salida esperada de revision:
  - que sigue vigente
  - que quedo deprecado
  - ajuste minimo propuesto

## Registro de links oficiales (evergreen)
### Multi-agente / repositorio
- AGENTS.md spec: https://agents.md/
- AGENTS.md reference repo: https://github.com/openai/agents.md
- GitHub blog (2,500+ repos): https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/
- Copilot repository instructions: https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
- Copilot custom agents: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents
- GitHub Actions workflow syntax: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
- GitHub Actions security hardening: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
- Claude Code memory: https://docs.claude.com/en/docs/claude-code/memory

### Base Python / tooling
- Packaging + `pyproject.toml`: https://packaging.python.org/en/latest/tutorials/packaging-projects/
- `setup.py` deprecation context: https://packaging.python.org/en/latest/discussions/setup-py-deprecated/
- Ruff docs: https://docs.astral.sh/ruff/
- Pytest docs: https://docs.pytest.org/en/stable/

### Dominio salud (si aplica)
- FHIR R5: https://hl7.org/fhir/r5
- FHIR R4: https://hl7.org/fhir/r4
- FHIR overview: https://www.hl7.org/fhir/overview.html
- SMART on FHIR: https://docs.smarthealthit.org/

## Aplicacion rapida al caso FHIR
Si creas un repo de historia clinica electronica:
1. Conserva esta estructura minima.
2. Agrega `specs/010-fhir-conformance.md`.
3. Agrega tests de contrato FHIR (schema + perfiles).
4. Define en `AGENTS.md` boundaries de privacidad por defecto.
5. Incrementa complejidad solo despues de CI estable.

## Versionado de esta guia
- Version: 2.1
- Ultima revision: 2026-02-07
- Criterio: minimalista, verificable, escalable
