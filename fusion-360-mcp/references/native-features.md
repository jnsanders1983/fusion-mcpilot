# Native features, assemblies, parameters and recovery

Use these tested helpers for their supported contracts. Prefer native MCP when
available; each generator returns a standalone Fusion script. CLI helpers use
the shared configured client and Python standard library. Resolve paths relative
to the skill folder. Log in the user's working-record directory.

## Verified feature families

`scripts/run_features.py --recipe <name> --document "Unique new document"`
`--set width=60 --set height=14 --log-dir <run-records>` creates a new design.
Only supply controls supported by that recipe. `feature_recipes.RECIPES` is the
single source of defaults and available controls; dimensions use millimeters,
counts are integers and `top_scale` is unitless.

| Recipe | Supported geometry |
| --- | --- |
| `box` | Constrained rectangular sketch and native extrusion |
| `filleted_box`, `chamfered_box` | Four vertical edges, live geometric selection |
| `open_box` | Native shell with the top face removed |
| `hole_plate` | Centered rectangular grid of through-holes, native feature pattern |
| `boolean_union`, `boolean_cut`, `boolean_intersect` | Two overlapping rectangular extrusions and native combine |
| `loft_block` | Two rectangular sections with a common scale ratio |
| `straight_sweep` | Rectangular profile along a constrained straight path |
| `revolved_tube` | Full revolution about the root Y axis |
| `circular_hole_flange` | Disk with a circular native pattern of through-holes |

These are bounded parametric recipe families, not universal wrappers for all
profiles, paths or existing-body edits. They check current solid count, bounds,
position, analytic volume, constrained sketches, feature health and applicable
hole centers inside one execution. Deferred sketch computation is always restored
before profile access and feature creation. Invalid inputs fail before dispatch.
Creation refuses an existing document name; inspect partial state before retrying.

## API input acceptance and compatibility

Check documented return types when configuring feature inputs.
`ExtrudeFeatureInput.setOneSideExtent` and `ConstructionPlaneInput.setByOffset`
return success booleans. On false, stop before adding the feature or plane and
inspect the partial document. Absence of an exception does not prove acceptance.

New constant-radius fillet code should use
`input.edgeSetInputs.addConstantRadiusEdgeSet(edges, radius, isTangentChain)`.
It returns a `ConstantRadiusFilletEdgeSetInput`, unlike the boolean returned by
the retired `FilletFeatureInput.addConstantRadiusEdgeSet`. Check the returned
object before creating the feature and independently verify geometry and health.

These are documented contracts, not newly live-verified migrations. Some bundled
recipes still contain unchecked setup calls or the retired fillet method.
Inspect the selected helper before adapting it. Validate any migration with
nominal geometry, meaningful parameter boundaries and restoration in isolated
Fusion documents before transferring live acceptance claims.

Sources: Autodesk's [extent contract](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_ExtrudeFeatureInput_setOneSideExtent.htm),
[plane contract](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_ConstructionPlaneInput_setByOffset.htm),
[retired fillet method](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_FilletFeatureInput_addConstantRadiusEdgeSet.htm)
and [edge-set method](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_FilletEdgeSetInputs_addConstantRadiusEdgeSet.htm).

## Existing user parameters

`scripts/parameters.py --document "Design" --log-dir <records>` inspects numeric
user parameters. `--set "width=2 * length" --set "height=14 mm"` edits them.
Names are case-sensitive. Use explicit dimensional units; expressions are Fusion
data, not Python. An optional `--expectations <json-file>` can specify
`root_body_count`, `root_size_mm` and `root_volume_mm3`.

Checkpoint an important unsaved design before experiments. The editor validates
names and unit-compatible expressions, remembers changed expressions, recomputes
and checks feature health. Failed acceptance triggers restoration of only those
parameters, with independent expression, health, count, solidity, bounds and
volume checks. `ok:false` is a failed edit even when rollback succeeds; CLI exits
nonzero. `rollback_verified:false` requires inspection and recovery. These checks
do not prove full topology equivalence. Transport timeout cannot trigger rollback
from the client: the operation may still be running. Do not replay it.

Use the specialized organizer editor for socket count/layout acceptance; generic
health and dimensions alone do not prove functional socket behavior.

## Assembly inspection and native measurements

`scripts/inspect_assembly.py --target-document "Design" --log-dir <records>`
expands occurrence instances, including nested and repeated components. It reports
world centers in millimeters, transforms, visibility, per-instance volumes and
feature issues. World bounding boxes are conservative transformed local-box
envelopes, not exact bounds for curved bodies. Summed instance volumes include
overlaps. Nested grounding is unavailable through the property used; it is `null`.

`scripts/measure_geometry.py --document "Design" --selectors <json-file>`
`--operation distance --log-dir <records>` runs native minimum distance between
two distinct body instances. `--operation interference` accepts 2–50 instances
and reports native interfering pairs, excluding coincident faces.

Selectors are JSON objects with `name` or `entity_token` and optional
`occurrence_path` from live inspection. Resolve tokens through `findEntityByToken`
and exact occurrence paths; reject ambiguous names. A root selector without an
occurrence path addresses root bodies. Measurement is read-only and requires
the named document to be active. Zero separation alone does not prove overlap.
No simulation stresses, interference volumes or permanent bodies are fabricated.

## Local checkpoints and restore

`scripts/recovery.py --log-dir <records> snapshot --directory <new-checkpoint-dir>`
exports F3D and viewport PNG for each open CAD document, then restores the original
active document. `--document "Design"` scopes it to one design. Existing files are
never overwritten; PNG is a viewport image, not a render. Cloud data is unchanged.

`scripts/recovery.py --log-dir <records> restore --archive <file.f3d>`
`--document "Unique recovery copy" --expectations <json-file>` reopens a local
archive in a new document. Optional checks: `body_count`, `size_mm`, `volume_mm3`
for root solids and `parameter_expressions` mapping names to saved expressions.
Keep a failed recovery copy open for diagnosis. Restored user documents lose
benchmark disposal markers. STEP import is also supported, but preserves geometry,
not native feature history or user parameters. F3Z/cloud references need another
explicit workflow; this helper supports local F3D and STEP only.

STEP import remains experimental in this integration: a live geometry round trip
passed, but script responses became empty after closing the imported STEP test
document. The cause is unresolved. Checkpoint first, isolate tests, and check
readiness after cleanup; stop on an unconfirmed response. F3D recovery tests did
not show this fault.

## Benchmarking and failures

`scripts/acceptance_suite.py --log-dir <records> --iterations 3 --seed 123`
`--initial-checkpoint` generates fresh randomized models, verifies each, checkpoints
it and closes only documents carrying the matching disposable-test owner.
`--recipes <names...>` scopes the run. Failures stop the suite and retain the
partial document. Never apply its disposable cleanup to a user design.

Log MCP round-trip, in-Fusion build/verification, and full case time separately.
Case time includes archive, image and cleanup. None measures assistant thinking.
Compare identical seeded controls before/after a change; do not infer superiority
over other servers from unrelated benchmarks.

An empty `success:true` script response is unconfirmed, not proof of execution.
The client records `fusion_protocol_error` and refuses automatic replay. Native
document reads can help establish live state even when script execution fails.
`scripts/health.py --log-dir <records>` distinguishes native document access from
script readiness using a fresh read-only nonce. Run it for connection trouble or
after recovery, rather than adding a probe before every known-good operation.
Do not restart Fusion or discard unsaved user documents to repair that channel.
