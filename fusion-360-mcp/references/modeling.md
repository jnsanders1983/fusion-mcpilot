# General modeling and document operations

Discover the server's actual schemas. Expected tools are fusion_mcp_read, fusion_mcp_execute, fusion_mcp_update, and fusion_mcp_electronics_read; native host names can have prefixes. Establish the target with Read {"queryType":"document","operation":"open"}; resolve ambiguity. Use activeCommand if an interactive dialog is known or a mutation is rejected; do not cancel the user's command automatically.

Read supports documents, projects, active commands, API documentation, licensing, and screenshots, not arbitrary geometry queries. Use Execute scripts for geometry/parameters/timeline inspection. Define def run(_context: str): and print concise structured results. Let exceptions propagate from run. Set readOnly=true only for scripts that create, change, or delete nothing; do not use Application.executeTextCommand in these scripts. Read-only scripts can inspect the design while a command dialog is open. For mutations ask the user to finish or close the dialog if required.

Query unfamiliar API members using apiDocumentation, apiCategory="member", searchPattern=<member name>, filter=<fully qualified class>. Putting Class.member in the searchPattern did not reliably match this server; use the filter instead. Class-level results may be summaries. Preserve user dimensions, coordinate systems, component ownership, and product type. Use UnitsManager conversions; raw length values are normally centimeters. Reacquire entities after topology changes. Prefer editable features and constrained sketches when the task benefits from them.

After arbitrary modeling verify relevant dimensions, solid state, body/component counts, and feature health. Use screenshots for visual intent, but do not treat images as proof of dimensions. Rendered images are separate from CAD changes.

Save only on an express request. Closing a modified user document requires their save/discard choice before setting server confirmation flags. Do not initiate unrelated purchases, external actions, exports, or network exposure. User-authorized disposable benchmark documents may be discarded once their results have been logged; preserve and restore the original active document.

An error or timeout can leave partial changes. Inspect before retrying. Undo/redo applies to the most recent transaction; use only a known relevant transaction or an explicit user request.

For Electronics confirm an active Electronics document, discover its entity types/schema resources, and follow returned pagination. Do not use CAD casts against an Electronics document.

## Native Derive and imported references

Use native `rootComponent.features.deriveFeatures` for a supported linked derivation workflow. Inspect the installed contract: `createInput(sourceDesign)`, `sourceEntities`, `excludedEntities` and `isPlaceObjectsAtOrigin`. Saving to a Fusion cloud location requires a user-selected or user-authorized destination.

In Fusion 2705.1.25, Derive rejected an unsaved imported STEP source with `Cannot derive from a design that has no recorded changes`. Adding a native datum sketch did not resolve it; saving the source did, and the subsequent Derive feature was healthy. Do not treat that message as proof that another sketch is needed, automatically replay the failed mutation, or invent a custom replacement. Inspect partial state, check the source save state, and resolve authorized storage. This is a bounded observed requirement, not a claim about every source type/version.

Whole-root derivation preserved 26 solid instances, their volumes and translations in this demonstration. It also retained rigid groups; adding duplicate groups was rejected as overconstrained. Inspect constraints in nested components as well as the root before adding assembly relationships. Motion was verified in the source, not in the derived copy. Volume/position comparisons do not establish full surface equivalence.

Label imported/derived geometry accurately. Reusing reference castings is not reconstructing their editable feature history from a technical drawing. Keep source evidence, newly modeled features, inherited geometry, motion acceptance and remaining limitations distinct.
