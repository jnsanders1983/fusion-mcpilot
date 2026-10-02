# Automation evidence and API routing

Research date: 2026-10-01. Autodesk's current documentation may describe functionality newer than the installed build. Check unfamiliar classes/members against the connected server before calling them. Keep tested knowledge per build/server; do not treat documentation as a successful execution.

## Evidence levels

1. Documented product capability: Autodesk describes the tool.
2. Documented API capability: a public method/object exposes the needed operation.
3. Live capability: the installed build/product/license and MCP schema support the path.
4. Verified recipe: an actual model meets defined postconditions in a live test.

Record the level for unfamiliar workflows. API access does not bypass feature licensing. UI commands may require an interactive workflow when a public API is absent; report that limitation explicitly rather than issuing guessed text commands.

## Products and document structure

Fusion documents contain products; CAD, CAM and Electronics have different object models. Obtain a product from the document where appropriate rather than assuming `activeProduct` is always CAD. Components define geometry; occurrences place component instances. Use assembly-context proxies and transforms for world-coordinate checks, and distinguish a component definition inventory from expanded instances. [Document/assembly API](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ComponentsProxies_UM.htm).

Current design-intent documentation distinguishes Part, Assembly and Hybrid designs and feature availability. Inspect the installed design type and supported methods before creating components/features that depend on this distinction. Avoid silently converting the user's design type. [Programming for design intent](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/DesignIntent_UM.htm).

## Route by task

| Task | Public API starting point | Present skill evidence |
|---|---|---|
| Solid geometry, parameters, sketches | `adsk.fusion`, component features, sketch constraints/dimensions | Primitive recipes and a constrained parameter/extrude experiment tested live |
| Assemblies | Occurrences, transforms, joints, proxies | Documented; transformed assembly workflows not yet tested |
| Configurations | Design configuration tables/columns/cells | Documented; feature-specific access/version checks needed |
| Manufacturing | Document `CAMProductType`, `adsk.cam`, setups/operations/parameters | Public API documented; current active document has no CAM product; no machine output tested |
| Electronics | `adsk.electron` appropriate product; MCP Electronics read | Public design-editing API currently read-only/preview |
| Rendering | Render manager and installed public members | Public manager documented; rendering operation not tested |
| Simulation, generative, drawings, lifecycle | Verify actual public interface or supported UI workflow | Product capabilities researched; automated solves/drawing generation/release workflows not verified |
| Third-party add-in | Vendor-supported callable interface | No add-in automation verified |

[API manual](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/UserManualIndex_UM.htm), [CAM API](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/CAMIntroduction_UM.htm), [Configuration API](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Configurations_UM.htm), [Render manager](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_RenderManager.htm).

## Tested parameter-driven technique

In a disposable document on build 2705.1.25: create numeric user parameters from unit-bearing expressions; add two concentric circles; constrain each center to the sketch origin; drive diameters with parameter expressions; select the profile with two loops; extrude using `DistanceExtentDefinition` and `setOneSideExtent`. Vary diameter/bore/thickness expressions, recompute, reacquire the body and verify feature health, bounding size, solid state and analytic annulus volume. Three parameter variants passed with one fully constrained sketch and one extrusion. No configuration table or engineering solver was used.

[User parameters](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_UserParameters_add.htm), [Driving diameter](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_SketchDimensions_addDiameterDimension.htm), [Extrude extent](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_ExtrudeFeatureInput_setOneSideExtent.htm).
