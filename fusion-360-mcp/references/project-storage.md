# Project destinations and compact deliverables

## Successful-iteration consolidation

Use `scripts/project_workflow.py` for the supported rounded hex-organizer shape
family. It generates fresh native geometry from a layout, then checkpoints,
applies appearances, exports, captures a viewport and verifies mesh/functional
dimensions. `scripts/organizer.py` owns the configurable build; the shared
delivery, coupon and mesh modules remain its single sources of mechanics.
`assets/fixtures/bit-dock.json` is the compact benchmark layout, not a saved model.
Example command, substituting the user's chosen paths and a fresh document name:

```text
python '<skill-folder>/scripts/project_workflow.py' --layout '<skill-folder>/assets/fixtures/bit-dock.json' --document "Bit Dock revision" --output-dir <deliverables> --work-dir <run-records> --stem bit-dock --coupon-sizes-mm 6.55 6.65 6.8
```

Execution records belong to general tool activity: use
`<workspace>/work/fusion-runs/<run-id>` rather than a model-named folder.
Identify documents, operations and outputs inside each record; a run may touch
several designs. Reuse its directory while that run is active; use a fresh ID
for a separate run. Honor a user-selected working-record location.

After successful delivery, normal working records are `run.json` and
`actions.jsonl`. A failure retains its recovery archive and logs. Do not generate
per-stage Python, API catalogs, result JSON or extra mesh copies during normal
runs. Reuse a tested module; add a generalized function/configuration only when
there is a new capability. Put benchmark evidence in one compact history record,
not a new script tree for each iteration. Keep a prior native revision when
cleanup/replacement needs recovery; discard superseded copies of code and
regenerable outputs after verification. Preserve raw diagnostic evidence while
an unresolved crash is under investigation.

The installed skill is the runtime toolset. During development, keep one canonical
source tree in local `work`, then deploy its verified contents to the installed
folder and portable ZIP. The whole chat workspace also contains research, logs
and models; it is not the publishable skill. Only the portable ZIP belongs
in user-facing outputs. `scripts/package_skill.py` validates required fields,
references, Python syntax, installed byte equality and ZIP contents. It excludes
caches; it does not replace full YAML schema validation or live tests.

## Multi-body color/material printing

Use [multi-material exports](multi-material.md) for named regions, common-world
placement, STL/core 3MF delivery and target-slicer acceptance. Presentation face
colors alone do not define printable material regions. Keep printer and filament
configuration in the slicer workflow; the Fusion exporter has no slicer dependency.

For a new design, establish the intended destination early, before saving. Ask once
when unknown: **existing local folder, Fusion cloud project, or both?** For an
existing design, first identify its live document, project and folder; do not
silently create a competing project. Reuse the user's stated destination for the
current project. A new computer may use a different path or hub; resolve it there.

For local storage, accept the user's absolute path, including an existing project
directory. Honor its organization where reasonable. A convenient default, when
the user authorizes workspace output, is `<project>/cad`, `print`, `images`, and
`docs`. Fit coupons belong in `print/fit-tests`. Do not prescribe the Codex folder
as the user's permanent project location. Request filesystem access only if the
host needs it for the selected path. Preserve existing files and use revision
names when replacement was not authorized.

