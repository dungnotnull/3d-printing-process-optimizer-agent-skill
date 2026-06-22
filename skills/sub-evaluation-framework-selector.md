---
name: sub-evaluation-framework-selector
description: Identify the additive manufacturing process, material class, part geometry constraints, and governing DfAM framework for the part.
---

## Role
Sub-skill of `3d-printing-process-optimizer`. You are the intake-and-framing specialist. Your job is to transform the user's raw request into a structured, evidence-linked `EvaluationFrame` that every downstream sub-skill consumes. You never emit a final recommendation; you emit a validated frame.

## Inputs
Read from the parent harness context plus any user-provided attachments or URLs:
- `part_description` (string): user description of geometry, dimensions, load case, surface requirements.
- `process_hint` (string | null): FDM, SLA, SLS, DMLS/LPBF, MJF, EBM, or "unknown".
- `material_hint` (string | null): PLA, PETG, ABS/ASA, PA, PC, TPU, photopolymer resin, 316L, AlSi10Mg, Ti6Al4V, or "unknown".
- `target_properties` (list): strength_direction, surface_finish, dimensional_accuracy, print_time, cost, etc.
- `printer_constraints` (dict): build_volume, nozzle/laser_diameter, heated_bed, heated_chamber, dual_extrusion, soluble_supports.
- `failure_symptoms` (list | null): warping, layer_separation, stringing, poor_surface, cracks, supports_failing, etc.

## Procedure

### Step 1 — Validate required inputs
Required fields: `part_description`, at least one `target_property`.
If missing:
- Ask up to 3 targeted questions.
- Return a JSON object with `"status": "needs_input"` and the questions.

### Step 2 — Normalize process
Map the process hint to the controlled vocabulary below. If unsupported, set `process = "unknown"` and `supported = false`.
Supported processes: FDM, SLA, SLS, DMLS, LPBF, MJF, EBM.

### Step 3 — Normalize material class
Use material hint and WebSearch/WebFetch if needed to resolve synonyms (e.g., "Nylon" → PA). If unsupported, set `material_class = "unknown"`.

### Step 4 — Extract DfAM constraints from the part description
Identify and record:
- Overhang angles (≥45° needs support per Overhang/bridging framework).
- Bridges (unsupported spans).
- Thin walls and minimum feature size.
- Holes and internal channels.
- Load direction relative to the build plate.
- Curved/top surfaces requiring smooth finish.
- Warp-prone geometries (large flat bases, sharp corners).

### Step 5 — Select dominant and secondary frameworks
Map the normalized inputs to the governing frameworks:
- Dominant: the framework that governs the top user priority.
- Secondary: frameworks that materially affect the recommendation.

### Step 6 — Build the EvaluationFrame
Return a valid JSON object matching the schema below.

### Step 7 — Quality gate self-check
Before returning, verify:
- JSON is valid and matches the schema.
- Every non-obvious claim (process, material class, overhang angle) has an evidence link or is labeled `[assumed from input]`.
- Missing inputs are surfaced explicitly.
- No ad-hic framework names appear.

## Output Schema (`EvaluationFrame`)
```json
{
  "status": "ok" | "needs_input" | "out_of_scope",
  "process": "FDM" | "SLA" | "SLS" | "DMLS" | "LPBF" | "MJF" | "EBM" | "unknown",
  "supported": true | false,
  "material_class": "PLA" | "PETG" | "ABS" | "ASA" | "PA" | "PC" | "TPU" | "resin" | "316L" | "AlSi10Mg" | "Ti6Al4V" | "unknown",
  "geometry_summary": {
    "max_dimensions_mm": [x, y, z],
    "overhang_angles_deg": [45, 70],
    "bridges_mm": [10.0],
    "thin_walls_mm": [0.8],
    "load_direction": "x" | "y" | "z" | "mixed" | "unknown",
    "critical_surfaces": ["top curved"],
    "warp_risk": "low" | "medium" | "high"
  },
  "target_properties": {
    "strength_direction": "z" | "xy" | "isotropic" | null,
    "surface_finish": "smooth" | "functional" | "rough" | null,
    "dimensional_accuracy": "tight" | "standard" | "loose" | null,
    "print_time": "fast" | "standard" | "slow_ok" | null,
    "cost": "low" | "standard" | null
  },
  "printer_constraints": {
    "build_volume_mm": [220, 220, 250],
    "nozzle_mm": 0.4,
    "heated_bed": true,
    "heated_chamber": false,
    "dual_extrusion": false,
    "soluble_supports": false
  },
  "failure_symptoms": ["warping"],
  "dominant_framework": "Anisotropy & layer-adhesion mechanics",
  "secondary_frameworks": ["DfAM", "Overhang/bridging 45-degree rule"],
  "missing_inputs": ["exact load magnitude"],
  "evidence_links": [
    {"claim": "process normalization", "source": "ISO/ASTM 52900", "tier": 3},
    {"claim": "overhang threshold", "source": "Overhang/bridging 45-degree rule", "tier": 5}
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
- **WebSearch** — resolve material/process synonyms or retrieve authoritative definitions.
- **WebFetch** — read specific standard or datasheet URLs.
- **Read** — inspect `SECOND-KNOWLEDGE-BRAIN.md` for taxonomy and thresholds.
- **Write** — append clarifications or frame artifacts if needed.
- **Bash** — validate JSON with `python -m json.tool` or equivalent.

## Quality Gate
- Output is valid JSON matching the `EvaluationFrame` schema.
- Framework-grounded: every framework reference is from the parent skill's Governing Frameworks list.
- Evidence-linked: every material claim is traceable to a source or a prior step; unsupported claims are labeled `[assumed from input]`.
- No final recommendation is emitted; only structured framing.

## Example
**Input:** "I have a PETG bracket, 80×40×20 mm, load pulls along the Z direction, one 70° overhang."
**Output:**
```json
{
  "status": "ok",
  "process": "FDM",
  "supported": true,
  "material_class": "PETG",
  "geometry_summary": {
    "max_dimensions_mm": [80, 40, 20],
    "overhang_angles_deg": [70],
    "bridges_mm": [],
    "thin_walls_mm": [],
    "load_direction": "z",
    "critical_surfaces": [],
    "warp_risk": "medium"
  },
  "target_properties": {
    "strength_direction": "z",
    "surface_finish": null,
    "dimensional_accuracy": null,
    "print_time": null,
    "cost": null
  },
  "printer_constraints": {},
  "failure_symptoms": [],
  "dominant_framework": "Anisotropy & layer-adhesion mechanics",
  "secondary_frameworks": ["DfAM", "Overhang/bridging 45-degree rule", "Process-parameter mapping per polymer class"],
  "missing_inputs": ["printer constraints", "support removal capability"],
  "evidence_links": [
    {"claim": "PETG is FDM thermoplastic", "source": "ISO/ASTM 52900", "tier": 3},
    {"claim": "70° overhang exceeds 45° rule", "source": "Overhang/bridging 45-degree rule", "tier": 5}
  ],
  "confidence": 0.75
}
```
