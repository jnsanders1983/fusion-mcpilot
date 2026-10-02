# Optimization and evidence

Use this when the task asks for lighter, stronger, cooler, easier to manufacture, cheaper, faster, or better fitting designs. Choose a measurable objective and constraints first. Minimize mass subject to stiffness and fit, for example; do not equate lower volume with improved engineering performance.

## A useful iteration loop

Record a baseline: parameter expressions, units, material, manufacturing assumptions, envelope, mass/volume and relevant fit measures. Generate a small set of bounded parameter variants. Recompute and reject unhealthy or invalid geometry before comparing metrics. Keep a table of inputs, measured outcomes and assumptions. Select a candidate using the stated objective; retain enough evidence to reproduce it. Geometry-only sweeps can compare volume and dimensions without a paid solver, but cannot establish strength, thermal performance or lifetime.

For changes with important functional requirements, separate CAD geometry validation, manufacturability checks and engineering validation. Mass requires the correct physical material/density; appearance changes alone do not establish it. Confirm expected changes and unchanged interfaces. A successful `computeAll()` return only means recomputation completed—inspect feature/timeline health separately, as the live API documentation specifies.

## Match analysis to the question

| Question | Analysis family | Important assumptions |
|---|---|---|
| Small deformation under steady mechanical loads | Static stress | Materials, supports, contacts, load cases |
| Resonance susceptibility | Modal | Constraints, mass distribution, relevant excitation |
| Steady temperatures / thermally induced distortion | Thermal / thermal stress | Heat input, convection/conduction, reference temperature |
| Slender component instability | Buckling | Load path, modes, physical imperfections |
| Large deformation, material nonlinearity, changing contact | Nonlinear / quasistatic event | Material data and contact behavior |
| Impact or transient events | Dynamic event | Time history, contact, inertia |
| Enclosure/PCB temperatures | Electronics cooling | Heat generation and airflow assumptions |
| Mold filling / plastic quality | Injection molding | Polymer, gate and process setup |
| Lightweight load paths / design alternatives | Shape optimization / generative | Preserved interfaces, obstacles, loads, manufacturing constraints |

Advanced studies and generative workflows depend on access and may incur token charges. An extension is not required for every possible paid-license study. Inspect the chosen study's current entitlement and solve cost; Personal access must not be assumed to include simulation. [Simulation capabilities](https://help.autodesk.com/cloudhelp/ENU/Fusion-Extensions/files/EXT-SIMULATION.htm), [Flex tokens](https://help.autodesk.com/cloudhelp/ENU/Fusion-CloudCredits/files/CC-CLOUD-CREDIT.htm).

Shape optimization returns a guide for redesign; it is not a stress-validation result. Validate the reconstructed geometry with an appropriate stress study. [Shape optimization](https://help.autodesk.com/cloudhelp/ENU/Fusion-Simulate/files/SIM-SHAPE-OPTIMIZATION.htm). Use mesh refinement and compare consistent physical locations for convergence rather than comparing unrelated peak-stress nodes. Convergence addresses discretization, not incorrect material or boundary assumptions. [Mesh convergence](https://help.autodesk.com/cloudhelp/ENU/Fusion-Simulate/files/SIM-MESH-CONVERGENCE.htm).

## Inspection beyond counts

Measure important positions, radii, clearances and section thicknesses. Use interference checks with assembly context; intentional gasket/contact overlap may require interpretation. Zebra, curvature analysis and isocurves help assess surface quality; draft and accessibility analyses help identify manufacturing problems. Screenshots communicate these findings but do not replace numeric requirements. [Analysis tools](https://help.autodesk.com/view/fusion360/ENU/?contextId=SLD-INSPECT-TOOLS).

Improve process performance by reducing unnecessary features, repeated round trips and excessive mesh complexity; retain evidence checks. Batch a coherent operation and its verification, then vary parameters on existing editable features rather than repeatedly rebuilding them. Benchmark geometry work separately from MCP latency and the user's total prompt wait. Do not assume a large model benefits from the same tolerance, meshing or batching settings as a primitive.
