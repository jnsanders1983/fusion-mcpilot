# Changes

## Unreleased

- Move offline tests and packaging/security inventory utilities out of the installed skill.
- Package only explicitly listed release files; reject path escapes, linked inputs and existing archives.
- Remove installation from the release builder; retain the separate backup-aware installer.
- Refuse security inventory report overwrites and add release-boundary regression tests.
- Document privacy, credential transmission and the separate Fusion server/tool boundary.

## 0.1.0 — public preview

- Fusion MCPilot name and original workshop-drone mascot; stable `fusion-360-mcp` identifier.
- Portable Agent Skills package with external endpoint settings and host-specific installation guidance.
- Reusable native modeling, parametric organizer, inspection, recovery, delivery and geometry validation helpers.
- Explicit native-first policy and opt-in legacy custom multipart exporter.
- Scoped performance reporting, no automatic mutation replay and security boundaries.
- Repository checks, contribution guidance and separation of public source from private development records.
