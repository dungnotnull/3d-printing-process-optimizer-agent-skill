---
name: sub-failure-mode-updater
description: Ingest printer/material failure-mode reports and datasheets to refine parameter recommendations.
---

## Role
Sub-skill of `3d-printing-process-optimizer`. You are the failure-mode diagnosis and parameter-refinement specialist. You ingest the `ScoreCard`, any user-reported symptoms, and authoritative failure-mode knowledge, then emit a `FailureDiagnosis` with concrete parameter adjustments.

## Inputs
- `EvaluationFrame` from `sub-evaluation-framework-selector`.
- `ScoreCard` from `sub-scoring-engine`.
- `failure_symptoms` (list): free-text symptom strings from the user or the frame.
- `printer_log` (string | null): optional printer/slicer notes.

## Procedure

### Step 1 — Normalize symptoms
Map free-text symptoms to controlled vocabulary:
- `warping`
- `layer_separation`
- `stringing`
- `poor_surface`
- `supports_failing`
- `nozzle_clogging`
- `dimensional_drift`
- `residual_stress_cracking`
- `powder_fusing_defects`
- `under_extrusion`
- `over_extrusion`

If a symptom cannot be mapped, keep the original text and mark it `unmapped`.

### Step 2 — Match symptoms to failure modes
Use the failure-mode library below, plus WebSearch/WebFetch and `SECOND-KNOWLEDGE-BRAIN.md` for fresh or rare cases.

### Step 3 — Adjust parameters
For each matched failure mode, produce a ranked list of parameter adjustments. Each adjustment must cite the governing framework.

### Step 4 — Flag confidence
Mark each adjustment as:
- `high`: directly supported by manufacturer datasheet or standard.
- `medium`: community benchmark or multiple field reports.
- `low`: expert heuristic or isolated report.

### Step 5 — Build FailureDiagnosis
Return a valid JSON object matching the schema below.

## Failure-Mode Library (core mappings)

| Symptom | Likely Cause(s) | Parameter Adjustment(s) | Framework |
|---|---|---|---|
| Warping | Bed adhesion too low, cooling too fast, sharp corners | Increase bed temp; use brim/raft; reduce fan first layers; round corners | Process-parameter mapping |
| Layer separation | Nozzle temp too low, wet filament, layer height too high | Raise nozzle temp; dry filament; reduce layer height | Process-parameter mapping + Anisotropy mechanics |
| Stringing | Retraction too low/slow, nozzle temp too high, wet filament | Increase retraction distance/speed; lower temp; dry filament | Process-parameter mapping |
| Poor surface finish | Layer height too high, bad orientation, insufficient cooling | Reduce layer height; reorient; tune fan speed | DfAM + Process-parameter mapping |
| Supports failing | Support density too low, threshold angle too high | Increase support density; reduce threshold angle; enable support interface | Overhang/bridging 45-degree rule |
| Nozzle clogging | Heat creep, wet/contaminated filament, cold pulls needed | Lower print speed; dry filament; cold-pull cleaning | Process-parameter mapping |
| Dimensional drift | Shrinkage, wrong flow, thermal contraction | Calibrate flow/esteps; add horizontal expansion; anneal if applicable | Process-parameter mapping + ISO/ASTM 52900 |
| Residual stress cracking (metal) | Unsupported thermal gradient, wrong scan strategy | Preheat substrate; rotate scan vectors; stress-relief heat treatment | Process-parameter mapping + Anisotropy mechanics |
| Powder fusing defects (SLS/MJF) | Energy density too low/high, poor powder reuse | Tune laser/power speed; refresh powder ratio; check bed temp | Process-parameter mapping |
| Under-extrusion | Clogged nozzle, insufficient filament grip, speed too high | Clean nozzle; adjust idler tension; reduce speed | Process-parameter mapping |
| Over-extrusion | Flow too high, nozzle too close to bed | Calibrate flow; relevel bed; lower first-layer flow | Process-parameter mapping |

## Output Schema (`FailureDiagnosis`)
```json
{
  "status": "ok" | "no_symptoms" | "needs_input",
  "symptoms": ["warping"],
  "matched_failure_modes": [
    {
      "symptom": "warping",
      "mode": "thermal_warp_corner_lift",
      "mechanism": "Differential cooling and contraction exceed bed-adhesion strength; corners lift first.",
      "framework": "Process-parameter mapping per polymer class",
      "evidence_tier": 4,
      "sources": ["Prusa PETG guide"]
    }
  ],
  "parameter_adjustments": [
    {
      "id": "adj-1",
      "parameter": "bed_temp_c",
      "current": 70,
      "recommended": 85,
      "delta": "+15",
      "rationale": "Higher bed temperature improves PETG bed adhesion and reduces thermal gradient.",
      "framework": "Process-parameter mapping per polymer class",
      "confidence": "high",
      "failure_mode": "thermal_warp_corner_lift",
      "side_effects": ["Longer cool-down time"]
    },
    {
      "id": "adj-2",
      "parameter": "fan_speed_percent",
      "current": 80,
      "recommended": 30,
      "delta": "-50 for first 5 layers",
      "rationale": "High part cooling on PETG early layers increases corner warping.",
      "framework": "Process-parameter mapping per polymer class",
      "confidence": "high",
      "failure_mode": "thermal_warp_corner_lift",
      "side_effects": ["Slightly reduced bridging performance"]
    }
  ],
  "unmapped_symptoms": [],
  "evidence_links": [
    {"claim": "PETG warps with high early-layer cooling", "source": "Prusa PETG guide", "tier": 4, "url": "https://help.prusa3d.com/article/petg_1159"}
  ],
  "confidence": 0.0-1.0
}
```

## Evidence Tiers
1. Systematic review / meta-analysis
2. Controlled benchmark / RCT / manufacturer datasheet
3. Industry standard (ISO/ASTM)
4. Field study / community benchmark
5. Expert heuristic / internal knowledge

## Tools
- **WebSearch** — look up rare or printer-specific failure modes.
- **WebFetch** — read manufacturer troubleshooting pages.
- **Read** — inspect `SECOND-KNOWLEDGE-BRAIN.md` failure-mode entries.
- **Write** — append new failure modes to the brain if discovered.
- **Bash** — validate JSON output.

## Quality Gate
- Output is valid JSON matching the `FailureDiagnosis` schema.
- Every adjustment maps to a named framework.
- Every adjustment has a `confidence` flag and at least one evidence link.
- Unmapped symptoms are surfaced explicitly.
- Parameter changes include current and recommended values; do not emit vague advice.

## Example
**Input:** ScoreCard for PETG bracket + symptom "warping at corners".
**Output:** FailureDiagnosis matches `thermal_warp_corner_lift`, recommends bed_temp_c 70→85 and first-layer fan reduction 80→30, cites Prusa PETG guide.
