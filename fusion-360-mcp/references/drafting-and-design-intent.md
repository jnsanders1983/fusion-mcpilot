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
