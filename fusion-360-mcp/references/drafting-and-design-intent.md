# Drafting and design intent

Read before reconstructing a dimensioned drawing or planning a mechanical feature tree. Record the feature strategy before construction; select a minimal, editable sequence that expresses function, symmetry and manufacturing intent.

## Read the drawing before modeling

- Establish units, drawing standard, first/third-angle projection, revision, scale, title-block tolerances, section planes and detail views. Do not measure a perspective image as a dimensioned orthographic drawing.
- Create a dimension ledger: feature, value, units, view, reference/datum, tolerance and evidence status (explicit drawing value, measured CAD value, derived value, or assumption). Resolve contradictory views rather than quietly mixing them.
- Identify functional datums and the model coordinate system. Baseline dimensions share a base point; ordinate dimensions share an origin; chain dimensions refer to preceding features. Do not treat all drawings as globally ordinate-dimensioned. A GD&T datum reference frame is a functional reference, not automatically the CAD origin.
- Read diameter/radius symbols, repeated-feature counts, centerlines, symmetry, hidden lines, section hatching, depth and through/blind/thread callouts. Overall envelope dimensions do not specify internal construction or every fillet.
- Distinguish nominal shape, reference dimensions, basic dimensions, size tolerances and geometric tolerances. Do not invent a fit or tolerance from a visually plausible gap. If the PDF omits part dimensions, the supplied STEP is separate measurement evidence, not evidence that those dimensions appear on the drawing.

## Express relationships instead of repeating coordinates

- Put intentional symmetry on stable origin/construction planes. Locate geometry with construction centerlines, midpoint/coincident relationships, symmetry and equality constraints. Prefer one driving dimension over duplicate dimensions for equal or symmetric features.
- Mirror an appropriate sketch, feature, body or component; pattern repeated features. Choose the level based on downstream edits and assembly identity. Do not independently draw both sides of a symmetric part unless they deliberately differ.
- Dimension position from the functional datum. Dimension size separately. Use named parameters and expressions for design relationships. Avoid Fix as a substitute for dimensional design intent; imported reference geometry is a different case.
- Validate native API-created constraints explicitly. The practice test found that `addCenterPointRectangle` produced four lines with no geometric constraints in the installed API. Numeric placement at the origin did not prevent translation during dimension edits. Add required horizontal/vertical and midpoint/coincident relationships and inspect `isFullyConstrained`.
- Test changes to width, height, thickness, hole pitch and diameter independently. Require preserved datum position, intended symmetry, solid count and feature health. A fully constrained sketch can still express the wrong intent; inspect the resulting geometry.

## Lessons from representative native tests

- Sketch coordinates are local to their plane. In the installed environment, positive local Y on an XZ sketch pointed toward negative world Z. Inspect `sketchToModelSpace`/`modelToSketchSpace` or the resulting world bounds; do not infer a wall's direction from the plane name. A constrained wall below its mounting base passed sketch checks and failed geometric acceptance.
- An axial section can encode concentric diameters and shoulder lengths with horizontal/vertical constraints, datum-referenced dimensions and a construction revolution axis. Validate each cylindrical radius and the stepped annular volume after edits, not just the overall envelope.
- A repeated hole is one seed feature plus a native pattern. When quantities or pitch change, inspect the resulting cylindrical face centers and count. A healthy pattern object alone does not prove every hole was regenerated in the intended position.
- Link guide-rail endpoints to section geometry with `Sketch.project2(..., True)` where appropriate. Validate the linked endpoints after both shrinking and enlarging sections. A straight-rail loft with free ends demonstrates rail attachment, not G1/G2 continuity.
- Native Rib exists in the application, but the installed `RibFeatures` API exposes enumeration without a creation method. A dimensioned triangular gusset made by native extrude and feature mirror is an explicit alternative with different edit semantics; do not label it a Rib feature or claim API coverage proves UI coverage.
- Joint occurrence order affects signed world motion. Validate the stationary occurrence, signed carriage translation, containment within the guide, minimum clearance and interference. Testing only absolute travel can accept a carriage moving out of its guide.
- Read the complete input contract as well as the end-condition method: `LoftSections.add` accepts a Path, Profile, face or point; raw BRepEdge is not a documented section input. For edge-defined surface boundaries, construct a native Path with `features.createPath(edge, False)` and add that Path. This corrected the earlier smooth-end rejection; it was an input-contract error, not an established API limitation. Native smooth-end conditions then succeeded. Across 288 seam samples in four variants, normals matched, but axial curvature residuals of roughly 0.000027–0.000048 per mm exceeded the original 0.000001 per mm test threshold. Keep native end-condition success separate from measured continuity acceptance; do not relax a failed threshold silently.
- Native sketch symmetry can propagate both circle-center position and radius. A 25-variant test used one diameter and one datum-based offset, with a constrained construction symmetry axis and a horizontal origin-to-center construction line. Both circle centers remained symmetric and both radii stayed equal without duplicate driving dimensions. Check the constraint's actual solved behavior rather than adding redundant dimensions.

Test coverage is recorded in the repository's `docs/modeling-practice-results.md`. The exercises validate bounded cases; exact vise reconstruction and manufacturing acceptance remain separate tasks.

## Progress from simple to advanced techniques

1. Centered plate: fully constrained rectangle, datum-linked construction, seed hole and native feature mirror; verify analytic volume and changed sizes.
2. Turned spacer: constrained axial section, construction axis, native revolve, concentric shoulders and bores; verify radial/axial dimensions and section-derived volume.
3. Mounting bracket: functional mounting datum, symmetric pads, patterned holes, native ribs, purposeful fillets; verify hole coordinates and wall thickness under edits.
4. Controlled transition: loft sections with intersecting rails and explicit end conditions; verify solid closure and G0/G1/G2 as required. Tangency (G1) means matching tangent direction, not necessarily matching curvature (G2).
5. Guided mechanism: separate components, mating interfaces, native joints and limits; inspect motion and interference across the range.
6. Reference reconstruction: dimension ledger and per-part feature plans before modeling; compare each finished part against reference geometry using measured deviations. Do not substitute an imported finished body for a reconstructed feature tree.

Promote a technique from researched to demonstrated only after its representative test passes. Keep failures and corrections in practice records, not as copied project geometry in the skill. A finite exercise set is evidence of proficiency on those cases, not mastery of all CAD.

## Authoritative references

- [Autodesk sketch constraints](https://help.autodesk.com/cloudhelp/ENU/Fusion-Sketch/files/SKT-CONSTRAINTS.htm)
- [Fully define sketches](https://help.autodesk.com/cloudhelp/ENU/Fusion-Sketch/files/SKT-FULLY-DEFINE-CONSTRAIN-SKETCH.htm)
- [Drawing dimensions: baseline, chain and ordinate](https://help.autodesk.com/cloudhelp/ENU/Fusion-Drawing/files/DWG-DIMENSIONS.htm)
- [NIST introduction to GD&T](https://www.nist.gov/publications/fundamentals-geometric-dimensioning-and-tolerancing-part-ii)
- [Autodesk loft guide rails](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-create-a-Loft-with-guide-rails-in-Fusion.html)
- [Autodesk sweep reference](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/SLD-REF-SWEEP.htm)
- [Native surface loft end conditions](https://help.autodesk.com/cloudhelp/ENU/Fusion-Patch/files/SFC-REF-LOFT-DLG.htm)
- [Smooth-end API contract](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/LoftSection_setSmoothEndCondition.htm)
- [Zebra continuity analysis](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/GUID-3F8BA6D3-5DF2-49FA-BE7D-8CCEF718C795.htm)
