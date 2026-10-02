# Evidence and limitations

Initial public preview: October 2026. Live development used Autodesk Fusion on Windows through its local MCP endpoint. Other host installation routes are documented from vendor sources but have not all been live-tested.

Offline regression tests cover script construction, input contracts, selectors, parameters, JSON/SSE responses, no-replay behavior, mesh validation, multipart transform chains, malformed input and bounded XML parsing. Run the complete suite rather than assuming an export-success message proves geometry.

Live development checks exercised primitives; selected native feature families; a constrained size-adaptive socket organizer; 14/10/12-socket regeneration after material partition; recovery archives; root-body and transformed-assembly exports. Recipe references state the verified scope. General rendering scene setters caused application crashes and are excluded from ordinary preview workflows. Cloud-save lifecycle and all paid extensions are not release acceptance claims.

A user inspected both a three-region 3MF and simultaneous STL imports in PrusaSlicer, accepted the multi-material prompt, and confirmed alignment on the bed and in sliced output. Corrected two-region organizer outputs also passed user visual inspection. This is reported GUI evidence, not automated host/slicer certification. Extruder assignments, physical printing and material bonding have not been verified.

A custom indexed-3MF defect produced 896/984 open edges at duplicated face-boundary vertices. Exact per-region coordinate deduplication eliminated indexed seams without moving triangles. Independent index validation is retained. Slicer repair counters alone did not expose that defect reliably.

Native exporters are preferred. Native multipart export tests are tracked separately from legacy custom writer tests; do not transfer success between implementations without checking the actual files.

Timing records separate connection setup, MCP round trip, Fusion execution/verification and helper total. Assistant thinking, tool scheduling and response writing are excluded from helper total. Measurements vary with model, host and runtime; no end-to-end latency promise is made.
