# Cross-Skill Wiring — science-industry / 3D Printing Process Optimizer

## Purpose
This document defines how the sub-skills and shared schemas of `3d-printing-process-optimizer` can be reused by sibling skills in the `science-industry` cluster without duplicating logic.

## Reusable Sub-Skills

| Sub-skill | Location | Reuse Pattern | Cluster Siblings Likely to Reuse |
|---|---|---|---|
| `sub-evaluation-framework-selector` | `skills/sub-evaluation-framework-selector.md` | Intake framing, process/material normalization, geometry constraint extraction | cnc-machining-process-planner, welding-process-selector, composites-layup-designer |
| `sub-scoring-engine` | `skills/sub-scoring-engine.md` | Multi-candidate scoring with framework-grounded dimensions and weighted aggregation | materials-selection-assistant, manufacturing-cost-estimator |
| `sub-failure-mode-updater` | `skills/sub-failure-mode-updater.md` | Symptom-to-cause mapping, parameter adjustment with confidence flags | predictive-maintenance-diagnostician, quality-defect-analyzer |
| `sub-improvement-roadmap` | `skills/sub-improvement-roadmap.md` | Effort×impact ranking and test-plan synthesis | continuous-improvement-coach, experiment-designer |

## Shared Artifacts

- **Scoring Schema:** `schemas/scoring-schema.json` — JSON Schema definitions for `EvaluationFrame`, `ScoreCard`, `FailureDiagnosis`, and `Roadmap`.
- **Knowledge Brain:** `SECOND-KNOWLEDGE-BRAIN.md` — curated AM-specific sources; siblings should create their own brain files but may reuse the evidence-tier concept.
- **Python Updater:** `tools/knowledge_updater.py` — generic enough to be copied and reconfigured for other domains via `--config` and `SearchProvider` subclassing.

## Wiring Rules

1. **No duplicated framework logic.** A sibling skill that needs a DfAM-like framework should invoke `sub-evaluation-framework-selector` or adapt its own framework-selector that references `schemas/scoring-schema.json`.
2. **Schema compatibility.** Any sibling that consumes the outputs of `sub-scoring-engine` must validate against `schemas/scoring-schema.json#/definitions/ScoreCard`.
3. **Evidence tiers are shared.** Use the same 5-tier evidence scale across the cluster so that cross-skill comparisons are meaningful.
4. **Knowledge refresh decoupled.** The `knowledge_updater.py` tool should be configured per skill via a dedicated JSON config file; never hard-code one skill's queries into another skill's copy of the tool.

## Integration Example

A sibling skill `cnc-machining-process-planner` could:
1. Replace the AM-specific governing frameworks with ISO/ASTM machining frameworks.
2. Reuse `schemas/scoring-schema.json` by changing dimension names inside `DimensionScore`.
3. Call `sub-scoring-engine` pattern (copy and specialize) to score candidate setups.
4. Use `sub-improvement-roadmap` pattern to rank tooling/fixturing actions by effort×impact.

## Maintenance Contract

- When a shared schema changes, update this document and bump the schema version in `$id`.
- New sub-skill reuse cases should be added to the table above.
- Keep `SECOND-KNOWLEDGE-BRAIN.md` domain-specific; siblings must maintain separate brain files.
