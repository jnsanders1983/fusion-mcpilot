# Install Fusion MCPilot

## Requirements

- A Windows or macOS host running Autodesk Fusion with its MCP service enabled. Fusion is not a native Linux application.
- An agent that can load an Agent Skills folder and execute local MCP tools or local scripts.
- For optional Python helpers: Python 3.11+ with a maintained security patch level. XML checks require Expat ≥ 2.7.2. No third-party Python packages are required.
- Your Fusion license and extensions determine available features. This skill does not unlock paid tools.

Download the repository ZIP from GitHub and extract it. Install **the entire inner `fusion-360-mcp` directory**, not only `SKILL.md`. Preserve the folder name and relative paths.

## Choose your agent

| Host | Skill installation | MCP connection |
| --- | --- | --- |
| ChatGPT Work / this Codex desktop setup | Personal `~/.codex/skills/fusion-360-mcp`; optional `Install.ps1` below | Settings → MCP servers; add `fusion360` with the URL shown in Fusion |
| Current Codex Agent Skills setup | Personal `~/.agents/skills/fusion-360-mcp`, or project `.agents/skills/fusion-360-mcp` | Configure the host's MCP server, or `codex mcp add fusion360 --url <URL>` where that command is available |
| Claude Code | Personal `~/.claude/skills/fusion-360-mcp`, or project `.claude/skills/fusion-360-mcp` | Register an HTTP MCP server in Claude Code using its supported MCP settings |
| Cursor | Personal `~/.cursor/skills/fusion-360-mcp`, or project `.cursor/skills/fusion-360-mcp` | Add Fusion's HTTP MCP endpoint through Cursor's MCP settings |
| Another compatible agent | Its documented Agent Skills folder | Its MCP registration and permission controls; discover the actual tool schema |

`~` means your user profile/home directory. Do not install identical skill copies in multiple discovery roots for one agent. Locations and UI labels can differ by host version; use its current documentation. These are documented integration paths, not a claim of live testing in every host.

Official sources: [Agent Skills specification](https://agentskills.io/specification), [OpenAI skill setup](https://learn.chatgpt.com/docs/build-skills), [OpenAI MCP setup](https://learn.chatgpt.com/docs/extend/mcp), [Claude Code skills](https://code.claude.com/docs/en/skills), [Claude Code MCP](https://code.claude.com/docs/en/mcp), [Cursor skills](https://prod.cursor.com/docs/skills), [Cursor MCP](https://cursor.com/docs/context/mcp).

## Optional Windows installer

Run from the extracted repository root:

```powershell
& '.\Install.ps1' -SkipConnection
```

This preserves the legacy personal Codex location used by the desktop setup. `-SkipConnection` leaves MCP registration to the host UI. To let an available Codex CLI register the endpoint instead:

```powershell
& '.\Install.ps1' -ServerUrl 'http://127.0.0.1:27182/mcp'
```

For another agent, explicitly choose its skill root and skip Codex connection registration:

```powershell
& '.\Install.ps1' -SkillDirectory "$env:USERPROFILE\.claude\skills" -SkipConnection
```

An existing installation is preserved unless you pass `-ReplaceSkill`. That switch makes a backup before replacing files. Inspect any local modifications before upgrading. Restart/reload the agent if discovery does not refresh; look for **Fusion MCPilot**, or invoke the stable identifier `$fusion-360-mcp` where supported.

## macOS and Linux agent installer

Autodesk documents Fusion for Windows and macOS; [native Linux installation is unsupported](https://help.autodesk.com/view/fusion360/ENU/?caas=caas%2Fsfdcarticles%2Fsfdcarticles%2FIs-there-any-way-to-install-Fusion-360-in-Linux.html). This installer installs the agent skill, not Fusion or a network tunnel.

From the extracted repository:

```sh
sh ./Install.sh --agent claude
sh ./Install.sh --agent cursor
sh ./Install.sh --agent codex
```

Choose **one** command for the intended agent. Generic/Codex defaults use `~/.agents/skills`; Claude and Cursor use their personal roots. For a project or another host, pass `--skill-directory /absolute/path/to/skills`. The same installer also runs on Windows as `python Install.py`. Use `--replace` after reviewing an update. It backs up an existing skill into the system temporary directory, checks copied bytes, and preserves files not present in the new source; review obsolete local files manually. It never registers MCP or grants permissions. Configure those in the host.

macOS agents can connect to Fusion on that Mac. Linux agents need an explicitly configured, supported connection to Fusion on Windows/macOS; `127.0.0.1` on Linux does not reach another computer. Shell syntax and isolated installation checks are separate from a live macOS Fusion integration test.

## Configure this computer

Use the exact endpoint displayed by Fusion. Register it under `fusion360` in your host. `127.0.0.1` refers to the computer executing the connection. A web/cloud agent cannot reach your desktop loopback just because it has this skill. Choose a supported local execution route; do not expose an unauthenticated service publicly.

Each host controls permissions. You may choose its personal “always allow” option where available, but the skill cannot grant, transfer or bypass approvals. Copying the skill to another computer does not copy MCP settings or your permission decisions. Change the address in that computer's host MCP settings without editing the skill.

## Agent-neutral fallback client

Native MCP tools are preferred. Helpers target Autodesk's `fusion_mcp_execute` contract; a third-party server with different tool arguments needs an adapter.

For an agent with local shell access, set the URL outside the skill:

```powershell
$env:FUSION_MCP_URL = 'http://127.0.0.1:27182/mcp'
python -B '<installed-skill-folder>/scripts/inspect_design.py' --log-dir '<workspace>/work/fusion-runs/first-inspection'
```

In a POSIX shell on a supported Fusion host:

```sh
FUSION_MCP_URL='http://127.0.0.1:27182/mcp' python3 -B '<installed-skill-folder>/scripts/inspect_design.py' --log-dir '<workspace>/work/fusion-runs/first-inspection'
```

For persistent fallback settings, create an external JSON file and set `FUSION_MCP_CONFIG` to its path:

```json
{"url":"http://127.0.0.1:27182/mcp","tool_timeout_sec":60}
```

Environment URL takes precedence over external JSON, then existing Codex `fusion360` configuration. Explicit invalid configuration fails instead of silently selecting another server. See [complete portability configuration](../fusion-360-mcp/references/portability.md) for environment-derived authentication headers. OAuth login is handled by native host tools, not the fallback client. Never commit secrets or personal config.

## First use and troubleshooting

1. Open a design in Fusion and keep the application running.
2. Ask for a read-only inventory before modeling. Confirm the intended document and destination.
3. Test an edit in a disposable document, not your only unsaved design.
4. After a timeout or error, inspect live state before retrying. A failed response can still leave partial geometry.

Connection refused: confirm Fusion is running and the address/port matches. Missing tools: refresh the host MCP connection and discover current schemas. Wrong schema: the server may not implement Autodesk's script contract. XML runtime rejected: use a patched Python build with a sufficiently recent Expat. Existing output directory: choose a new revision; helpers protect existing deliverables. Host permissions rejected: change host policy yourself; the skill cannot override it.

To uninstall, remove the installed `fusion-360-mcp` directory and separately remove the MCP connection if no other skill uses it. Preserve CAD files and run records. Deleting the skill does not delete Fusion cloud projects.
