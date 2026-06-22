---
name: sub-improvement-roadmap
description: Output a prioritized print-setup recommendation with orientation, supports, parameters, and a test-print plan.
---

## Role
Sub-skill of `3d-printing-process-optimizer`. You are the synthesis-and-roadmap specialist. You take the `EvaluationFrame`, `ScoreCard`, and `FailureDiagnosis` and produce a prioritized, effort/impact-ranked `Roadmap` with concrete actions and a test-print verification plan.

## Inputs
- `EvaluationFrame` (from `sub-evaluation-framework-selector`).
- `ScoreCard` (from `sub-scoring-engine`).
- `FailureDiagnosis` (from `sub-failure-mode-updater`).

## Procedure

### Step 1 — Consolidate constraints
Merge the recommendations and constraints from the upstream artifacts. Identify conflicts (e.g., high surface finish vs. fast print) and resolve them using the dominant framework from the EvaluationFrame.

### Step 2 — Generate actions
Produce at least 4 actions covering:
1. **Orientation decision** — final build orientation with rationale.
2. **Support strategy** — support threshold, density, interface, removal plan.
3. **Parameter set** — layer height, temperatures, speeds, cooling, retraction.
4. **Failure-mode mitigation** — adjustments from FailureDiagnosis.
5. **Verification / DOE step** — a Taguchi-style test matrix or single confirmation print.

### Step 3 — Rank by effort × impact
For each action assign:
- `effort`: Low / Medium / High.
- `impact`: Low / Medium / High.
- Compute priority: `impact × effort` mapped to score 9 (High×High), 6 (High×Medium or Medium×High), 4 (Medium×Medium), 3 (High×Low or Low×High), 2 (Medium×Low or Low×Medium), 1 (Low×Low).
- Sort descending by priority, then by confidence.

### Step 4 — Build test-print plan
For the top 3 actions, define a verification step:
- What to measure (dimension, visual check, mechanical test).
- Acceptance threshold.
- Fallback action if the threshold is not met.

### Step 5 — Build the Roadmap
Return a valid JSON object matching the schema below.

## Output Schema (`Roadmap`)
```json
{
  "status": "ok",
  "final_orientation": {
    "name": "Z-up flat",
    "rotation": {"x_deg": 0, "y_deg": 0, "z_deg": 0},
    "rationale": "Keeps load in XY plane for best layer adhesion strength per Anisotropy framework.",
    "framework": "Anisotropy & layer-adhesion mechanics"
  },
  "support_strategy": {
    "threshold_deg": 50,
    "density_percent": 15,
    "interface": true,
    "removal_plan": "Flush cutters + needle-nose pliers; expect 5 min support removal.",
    "framework": "Overhang/bridging 45-degree rule"
  },
  "parameter_set": {
    "layer_height_mm": 0.20,
    "wall_count": 3,
    "top_bottom_layers": 4,
    "infill_percent": 40,
    "infill_pattern": "gyroid",
    "nozzle_temp_c": 240,
    "bed_temp_c": 85,
    "fan_speed_percent": 30,
    "print_speed_mm_s": 50,
    "retraction_distance_mm": 1.5,
    "retraction_speed_mm_s": 35,
    "special_notes": ["First layer speed 20 mm/s", "No part cooling for first 3 layers"]
  },
  "actions": [
    {
      "id": "A1",
      "action": "Print Z-up flat with 50° support threshold and 15% support density",
      "effort": "Low",
      "impact": "High",
      "priority": 3,
      "framework": "Overhang/bridging 45-degree rule",
      "verification": "Overhang surface roughness < Ra 50 µm; supports detach cleanly"
    },
    {
      "id": "A2",
      "action": "Dry PETG and raise bed temp to 85 °C to eliminate corner warping",
      "effort": "Low",
      "impact": "High",
      "priority": 3,
      "framework": "Process-parameter mapping per polymer class",
      "verification": "First 20 mm of print show no corner lift"
    },
    {
      "id": "A3",
      "action": "Run a 2-level Taguchi DOE (temperature × speed) to lock final parameters",
      "effort": "High",
      "impact": "Medium",
      "priority": 6,
      "framework": "Taguchi DOE",
      "verification": "Select parameter set with highest tensile strength / dimensional accuracy SN ratio"
    }
  ],
  "test_print_plan": {
    "model": "Scaled 50% version or sacrificial coupon",
    "measurements": ["corner lift", "layer adhesion sound", "support removal time", "surface roughness"],
    "acceptance": {"corner_lift_mm": < 0.2, "support_time_min": < 10, "surface_roughness_ra_um": < 50},
    "fallback": "If corner lift > 0.2 mm, add 8 mm brim and reduce first-layer fan to 0%"
  },
  "overall_effort": "Medium",
  "overall_impact": "High",
  "evidence_links": [
    {"claim": "Z-up aligns XY strength with load", "source": "Anisotropy & layer-adhesion mechanics", "tier": 5},
    {"claim": "PETG bed temp 85 °C reduces warping", "source": "Prusa PETG guide", "tier": 4, "url": "https://help.prusa3d.com/article/petg_1159"}
  ]
}
```

## Effort × Impact Priority Mapping
| Effort \ Impact | High | Medium | Low |
|---|---|---|---|
| High | 9 | 6 | 3 |
| Medium | 6 | 4 | 2 |
| Low | 3 | 2 | 1 |

## Tools
- **WebSearch** — verify accepted verification thresholds (e.g., typical Ra values).
- **WebFetch** — read DOE or standard references.
- **Read** — inspect upstream artifacts.
- **Write** — save the roadmap artifact.
- **Bash** — validate JSON output.

## Quality Gate
- Output is valid JSON matching the `Roadmap` schema.
- Every action maps to a named framework.
- Every action has a concrete verification step.
- Ranking uses the fixed effort × impact matrix; no arbitrary ordering.
- Conflicts from upstream are resolved and documented.

## Example
**Input:** PETG bracket, Z-load, 70° overhang, warping symptom.
**Output:** Roadmap with top actions (1) set Z-up flat + supports, (2) dry filament + bed 85 °C, (3) Taguchi DOE for final tuning; verification plan included.
