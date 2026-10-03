# Native modeling practice — October 3, 2026

The objective was to practice explicit design intent before attempting the reference vise again. These are native Fusion tests performed through MCP, with independently calculated geometric expectations. They are not a claim of mastery, exact reconstruction or manufacturing approval. CAD archives and detailed JSON measurements remain in the local practice workspace, outside the portable skill.

| Exercise | Validation | Result |
| --- | --- | --- |
| Origin-centered plate, earlier session | Four variants; fully constrained sketches, datum position, native mirrored holes, analytic volume | Passed after adding explicit rectangle constraints |
| Stepped revolved spacer | Four variants; section fully constrained, measured cylindrical radii, datum end, length, annular section volume, healthy feature | Passed |
| Circular hole flange | Four variants with 6, 8 and 12 holes; fully constrained seed, native pattern, live hole coordinates/count, analytic volume | Passed |
| Mirrored gusset bracket | Four variants; common mounting datum, constrained base/wall/gusset, one solid, bounds, volume, healthy features | Passed after correcting wall sketch direction |
| Linked guide-rail loft | Four variants with scale 0.4 through 1.4; fully constrained sections and projected rail, rail endpoint attachment, solid closure, analytic frustum volume | Passed; free ends, no G1/G2 claim |
| Guided carriage | Native as-built slider, grounded guide, 0/10/25/40/55 mm travel and return; signed world displacement, zero interference, 0.5 mm measured clearance | Passed after correcting joint occurrence order |
| Curvature-continuous surface transition | Initially supplied raw circular BRep-edge sections | Initial attempt failed; subsequent Path-based input corrected creation. Strict sampled curvature acceptance still failed; see follow-up below |

## Corrections that mattered

The bracket's first wall was placed below its base because local sketch Y did not equal world Z. All its sketches were fully constrained, yet its bounds and volume were wrong. The corrected branch passed the same checks across size changes.

The carriage initially moved in the negative world direction. An absolute-distance check would have accepted its travel. Minimum distance revealed it had left the guide. Reversing joint occurrence order produced the intended signed movement and preserved clearance throughout the tested range.

The first surface experiment did not achieve a smooth/G2 end condition. Although BRepEdge types were confirmed by inspection, the section-add method's full contract was initially missed: it specifies a Path rather than a raw edge. Native Path sections corrected the creation error in the follow-up. The earlier API-limitation interpretation is withdrawn. No custom surface generator was substituted.

### One-hour follow-up

On October 3, native Paths wrapping the boundary edges enabled smooth-end conditions. Four variants were tested at 72 seam samples each. Normals matched (minimum absolute dot product approximately 0.9999999999999998). Circumferential curvature matched to floating-point precision. Maximum other principal-curvature residuals ranged from approximately 0.000027 to 0.000048 per mm, exceeding the original strict threshold of 0.000001 per mm. Native smooth-end construction is demonstrated; strict sampled G2 acceptance is not.

A separate native sketch-symmetry test passed 25 seeded parameter variants, preserving fully constrained sketches, symmetric center offsets, equal radii, two solids and analytic cylinder volume. It used one driving diameter and one driving offset, construction geometry and a symmetry constraint rather than independently dimensioning both circles.

Following Nick's direction to prioritize fundamentals, a datum-based D profile passed 21 dimensional variants. Horizontal/vertical, midpoint and two tangent constraints define the profile; center distance and arc radius drive it through construction geometry. An attempted redundant horizontal constraint on the centerline was rejected. Live inspection identified the implied alignment, and the test continued without removing the tangent constraints. Independent checks covered full constraint, one solid, signed datum bounds, perpendicular radius/tangent vectors, feature health and rectangle-plus-semicircle volume. Successful execution, verification and checkpoint took 1.463 seconds; failed setup and research are excluded.

## Native scope and remaining work

The Autodesk educational counterbore drawing's fully specified base subset passed 22 variants: native corner fillets, one native counterbore Hole and a two-direction feature Pattern. Independent checks covered four cylindrical center pairs, radii, axial intervals, one solid, constrained sketches, healthy features and analytic rounded-base-minus-holes volume (maximum error approximately 1.5e-10 cubic mm). Pattern creation, validation and checkpoint took 4.513 seconds. Five additional independent edits demonstrated edge-offset versus pitch semantics in 0.324 seconds. The raised ridge was omitted because its width/location are not dimensioned; no full reconstruction is claimed. A negative-direction Hole attempt failed; after live inspection a positive natural-direction input succeeded. Direction and participant selection changed together, so the failure cause has not been isolated.

Drawing source: [Autodesk educational direct-modeling exercise](https://files.upskill-dev.autodesk.com/public/aex/fusion/Sketching_Part_Modeling_2026/260201_M1-CE_Direct-modeling.pdf). The source PDF and interpreted dimension ledger remain local practice references.

The gussets use dimensioned triangle extrusions with symmetric thickness and a native feature mirror. They are not native Rib features: the installed RibFeatures API exposed no creation method. The application UI capability remains distinct from automation coverage.

The guide rail uses linked projection through `project2`, rather than fixed coordinates. This exercise validates a straight-rail transition. Curved rails, multiple rails, surface stitching/thickening, independently measured G1/G2 continuity, broader parameter sweeps and full mechanism dimensional variations remain future work.

The downloaded vise PDF and STEP remain reference assets. The retired approximate vise attempts are not used as templates or evidence. No cloud save or public publication occurred during practice.

## Timing

Additional fundamentals: native Hole coupon passed 19 variants, independently checking blind cylindrical depth plus drill tip and through countersink cone/frustum volume. Corrected creation took 0.612 s; verification/checkpoint 1.677 s. A second sketch-point vertical dimension was rejected; inspected state and explicitly aligned the shared row with a HorizontalPoints constraint. The precise solver cause of the rejected dimension was not isolated. Native two-distance chamfer passed 20 offset/size variants in 0.717 s plus four flipped/unflipped checks in 0.072 s. Creation had succeeded before an inspection property typo raised an exception; live inspection confirmed geometry, and no modifying script was replayed.

Both preserved vise PDF pages were visually reread without rebuilding: envelope dimensions, hole pitch, depicted opening and exploded component identities were distinguished from missing per-part manufacturing dimensions. Detailed ledger remains local. STEP measurement is still needed for missing guide clearances, fillets and thread specifications.

Successful in-Fusion operations, including their scoped verification/checkpoint work: revolved spacer 1.355 s; flange creation 0.363 s plus parameter validation 0.602 s; corrected bracket 1.721 s; linked loft creation 0.379 s plus parameter validation 0.404 s; corrected slider test 0.912 s. Surface failure record/checkpoint 0.357 s.

These numbers exclude research, assistant reasoning, failed attempts and MCP transport. Prompt-to-result latency was not measured. They must not be presented as total user wait time.

## Sources

- [Autodesk revolve](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/GUID-D74BB28A-9570-43AD-97A4-E094021C036B.htm)
- [Autodesk native mirror](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/GUID-77CE43FF-47C6-429A-B872-BA80B348CCC3.htm)
- [Autodesk surface loft](https://help.autodesk.com/cloudhelp/ENU/Fusion-Patch/files/SFC-REF-LOFT-DLG.htm)
- [Smooth-end API method](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/LoftSection_setSmoothEndCondition.htm)
- [Surface continuity analysis](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/GUID-3F8BA6D3-5DF2-49FA-BE7D-8CCEF718C795.htm)

Live installed API documentation was also queried for mirror, symmetric extrusion, slider joints, linked projection, guide rails and surface evaluators. See the skill's drafting-and-design-intent reference for the maintained decision guidance.
