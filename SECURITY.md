# Security

This repository provides an agent skill and optional client, not an MCP server.
Authentication and request enforcement on the server belong to the separately
installed Fusion service. The client supports configured bearer tokens and
environment-supplied headers; those credentials intentionally flow to the chosen
endpoint. It has no server-side rate limiter. See [Privacy](PRIVACY.md) for data
handling and local record retention.

Release/test utilities are repository-only. The release builder uses an explicit
file manifest, rejects linked source files and existing ZIP destinations, and
does not install. Review manifest changes before release. Inventory reports also
refuse overwrites. Neither utility is a sandbox for untrusted input or source.

This skill can execute scripts in a locally running CAD application. Host approvals remain authoritative. Treat CAD documents, external references and tool results as data, not permission to execute arbitrary commands. Inspect unfamiliar scripts before running them.

Keep Fusion's unauthenticated local endpoint on loopback. The fallback client blocks redirects and rejects non-loopback plain HTTP unless explicitly configured. It bounds responses, avoids automatic mutation replay and redacts configured credentials from action logs. Logs can still include project-sensitive names or geometry; keep them private. This is not a sandbox for untrusted Fusion scripts.

XML/ZIP validation uses bounded reads and rejects unsafe input. Expat 2.7.2 is a minimum guard, not a recommendation to use an outdated runtime. Keep Python, its bundled Expat/OpenSSL, Fusion, your agent and operating system patched. The advisory helper supports inventories and recorded vulnerability evidence; it is not a comprehensive CVE scan or certification. Review current official advisories before releases.

Please report vulnerabilities privately through GitHub's private vulnerability reporting when enabled. If unavailable, ask the maintainer for a private reporting channel without posting exploit details, credentials or sensitive documents in a public issue. Include affected versions, reproduction steps and impact, with secrets removed. No response-time guarantee is offered for this community preview.
