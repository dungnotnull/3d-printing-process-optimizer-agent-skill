# CLAUDE.md — 3D Printing Process Design & Optimization (Additive Manufacturing)

**Skill slug:** `3d-printing-process-optimizer`
**Source idea:** #172 (Vietnamese backlog `ideas.md`)
**Cluster:** science-industry — Science, Engineering & Industry
**Tagline:** Optimize orientation, supports, and print parameters for complex additive-manufactured parts.
**Current phase:** Phase 5 — Integration & Cross-Skill Wiring (complete)

## Problem This Skill Solves
Engineers print complex parts with default slicer settings and then fight warping, weak layers, failed supports, and wasted material. This skill analyzes a part's geometry and target properties, recommends orientation/support/parameter strategy grounded in materials mechanics and DfAM principles, and continuously ingests printer-specific failure modes and material datasheets.

## Harness Flow (Summary)
1. **Intake** → `sub-evaluation-framework-selector` gathers inputs and frames the problem.
2. **Screen / select** → `sub-scoring-engine` selects the governing framework and screens risk/scope.
3. **Score / analyze** → `sub-failure-mode-updater` produces a multi-dimensional score against named frameworks.
4. **Knowledge refresh** → optional `tools/knowledge_updater.py` run keeps SECOND-KNOWLEDGE-BRAIN.md current.
5. **Gate** → quality / evidence gates must pass.
6. **Synthesize** → main harness emits the scored deliverable + prioritized improvement roadmap.

## Sub-skills
- `skills/sub-evaluation-framework-selector.md` — Identify the process (FDM/SLA/SLS/DMLS), material class, and the governing DfAM constraints for the part.
- `skills/sub-scoring-engine.md` — Score candidate orientations and parameter sets for strength, support cost, surface finish, and print-time/printability.
- `skills/sub-failure-mode-updater.md` — Ingest printer/material failure-mode reports and datasheets to refine parameter recommendations.
- `skills/sub-improvement-roadmap.md` — Output a prioritized print-setup recommendation with orientation, supports, parameters, and a test-print plan.

## Tools Required
WebSearch, WebFetch, Read, Write, Bash

## Knowledge Sources (for crawl + reasoning)
- ASTM/ISO 52900 additive manufacturing standards
- Manufacturer material datasheets (Prusa, Ultimaker, Stratasys, EOS)
- ArXiv (cond-mat.mtrl-sci, physics.app-ph) for AM mechanics research
- Reputable AM communities & knowledge bases (All3DP, Hubs, slicer docs)
- Google Scholar for process-parameter optimization studies

## Supporting Python Tools
- `tools/knowledge_updater.py` — production-grade crawl4ai + WebSearch pipeline that fetches latest papers/reports from the domain sources above, scores by recency + relevance, deduplicates by URL/DOI hash, and appends to `SECOND-KNOWLEDGE-BRAIN.md`. Supports `--dry-run`, `--since`, `--config`, `--timeout`, `--max-retries`, and `--init-config`. Recommended schedule: weekly cron.
- `tools/test_knowledge_updater.py` — unit tests for the knowledge updater.
- `tests/validate_fixtures.py` — validates all scenario fixtures against JSON well-formedness.

## Shared Schemas
- `schemas/scoring-schema.json` — JSON Schema definitions for `EvaluationFrame`, `ScoreCard`, `FailureDiagnosis`, and `Roadmap`.
- `docs/cross-skill-wiring.md` — reuse patterns for sibling `science-industry` skills.

## Active Development Tasks
- [x] Scaffold all required deliverables
- [x] Define >=3 sub-skills with quality gates
- [x] Ground scoring in named world-renowned frameworks
- [x] Wire knowledge_updater crawl sources
- [x] Expand SECOND-KNOWLEDGE-BRAIN with curated authoritative entries
- [x] Add regression fixtures from the test scenarios
- [x] Complete cross-skill wiring and shared scoring schema
- [x] Validate all Python code and fixtures

## Reference Docs (this folder)
- `PROJECT-detail.md` — full technical spec
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — phase roadmap
- `SECOND-KNOWLEDGE-BRAIN.md` — self-improving knowledge base
- `skills/main.md` — harness entry point
- `schemas/scoring-schema.json` — shared schemas
- `docs/cross-skill-wiring.md` — cluster reuse guide
- `tests/test-scenarios.md` — scenario-based test plan
- `tests/fixtures/` — regression fixtures
