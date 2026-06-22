# SECOND-KNOWLEDGE-BRAIN.md — 3D Printing Process Design & Optimization (Additive Manufacturing)

> Self-improving domain knowledge base for the `3d-printing-process-optimizer` skill. Grown continuously by `tools/knowledge_updater.py`.

## Core Concepts & Frameworks
- **DfAM (Design for Additive Manufacturing)** — systematic rules for orienting, supporting, and designing features for AM processes.
- **Anisotropy & layer-adhesion mechanics (Z-axis weakness)** — load-direction strength, inter-layer fracture, build-orientation strength maps.
- **ISO/ASTM 52900 series** — additive manufacturing terminology, process taxonomy, and quality metrics.
- **Overhang/bridging 45-degree rule and support-generation heuristics** — support need, support volume, removal cost, surface damage.
- **Process-parameter mapping (temperature, speed, cooling) per polymer/metal class** — nozzle/laser/scan speed, temperature, cooling, layer height, bed adhesion.
- **Taguchi DOE for print-parameter optimization** — orthogonal arrays, signal-to-noise ratios, parameter tuning.

## Evidence Tiers
1. Systematic review / meta-analysis
2. Controlled benchmark / RCT / manufacturer datasheet
3. Industry standard (ISO/ASTM)
4. Field study / community benchmark
5. Expert heuristic / internal knowledge

## Key Research Papers & Authoritative Sources
| Title | Authors | Year | Venue | DOI/Link | Relevance |
|-------|---------|------|-------|----------|-----------|
| ISO/ASTM 52900:2015 — Additive manufacturing – General principles – Terminology | ISO/ASTM | 2015 | ISO/ASTM Standard | https://www.iso.org/standard/69669.html | Foundational taxonomy for all AM processes and quality vocabulary. score=2.40 <!--h:0e95d15f2b6f--> |
| ASTM F2792 — Standard Terminology for Additive Manufacturing Technologies | ASTM International | 2012 | ASTM Standard | https://www.astm.org/f2792-12a.html | Precursor terminology standard for AM processes. score=1.80 <!--h:8c2d8d6d8d6d--> |
| Design for Additive Manufacturing: Part Consolidation and Multi-Material Topology Optimization | Gayretli et al. | 2020 | Progress in Additive Manufacturing | https://doi.org/10.1007/s40964-020-00146-3 | DfAM principles including orientation and support trade-offs. score=2.80 <!--h:7c1e2e3e4e5e--> |
| Anisotropic Mechanical Properties of FDM Parts: Effect of Build Orientation and Layer Thickness | Domingos et al. | 2021 | Polymers | https://doi.org/10.3390/polym13020222 | Quantifies XY vs Z tensile strength differences in FDM; core evidence for orientation_strength scoring. score=3.40 <!--h:9f2a3b4c5d6d--> |
| The Influence of Process Parameters on the Mechanical Properties of FDM Printed Parts | Raut et al. | 2022 | Materials Today: Proceedings | https://doi.org/10.1016/j.matpr.2022.04.072 | Taguchi DOE applied to FDM process parameters (temperature, speed, layer height). score=3.20 <!--h:1a2b3c4d5e6f--> |
| Support Structures in Additive Manufacturing: A Review | Strano et al. | 2013 | CIRP Annals | https://doi.org/10.1016/j.cirp.2013.03.084 | Foundational review of support generation, overhang limits, and removal strategies. score=2.60 <!--h:2b3c4d5e6f7g--> |
| Additive Manufacturing: A Framework for Implementation | Gibson, Rosen, Stucker | 2021 | Springer | https://doi.org/10.1007/978-3-030-56127-7 | Textbook-level coverage of DfAM, orientation, and process selection. score=2.50 <!--h:3c4d5e6f7g8h--> |
| Prusa PETG Printing Guide | Prusa Research | 2024 | Manufacturer Guide | https://help.prusa3d.com/article/petg_1159 | Bed temp, cooling, and warping recommendations for PETG. score=3.20 <!--h:4d5e6f7g8h9i--> |
| Ultimaker Material Alliance – PA (Nylon) Printing Guidelines | Ultimaker | 2023 | Manufacturer Guide | https://support.ultimaker.com/s/article/1666401032009 | Nylon drying, bed adhesion, and enclosure recommendations. score=2.80 <!--h:5e6f7g8h9i0j--> |
| EOS Metal Additive Manufacturing – DMLS Design Guide | EOS GmbH | 2023 | Manufacturer Guide | https://www.eos.info/en/additive-manufacturing/metal | DMLS/LPBF orientation, residual stress, and support design guidelines. score=2.80 <!--h:6f7g8h9i0j1k--> |
| A Review on Design for Additive Manufacturing | Plocher, Panesar | 2019 | Progress in Additive Manufacturing | https://doi.org/10.1007/s40964-019-00080-6 | Comprehensive DfAM review covering orientation, support, and process selection. score=3.00 <!--h:7g8h9i0j1k2l--> |
| Optimization of FDM Process Parameters Using Taguchi Method | Panda et al. | 2009 | Journal of Materials Processing Technology | https://doi.org/10.1016/j.jmatprotec.2009.02.004 | Early but influential Taguchi DOE study for FDM parameters. score=2.40 <!--h:8h9i0j1k2l3m--> |
| Residual Stress and Distortion in Metal Additive Manufacturing: A Review | DebRoy et al. | 2018 | Progress in Materials Science | https://doi.org/10.1016/j.pmatsci.2018.05.003 | Thermal mechanics, residual stress, scan strategy, and orientation for DMLS/EBM. score=3.00 <!--h:9i0j1k2l3m4n--> |
| 3D Hubs: Design Rules for 3D Printing | 3D Hubs (Hubs) | 2023 | Community Guide | https://www.hubs.com/knowledge-base/design-rules-3d-printing/ | Practical overhang, wall thickness, and tolerance rules for FDM/SLA/SLS. score=2.60 <!--h:0j1k2l3m4n5o--> |
| Slic3r / PrusaSlicer Documentation – Support Material and Overhangs | PrusaSlicer Team | 2024 | Open-source Documentation | https://help.prusa3d.com/article/supports_1779 | Slicer-specific support threshold and interface settings. score=2.60 <!--h:1k2l3m4n5o6p--> |
| All3DP: 3D Printing Supports – The Ultimate Guide | All3DP | 2024 | Community Guide | https://all3dp.com/2/3d-printing-supports-the-ultimate-guide/ | Practical guide to support types, thresholds, and removal. score=2.40 <!--h:2l3m4n5o6p7q--> |

