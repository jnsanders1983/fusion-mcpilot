# Portable agent setup

The core is an Agent Skills directory: `SKILL.md`, `scripts/`, `references/`, and reusable benchmark data in `assets/fixtures/`. Copy the complete `fusion-360-mcp` directory into the target agent's supported skill directory. Keep relative resource paths intact. `agents/openai.yaml` is optional host UI metadata; other agents can ignore it. The sibling Windows installer is a Codex/ChatGPT adapter, not a runtime dependency.

Register Fusion's MCP endpoint using the target agent's own connection settings and approval controls. The skill cannot transfer an always-allow permission between hosts or grant permissions itself. Other agents may prefix tool names differently; discover the actual schema. The bundled execution recipes expect Autodesk's `fusion_mcp_execute` script contract. Other Fusion server contracts require an explicitly implemented adapter; ordinary MCP compliance alone does not make tool arguments interchangeable.

Prefer native tools. For the Python fallback, configuration precedence is:

1. `FUSION_MCP_URL`: explicit HTTP(S) endpoint. Optional `FUSION_MCP_TIMEOUT_SEC` and `FUSION_MCP_BEARER_TOKEN_ENV` (the name of an environment variable containing the token).
2. `FUSION_MCP_CONFIG`: path to a JSON configuration outside the skill. Keys: `url`, `tool_timeout_sec`, `http_headers`, `env_http_headers`, `bearer_token_env_var`, and optional `enabled`.
3. Existing Codex `mcp_servers.fusion360` settings, for compatibility with installed personal setups.

An explicitly selected configuration that is invalid fails visibly; it never silently uses another server. For example, in PowerShell:

```powershell
$env:FUSION_MCP_URL = 'http://127.0.0.1:27182/mcp'
python '<skill-folder>/scripts/inspect_design.py' --log-dir '<workspace>/work/fusion-runs/<run-id>'
```

In a POSIX shell:

```sh
FUSION_MCP_URL='http://127.0.0.1:27182/mcp' python3 '<skill-folder>/scripts/inspect_design.py' --log-dir '<workspace>/work/fusion-runs/<run-id>'
```

The POSIX example is for agents executing on a supported Fusion host or reaching an explicitly configured host. It does not imply a native Fusion Linux application. Loopback addresses always refer to the machine executing the connection. Cloud agents need a supported connection route to Fusion; uploading a skill does not provide that route. Use native host tools for OAuth connections: the fallback client supports static or environment-derived headers, not an OAuth login flow.

Keep credentials, machine addresses, approvals, logs, CAD files and research snapshots outside the skill. The standard skill format supports discovery and resources; each host still controls execution, MCP registration and authorization. Format compatibility is not proof of successful integration with every agent.
