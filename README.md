# 3D Printing Process Optimizer — Agent Skill

<div align="center">

<img src="https://img.shields.io/badge/Cluster-science--industry-0055ff" alt="Cluster">
<img src="https://img.shields.io/badge/Status-production--ready-brightgreen" alt="Status">
<img src="https://img.shields.io/badge/Phases-0--5%20complete-success" alt="Phases">
<img src="https://img.shields.io/badge/License-MIT-blue" alt="License">
<img src="https://img.shields.io/badge/Framework-DfAM%20%7C%20ISO%2FASTM%2052900%20%7C%20Taguchi-orange" alt="Frameworks">

**Optimize orientation, supports, and print parameters for complex additive-manufactured parts — grounded in named engineering frameworks and continuously refreshed evidence.**

</div>

---

## Table of Contents

- [Why this skill exists](#why-this-skill-exists)
- [What it does](#what-it-does)
- [Who it is for](#who-it-is-for)
- [Architecture](#architecture)
- [Governing frameworks](#governing-frameworks)
- [Repository layout](#repository-layout)
- [Quick start](#quick-start)
- [Usage examples](#usage-examples)
- [Sub-skills in detail](#sub-skills-in-detail)
- [Knowledge pipeline](#knowledge-pipeline)
- [Test scenarios](#test-scenarios)
- [Validation](#validation)
- [Cross-skill reuse](#cross-skill-reuse)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Why this skill exists

Engineers often print complex parts with default slicer settings and then fight predictable problems: warping, weak layers along the build direction, failed supports, poor surface finish, and wasted material. Most chat assistants answer these questions with generic tips. This skill answers them with a **research-first, framework-grounded process-engineering harness**:

- Every material judgment maps to a named, citable framework.
- Every score is traceable to evidence with an explicit confidence tier.
- Every recommendation includes a ranked improvement roadmap and a test-print verification plan.
- Knowledge is continuously refreshed from standards bodies, manufacturer datasheets, and peer-reviewed research.

The result is a **professional, reproducible artifact** rather than a casual chat reply.

---

## What it does

Given a part description, target process/material, and target properties, the harness:

1. **Frames** the problem — normalizes process, material, geometry constraints, and missing inputs.
2. **Selects** governing frameworks — DfAM, ISO/ASTM 52900, anisotropy mechanics, overhang rules, process-parameter mapping, Taguchi DOE.
3. **Scores** candidate orientations and parameter sets across five dimensions.
4. **Diagnoses** failure modes and refines parameters with current → recommended deltas.
5. **Refreshes** knowledge from `SECOND-KNOWLEDGE-BRAIN.md` if it is stale.
6. **Gates** output through evidence, framework, schema, and devil's-advocate challenge gates.
7. **Synthesizes** a scored report + prioritized improvement roadmap.

---

## Who it is for

Primary users are practitioners and decision-makers in **Science, Engineering & Industry**:

- Manufacturing engineers choosing build orientation for a load-bearing bracket.
- Designers deciding whether an overhang needs supports or a reorientation.
- Print farm operators diagnosing PETG warping, PLA stringing, or layer separation.
- Materials engineers optimizing DMLS parameters for residual-stress-sensitive metal parts.
- Researchers and educators who need transparent, citable reasoning for AM process decisions.

---

## Architecture

```
User request
    |
    v
[ skills/main.md harness ]
    |
    +--> sub-evaluation-framework-selector  (intake + framing)
    +--> sub-scoring-engine                  (framework selection + multi-dimensional scoring)
    +--> sub-failure-mode-updater             (symptom diagnosis + parameter refinement)
    +--> tools/knowledge_updater.py          (optional knowledge refresh)
    +--> sub-improvement-roadmap              (effort × impact ranking + test plan)
    |
    v
Quality gates (evidence / framework / challenge / schema)
    |
    v
Scored report + prioritized roadmap (7-section deliverable)
```

The harness refuses or degrades gracefully on:
- Insufficient inputs (asks up to 3 targeted questions).
- Unsupported processes or materials (clear scope disclaimer).
- Unsafe or regulated requests (weapons, medical implants, flight-critical aerospace without qualified review).
- Offline environments (uses seeded brain and states the limitation).

---

## Governing frameworks

All scoring dimensions must map to one of these named frameworks. The skill never uses ad-hoc rubrics.

| # | Framework | What it governs |
|---|-----------|-----------------|
| 1 | **DfAM (Design for Additive Manufacturing)** | Orientation, feature accessibility, self-supporting angles, build-direction trade-offs. |
| 2 | **Anisotropy & layer-adhesion mechanics** | Load-direction strength, Z-axis weakness, inter-layer fracture. |
| 3 | **ISO/ASTM 52900 series** | Terminology, process taxonomy, standards-based vocabulary. |
| 4 | **Overhang/bridging 45-degree rule** | Support need, support volume, removal cost, surface damage. |
| 5 | **Process-parameter mapping per polymer/metal class** | Temperature, speed, cooling, layer height, bed adhesion, retraction. |
| 6 | **Taguchi DOE for print-parameter optimization** | Orthogonal arrays, signal-to-noise analysis, experimental matrices. |

---

## Repository layout

```
3d-printing-process-optimizer/
├── CLAUDE.md                              # Skill manifest for Claude / Codex
├── PROJECT-detail.md                      # Full technical specification
├── PROJECT-DEVELOPMENT-PHASE-TRACKING.md    # Phase roadmap (all phases ✅)
├── README.md                              # This file
├── SECOND-KNOWLEDGE-BRAIN.md              # Curated, self-updating knowledge base
├── .gitignore                             # Python / editor cache exclusions
│
├── skills/
│   ├── main.md                            # Main harness entry point
│   ├── sub-evaluation-framework-selector.md
│   ├── sub-scoring-engine.md
│   ├── sub-failure-mode-updater.md
│   └── sub-improvement-roadmap.md
│
├── tools/
│   ├── knowledge_updater.py               # Production-grade knowledge pipeline
│   ├── knowledge_updater.json             # Default updater configuration
│   └── test_knowledge_updater.py          # Unit tests for the updater
│
├── schemas/
│   └── scoring-schema.json                # Shared JSON schemas for all sub-skill outputs
│
├── docs/
│   └── cross-skill-wiring.md              # Reuse patterns for science-industry siblings
│
└── tests/
    ├── test-scenarios.md                  # 6 concrete test scenarios
    ├── validate_fixtures.py               # Fixture validator
    └── fixtures/
        ├── scenario-1-frame.json
        ├── scenario-1-score.json
        ├── scenario-1-diagnosis.json
        ├── scenario-1-roadmap.json
        └── ... (24 fixtures across 6 scenarios)
```

---

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/dungnotnull/3d-printing-process-optimizer-agent-skill.git
cd 3d-printing-process-optimizer-agent-skill
```

### 2. Run the knowledge updater (dry-run recommended)

```bash
cd tools
python knowledge_updater.py --dry-run --verbose
```

For a live update over the network:

```bash
python knowledge_updater.py --max-results 10 --timeout 30
```

### 3. Validate the scenario fixtures

```bash
python tests/validate_fixtures.py
```

Expected output:

```text
All 24 fixtures are valid JSON and every scenario has complete artifacts.
```

### 4. Run the knowledge updater unit tests

```bash
cd tools
python -m pytest test_knowledge_updater.py -v
```

Or, without pytest:

```bash
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('tools').resolve()))
import test_knowledge_updater as t
t.test_entry_hash_uses_doi()
t.test_entry_hash_differs_by_url_when_no_doi()
t.test_relevance_counts_keywords_and_recency()
t.test_relevance_old_entry_gets_lower_score()
t.test_parse_arxiv_atom_extracts_entries()
t.test_existing_hashes_finds_hashes()
t.test_append_entries_deduplicates_and_appends()
t.test_append_entries_dry_run_does_not_write()
t.test_config_from_json()
t.test_not_older_than()
t.test_domain_crawl_provider_graceful_without_crawl4ai()
print('ALL KNOWLEDGE UPDATER TESTS PASSED')
"
```

---

## Usage examples

### Example 1 — PETG bracket orientation for Z-direction strength

**Input:**

```text
80×40×20 mm PETG bracket, load pulls along Z, one 70° overhang.
```

**Harness behavior:**
- `EvaluationFrame` selects **Anisotropy & layer-adhesion mechanics** as the dominant framework.
- `ScoreCard` recommends **Z-up flat** (load in XY plane) with `orientation_strength = 0.85`.
- `Roadmap` ranks support strategy and Taguchi DOE actions, with a verification plan.

### Example 2 — PETG corner warping diagnosis

**Input:**

```text
Flat PETG base plate warps at corners.
```

**Harness behavior:**
- `FailureDiagnosis` maps symptom → `thermal_warp_corner_lift`.
- Parameter adjustments include `bed_temp_c: 70 → 85` and first-layer fan reduction.
- `Roadmap` ranks brim, bed temperature, and DOE steps.

### Example 3 — DMLS Ti6Al4V residual-stress mitigation

**Input:**

```text
Ti6Al4V aerospace bracket, minimal residual stress, tight tolerances.
```

**Harness behavior:**
- Selects **Anisotropy mechanics** + **process-parameter mapping for metals**.
- Recommends scan strategy, stress-relief heat treatment, and a Taguchi DOE matrix.
- Adds a **flight-critical design-review disclaimer** before production recommendations.

---

## Sub-skills in detail

### `skills/main.md`
The orchestrator. Defines the 7-section output format, quality gates, refusal/degradation rules, and the shared schemas that all sub-skills must emit.

### `skills/sub-evaluation-framework-selector.md`
Transforms raw user input into a structured `EvaluationFrame` with normalized process/material, geometry constraints, target properties, missing inputs, and framework selection.

### `skills/sub-scoring-engine.md`
Generates candidate orientations, scores each across five framework-grounded dimensions, and emits a `ScoreCard` with weighted aggregate recommendation and parameter set.

### `skills/sub-failure-mode-updater.md`
Maps symptoms (warping, stringing, layer separation, etc.) to failure modes and emits concrete `parameter_adjustments` with current → recommended values, rationale, confidence, and side effects.

### `skills/sub-improvement-roadmap.md`
Synthesizes upstream artifacts into an effort × impact-ranked `Roadmap` with final orientation, support strategy, parameter set, ranked actions, and a test-print verification plan.

---

## Knowledge pipeline

`tools/knowledge_updater.py` is a production-grade, gracefully degrading pipeline:

- **Sources:** ArXiv `cond-mat.mtrl-sci` and `physics.app-ph`; authoritative domains (ASTM, ISO, All3DP).
- **Scoring:** keyword relevance + 2-year recency decay.
- **Deduplication:** SHA-1 hash of DOI or canonical URL.
- **Configurability:** JSON/YAML config via `--config`.
- **Safety:** `--dry-run` preview, `--since` date filter, `--timeout` and `--max-retries`, exponential backoff for 429/503 responses.
- **Extensibility:** pluggable `SearchProvider` class; swap in Serper/SerpAPI for broader web search.

Configuration file (`tools/knowledge_updater.json`):

```json
{
  "brain": "../SECOND-KNOWLEDGE-BRAIN.md",
  "arxiv_categories": ["cond-mat.mtrl-sci", "physics.app-ph"],
  "search_queries": [
    "additive manufacturing process parameter optimization",
    "FDM layer adhesion anisotropy",
    "support structure generation overhang",
    "design for additive manufacturing DfAM"
  ],
  "domains": ["astm.org", "iso.org", "all3dp.com"],
  "max_results": 15,
  "max_age_days": 730
}
```

---

## Test scenarios

Six end-to-end scenarios cover the target use cases from `PROJECT-detail.md`:

1. **Bracket orientation for maximum load-direction strength.**
2. **70° overhang — support strategy or reorientation.**
3. **PETG corner warping — cooling/bed-adhesion diagnosis.**
4. **Smooth curved top surface — SLA vs FDM process selection.**
5. **DMLS metal part — minimal residual stress + DOE test matrix.**
6. **Failing prints — multi-symptom failure-mode diagnosis.**

Each scenario has four JSON fixtures representing the expected outputs of the four sub-skills.

---

## Validation

| Check | Command | Expected result |
|---|---|---|
| Python syntax | `python -m py_compile tools/*.py tests/*.py` | No errors |
| Fixture validity | `python tests/validate_fixtures.py` | `All 24 fixtures are valid JSON...` |
| Updater unit tests | `python -m pytest tools/test_knowledge_updater.py -v` | All tests pass |
| Placeholder scan | Manual review | No `TODO`, `FIXME`, `dummy`, or `seed — populate` placeholders |

---

## Cross-skill reuse

The `science-industry` cluster can reuse this skill's artifacts without duplicating logic:

- **`schemas/scoring-schema.json`** — shared JSON schemas for `EvaluationFrame`, `ScoreCard`, `FailureDiagnosis`, `Roadmap`.
- **`docs/cross-skill-wiring.md`** — documented reuse patterns for sibling skills.
- **`tools/knowledge_updater.py`** — generic knowledge pipeline configurable for other domains.
- **Evidence tiers** — consistent 5-tier evidence scale across the cluster.

Siblings such as CNC machining planner, welding process selector, or composites layup designer can import the schemas and adapt the framework names while keeping the same harness structure.

---

## Roadmap

This skill is intentionally complete for production use. Future enhancements (outside the current phase scope) could include:

- Integration with real search APIs (Serper, Google Programmable Search Engine).
- Direct STL/mesh analysis hooks (compute actual overhang angles and support volume).
- Slicer profile export (PrusaSlicer / Cura / Bambu Studio ini generation).
- Multi-material and continuous-fiber AM extensions.

---

## Contributing

Contributions are welcome. If you extend a sub-skill or add a new failure-mode mapping:

1. Keep all scoring dimensions mapped to the named governing frameworks.
2. Add or update regression fixtures in `tests/fixtures/`.
3. Run `python tests/validate_fixtures.py` and the updater unit tests.
4. Update `SECOND-KNOWLEDGE-BRAIN.md` with authoritative sources if adding new evidence claims.
5. Follow the 5-tier evidence scale and cite sources for every material claim.

---

## License

MIT License — see [LICENSE](./LICENSE) or use freely for research, commercial, and open-source projects.

---

## Acknowledgments

Built on top of widely accepted engineering knowledge:
- ISO/ASTM 52900 additive manufacturing standards
- DfAM research and design-rule literature
- Manufacturer datasheets and community knowledge bases
- ArXiv research in materials science and applied physics

The skill does not claim to replace qualified engineering review for safety-critical or regulated applications; it provides a transparent, evidence-grounded starting point.

---

<div align="center">

**Made for the science-industry cluster — optimize prints with engineering rigor.**

</div>
