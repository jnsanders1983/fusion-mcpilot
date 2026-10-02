# Fast primitive recipes

For native tools, read scripts/primitives.py and set its top-level SHAPE, DIMENSIONS_MM, REPLACE_BODY, EXPECT_DOCUMENT_NAME, and FIT_VIEW assignments in the script sent to fusion_mcp_execute. Do not edit the installed defaults for each request. Pass featureType="script", object.script=<complete adjusted script>, readOnly=false.

If native tools are absent, invoke scripts/run_primitive.py instead of composing a new MCP client. It reads personal configuration dynamically, initializes a session, renders the packaged script using AST assignments, runs it once, and logs actions and performance automatically. It supports anonymous local servers and configured header/token environment variables; it does not load the desktop app's OAuth credential store. Use native tools for OAuth-connected servers.

Example (substitute the installed skill's actual path and the available Python executable):

```powershell
python '<skill-folder>/scripts/run_primitive.py' --shape sphere --radius-mm 22 --log-dir '<workspace>/work/fusion-runs/<run-id>'
python '<skill-folder>/scripts/run_primitive.py' --shape torus --major-radius-mm 35 --tube-radius-mm 8 --replace-body 'Skill sphere' --target-document 'Untitled' --log-dir '<workspace>/work/fusion-runs/<run-id>'
```

Only pass --replace-body when replacement is authorized. Use the actual returned body name; Fusion may add suffixes such as (1). An ambiguous or missing name rejects the operation before changing geometry. --target-document guards against an unexpected active document. --dry-run prints the rendered script without connecting. --no-fit is for benchmarks or a user's explicit request to preserve their view; otherwise instant fitting is enabled.

Shapes and inputs:

- sphere: {"radius":25}; default sphere diameter 50 mm when no size is given.
- torus: {"major_radius":35,"tube_radius":8}; major radius must exceed tube radius.
- frustum: {"base_radius":25,"top_radius":10,"height":60}; set top_radius=0 for a cone, or top_radius=base_radius for a cylinder.

For a random shape, choose dimensions freshly with SystemRandom; choose a different shape than the previous test. Give reasonable millimeter dimensions and report the chosen values. Set REPLACE_BODY to the exact previous generated body's name only when deletion/replacement is authorized. The script accepts only bodies marked with this skill's attribute or named Sphere 50 mm / Random torus from the original tests. It creates and verifies the replacement before removing the requested prior shape. If anything fails, inspect live state before retrying; partial creations can exist.

The recipe creates a closed sketch profile on the root XZ plane and revolves it 360 degrees about the root Z axis as a new body. It uses UnitsManager.evaluateExpression for millimeter conversion. It verifies solid state, analytic volume, bounding dimensions, and feature health; it does not save the document. Non-root components or other origins require adapting and checking the geometry. It retains existing sketches when replacing a body to avoid deleting potentially reused geometry.

The viewport is fitted with camera.isFitView=true and camera.isSmoothTransition=false, then the camera is reassigned to the viewport. This frames the entire model without the measured approximately half-second fit animation. Global Fusion graphics preferences are not changed.

Performance logs include preparation, modeling, verification, replacement, and view phases inside Fusion, plus MCP round trip, connection setup, and runner total. The latter is not prompt-to-result latency. The setup ZIP includes the identical scripts, so the next computer needs no hardcoded account path or URL change in the code.

Known API contracts established against the local Fusion server during setup:

- SketchArcs.addByThreePoints(startPoint, point, endPoint); orientation may swap arc endpoints.
- SketchCircles.addByCenterRadius(centerPoint, radius); numeric radius is in internal centimeters.
- RevolveFeatures.createInput(profile, axis, NewBodyFeatureOperation).
- RevolveFeatureInput.setAngleExtent(False, ValueInput.createByString("360 deg")).
- UnitsManager.evaluateExpression(expression, units) returns internal units.
- Camera.isFitView frames the whole model; Camera.isSmoothTransition=false disables the camera animation for this operation.

Refresh relevant documentation on a signature error or changed server capabilities. Reuse knowledge of methods, never entity objects or a prior success response.
