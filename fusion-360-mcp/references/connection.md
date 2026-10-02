# Connection and per-computer settings

Use an agent with MCP or local script execution access to Autodesk Fusion. Keep Fusion and its MCP service running. Loopback (`127.0.0.1`) points to the computer executing the connection; an ordinary hosted web/cloud session cannot use your PC's loopback service merely because this skill is uploaded. For other agents or an external JSON configuration, read [portable setup](portability.md).

The initial URL supplied by the user is `http://127.0.0.1:27182/mcp`. This is an example/default for setup, not a runtime override. Always use the connection actually configured in the host.

## Native settings

In ChatGPT desktop open Settings, MCP servers. Add a server named `fusion360`, choose Streamable HTTP, and enter the URL displayed by Fusion. Save and select Restart. Use `/mcp` in the composer to inspect connected servers.

To change computers, install the skill on the new PC and configure `fusion360` there with that PC's Fusion MCP URL. The skill instructions stay the same. The native MCP configuration is the setting for the server address; editing this Markdown file does not reconfigure the connection.

For clients using the local configuration, the equivalent entry in the applicable CODEX_HOME/config.toml (normally ~/.codex/config.toml) is:

```toml
[mcp_servers.fusion360]
url = "http://127.0.0.1:27182/mcp"
```

The CLI equivalent is `codex mcp add fusion360 --url http://127.0.0.1:27182/mcp`. Keep one entry for this server and preserve other settings.

## Troubleshooting

Confirm Fusion is running and its MCP service is enabled; copy its currently displayed URL. Check `/mcp`, then restart the connection/client after settings changes. Report the actual error. If a script is blocked by an active dialog, ask the user to finish it before modifying geometry. Do not change firewall rules, expose Fusion publicly, or install a tunnel just to solve a loopback connection issue.

## Official documentation

- [MCP configuration and desktop settings](https://learn.chatgpt.com/docs/extend/mcp)
- [Skill invocation and local discovery](https://learn.chatgpt.com/docs/build-skills)

The setup check successfully initialized the user's endpoint and listed four tools. No CAD geometry was changed during setup. Re-discover schemas during actual work because server capabilities can change.
