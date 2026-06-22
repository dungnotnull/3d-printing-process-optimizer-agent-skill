# tests/test-scenarios.md — 3D Printing Process Design & Optimization (Additive Manufacturing)

Scenario-based tests for the `3d-printing-process-optimizer` harness. Each scenario asserts the harness flow, framework-grounded scoring, gate enforcement, and deliverable shape.

## Regression Fixtures
For every scenario there is a JSON fixture in `tests/fixtures/` describing the expected upstream artifacts:
- `scenario-{N}-frame.json` — expected `EvaluationFrame` from `sub-evaluation-framework-selector`.
- `scenario-{N}-score.json` — expected `ScoreCard` from `sub-scoring-engine`.
- `scenario-{N}-diagnosis.json` — expected `FailureDiagnosis` from `sub-failure-mode-updater`.
- `scenario-{N}-roadmap.json` — expected `Roadmap` from `sub-improvement-roadmap`.

A validation script `tests/validate_fixtures.py` checks that every fixture is valid JSON and matches the documented schemas.

## Scenario 1 — Bracket orientation for maximum Z-direction strength
- **Given:** User uploads a bracket geometry and asks for the orientation that maximizes load-direction strength.
- **Inputs:**
  - `part_description`: "80×40×20 mm PETG bracket, load pulls along Z (vertical), 70° overhang on one side."
  - `process_hint`: FDM
  - `material_hint`: PETG
  - `target_properties`: strength_direction="z"
- **Expected harness behavior:**
  1. `sub-evaluation-framework-selector` returns `EvaluationFrame` with `dominant_framework="Anisotropy & layer-adhesion mechanics"`, `secondary_frameworks` includes DfAM and overhang rule, `warp_risk="medium"`.
  2. `sub-scoring-engine` returns `ScoreCard` with at least 3 candidates; recommended candidate aligns load with XY layers (i.e., Z-up flat or tilted), orientation_strength ≥ 0.7, cites anisotropy framework.
  3. `sub-failure-mode-updater` returns `FailureDiagnosis` with matched failure modes for 70° overhang supports.
  4. `sub-improvement-roadmap` returns `Roadmap` with support threshold ≤ 55°, ranked actions, and verification plan.
  5. Final report includes all 7 output sections, every score cites framework + evidence.
- **Pass criteria:** all quality gates pass; every score cites its framework; roadmap items are effort/impact-ranked.
- **Fixture:** `tests/fixtures/scenario-1-*.json`

## Scenario 2 — 70° overhang support strategy
- **Given:** Part has a 70-degree overhang; skill recommends support strategy or a reorientation to avoid supports.
- **Inputs:**
  - `part_description`: "Complex housing with a 70° overhang and a 12 mm bridge. Target FDM, PLA, functional surface finish."
  - `process_hint`: FDM
  - `material_hint`: PLA
  - `target_properties`: surface_finish="functional"
- **Expected harness behavior:**
  1. `EvaluationFrame` notes `overhang_angles_deg=[70]`, `bridges_mm=[12]`, `warp_risk="low"`.
  2. `ScoreCard` scores support_cost lower for orientations that expose the 70° face; at least one candidate reorients the overhang to avoid supports or accepts supports with density ≥ 15%.
  3. Final roadmap recommends either reorientation (preferred) or support strategy with threshold ≤ 50° and a removal plan.
- **Pass criteria:** recommendation addresses the overhang; evidence cites Overhang/bridging 45-degree rule.
- **Fixture:** `tests/fixtures/scenario-2-*.json`

## Scenario 3 — PETG corner warping diagnosis
- **Given:** PETG prints warp at the corners; skill diagnoses cooling/bed-adhesion parameters and proposes fixes.
- **Inputs:**
  - `part_description`: "Flat PETG base plate, 120×80×5 mm, corners lifting after 10 layers."
  - `process_hint`: FDM
  - `material_hint`: PETG
  - `failure_symptoms`: ["warping"]
- **Expected harness behavior:**
  1. `EvaluationFrame`: `warp_risk="high"`, `dominant_framework="Process-parameter mapping per polymer class"`.
  2. `FailureDiagnosis` matches `thermal_warp_corner_lift` and produces parameter adjustments: bed_temp_c 70→85, first-layer fan reduced.
  3. `ScoreCard` printability score reflects high warp risk.
  4. `Roadmap` ranks bed-temp/fan/brim actions high and includes verification threshold: corner lift < 0.2 mm.
