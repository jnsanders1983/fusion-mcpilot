"""Portable local skill installer. Does not configure MCP or grant permissions."""
import argparse,json,os,shutil,tempfile
from pathlib import Path

def install(source,skill_directory,replace=False):
    source=Path(source).resolve();parent=Path(skill_directory).expanduser().resolve()
    target=parent/'fusion-360-mcp'
    if not (source/'SKILL.md').is_file():raise ValueError('Extract the complete package first.')
    if target==source or parent.is_relative_to(source) or source.is_relative_to(target):raise ValueError('Installation must be separate from source.')
    files=[p for p in source.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    if any(p.is_symlink() for p in source.rglob('*')) or target.is_symlink():raise ValueError('Symlinked skill trees are not supported by this installer.')
    backup=None
    if target.exists():
        if not replace:raise FileExistsError('Skill already exists; review changes and pass --replace to update.')
        backup=Path(tempfile.mkdtemp(prefix='fusion-mcpilot-backup-'))/'fusion-360-mcp'
        shutil.copytree(target,backup)
    target.mkdir(parents=True,exist_ok=True)
    for path in files:
        output=target/path.relative_to(source);output.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,output)
        if output.read_bytes()!=path.read_bytes():raise RuntimeError('Installed bytes differ.')
    return {'installed':str(target),'backup':str(backup) if backup else None,'files_checked':len(files),'mcp_configured':False}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent',choices=['codex','claude','cursor','generic'],default='generic')
    parser.add_argument('--skill-directory',help='Parent directory containing installed skills.')
    parser.add_argument('--replace',action='store_true')
    args=parser.parse_args()
    defaults={'codex':'.agents/skills','claude':'.claude/skills','cursor':'.cursor/skills','generic':'.agents/skills'}
    destination=args.skill_directory or str(Path.home()/defaults[args.agent])
    print(json.dumps(install(Path(__file__).resolve().parent/'fusion-360-mcp',destination,args.replace),indent=2))
    print('Configure Fusion MCP in your agent separately, then reload skill discovery.')

if __name__=='__main__':main()
