# Capability and access map

Research date: 2026-10-01. This maps capability families, not every command or a permanent entitlement table. Read it when choosing a workspace, considering an extension, or encountering an access restriction. The host's live license and installed build take precedence over this research snapshot. An advertised feature, an available API member, and a working MCP operation are three different levels of evidence.

## Access models

| Access | Practical treatment |
|---|---|
| Personal use | Core hobby modeling with restricted manufacturing, documentation, collaboration and data interchange. Do not assume paid extensions or simulation access. |
| Education | Eligibility-based educational access; check assignment and extension-specific availability. It is not a commercial license or proof of every extension entitlement. |
| Startup | Application-based program; verify current eligibility and assigned capabilities instead of treating it as Personal. |
| Fusion subscription | Integrated design, manufacturing, electronics and collaboration foundation. Individual advanced features can still require an extension or tokens. |
| Fusion for Design / Manufacturing | Bundled offerings with broader respective capabilities; inspect the actual assigned bundle rather than equating their names with every paid feature. |
| Extensions / Flex | Feature-specific access; purchase options and token charges depend on license and action. Confirm the displayed access/cost before a chargeable action. |

Personal use includes limited 2/3-axis milling, turning, FFF and cutting workflows; Autodesk's comparison excludes automatic tool change, rapid feed and 3+2 capabilities from Personal. It lists two schematic sheets and four signal layers for Personal. Export support is format-specific: a blank broad comparison row must not be interpreted as no export at all. [Personal comparison](https://www.autodesk.com/products/fusion-360/personal/compare).

Personal is intended for qualifying home-based noncommercial work; Autodesk specifies a revenue threshold and exclusions. Verify current terms when license suitability matters. [Personal access](https://www.autodesk.com/products/fusion-360/personal). Education, startup and bundled offerings have separate eligibility/access conditions. [Offerings](https://www.autodesk.com/products/fusion-360/extensions).

## Extension families

| Family | Useful situations |
|---|---|
| Design | Plastic rules, bosses/snap fits, manufacturing advice, configuration rules, graded geometric patterns, organic mesh conversion and volumetric lattices. |
| Simulation | Advanced structural, thermal, electronics-cooling, molding and event studies; generative alternatives. Study setup and outcome validation remain necessary. |
| Manufacturing | Advanced multi-axis strategies, toolpath edits, inspection/alignment, nesting and metal additive workflows. |
| Fusion Manage | Product lifecycle processes, changes/releases, requirements and BOM-related collaboration. It is a separate product with Fusion integration. |
| Third-party add-ins | Specific generators, import/export, parameter tools and integrations. Their license, compatibility and automation interface are independent. |

The former Machining, Additive Build and Nesting & Fabrication extensions are consolidated into Manufacturing; Generative Design is included in Simulation. Signal Integrity is no longer offered for new purchase/trial according to current help. Older comparison pages still list it; retain this discrepancy rather than recommending a new purchase. [Current extension overview](https://help.autodesk.com/cloudhelp/ENU/Fusion-Extensions/files/GUID-EEE56836-C03A-4B10-A51C-A6203CF46AC4.htm), [Manufacturing](https://help.autodesk.com/cloudhelp/ENU/Fusion-Extensions/files/EXT-MANUFACTURING.htm), [Simulation](https://help.autodesk.com/cloudhelp/ENU/Fusion-Extensions/files/EXT-SIMULATION.htm).

## Live access checks

Use `fusion_mcp_read` with `queryType=licensing` when the requested tool is gated or license state changes. Do not add this round trip to routine known primitive requests. Record the timestamp, license summary, service entitlement states, active extensions and checking/initialization flags. A listed purchasable extension is not an active extension. Unknown token balance is not zero. Conflicting legacy premium/ultimate flags do not override Personal/Hobbyist service data. If entitlement checking persists, keep access provisional and verify the specific command in the application.

The 2026-10-01 local snapshot reported Personal/Hobbyist, no active extensions, unknown tokens and entitlement checking in progress, alongside contradictory premium/ultimate summary flags. This is evidence from that session, not a setting to hardcode for other computers. Revalidate subscriptions, prices, extension availability and recent/preview APIs when they affect a new task; stable modeling guidance can be reused.
