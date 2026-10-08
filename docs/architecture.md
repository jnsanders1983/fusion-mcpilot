# Architecture and source ownership

This package does not define or host MCP server tools. Autodesk Fusion's separate
service supplies the live tool schemas; the agent discovers them at connection
time. The optional client transmits requests and supports configured authentication.
Host permissions and server controls remain authoritative. The skill does not
install a scraper, scheduler, or autonomous learning service.

Offline tests live in `tests/`; packaging and local security inventory live in
`devtools/`. They are excluded from the install unit. The release file allowlist
is `devtools/release-files.json`; additions require review. The live acceptance
suite stays optional in the skill because it checks native CAD behavior and needs
explicit disposable documents. It never runs as part of offline CI.

The repository is the editable source of truth. `fusion-360-mcp/` is the portable install unit. Personal agent skill folders are runtime copies. The release ZIP is generated from an explicit selection of this skill, installer, setup guide and license; Git metadata, private work records and repository automation are excluded.

The agent loads `SKILL.md` first, then only task-relevant references. Recipes construct scripts using data serialized as JSON, execute supported Fusion API operations, and inspect live results. The optional standard-library client handles HTTP MCP when the host does not expose native tools. Settings remain external. Modifying requests are not automatically replayed.

Native Fusion features create editable geometry; acceptance checks cover each recipe's documented contract. Generic mesh validators check finite coordinates, dimensions, volume, closure and winding. They do not prove arbitrary design intent, all self-intersections, physical print quality, or mechanical performance.

For delivery, prefer Fusion's native exporters. The legacy custom multipart writer is retained behind explicit selection for diagnostics. It exact-deduplicates coincident vertices within each region; it never rounds coordinates or merges separate material regions. Removing that writer safely requires testing all assembly/subset contracts, not assuming a single-body export proves every case. Custom OBJ conversion is optional and must not replace an existing tool without a demonstrated need.

Projects choose local destination, Fusion cloud destination, or both. Ask once when that choice is unknown, then reuse it. CAD/print/images/docs are deliverables; logs, test scripts, recovery evidence and research snapshots are development records. Do not upload unrelated artifacts to Fusion cloud projects.

After an improvement: reuse existing modules, add representative checks, record the supported contract, update the installed copy and portable ZIP, and remove superseded temporary files after successful verification. Do not grow the skill by cloning project-specific scripts. The two coupon helpers currently serve different existing workflows and dimensions; consolidate their common mechanics before removing a callable interface.
