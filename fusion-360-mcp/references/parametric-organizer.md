# Native parametric organizer

Use this route when overall dimensions and socket count should regenerate inside
Fusion. `scripts/parametric_organizer.py` creates five fully constrained driving
sketches (base, rack, tray, seed hex and grip detail), native extrusions/fillets,
and rectangular feature patterns. It does not rebuild the document when parameters
change. Shared export, appearance, preview and mesh tools remain unchanged.

## Controls

Edit `overall_width`, `overall_length`, `overall_height`, `socket_pitch` and
`socket_af` in Fusion's **Modify > Change Parameters**. Dimensions are millimeters.
Other primary controls include `base_height`, `tray_floor`, `corner_radius`,
`side_wall`, `front_rim`, `bank_gap`, `socket_margin`, `socket_depth`, `lead_in`
and `rim_bevel`. Derived parameters should normally retain their expressions.

The tray length is one-third of overall length. The bank occupies the remainder
after the front rim, tray and bank gap. The grid is centered in that bank:

```text
socket_columns = 1 + floor((overall_width - 2 * socket_margin) / socket_pitch)
socket_rows    = 1 + floor((bank_length - 2 * socket_margin) / socket_pitch)
socket_count   = socket_columns * socket_rows
```

Thus increasing size does not necessarily add a socket immediately; it must cross
a pitch/margin threshold. Increasing pitch reduces capacity. User-chosen socket
counts are not independent controls in this auto-fit mode. If a fixed count is
requested, implement a separate spacing/extent rule rather than overriding the
derived count and risking overlap. [Autodesk floor-based pattern guidance](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-create-a-Parametric-Formula-that-increases-a-pattern-in-Fusion.html).

## Execution and verification

Create and deliver with the shared runner:

```text
python '<skill-folder>/scripts/project_workflow.py' --parametric --layout '<skill-folder>/assets/fixtures/bit-dock-parametric.json' --document "Parametric dock" --output-dir <chosen-output> --work-dir <workspace>/work/fusion-runs/<run-id> --stem bit-dock --coupon-sizes-mm 6.55 6.65 6.8
```

For a live parameter edit, use native MCP with `variants_script`, or:

```text
python update_organizer.py --target-document "Parametric dock" --set overall_width=130 --set overall_length=85 --log-dir <workspace>/work/fusion-runs/<run-id>
```

The edit route checks the current design contract and validates the complete live
parameter set with the proposed changes before mutation. Verification reacquires
the body, checks bounds, solid/feature health, all constrained sketches, actual
hex-floor count/centers and analytic volume including groove and bevel removal.
Changing topology can reset face-specific appearances; reapply the appearance
helper after the final geometry change, then export/preview again if requested.
Exports represent their saved parameter state, not later unsaved edits.

Supported geometry requires at least two columns and one row, up to 200 sockets;
positive dimensions, a solid floor and sufficient margin/pitch/radii. Defaults
are 104 x 66 x 18 mm, 15 mm pitch, 9 mm margin and 6.65 mm socket AF. Direct manual
UI edits can exceed these limits; Fusion may report failed features. The helper
rejects such input before mutation, but no automatic UI clamping/add-in is installed.
No claim that every possible parameter combination has been tested.

The original numeric-coordinate organizer still handles explicitly placed layout
data. Prefer this native route for size-adaptive regular grids; do not maintain
new per-job copies of either builder. `scripts/test_parametric.py` covers quantity
thresholds and invalid input. Random live tests should record their seed and values
in the general run record and restore a chosen final state after testing.

## Live learning

The 2026-10-01 test changed parameters in the same document through six randomized
variants, a 36 x 54 x 18 mm two-socket boundary case and a return to defaults.
All regenerated as one healthy solid, with five fully constrained sketches,
correct live count/placement and full styled analytic volume. Tests included
single-row and three-row patterns and capacities 2–18. This was native regeneration,
not a series of imported or rebuilt cached meshes. Physical printing/fit remains
untested. An over-constrained per-vertex dimension approach was replaced by a
construction circle with coincident vertices, equal polygon edges and orientation.
