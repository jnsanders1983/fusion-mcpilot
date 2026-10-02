# General modeling and document operations

Discover the server's actual schemas. Expected tools are fusion_mcp_read, fusion_mcp_execute, fusion_mcp_update, and fusion_mcp_electronics_read; native host names can have prefixes. Establish the target with Read {"queryType":"document","operation":"open"}; resolve ambiguity. Use activeCommand if an interactive dialog is known or a mutation is rejected; do not cancel the user's command automatically.

Read supports documents, projects, active commands, API documentation, licensing, and screenshots, not arbitrary geometry queries. Use Execute scripts for geometry/parameters/timeline inspection. Define def run(_context: str): and print concise structured results. Let exceptions propagate from run. Set readOnly=true only for scripts that create, change, or delete nothing; do not use Application.executeTextCommand in these scripts. Read-only scripts can inspect the design while a command dialog is open. For mutations ask the user to finish or close the dialog if required.

Query unfamiliar API members using apiDocumentation, apiCategory="member", searchPattern=<member name>, filter=<fully qualified class>. Putting Class.member in the searchPattern did not reliably match this server; use the filter instead. Class-level results may be summaries. Preserve user dimensions, coordinate systems, component ownership, and product type. Use UnitsManager conversions; raw length values are normally centimeters. Reacquire entities after topology changes. Prefer editable features and constrained sketches when the task benefits from them.

After arbitrary modeling verify relevant dimensions, solid state, body/component counts, and feature health. Use screenshots for visual intent, but do not treat images as proof of dimensions. Rendered images are separate from CAD changes.

Save only on an express request. Closing a modified user document requires their save/discard choice before setting server confirmation flags. Do not initiate unrelated purchases, external actions, exports, or network exposure. User-authorized disposable benchmark documents may be discarded once their results have been logged; preserve and restore the original active document.

An error or timeout can leave partial changes. Inspect before retrying. Undo/redo applies to the most recent transaction; use only a known relevant transaction or an explicit user request.

For Electronics confirm an active Electronics document, discover its entity types/schema resources, and follow returned pagination. Do not use CAD casts against an Electronics document.
