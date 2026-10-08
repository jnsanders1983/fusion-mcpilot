# Privacy and data handling

Fusion MCPilot is a downloadable agent skill and optional MCP client. It does not
operate a hosted service, implement an MCP server, or include analytics or an
automatic telemetry upload mechanism.

The optional client reads the configured endpoint and connection settings from
environment variables, an explicitly selected JSON file, or host configuration.
Configured credentials are sent as authentication headers to that endpoint.
Choose an endpoint you trust; redirects are blocked. Native MCP access is managed
by the hosting agent instead of this client.

Requests can contain scripts, document names and modeling parameters. Responses
can contain CAD geometry and project information. Local action logs redact
configured authentication values but can retain project names, parameters,
geometry and error details. Exports and recovery checkpoints can contain complete
designs. Users choose storage destinations and control retention and deletion;
keep these records out of public repositories and releases.

The repository-only security inventory utility reads the selected directory and
writes file hashes, relative filenames and runtime versions to a local report.
It makes no network requests. Reports require a new destination filename.

Research instructions use the agent's available research tools; this package has
no web scraper or autonomous research service. Microsoft schema URLs in 3MF
files identify XML namespaces and relationships; they are not download requests.

Autodesk Fusion, the hosting agent, any configured remote endpoint, GitHub and
third-party directory listings have their own data practices. This document
describes this repository's helpers, not those services or directory approval.
For questions, use the repository's GitHub discussions/issues without including
private CAD data or credentials. See [Security](SECURITY.md) for vulnerability
reporting.