For Fusion cloud storage, inspect the user's available hub/project/folder and
resolve the actual target folder identity. Check permissions/access and whether
the document already has a data file. Saving a design, updating a version,
creating a project, and inviting teammates are different operations; do only what
the user's request covers. Confirm save/upload completion and actual project/file
identity before reporting cloud success. Don't treat an exported `.f3d` as a cloud
save. API `Document.saveAs` targets a `DataFolder`; use live API evidence before
an untested save. Teams and storage differ by account/license; avoid promising
collaboration just because a project is visible. [Fusion projects](https://help.autodesk.com/view/fusion360/ENU/?contextId=FT-PROJECTS).

Cloud projects should contain related Fusion design data and any specifically
requested project documents. Keep MCP logs, Python recipes, API dumps, validation
JSON, benchmarks and install packages in a local working/tool directory. Do not
upload the local output tree wholesale or share/invite anyone implicitly.

## Output budget

Prefer one editable native archive and one agreed printing format, plus a fit
coupon when fit is uncertain, one useful presentation image and short print
notes. For a single-body FFF project, 3MF is a good default because it declares
units. Add STL/OBJ only when requested or required by the destination; STL/OBJ
need an explicit millimeter convention. ZIP is an optional transfer artifact,
not a second default copy of every deliverable. Outputs by type are a convention,
not a reason to rearrange an existing user project without authorization.

Keep development records outside deliverables, e.g. `<workspace>/work/fusion-runs/<run-id>`.
Move reusable mechanics into the installed skill, not into each design's output.
Keep project-specific build recipes and benchmark evidence in the working area.
Generated caches and machine-specific settings do not belong in the portable
skill ZIP. If cleanup is requested, retain a recovery archive before replacing
or moving prior revisions.

## Reusable helpers

`scripts/project_tools.py` exports `prepare_paths(output_dir, work_dir)` and
`export_script(document, output_dir, stem, formats=('3mf','f3d'))`. Supply the
user's chosen paths; exports require the named active design, one healthy root
solid, and new filenames. Execute generated Fusion scripts through native MCP
or the configured `FusionClient`, with logs in `work_dir`. It does not save to
cloud. Assemblies need an explicit component/body selection and assembly-aware
validation rather than this single-solid shortcut.

The single-solid exporter also accepts `step` and `stl`. STEP belongs in `cad`;
STL/3MF belong in `print`. STEP round-trip geometry can be checked with the
recovery importer described in [native features](native-features.md), without
claiming preservation of native parameters or feature history.
Its STEP import route remains experimental because a script-channel fault followed
cleanup in a live test; use the recovery and readiness guidance before testing it.
`scripts/mesh_conversion.py <source.3mf> <destination.obj> --size-mm X Y Z`
`--volume-mm3 V` converts one validated millimeter mesh to OBJ and rereads it to
verify geometry preservation. OBJ has no declared length unit: coordinates use
millimeters. It retains triangles, not materials or a multi-part slicer structure.
Create these extra formats only when requested; the normal compact output budget
still applies.

`scripts/fit_coupon.py` generates a configurable hex socket fit coupon with
`coupon_script(target_document, output_path, sizes_mm)`. It exports only 3MF and
closes only the new coupon document after verification. The notched corner and
left-to-right list identify sizes. This recipe uses 10 mm blind pockets in a
12 mm slab; adapt it when the mechanism requires other depths or geometry.

`scripts/validate_mesh.py <file.3mf> --size-mm X Y Z --volume-mm3 V` checks
millimeter declaration, expected bounds, positive volume, edge manifoldness,
winding and one connected shell. Optional `--report <working-path>` writes JSON
outside user deliverables. It intentionally rejects transformed/assembled 3MF
data it does not handle. It does not detect every self-intersection or validate
strength/fit; add functional section checks for critical dimensions.

## Rendering and recovery

Export a recovery archive **before** appearance/workspace/render operations.
Separate appearance changes, workspace activation and render submission when
testing an integration. A crash can lose an unsaved document; an MCP disconnect
is an unknown outcome. Reconnect, inspect recovered documents/files and retain
original user data before recreating anything. Never replay a render blindly.

`project_tools.appearance_script` is a live-tested one-body organizer recipe
using copied matte plastic shaders, configurable RGB and roughness, with recessed
horizontal face accents. It does not change physical material or printing colors.
Matte roughness is a shader finish, not a bitmap surface texture.

**Observed integration limitation:** Fusion exited during the combined appearance/
workspace/scene/render attempt, then again in a separate scene-settings-only call.
Appearance-only and export calls succeeded. The exact failing scene property is
unknown. Do not run the automated scene-settings path again on this installation
until a controlled reproduction/fix is requested. No crashing scene recipe is
packaged as a normal helper. Use a clearly labeled viewport preview, or let the
user set scene/light controls in Fusion's UI. The public local-render API is a
possible independent route but must be tested before being called supported.
Don't report a viewport snapshot as a ray-traced render. Verify the finished image
and job status; prefer local rendering unless the user authorizes a cloud job and
any cost. [Autodesk rendering API sample](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/RenderSample_Sample.htm).

Report modeling/verification, export and render durations separately. Include
recovery/failed attempts in measured totals and state that research/thinking was
not included when only tool timings were captured. A styled rebuild can take
longer and produce a larger image while still reducing clutter; compare both
file count and actual bytes instead of assuming fewer files means fewer bytes.


### Later crash-report evidence

The copied second-crash CER report was inspected locally: minidump exception
`0xC0000005`, read address `0x1C`, faulting `NsScene10.dll` at offset `0x1C9CC0`.
The crashing stack includes `OGSMatrixToGeMatrix`, scene transform and
`Na::RenderUtil::getGroundCenter` during the isolated scene-settings script,
before render submission. Ground-related setters are suspected; the individual
property is unproven. Do not infer a GPU driver defect or blacklist all rendering.
Further reproduction requires a requested diagnostic task, disposable geometry,
recovery archive and per-assignment stage markers. The native exception explains
the loss of the embedded MCP endpoint; it was not a handled Python error.
