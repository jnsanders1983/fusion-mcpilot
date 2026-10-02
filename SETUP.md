# Fusion MCPilot setup

For complete current installation and other-agent instructions, see `docs/installation.md` in the source repository. The portable distribution retains the agent-neutral setup reference at `fusion-360-mcp/references/portability.md`.

This package contains a standard Agent Skills directory and an optional Windows installer for Codex/ChatGPT Work. Other compatible agents can install the complete inner `fusion-360-mcp` directory in their supported skill location. See its `references/portability.md` for agent-neutral runtime configuration. The MCP address and permissions are configured separately on each computer; no credentials or user approvals are packaged.

The optimized skill includes sphere, torus, cone, cylinder, and circular frustum recipes with geometry verification in the same call. It uses an instant camera fit, a reusable command runner, and automatic timing/action logs. The comparative camera benchmark measured a median MCP round trip of 0.763 seconds before and 0.204 seconds after (15 runs each, September 30, 2026). These are execution times, not total ChatGPT response times; other computers and designs will differ. Existing skill backups made with -ReplaceSkill go to the Windows temporary folder under fusion-360-skill-backups, outside the skill discovery directory.

## Runtime and logs

Native Fusion MCP tools are preferred. The optional fallback command runner needs Python 3.11+ with no third-party packages. It reads `FUSION_MCP_URL`, then external JSON selected by `FUSION_MCP_CONFIG`, then existing Codex `fusion360` settings. It supports anonymous local connections and configured static/token headers; use native tools for OAuth-connected servers. Helpers target Autodesk's native execution tool contract; alternative server schemas need an adapter.

The primitive runner writes actions.jsonl and performance.csv in the chosen --log-dir (default a unique work/fusion-runs/run-<id> in the current working directory). Other helpers keep their documented compact run records. It separates MCP round-trip time, Fusion execution/verification, connection setup, and runner total. Assistant thinking, tool scheduling, and response-writing time are excluded from runner total. Errors are logged and modifying requests are never automatically replayed.

To check the portable helper code without connecting to Fusion, run `python <installed-skill-folder>/scripts/self_test.py`. This tests parameter validation, safe script rendering, JSON/SSE handling, and no-replay error handling using mock responses. It writes only temporary test files.

## Install on Windows

Extract the entire package into a folder. In PowerShell run:

```powershell
& '.\Install.ps1'
```

The installer copies the skill into your personal skill directory and registers the `fusion360` server through the Codex CLI when available. It backs up an existing host configuration before registering the server. An existing skill is left alone unless you pass `-ReplaceSkill`.

To choose a different URL during installation:

```powershell
& '.\Install.ps1' -ServerUrl 'http://127.0.0.1:27182/mcp'
```

If the CLI is unavailable, installation still copies the skill and prints instructions to add the connection in Settings -> MCP servers. Restart the desktop app, then start a local Work chat. Type `@` and select Autodesk Fusion 360; in Codex you can use `$fusion-360-mcp`.

Example request: "Use the Fusion 360 skill to inspect my active design, list its components and parameters, and report any unhealthy features. Do not change the design."

## Change the address later

Open Settings -> MCP servers and update `fusion360` with the URL shown by Fusion on that computer. Save and restart. You do not need to edit or reinstall the skill. Copy this package to another PC and install it there; the installed desktop app alone does not copy this local skill automatically.

Fusion must run on the computer used for local execution when using `127.0.0.1`. Hosted ChatGPT web/cloud skill uploads do not by themselves connect to this local endpoint.

Official references: [MCP desktop settings](https://learn.chatgpt.com/docs/extend/mcp), [skills and invocation](https://learn.chatgpt.com/docs/build-skills).
