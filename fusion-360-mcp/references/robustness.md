# Robust workflows

Every reusable operation needs an explicit contract: target document and component, units, resolved entity selection, input limits, intended geometry, changed entities, feature health, and relevant measurements. Compile arguments as data rather than interpolating executable strings. Use explicit exceptions for required checks; Python optimization can remove assertions and their side effects.

Bundle related modeling and verification into one short Fusion execution. Keep changing geometry on the Fusion API thread. Do not copy FreeCAD's `Part`, `FreeCADGui`, recompute, document transaction, or headless process APIs into Fusion scripts.

Transport completion, feature health, and design correctness are distinct. A healthy feature can still point along the wrong axis. Check positions/orientation and analytic geometry when the recipe permits; use visual verification for visual requirements. Resolve body/face/edge selection live and reject ambiguous matches. Assembly inspection must specify component-local versus world coordinates and whether it counts definitions or occurrence instances.

The client writes a unique operation ID and script hash before dispatch. A timeout or lost reply remains an unconfirmed outcome. Inspect the live model before deciding what to do next. This audit ID is not server-side deduplication and does not guarantee exactly-once execution. Avoid broad undo because it can affect the user's intervening work.

Run `inspect_design.py` for recovery inventory. It never edits, fits the view, or saves. Feature warnings are listed separately; an empty list is not an OCCT-style full shape-validity test. Bodies and bounds are component definitions, not an expanded assembly BOM.

The supported bounded feature families, parameter rollback and occurrence-aware measurements are documented in [native features](native-features.md). Further expansion should address arbitrary profile/path selection, joints, targeted existing-body edits and manufacturing contracts. Each added operation needs a valid live case, rejected invalid inputs, and an appropriate failure/recovery test. Do not advertise unimplemented recipes as supported tools.

Add-in work, rather than skill-folder changes, is required for a GUI job queue with per-request response channels, queue/run timing, cancellation-before-start, non-GUI health checks, and persistent completion/deduplication records. A client timeout cannot stop already-running Fusion code. Do not disable modal guards to gain throughput.
