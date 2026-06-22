---
name: sub-scoring-engine
description: Score candidate orientations and parameter sets for strength, support cost, surface finish, and print-time/printability against named frameworks.
---

## Role
Sub-skill of `3d-printing-process-optimizer`. You are the quantitative scoring engine. You receive an `EvaluationFrame` and produce a `ScoreCard` that ranks candidate orientations and parameter sets. Every score cites the governing framework and the evidence used.

## Inputs
- `EvaluationFrame` JSON from `sub-evaluation-framework-selector`.
- Optional user constraints: maximum support volume, required surface roughness Ra, layer height preference.

## Procedure

### Step 1 — Validate the EvaluationFrame
- If `status != "ok"`, propagate the status and stop.
- If `supported == false`, return a `ScoreCard` with a scope disclaimer and no numeric scores.

### Step 2 — Generate candidate orientations
Create at least 3 candidate build orientations:
1. **Z-up (flat on build plate)** — largest XY footprint, shortest Z height.
2. **X-up or Y-up (on edge)** — load direction aligned with Z-axis layers if strength is required along that axis.
3. **Tilted (15°–45°)** — compromise between surface finish and support need.

For each orientation compute:
- Layer direction relative to load direction.
- Estimated support volume (from overhang/bridge analysis).
- Number of supported surfaces and accessibility for removal.

### Step 3 — Score dimensions
For each candidate, produce five scores in `[0.0, 1.0]`.

#### orientation_strength
Framework: **Anisotropy & layer-adhesion mechanics (Z-axis weakness)**.
- 1.0: load direction is in-plane with layers (XY), layers not perpendicular to principal stress.
- 0.0: load direction is purely across layers (Z) with no compensation.
- Intermediate if tilted or reinforced.

#### support_cost
Framework: **Overhang/bridging 45-degree rule and support-generation heuristics**.
- 1.0: self-supporting, no supports.
- 0.0: severe overhangs requiring dense, hard-to-remove supports.

#### surface_finish
Framework: **DfAM + Process-parameter mapping**.
- 1.0: top surfaces are flat/curved in XY with fine layer height; stair-stepping minimized.
- 0.0: steep curved surfaces facing build direction with coarse layers.

#### printability
Framework: **Process-parameter mapping per polymer/metal class**.
- 1.0: geometry and material well within known print window (temperature, speed, cooling, bed adhesion).
- 0.0: high warp risk, extreme temperature sensitivity, or unsupported configuration.

#### parameter_confidence
Framework: **Taguchi DOE for print-parameter optimization**.
- 1.0: parameters derived from a completed DOE or manufacturer benchmark.
- 0.0: parameters are pure guess with no experimental backing.

### Step 4 — Select the recommended orientation
Aggregate the per-dimension scores using a weighted sum. Default weights:
```
orientation_strength: 0.30
support_cost: 0.25
surface_finish: 0.20
printability: 0.15
parameter_confidence: 0.10
```
If the user specifies a priority, adjust weights and state the adjustment.

### Step 5 — Recommend parameters
Map the chosen orientation to a starting parameter set based on material class and process. Include:
- Layer height, wall/top/bottom counts, infill % and pattern.
- Nozzle/laser speed, extrusion/bed temperature, cooling fan %.
- Support density, overhang threshold, support interface.
- Retraction settings for stringing-prone materials.
- Special notes (e.g., annealing for ASA/PC).

### Step 6 — Build the ScoreCard
Return a valid JSON object matching the schema below.

### Step 7 — Quality gate self-check
- All scores in `[0.0, 1.0]`.
- Every score has `framework` and `evidence` fields.
- Aggregate score is deterministic given the same inputs and weights.
- Unsupported processes return a scope disclaimer, not fabricated numbers.

## Output Schema (`ScoreCard`)
```json
{
  "status": "ok" | "unsupported" | "needs_input",
  "candidates": [
    {
      "name": "Z-up flat",
      "rotation": {"x_deg": 0, "y_deg": 0, "z_deg": 0},
      "scores": {
        "orientation_strength": {"value": 0.85, "framework": "Anisotropy & layer-adhesion mechanics", "evidence": "Z layers perpendicular to XY load; source: [expert heuristic]"},
        "support_cost": {"value": 0.90, "framework": "Overhang/bridging 45-degree rule", "evidence": "Only 70° overhang needs support; source: [expert heuristic]"},
        "surface_finish": {"value": 0.70, "framework": "DfAM + Process-parameter mapping", "evidence": "Top surface in XY; side surfaces show layer lines"},
        "printability": {"value": 0.80, "framework": "Process-parameter mapping per polymer class", "evidence": "PETG on heated bed; source: manufacturer datasheet / community profile"},
        "parameter_confidence": {"value": 0.60, "framework": "Taguchi DOE", "evidence": "Default PETG profile; no part-specific DOE yet"}
      },
      "aggregate": 0.81
    }
  ],
  "recommended_candidate": "Z-up flat",
  "weights": {
    "orientation_strength": 0.30,
    "support_cost": 0.25,
    "surface_finish": 0.20,
    "printability": 0.15,
    "parameter_confidence": 0.10
  },
  "parameter_recommendations": {
    "layer_height_mm": 0.20,
    "wall_count": 3,
    "top_bottom_layers": 4,
    "infill_percent": 40,
    "infill_pattern": "gyroid",
    "nozzle_temp_c": 240,
    "bed_temp_c": 80,
    "fan_speed_percent": 40,
    "print_speed_mm_s": 50,
    "support_threshold_deg": 50,
    "support_density_percent": 15,
    "support_interface": true,
    "retraction_distance_mm": 1.5,
    "retraction_speed_mm_s": 35,
    "special_notes": ["Keep part cooling low for first layers to avoid warping"]
  },
  "scope_disclaimer": null,
  "evidence_links": [
    {"claim": "PETG warps with high cooling", "source": "Prusa PETG guide", "tier": 4, "url": "https://help.prusa3d.com/article/petg_1159"}
  ]
}
```

## Framework Map
| Dimension | Framework | Typical Evidence |
|---|---|---|
| orientation_strength | Anisotropy & layer-adhesion mechanics | Datasheet tensile XY vs Z, research paper, [expert heuristic] |
| support_cost | Overhang/bridging 45-degree rule | Geometry analysis, slicer heuristic, DfAM guide |
| surface_finish | DfAM + Process-parameter mapping | Layer height / stair-step geometry reasoning |
| printability | Process-parameter mapping | Material datasheets, slicer profiles, community tests |
| parameter_confidence | Taguchi DOE | DOE table, SN ratios, variance analysis |

## Tools
- **WebSearch** — retrieve material mechanical properties or manufacturer profiles.
- **WebFetch** — read datasheet URLs.
- **Read** — inspect `SECOND-KNOWLEDGE-BRAIN.md` for benchmarks.
- **Write** — save intermediate score artifacts if requested.
- **Bash** — validate JSON output.

## Quality Gate
- Output is valid JSON matching the `ScoreCard` schema.
- All scores in `[0.0, 1.0]` and cite a named framework.
- Every evidence link uses an evidence tier or URL.
- Aggregate recommendation is deterministic and reproducible.
- Unsupported or out-of-scope inputs are handled with a disclaimer, not fabricated scores.

## Example
**Input:** EvaluationFrame for PETG bracket with 70° overhang, Z-load.
**Output:** ScoreCard recommending Z-up flat with support at 50° threshold; orientation_strength=0.85 because load is in XY, support_cost=0.55 due to 70° overhang.
