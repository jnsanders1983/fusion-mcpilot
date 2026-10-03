# Drawing reconstruction and native motion validation

Treat this workflow as a validation contract, not as proof that a specific example is production-ready.

## Drawings

Inspect every relevant sheet visually, including sections, thread notes and the bill of materials. OCR alone is insufficient for fractional dimensions, diameter symbols, hidden lines and tolerance classes. Preserve source-unit expressions (for example, `7.25 in`) and select millimeter display units independently. Do not estimate from a sheet's printed scale when a dimension is provided.

Maintain a dimension ledger linking each control to its sheet and view. Mark missing dimensions, conflicting interpretations, inferred interfaces and deliberately simplified hardware. Published supplier envelope drawings are not complete manufacturing drawings. Public availability does not establish permission to redistribute an image; use a source link until rights are established.

## Native geometry

Use editable native sketches and features. Ground the stationary component and retain independent component identities for moving parts. Query the installed thread catalog using exact family names: `ISO Metric profile` and `ISO Metric Trapezoidal Threads` are different families. Catalog size strings can contain numbered screw labels such as `0.06(#0)`; never blindly parse every size as a float.

Determine extrusion direction from the actual sketch plane and inspect resulting world bounds. A familiar plane name does not establish its normal direction. Validate feature health after full recomputation, not only immediately after feature creation.

## Motion

Create native joints and motion links. Joint direction enums refer to the joint geometry's coordinate system. Verify the resulting direction vectors in assembly coordinates. When editing an existing joint's custom direction, roll the timeline immediately before that joint and restore it to the end in a `finally` block.

For screw drives, use the drawing's actual pitch or lead. A single-start 11-TPI thread advances `1 in / 11` per revolution. Do not silently apply this relationship to multi-start threads.

A successful motion-link creation is not evidence of linked movement. Measure actual occurrence transforms under native Drive Joints or Animate Joint Relationships. Native joint-motion value setters can drive linked movement: set the value, process events, refresh the viewport, and inspect the live joint values and `Occurrence.transform2` before a full recomputation. A subsequent `computeAll()` can reset a driven pose to its assembly definition; an unchanged transform after recomputation does not establish that driving failed. Separate feature-health recomputation from pose validation. Restore the starting pose after testing. Command launch alone does not prove animation success.

Previous approximate bench-vise attempts are retired and must not be used as validation or as a reconstruction template. Follow the skill's drafting and design-intent guidance and establish fresh evidence for each new practice part and mechanism.

Autodesk distinguishes Animate Joint (isolated joint) from Animate Joint Relationships (assembly relationships). An active native animation preview can block modifying MCP scripts. Inspect the active command; stop dependent mutations until the preview is closed. Do not mark a modifying script read-only to bypass this restriction.

## Independent acceptance

Check component and solid counts, source dimensions, feature health, guide clearance, screw capture, travel limits and interference at representative positions. A healthy feature timeline can still contain mechanically overlapping solids. Interference between a rod and its ball grips may represent an intentional join in a simplified assembly; interference between the sliding jaw and stationary bed requires correction. Document the distinction instead of accepting every overlap or silently excluding it.

After a Join operation, verify the expected body count in that component. Disjoint additions can leave separate solids even if the feature succeeds. Reacquire participant bodies after topology changes and validate cuts after full recomputation. Avoid overlapping lofts and crowns that leave small ledges; join matching sections where possible before selecting casting fillets.

Do not publish a demonstration as a faithful or functional reconstruction while dimensional assumptions, unintended interference or motion verification remain unresolved.

References:

- [Autodesk: Edit joints](https://help.autodesk.com/cloudhelp/ENU/Fusion-Assemble/files/GUID-C0DCB65B-87F6-43AC-8A62-CC68B27EEB6E.htm)
- [Autodesk: Motion Link](https://help.autodesk.com/cloudhelp/ENU/Fusion-Assemble/files/GUID-074622A9-EC62-4A2E-9BBC-DB61748C869F.htm)
- [Autodesk: SketchCurve.isFixed](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_SketchCurve_isFixed.htm)
