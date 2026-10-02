# Choose a model that is easy to change

Use this for unfamiliar shapes or a design expected to evolve. Start from the functional interfaces, envelope, manufacturing process and important dimensions. Infer routine details when possible; obtain missing load, fit or process requirements when they determine the geometry. State assumed dimensions in the result.

## Choose the representation

| Geometry / purpose | Starting method | Verification focus |
|---|---|---|
| Prismatic bracket, plate, enclosure | Constrained sketches plus extrude/cut, holes, shell, ribs | Thickness, hole spacing, clearances, one intended solid |
| Rotational part | Revolve an axial section | Axis, concentricity, diameters, wall thickness |
| Tube, cable channel, constant section along a path | Sweep | Path continuity, orientation/twist, minimum bend radius |
| Transition between distinct sections | Loft with controlled profiles/rails | Profile order, rail intersections, twisting and end continuity |
| Complex industrial surfaces | Surface construction, trim/extend, stitch/thicken | Gaps, G1/G2 transitions, thickness and solid closure |
| Organic grip or styling | Form/T-Spline with restrained topology and symmetry | Self-intersection, finish/conversion success, functional interface accuracy |
| Scan/STL repair or reverse engineering | Mesh repair/reduction and appropriate conversion | Source units, watertightness, deviation and face complexity |
| Bent sheet component | Sheet Metal component and process-specific rule | Bend radius, relief, thickness and valid flat pattern |
| Moving product | Separate components/occurrences and joints | Intended degrees of freedom, motion limits, interference |

Extrude, revolve, sweep and loft provide distinct geometric controls; rib and web differ in extrusion direction relative to the sketch. Feature operations distinguish new bodies from join/cut/intersect. Specify participants for cuts rather than relying on all intersecting bodies. [Solid creation tools](https://help.autodesk.com/view/fusion360/ENU/?guid=SLD-CREATE-SOLID-FROM-SKETCH).

For lofts, rails must intersect the sections and extend to their ends; select G1/G2 end conditions when continuity matters. Avoid extra sections that add complexity without expressing design intent. [Loft reference](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/GUID-EC6CECCD-55C1-4B08-95E4-5B1EEDE78D07.htm).

Form edits a T-Spline control structure rather than ordinary feature dimensions. Use it for styling and return to solid features for precise interfaces. [Create Form](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/GUID-5E68A3D4-1871-4F15-A80A-B0ACF3B9864A.htm).

## Parameter and dependency design

Name driving parameters after their function: wall thickness, mounting pitch, clearance, bore diameter. Preserve expressions and units; distinguish driving from reference dimensions. Constrain sketch position and intended geometric relationships rather than fixing everything to suppress movement. Full constraint is useful for repeatable dimensional designs, but not universally required for exploratory geometry. [Sketch constraint guidance](https://help.autodesk.com/cloudhelp/ENU/Fusion-Sketch/files/SKT-FULLY-DEFINE-CONSTRAIN-SKETCH.htm).

Use stable origin planes/axes or deliberate construction references where possible. A fragile projected edge can change after upstream topology edits. Group logical features, use descriptive names, and pattern a suitable feature/body/component instead of manually duplicating unrelated geometry. Apply finishing features after the main functional geometry when this reduces dependencies. Make reusable parts separate components when they need assembly identity; a body alone does not define a moving assembly.

Configurations express intentional product variants via parameters and other configurable aspects. They are different from repeated one-off parameter changes. Configuration Rules are an advanced Design Extension capability; basic configuration tables and rules have different access requirements. Verify every resulting combination for valid geometry. [Configuration table](https://help.autodesk.com/cloudhelp/ENU/Fusion-Configurations/files/CFG-CONFIGURATIONS.htm), [Design Extension](https://help.autodesk.com/cloudhelp/ENU/Fusion-Extensions/files/EXT-PRODUCT-DESIGN.htm).

## Imported geometry and specialty tools

Faceted mesh conversion can create a BRep face per triangle. Prismatic conversion uses face groups for manufactured shapes; organic conversion targets freeform shapes and is extension-gated. Repair and establish units first; use a measured fidelity requirement rather than maximum resolution by default. A non-watertight mesh may convert to a surface instead of a solid. [Mesh conversion](https://help.autodesk.com/view/fusion360/ENU/?guid=MESH-CONVERT-TO-SOLID).

Sheet metal rules encode thickness, K-factor, gaps, bend radius and relief. Use fabrication-specific settings, then verify the flat pattern; a plausible folded model does not establish the correct blank. [Sheet metal rules](https://help.autodesk.com/cloudhelp/ENU/Fusion-Sheet-Metal/files/SM-RULES-REF.htm).

Use joints to express assembly behavior. Joint and As-Built Joint differ in whether positioning is established; select the needed motion and limits rather than adding free motion indiscriminately. [Assembly relationships](https://help.autodesk.com/cloudhelp/ENU/Fusion-Assemble/files/ASM-JOINTS.htm).

Plastic features, modeled/cosmetic threads, draft, holes, embossing, shells, fillets and chamfers should express the production requirement. Do not impose generic wall/fillet/draft values without material and process context. Design Extension automation may simplify these workflows, but core features can still construct many equivalent shapes; equivalence of geometry does not imply equivalent rule-driven behavior.
