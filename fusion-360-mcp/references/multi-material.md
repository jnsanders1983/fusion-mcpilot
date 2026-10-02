# Multi-body color and material exports

Use separate, solid regions with no volumetric overlap. Coincident interfaces are allowed. Keep every instance in the root assembly coordinate frame: tessellate native geometry, apply the complete occurrence transform chain, then convert Fusion centimeters to millimeters. Never center each part separately. Material names/colors describe regions; they do not configure printer extruders or prove filament compatibility.

Prefer Fusion's native `ExportManager.createC3MFExportOptions` and `createSTLExportOptions` for production delivery. Check their geometry contract and verify actual region placement, units and topology. The bundled `project_tools.export_script` currently covers one root solid; multipart native export requires a scoped script and separate acceptance checks. Do not infer assembly/subset behavior from a single-body test.

The legacy custom multipart writer requires an explicit user choice or demonstrated native gap. Invoke it with `scripts/export_multipart.py --backend custom --document "Exact active document" --regions <external-regions.json> --directory <new-output-directory> --log-dir <run-directory>`. Its external JSON list contains 2–32 entries:

```json
[
  {"selector":{"name":"Base"},"material":{"name":"PLA dark","color":"#404850"}},
  {"selector":{"name":"Insert solid","occurrence_path":"Carrier:1+Insert:1"},"material":{"name":"PLA teal","color":"#00A0A0"}}
]
```

Resolve current names/tokens and exact occurrence paths; do not reuse example paths without inspecting the live assembly. Repeated instances of a component require separate occurrence selectors. The helper is read-only in Fusion, checks interference, and writes numbered binary STLs, a core 3MF and one compact validation record. Output directory must be new; partial outputs on failure are unconfirmed and retained for diagnosis. XML checks require a Python runtime with Expat 2.7.2 or later; this is a minimum parser requirement, not a complete security certification.

STL is unitless; exported coordinates and validation are millimeters. Core 3MF declares millimeters, stores region names/colors, and references the region meshes from one assembly build item. Import behavior depends on the slicer. Validate per-region bounds/volume, mesh edge incidence/winding, and relative placement; these checks do not prove absence of all self-intersections.

Fusion tessellation can return separate vertex entries at exactly identical coordinates along face boundaries. Before writing indexed 3MF meshes, share these exact coordinates within each region and remap triangle indices. Do not merge between regions or round coordinates to close real gaps. Both index-based manifold adjacency and exact-coordinate geometric closure must pass; coordinate closure alone can conceal open indexed seams. This follows the [3MF core mesh rules](https://3mf.io/wp-content/uploads/sites/106/2025/02/3MF_Core_Specification_v1.3.0.pdf). The bit-dock defect reproduced the user's 896/984 open-edge counts; exact deduplication eliminated them without changing any triangle coordinates. PrusaSlicer CLI repair counters reported zero for the defective input too, so they are not a substitute for index validation or a GUI check.

The user verified the October 2, 2026 root-body fixture in PrusaSlicer: both the 3MF and all three STLs imported together prompted for multi-material import. Accepting the prompt preserved alignment on the bed and after slicing. This is user-reported GUI evidence for that fixture, not an automated test of every slicer or printer. Filament-slot assignments and physical prints were not verified. CLI behavior is a separate workflow and must not be inferred from GUI success or an export-success log.

For a new GUI acceptance test, import all STL regions together, accept the multi-part prompt, check the object contains separate parts, assign the intended slots and inspect sliced interfaces. Printer profiles, slicing and G-code belong to the slicer workflow. Keep that dependency optional: Fusion export works without PrusaSlicer installed. Retain recovery F3D only when requested or warranted; do not export development logs/code into Fusion cloud projects.

## Creating material regions

`scripts/material_regions.py` provides `split_script(document, selector, 'z', offset_expression, regions)`. It splits one selected root solid at a parametric XY plane into exactly two named solids, lower then upper. Each region specifies `name` and optional `rgb` integer channels. Execute with modifying MCP mode, after a local recovery checkpoint. No automatic replay or undo occurs on failure; inspect partial state. Assembly-context partitions and X/Y planes are outside the verified contract.

The helper checks an interior plane, two solid outputs, preserved total volume, aligned interface bounds and healthy native features. Color uses copied matte appearances without render scene changes. Material appearance does not alter engineering properties. A plane driven by `base_height` separates the graphite foundation/tray from the teal socket rack at Z = 8 mm. This creates true separate regions rather than face-color overrides.

After partition, use `parametric_organizer.variants_script(document, variants, expected_body_count=2)` for the two-region dock. It validates aggregate bounds and analytic volume, interface height, feature health, socket counts and positions. When the interface coincides with socket floors, it counts matching hex inner loops rather than missing merged floor faces. The post-partition dock was verified at 14, 10 and 12 sockets with clean exports, then restored to baseline. Never treat GUI evidence from the earlier fixture as acceptance of a new deliverable.

For a small two-color fit coupon, create a 50 × 20 × 9 mm rectangular blank with `profile_modeling.build_script`, then apply `hex_fit_coupon.cut_script(document, [6.55, 6.65, 6.75])`. Split at Z = 3 mm and export both regions. AF increases left-to-right; the middle pocket matches the dock. The coupon helper checks blank bounds, volume, constrained profiles, blind cut depth, entrance edges and analytic final volume. Pockets use fixed geometry coordinates; rebuild for different AF values. Printing the coupon checks fit and the interface, not full-dock warping or compatibility of unlike polymers.
