---
name: fusion-360-mcp
license: MIT (see LICENSE)
description: Inspect, model, and improve Autodesk Fusion designs through MCP. Use for geometry, sketches, parameters, assemblies, manufacturing preparation, and Fusion capability or extension guidance. Electronics inspection requires an Electronics document.
compatibility: Requires Autodesk Fusion with its MCP service and an agent with local MCP or script execution access. Optional command helpers require Python 3.11+ and HTTP(S) access to Fusion.
---

# Fusion MCPilot — Autodesk Fusion through MCP

Research unfamiliar workflows and check supported native Fusion operations and established libraries before implementing a custom route. Prefer native modeling and export features when they meet the requirements. Custom implementations need a demonstrated gap or the user's explicit choice. Independent validation remains useful even when production uses native exporters. The bundled custom multipart writer is a legacy, explicitly selected route; it must not silently replace Fusion's native export.

Use the user's configured Fusion MCP server, conventionally named `fusion360`. Its address and permissions belong to the host's personal MCP settings or external runtime configuration, never a hardcoded script URL. Read [connection setup](references/connection.md) only for setup or connection failures. For installation in another agent, read [portable agent setup](references/portability.md). Resolve all packaged resources relative to this skill's directory; do not assume a working directory or installation path.

## Fast primitive requests

For a sphere, torus, cone, cylinder, or circular frustum at the root origin, use [primitive recipes](references/primitives.md) and the packaged script. Reuse documented method knowledge while the server is unchanged; do not re-research known recipes. Always inspect live document/product and replacement state inside the script. Never use previous geometry or a previous success response as evidence of current state.

Prefer the native `fusion_mcp_execute` tool when available. If it is absent, the packaged `scripts/run_primitive.py` provides a single-command route through the configured MCP endpoint and automatically logs results/timings. It needs Python 3.11+ and no third-party packages. Do not rewrite the client or primitive recipe for an ordinary request. Change only numeric arguments and the explicit replacement/target document. Use fresh random dimensions when requested, and report the actual chosen values.

The recipe verifies solid geometry, bounding dimensions, analytic volume, feature health, and replacement body count in the same execution call. Its instant camera fit still frames the model. A second verification call or screenshot is needed only for incomplete results, unusual geometry, or a visual request. The server rejects mutations during an active dialog; inspect the dialog after that rejection instead of querying it routinely.

## Other Fusion work

For dimensioned drawings and mechanical feature planning, read [drafting and design intent](references/drafting-and-design-intent.md). Identify functional datums, record dimension evidence, and express symmetry with construction geometry, constraints and native mirrors/patterns. Verify behavior under parameter changes before calling a reconstruction faithful.

For learning and practice, use a focused research-build-check-retain cycle. Reuse demonstrated contracts while applicable, cover distinct concepts, and start with nominal and meaningful boundary cases. Expand research or randomized testing for actual uncertainty or failures. Avoid idle gaps during an authorized practice window. Close completed temporary practice documents without saving when the user has authorized discarding them; retain evidence or a recovery checkpoint first when needed. Track documents created by the run and never close unrelated or user-owned designs merely because their names look similar. Measure overall progress separately from native operation speed; see the efficient-learning section in drafting and design intent.

For verified extrude, shell, fillet/chamfer, boolean, loft, straight sweep, revolve and hole-pattern families, use [native feature tools](references/native-features.md). That reference also covers general user-parameter edits with verified rollback, assembly instance inspection, minimum distance/interference, local checkpoints and fresh-model regression tests. Reuse the tested helper when its contract fits; inspect unfamiliar geometry before adapting it.

For size-adaptive regular socket grids, use [native parametric organizer](references/parametric-organizer.md). Overall dimensions and pitch drive centered grid counts through fully constrained sketches and native feature patterns; validate live regenerated geometry after parameter changes.

For project creation, existing-folder work, exports or cloud delivery, read [project storage and compact outputs](references/project-storage.md). Establish local folder, Fusion cloud project, or both early when unknown; reuse the user's chosen destination. Keep development records local and reusable tools in the skill. Export a recovery archive before experimenting with rendering on an unsaved design.

For separate color/material regions and assembly exports, read [multi-material exports](references/multi-material.md). Use the reusable export helper to preserve the full occurrence transform chain and millimeter coordinates. Slicer settings and G-code are separate from Fusion export.

After a successful iteration, review generated artifacts for reusable mechanics. Consolidate them into existing skill modules or configuration-driven helpers and validate them. Rebuild the portable package when affected; install or synchronize only within the user's authorized deployment scope. Keep one compact run record and logs; remove superseded generated scripts/API dumps only after verified delivery. Do not copy project-specific geometry, paths, screenshots or logs into the skill as new per-job code. See the organizer benchmark in the storage reference.

Choose methods by functional geometry, editability and manufacturing process. For unfamiliar or evolving designs, read [design strategy](references/design-strategy.md). For improvements to mass, fit, performance or manufacturability, read [analysis and optimization](references/analysis-and-optimization.md). For paid features/access questions, read [capability map](references/capabilities.md); query licensing only when access matters. For CAM, Electronics, drawings, rendering, lifecycle work or third-party add-ins, read the relevant sections of [production and delivery](references/production-and-delivery.md). Check [API evidence](references/api-capabilities.md) when choosing an untested automation route. Read only the guidance relevant to the request; do not load the full knowledge set for a known primitive.

Read [modeling guidance](references/modeling.md) for arbitrary geometry, non-root components, scripts, document management, Electronics, and unfamiliar API methods. Discover live schemas on first use, a connection/server change, or a schema error; retain them within the current connected chat. Resolve ambiguous document targets before editing.

Execute the user's requested edits without routine reconfirmation. Save/export only within the user's requested delivery scope and resolved destination; do not silently choose a cloud project. On an error or timeout, inspect live state before retrying: partial geometry can exist. Never automatically replay a modifying request or undo unrelated transactions.

For live body inventory, feature warnings, or recovery after an uncertain result, use `scripts/inspect_design.py --target-document "Document name" --log-dir <workspace-log-directory>` through the configured endpoint, or its read-only recipe through native MCP. It returns component definitions, body tokens, bounds in component coordinates, volumes, and feature warnings. Tokens must be resolved using Fusion's `findEntityByToken`; do not compare token strings as persistent identity. Inspection does not prove arbitrary geometry meets the user's design intent. See [robust workflows](references/robustness.md) for operation contracts and expansion priorities.

## Timing and results

After every Fusion prompt, report execution-and-verification seconds with its scope. The runner separately reports the MCP round trip, in-Fusion execution, connection setup, and runner total. **Runner total excludes assistant thinking and response writing.** If the host exposes a trustworthy prompt start time, also report prompt-to-result latency; otherwise say it was not measured. Never imply subsecond Fusion time equals the user's total wait.

Store execution records under `work/fusion-runs/<run-id>` in the writable workspace, or the user's chosen records location. Keep model identity inside the records. Use that run directory for `--log-dir`/`--work-dir` and reuse it while the run is active; use a fresh ID for a separate run. Native calls should log the same scope when timing is available. If timing cannot be measured, state that; for prompts without Fusion operations, say execution time is not applicable. Report the result, verification outcome, and unsaved/saved status concisely.
