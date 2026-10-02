# Production, electronics and deliverables

Read only the sections relevant to the requested output. A modeled part, a production setup and a verified manufacturing output are separate deliverables.

## Manufacture

Start from process, machine/controller, stock, fixtures, workholding and work coordinate system. Choose tools and strategies appropriate to material and geometry: clearing before finishing, accessible radii, drilling/hole work, turning or cutting where appropriate. Compare stock removal, remaining stock, collision status and cycle-time estimates instead of assuming a shorter toolpath is better. Machine settings and estimates must match the intended equipment.

Set model, stock and fixtures explicitly; check WCS orientation and origin. Include fixtures in relevant simulation. Confirm regeneration status after design changes. Postprocessing additionally requires the correct controller/post and output settings; a postprocessed file is not proof that a physical setup is correct. [Setup reference](https://help.autodesk.com/cloudhelp/ENU/Fusion-CAM/files/MFG-REF-SETUP-MILL.htm).

Manufacturing Extension tools can add simultaneous multi-axis paths, collision-avoidance controls, toolpath modification, part alignment/inspection, nesting and metal additive support/build workflows. Choose them to resolve a specific process need and verify access. They do not make a machine multi-axis merely because the software supports it. [Manufacturing Extension](https://help.autodesk.com/cloudhelp/ENU/Fusion-Extensions/files/EXT-MANUFACTURING.htm).

For FFF and mesh export check scale, orientation, wall thickness, manifold/solid state and intended tessellation. For nesting distinguish layout utilization from verified cut-ready output; consider material, sheet size, spacing, grain/orientation and quantities. Sheet metal delivery must use the intended flat pattern and bend information. Do not automatically export/post/run a machine when the user requested only a model.

## Electronics

Fusion supports schematic, PCB, libraries and mechanical PCB integration. Check enclosure fit, connectors, mounting holes and component envelopes in the correct coordinate frame. Electronics cooling and signal-integrity analysis address different questions.

The current public `adsk.electron` API is preview and read-only for design modifications: it supports inspection/navigation and supported exports, not public layout creation/editing. The installed MCP Electronics read tool is also an inspection route. Confirm document type and pagination. Do not substitute a CAD `Design` cast or promise automated routing/board edits from an inspection API. [Electronics API](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ElectronicsIntro.htm).

## Drawings, presentation and data

Drawings convey views, sections, details, dimensions, holes/threads, tolerances and assembly information. Check standard, units, references and current design version. Drawing automation has configurable annotation/view preferences; it still requires review of functional dimensions. [Drawing automation](https://help.autodesk.com/cloudhelp/ENU/Fusion-Drawing/files/DWG-REF-AUTO-PREFERENCES.htm).

Rendering communicates materials, lighting and appearance. Animation communicates assembly or motion; neither validates strength or fit. Inspect local/cloud options and output costs before a cloud submission. Document and version operations must identify the correct project/file rather than a fuzzy title alone. Fusion Manage adds lifecycle processes; local filenames do not establish release approval. [Workspace map](https://help.autodesk.com/cloudhelp/ENU/Fusion-GetStarted/files/GS-WORKSPACES.htm).

## Third-party extensions to the workflow

Scripts/add-ins and Autodesk paid extensions are different. Marketplace categories can fill needs such as gears/fasteners, parameter utilities, BOM/export, specialized imports and production integrations. Evaluate a candidate's actual vendor documentation/source, supported Fusion version/platform, license, installation path, callable API/commands, output fidelity and required network services. A visible toolbar button is not evidence it can be invoked through this MCP. Prefer an existing tested core route when it accomplishes the task without extra dependencies.

No third-party add-in is installed or endorsed by this knowledge update. Choose and evaluate a concrete add-in when its capability is required. [Scripts/add-ins and marketplace](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/SLD-ADD-IN-TOOLS.htm).
