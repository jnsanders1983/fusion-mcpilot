[CmdletBinding()]
param(
    [string]$ServerUrl = 'http://127.0.0.1:27182/mcp',
    [string]$SkillDirectory = $(if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex/skills' }),
    [string]$ConfigDirectory = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }),
    [switch]$ReplaceSkill,
    [switch]$SkipConnection
)
$ErrorActionPreference = 'Stop'
$fusionUri = $null
if (-not [Uri]::TryCreate($ServerUrl, [UriKind]::Absolute, [ref]$fusionUri) -or $fusionUri.Scheme -notin @('http', 'https') -or $fusionUri.UserInfo) {
    throw 'ServerUrl must be an absolute HTTP or HTTPS URL without embedded credentials.'
}
$fusionSource = Join-Path $PSScriptRoot 'fusion-360-mcp'
$fusionDestination = Join-Path $SkillDirectory 'fusion-360-mcp'
if (-not (Test-Path -LiteralPath (Join-Path $fusionSource 'SKILL.md'))) { throw 'Extract the complete package before installing.' }
if (Test-Path -LiteralPath $fusionDestination) {
    if (-not $ReplaceSkill) { throw 'The skill already exists. Use -ReplaceSkill to update it, or edit the MCP URL in the app settings.' }
    $fusionBackupRoot = Join-Path ([IO.Path]::GetTempPath()) 'fusion-360-skill-backups'
    New-Item -ItemType Directory -Path $fusionBackupRoot -Force | Out-Null
    $fusionBackup = Join-Path $fusionBackupRoot ([Guid]::NewGuid().ToString('N'))
    Copy-Item -LiteralPath $fusionDestination -Destination $fusionBackup -Recurse
}
New-Item -ItemType Directory -Path $fusionDestination -Force | Out-Null
Get-ChildItem -LiteralPath $fusionSource | ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $fusionDestination -Recurse -Force }
Write-Output "Installed skill: $fusionDestination"
if (-not $SkipConnection) {
    $fusionCli = Get-Command codex -ErrorAction SilentlyContinue
    if ($fusionCli) {
        New-Item -ItemType Directory -Path $ConfigDirectory -Force | Out-Null
        $fusionConfig = Join-Path $ConfigDirectory 'config.toml'
        if (Test-Path -LiteralPath $fusionConfig) {
            Copy-Item -LiteralPath $fusionConfig -Destination "$fusionConfig.fusion-backup-$([Guid]::NewGuid().ToString('N'))"
        }
        $fusionPreviousHome = $env:CODEX_HOME
        try {
            $env:CODEX_HOME = $ConfigDirectory
            & $fusionCli.Source mcp add fusion360 --url $ServerUrl
            if ($LASTEXITCODE -ne 0) { throw 'MCP registration failed. Configure fusion360 in the app settings.' }
        } finally { $env:CODEX_HOME = $fusionPreviousHome }
    } else {
        Write-Output "Add server fusion360 in Settings -> MCP servers, choose Streamable HTTP, URL: $ServerUrl"
    }
}
Write-Output 'Restart the desktop app and select Autodesk Fusion 360 in a local Work chat.'
