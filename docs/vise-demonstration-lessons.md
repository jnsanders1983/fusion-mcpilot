# Vise demonstration review — 2026-10-03

This demonstration reused the preserved STEP assembly through native Derive. It did not rebuild the castings as parametric features from the drawing. Reference PDFs, geometry, screenshots and run scripts remain local job records, outside the skill and repository deliverables.

## Verified results

- Fusion 2705.1.25 rejected two unsaved-source Derive attempts. A datum sketch alone did not resolve the error. After user-authorized cloud saving, Derive succeeded with healthy feature state.
- All 26 derived solid instances matched source volumes and translations within the declared checks; this is not a comprehensive surface comparison.
- Native source rigid groups and an as-built slider produced measured +20 and +50 mm world-Z travel for -20 and -50 mm drive values, then restored the original position. The initial sign assertion failed and was corrected after inspection.
- A 41-frame source animation traveled 50 mm and returned with zero measured restoration error. Screw rotation, pitch coupling and interference were not validated. The spindle was rigidly grouped with the translating carriage.
- Derived geometry retained rigid groups. Adding duplicate groups failed with overconstraint; derived-copy motion remains unverified.
- The working derived assembly was rotated as one parent occurrence to make +Z vertical. All 26 solid volumes remained unchanged. This orientation edit was unsaved at verification.

## User review and retained guidance

Nick preferred Z-up and identified accidental fragmentation of physical parts as a modeling concern. Z-up is recorded in the local workspace AGENTS.md; it is not imposed on every portable-skill user. Maintained drafting guidance now requires an intended part/body map, explicit Join versus New Body decisions and body/connectivity checks. The current imported divisions do not prove that a particular earlier extrude was corrected. No earlier reconstruction was repaired in this demonstration.

The maintained modeling reference records the saved-source observation, nested-constraint inspection and honest distinction between derived reference geometry and reconstruction. No one-off vise builder was added to the skill.

## Timing and next acceptance

The successful native save/check, Derive, finishing/check and animation blocks totaled 13.31 seconds. The later Z-up operation/check took 0.83 seconds. These exclude research, assistant reasoning, failed attempts and other reads; end-to-end latency was not measured.

Further work: reconstruct editable physical parts from drawing/CAD evidence, verify joins and datums, couple spindle rotation to travel using verified pitch, and check interference/clearance over the intended motion range. Visual similarity alone is insufficient.

## Sources

- [Native Derive input](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_DeriveFeatures_createInput.htm)
- [Native slider motion](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_AsBuiltJointInput_setAsSliderJointMotion.htm)
- [Drive-joint displacement units](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_SliderJointMotion_slideValue.htm)

Installed API docstrings were consulted for save, cloud project/folder creation, rigid groups and position capture. Installation and pushing require Nick's separate review; this change is source guidance only.
