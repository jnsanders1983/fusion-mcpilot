# Fusion fundamentals practice — October 3, 2026

Authorized window: 15:06:01–16:06:01 UTC. Practice emphasized fundamental drafting and editable native modeling after Nick's steering. Earlier scheduled blocks contained idle gaps; later work continued directly. The window is not a claim of sixty minutes of continuous execution or CAD mastery.

## Demonstrated fundamentals

| Exercise | Evidence and result |
| --- | --- |
| Datum/construction symmetry | 25 dimensional cases: fully constrained circles, symmetric centers, equal radii and analytic volume. |
| Tangent D-profile | 21 cases: native tangency, midpoint datum and construction length; bounds, perpendicular tangent/radius vectors and volume passed. Removed a redundant constraint after inspecting dependencies. |
| Reading an Autodesk drawing | Dimension ledger separates explicit, derived and missing values. Edge offset plus pitch converted to datum coordinates. Unspecified raised ridge omitted from the practice subset. |
| Native counterbores and pattern | 22 cases: four hole centers, radii, cylindrical depth intervals, rounded-base volume, healthy features and constraint passed. Five independent edits preserved edge-offset/pitch intent. |
| Blind holes and countersinks | 19 cases: drill shoulder depth distinguished from conical tip depth, included-angle geometry and analytic removed volume passed. |
| Two-distance chamfer | 20 cases plus four flip checks: unequal adjacent-surface offsets, top radius, axial interval and frustum volume passed. |
| Aligned/angular/reference dimensions | 17 acute cases: signed tip coordinates, aligned length versus projection, driven reference dimension and triangle volume passed. |
| Native straight slots | Three definitions at nominal/two boundaries/restoration. Generated native tangent profiles needed expression rebinding and reference-line constraints. Centers, radii, solids, volume and full constraint passed. |
| Native curved slot | Nominal/two boundaries/restoration: separate radial direction and sweep, datum links, fully constrained profile, end centers, radii and sector-plus-caps volume passed. |
| Archive persistence | Reopened curved-slot F3D, verified expressions/constraints, changed sweep and restored it successfully. |

Counts include restoration cases and are not counts of unique designs. Practice geometry and compact evidence remain outside the skill under `work/modeling-practice`. Maintained guidance contains reusable methods, not these job models.

## Important corrections and remaining limits

- Numeric initial placement does not establish datum constraints. Native helper-generated geometry still needs inspection of solved constraints and parameter expressions.
- Native slot dimension inputs became numeric constants in Fusion 2705.1.25. Straight-slot angular reference geometry and curved-slot datum/sweep relationships needed explicit completion. These are version-specific observations, not universal API failure claims.
- A Hole creation attempt failed; direction and participant selection changed together during correction, so exact causality remains unisolated. A second point dimension was rejected in the hole coupon; an explicit shared-row relationship worked, but the solver rejection cause remains unisolated.
- A chamfer inspection used the wrong finished-feature property after creation had succeeded. Live inspection prevented duplicate creation; the finished feature uses `edgeSets`.
- The preserved vise PDF is an assembly envelope/exploded diagram. It does not supply all guide clearances, fillets, threads and per-part dimensions. It was reread, not rebuilt. STEP measurements must be labeled separately from drawing evidence.
- Earlier smooth-loft input was corrected to native Path sections. Native smooth-end creation succeeded, but strict sampled axial-curvature acceptance still failed. Limited stitch/thicken end-wall checks passed after expression correction; global wall checks and isolated creation behavior remain unresolved. Advanced work was deferred.
- No manufacturing tolerance, loaded mechanism, arbitrary slot orientation, or exact vise reconstruction acceptance is claimed.

## Timing and efficiency

Measured successful in-Fusion scopes, in seconds: symmetry 1.288; tangent profile 1.463; counterbore pattern/verification/checkpoint 4.513 plus datum edits 0.324; hole creation 0.612 plus verification/checkpoint 1.677; chamfer variants 0.717 plus flips 0.072; aligned-profile creation 0.885 plus verification/checkpoint 0.597; straight-slot creation 1.118, correction 0.207 and verification/checkpoint 0.637; curved-slot creation 0.926, corrections 0.099 and verification/checkpoint 0.490; archive round-trip 0.386.

These timings exclude research, reasoning, transport and unmeasured failures. They are not total user wait times. The curved-slot documentation/build/correction/verification block took roughly six minutes end-to-end. Exact active-time accounting for the entire hour was not captured.

Nick's efficiency instruction is retained in workspace standing instructions and the portable skill: focused official research, native implementation, nominal and meaningful boundary checks, retain the lesson, then advance to a distinct concept. Broader randomized tests require a specific risk or failure. Early repeated batches were less efficient than this revised approach.

## Sources and delivery

- [Autodesk dimension tools and reference conventions](https://help.autodesk.com/cloudhelp/ENU/Fusion-Drawing/files/DWG-DIMENSIONS.htm)
- [Autodesk dimensioned bracket exercise](https://files.upskill-dev.autodesk.com/public/aex/fusion/Sketching_Part_Modeling_2026/260201_M1-CE_Direct-modeling.pdf)
- [Autodesk Hole reference](https://help.autodesk.com/view/fusion360/ENU/?contextId=MODEL-HOLE-CMD)
- [Native center-point slot API](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Sketch_addCenterPointSlot.htm)
- [Native center-point arc slot API](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Sketch_addCenterPointArcSlot.htm)
- Live installed API contracts for angular/driven dimensions, Hole extents and drill point, Chamfer input/edge-set edits, Slot return objects, archive export/import.

Updated source and installed skill guidance, rebuilt portable ZIP, and made local Git commits as Nick requested. No push or cloud save. Original reference PDFs and STEP preserved. Final deadline/automation closure is recorded in the local session log.