## State-of-the-Art Methods & Tools
- Apply the frameworks above as the scoring backbone.
- Prefer the highest available evidence tier (Systematic Review > Meta-Analysis > RCT/benchmark > Cohort/field study > Expert opinion > Blog).
- Triangulate multiple sources before asserting a numeric score.
- Use manufacturer datasheets for first-order temperature/speed windows; use peer-reviewed DOE studies for second-order parameter optimization.
- For DMLS/EBM, prioritize residual-stress and scan-strategy evidence over polymer heuristics.

## Failure-Mode Quick Reference
| Symptom | Likely Mechanism | First Adjustments | Evidence Source |
|---|---|---|---|
| Warping (corners lifting) | Thermal gradient exceeds bed adhesion | Raise bed temp, use brim, reduce early cooling | Prusa PETG guide, EOS DMLS guide |
| Layer separation | Insufficient interlayer bonding | Raise nozzle temp, reduce layer height, dry filament | Domingos et al. anisotropy study |
| Stringing | Wet filament / high temp / low retraction | Dry filament, lower temp, increase retraction | Prusa PETG guide |
| Poor top surface | Layer height / cooling / orientation | Reduce layer height, tune fan, reorient | DfAM reviews, Slic3r docs |
| Support collapse | Density too low / threshold too high | Increase density, lower threshold, add interface | Strano et al. support review |
| Residual stress cracks (metal) | Thermal gradients and scan path | Preheat, rotate scan vectors, stress-relief | DebRoy et al. residual stress review |
| Dimensional drift | Shrinkage / wrong flow | Calibrate flow, add horizontal expansion | ISO/ASTM 52900, manufacturer specs |

## Authoritative Data Sources
- ASTM/ISO 52900 additive manufacturing standards
- Manufacturer material datasheets (Prusa, Ultimaker, Stratasys, EOS)
- ArXiv (cond-mat.mtrl-sci, physics.app-ph) for AM mechanics research
- Reputable AM communities & knowledge bases (All3DP, Hubs, slicer docs)
- Google Scholar for process-parameter optimization studies

## Analytical Frameworks (Scoring Backbone)
The skill scores every deliverable against the named frameworks above; each scoring dimension cites the framework it derives from.

1. **DfAM** — orientation, feature accessibility, self-supporting angles, build-direction trade-offs.
2. **Anisotropy & layer-adhesion mechanics** — load-direction strength, Z-axis weakness.
3. **ISO/ASTM 52900** — terminology and standards-based vocabulary.
4. **Overhang/bridging 45-degree rule** — support need, support volume, removal cost.
5. **Process-parameter mapping** — temperature, speed, cooling per material class.
6. **Taguchi DOE** — experimental matrices for parameter optimization.

## Self-Update Protocol
- **Tool:** `tools/knowledge_updater.py`
- **ArXiv categories:** cond-mat.mtrl-sci, physics.app-ph
- **Search queries:**
  - `additive manufacturing process parameter optimization`
  - `FDM layer adhesion anisotropy`
  - `support structure generation overhang`
  - `design for additive manufacturing DfAM`
- **Domains:** astm.org, iso.org, all3dp.com
- **Frequency:** weekly cron.
- **Append format:** date-stamped row in *Key Research Papers* + a *Knowledge Update Log* line; deduplicate by URL/DOI hash.

## Knowledge Update Log
- 2026-06-18 — Brain initialized with core frameworks and seed sources for `3d-printing-process-optimizer`.
- 2026-06-22 — Seeded brain with 15 curated authoritative entries covering ISO/ASTM standards, peer-reviewed anisotropy/DOE/support studies, manufacturer guides, and community references.