- **Pass criteria:** diagnosis maps symptom to mechanism; adjustments include concrete current→recommended values.
- **Fixture:** `tests/fixtures/scenario-3-*.json`

## Scenario 4 — Smooth top surface on curved part (SLA vs FDM)
- **Given:** User wants a smooth top surface on a curved part; skill recommends SLA vs FDM and slice settings.
- **Inputs:**
  - `part_description`: "Curved consumer-grade enclosure, radius 30 mm, visible top surface must be smooth."
  - `process_hint`: unknown
  - `material_hint`: unknown
  - `target_properties`: surface_finish="smooth"
- **Expected harness behavior:**
  1. `EvaluationFrame` marks process/material as unknown and asks targeted clarification (max 3 questions).
  2. If user confirms SLA resin: `ScoreCard` recommends SLA with layer_height_mm ≤ 0.05, orientation to minimize support touch-points on the curved surface.
  3. If user confirms FDM: `ScoreCard` recommends fine layer height (≤0.15 mm), orientation that puts curved surface in XY plane.
  4. Final report compares processes using surface_finish and support_cost dimensions.
- **Pass criteria:** process recommendation is evidence-linked; orientation preserves the visible surface.
- **Fixture:** `tests/fixtures/scenario-4-*.json`

## Scenario 5 — Metal DMLS part minimal residual stress + DOE matrix
- **Given:** Metal DMLS part needs minimal residual stress; skill recommends orientation and a DOE test matrix.
- **Inputs:**
  - `part_description`: "Ti6Al4V aerospace bracket, thin walls, critical fatigue life, minimal residual stress desired."
  - `process_hint`: DMLS
  - `material_hint`: Ti6Al4V
  - `target_properties`: strength_direction="xy", dimensional_accuracy="tight"
- **Expected harness behavior:**
  1. `EvaluationFrame`: `dominant_framework="Anisotropy & layer-adhesion mechanics"`, secondary frameworks include process-parameter mapping and ISO/ASTM 52900.
  2. `ScoreCard` includes scope disclaimer for flight-critical parts unless user explicitly accepts design-review-required disclaimer.
  3. `Roadmap` includes a Taguchi DOE matrix (laser power × scan speed × hatch spacing) and a stress-relief heat-treatment step.
  4. Evidence links include DebRoy et al. residual-stress review and EOS DMLS guide.
- **Pass criteria:** DOE matrix is concrete; residual-stress mitigation is framework-grounded; regulated disclaimer present if applicable.
- **Fixture:** `tests/fixtures/scenario-5-*.json`

## Scenario 6 — Failing prints failure-mode updater
- **Given:** User submits failing prints; failure-mode updater matches symptoms to known causes and corrects parameters.
- **Inputs:**
  - `part_description`: "PLA print shows stringing and poor top surface."
  - `process_hint`: FDM
  - `material_hint`: PLA
  - `failure_symptoms`: ["stringing", "poor_surface"]
- **Expected harness behavior:**
  1. `FailureDiagnosis` maps `stringing` → retraction/temp adjustments; `poor_surface` → layer height/cooling/orientation adjustments.
  2. Parameter adjustments have current/recommended values and confidence flags.
  3. `Roadmap` actions are ranked by effort × impact; top actions are low-effort/high-impact.
- **Pass criteria:** both symptoms matched; every adjustment cites process-parameter mapping framework.
- **Fixture:** `tests/fixtures/scenario-6-*.json`

## Cross-cutting checks
- **Graceful degradation:** with WebSearch/WebFetch disabled, the harness still produces a deliverable and explicitly states the knowledge-currency limitation.
- **Refusal/scope:** out-of-scope or unsafe requests (weapons, regulated medical implants, flight-critical aerospace without disclaimer) are refused or redirected.
- **Determinism of structure:** every run yields the seven Output-Format sections.
- **Schema validity:** `tests/validate_fixtures.py` passes for all fixture JSON files.

## Running the validation
```bash
python tests/validate_fixtures.py
```
Expected output: `All X fixtures are valid JSON.`
