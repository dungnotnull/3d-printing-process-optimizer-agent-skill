# PROJECT-detail.md — 3D Printing Process Design & Optimization (Additive Manufacturing)

## Executive Summary
This skill is a full Claude harness that turns optimize orientation, supports, and print parameters for complex additive-manufactured parts. It operates research-first: every material judgment is grounded in a named, citable framework and, where possible, a freshly retrieved source. It produces a professional-grade deliverable: a multi-dimensional score against the chosen framework plus a prioritized, effort/impact-ranked improvement roadmap.

## Problem Statement
Engineers print complex parts with default slicer settings and then fight warping, weak layers, failed supports, and wasted material. This skill analyzes a part's geometry and target properties, recommends orientation/support/parameter strategy grounded in materials mechanics and DfAM principles, and continuously ingests printer-specific failure modes and material datasheets.

## Target Users & Use Cases
Primary users are practitioners and decision-makers in the **Science, Engineering & Industry** domain. Trigger examples:
1. User uploads a bracket geometry and asks for the orientation that maximizes load-direction strength.
2. Part has a 70-degree overhang; skill recommends support strategy or a reorientation to avoid supports.
3. PETG prints warp at the corners; skill diagnoses cooling/bed-adhesion parameters and proposes fixes.
4. User wants a smooth top surface on a curved part; skill recommends SLA vs FDM and slice settings.
5. Metal DMLS part needs minimal residual stress; skill recommends orientation and a DOE test matrix.
6. User submits failing prints; failure-mode updater matches symptoms to known causes and corrects parameters.

## Harness Architecture
```
/3d-printing-process-optimizer (main.md harness)
  -> sub-evaluation-framework-selector              [intake / framing]
  -> sub-scoring-engine              [framework selection / risk-scope screen]
  -> knowledge refresh   [SECOND-KNOWLEDGE-BRAIN via knowledge_updater.py]
  -> sub-failure-mode-updater              [multi-dimensional scoring]
  -> evidence + challenge gate
  -> improvement roadmap [prioritized, effort/impact]
  -> SYNTHESIZE          [final scored deliverable]
```

## Full Sub-Skill Catalog
### sub-evaluation-framework-selector
- **Purpose:** Identify the process (FDM/SLA/SLS/DMLS), material class, and the governing DfAM constraints for the part.
- **Inputs:** outputs of the prior stage + user-provided context.
- **Outputs:** structured findings passed to the next stage.
- **Tools:** WebSearch, WebFetch, Read, Write, Bash
- **Quality gate:** output is schema-valid, evidence-linked, and framework-grounded before the harness proceeds.
### sub-scoring-engine
- **Purpose:** Score candidate orientations and parameter sets for strength, support cost, surface finish, and print-time/printability.
- **Inputs:** outputs of the prior stage + user-provided context.
- **Outputs:** structured findings passed to the next stage.
- **Tools:** WebSearch, WebFetch, Read, Write, Bash
- **Quality gate:** output is schema-valid, evidence-linked, and framework-grounded before the harness proceeds.
### sub-failure-mode-updater
- **Purpose:** Ingest printer/material failure-mode reports and datasheets to refine parameter recommendations.
- **Inputs:** outputs of the prior stage + user-provided context.
- **Outputs:** structured findings passed to the next stage.
- **Tools:** WebSearch, WebFetch, Read, Write, Bash
- **Quality gate:** output is schema-valid, evidence-linked, and framework-grounded before the harness proceeds.
### sub-improvement-roadmap
- **Purpose:** Output a prioritized print-setup recommendation with orientation, supports, parameters, and a test-print plan.
- **Inputs:** outputs of the prior stage + user-provided context.
- **Outputs:** structured findings passed to the next stage.
- **Tools:** WebSearch, WebFetch, Read, Write, Bash
- **Quality gate:** output is schema-valid, evidence-linked, and framework-grounded before the harness proceeds.

## Skill File Format Specification
Every skill file uses YAML frontmatter (`name`, `description`) followed by the required sections: Role & Persona, Workflow (Harness Flow), Sub-skills Available, Tools, Output Format, Quality Gates. The main harness invokes sub-skills via the Skill tool in the order shown above.

## E2E Execution Flow
1. Parse the user request; if inputs are insufficient, `sub-evaluation-framework-selector` asks targeted intake questions.
2. `sub-scoring-engine` selects the governing framework(s) and screens scope/risk; branch to a refusal or disclaimer if out of scope.
3. Refresh knowledge if the brain is stale (>7 days) and WebSearch/WebFetch are available; otherwise degrade gracefully to internal knowledge with a stated limitation.
4. `sub-failure-mode-updater` scores each dimension, citing evidence per claim.
5. Run the evidence/quality gate(s) and a devil's-advocate challenge pass.
6. Emit the scored report + roadmap in the Output Format below.

## SECOND-KNOWLEDGE-BRAIN Integration
- **Sources:** ASTM/ISO 52900 additive manufacturing standards; Manufacturer material datasheets (Prusa, Ultimaker, Stratasys, EOS); ArXiv (cond-mat.mtrl-sci, physics.app-ph) for AM mechanics research; Reputable AM communities & knowledge bases (All3DP, Hubs, slicer docs); Google Scholar for process-parameter optimization studies
- **Crawl config:** see `tools/knowledge_updater.py` (ArXiv categories cond-mat.mtrl-sci, physics.app-ph; domain queries seeded from the idea).
- **Append format:** date-stamped entries with Title, Authors, Year, Venue, DOI/URL, key finding, relevance note; deduplicated by URL/DOI hash.

## Supporting Tools Spec — knowledge_updater.py
- **Inputs:** search queries + source list (in-file config), optional `--since` date.
- **Outputs:** appended entries in `SECOND-KNOWLEDGE-BRAIN.md` + a run log.
- **Schedule:** weekly cron (graceful no-op when offline).

## Quality Gates
- **Evidence gate:** every material claim is traceable to a cited source or a prior step; prefer the highest evidence tier available.
- **Framework gate:** all scoring is grounded in the named frameworks below — never ad-hoc criteria.
- **Challenge gate:** a devil's-advocate pass has stress-tested the recommendation before it is shown.

## Test Scenarios
See `tests/test-scenarios.md` (>=5 concrete scenarios with expected harness behavior).

## Key Design Decisions
1. Framework-grounded scoring only — no ad-hoc rubrics.
2. Research-first with graceful degradation when offline.
3. Composable sub-skills (>=3) so cluster siblings can reuse them.
4. Deliverable is an artifact (scored report + roadmap), not a chat reply.
5. Evidence/quality gate enforced before any sensitive/regulated output.
