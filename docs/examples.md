# Example requests

Start in a disposable design. Replace dimensions and destinations with your own requirements. The agent must inspect current state and resolve ambiguous targets; these prompts are examples, not a preauthorization to alter unrelated models.

**Inspect:** “Use Fusion MCPilot to list the active design's components, solids, parameters and feature warnings. Do not change it.”

**Primitive:** “In a new disposable design, create a 20 mm diameter sphere. Verify its dimensions, solid count and volume; report execution-and-verification time.”

**Parametric grid:** “Create a metric hex-bit organizer with overall size 104 × 66 × 18 mm and 15 mm socket pitch. Use editable native parameters and constrained sketches. Ask for the output destination before exporting.”

**Regeneration:** “For the organizer you just created, test three valid overall-size/pitch combinations. Verify socket counts, placement, dimensions, volume and feature health; restore the baseline afterward.”

**Material regions:** “Checkpoint this organizer, then split it into separate foundation and rack solids at its base-height parameter. Apply distinct appearances. Check total volume and interference. Prefer native export, preserving one common coordinate frame.”

**Assembly check:** “Inspect this assembly's instances and transforms. Measure the minimum distance between these two selected body instances. Resolve the exact occurrence paths before running the measurement.”

**Storage:** “Work in this existing local project directory and use this Fusion cloud project only for native CAD files. Keep print exports local and development records outside the deliverables.”

Native exporter availability, licenses, server schemas and document state are checked at use time. Never treat these examples as proof of mechanical suitability or a successful physical print.
