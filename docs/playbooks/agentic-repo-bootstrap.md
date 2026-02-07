# Guia Reutilizable: Infraestructura Inicial Moderna (Agentic)

## Objetivo
Tener un framework base minimalista para cualquier repo:
- consistente para humanos y agentes
- simple de operar en etapas tempranas
- escalable para complejidad futura

Esta guia aplica tanto a proyectos de trading como a dominios regulados (por ejemplo, historia clinica electronica con FHIR).

## Marco mental
Piensa el repo en 5 capas:
1. Direccion: que problema resuelve y en que fase esta (`AGENTS.md` + spec activa).
2. Arquitectura: como esta construido hoy (`docs/architecture/overview.md`).
3. Contrato de cambio: que entra y que no entra por iteracion (`specs/*.md`).
4. Calidad automatica: que siempre se valida (`.github/workflows/ci.yml`).
5. Consistencia de tooling: mismas reglas para todos (`pyproject.toml`).

Si falta una capa, aparece friccion o deriva de contexto.

## Estructura minima recomendada
```text
repo/
├── AGENTS.md
├── CLAUDE.md
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

## Funcion de cada archivo
- `AGENTS.md`: contrato operativo canónico (reglas, limites, comandos, seguridad).
- `CLAUDE.md`: shim para Claude Code; referencia a `AGENTS.md`.
- `.github/copilot-instructions.md`: shim para Copilot; referencia a `AGENTS.md`.
- `docs/architecture/overview.md`: estado tecnico real del sistema.
- `specs/001-*.md`: alcance/no-alcance/aceptacion para la iteracion.
- `pyproject.toml`: configuracion central de herramientas.
- `.github/workflows/ci.yml`: validacion automatica en cada push/PR.
- `tests/test_smoke.py`: minima red de seguridad contra regresiones basicas.

## Checklist de bootstrap (30-60 min)
1. Definir fase actual (ej: foundation de datos).
2. Crear `AGENTS.md` con reglas concretas y comandos ejecutables.
3. Crear `overview.md` con arquitectura real (sin aspiracional).
4. Crear `spec` inicial con alcance reducido.
5. Configurar `pyproject.toml` con reglas minimas de tooling.
6. Crear `tests` de humo.
7. Crear `ci.yml` con checks basicos (instalar deps, compilacion, tests).

## Plantilla de instrucciones para cualquier agente
Copia y pega esto al iniciar una tarea:

```text
Objetivo: Diseñar/actualizar infraestructura base de este repo sin sobre-ingenieria.

Instrucciones:
1) Revisa primero AGENTS.md, specs activas y docs/architecture/overview.md.
2) Antes de proponer cambios, verifica practicas actuales en documentacion oficial:
   - GitHub Copilot custom instructions y custom agents
   - GitHub Actions workflow syntax
   - Claude Code memory/CLAUDE.md
   - AGENTS.md spec
   - (si aplica) estandares de dominio (ej: HL7 FHIR)
3) Propon solo la version minima viable y escalable.
4) Explica tradeoffs y deja fuera cualquier complejidad no necesaria ahora.
5) Si hay incertidumbre, indicala explicitamente y no asumas.
6) Entrega:
   - Plan por fases (foundation -> growth -> scale)
   - Cambios concretos por archivo
   - Checklist de validacion automatica
   - Links oficiales usados
```

## Politica de actualizacion continua
- Cadencia recomendada: mensual o por fase importante.
- Regla: actualizar links y decisiones solo con fuentes oficiales.
- Salida esperada de cada revision:
  - que sigue vigente
  - que quedo deprecado
  - ajuste minimo necesario

## Registro de links oficiales (evergreen)
### Multi-agente / repositorio
- AGENTS.md format: https://agents.md/
- AGENTS.md reference repo: https://github.com/openai/agents.md
- GitHub Copilot repo instructions: https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
- GitHub Copilot custom agents: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents
- GitHub Actions workflow syntax/reference: https://docs.github.com/en/actions/reference/workflows-and-actions
- Claude Code memory (`CLAUDE.md`): https://code.claude.com/docs/en/memory
- Codex product/context: https://openai.com/codex/

### Base Python / tooling
- Python packaging + `pyproject.toml`: https://packaging.python.org/en/latest/tutorials/packaging-projects/
- `setup.py` deprecation context: https://packaging.python.org/en/latest/discussions/setup-py-deprecated/

### Dominio salud (si aplica)
- FHIR current published version (R5): https://hl7.org/fhir/r5
- FHIR R4 (adopcion amplia en healthcare legacy): https://hl7.org/fhir/r4
- FHIR overview: https://www.hl7.org/fhir/overview.html
- SMART on FHIR docs: https://docs.smarthealthit.org/

## Aplicacion rapida al caso FHIR (ejemplo)
Si creas un repo de historia clinica electronica:
1. Conserva la estructura minima de esta guia.
2. Agrega una spec de cumplimiento (`specs/010-fhir-conformance.md`).
3. Agrega tests de contrato FHIR (payload/estructura/perfiles).
4. Define en `AGENTS.md` limites de seguridad y privacidad por defecto.
5. Mantiene CI primero para validacion, luego agrega complejidad clinica.

