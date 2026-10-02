"""Validate, install and zip an existing skill/installer tree without cache files."""
from pathlib import Path
import argparse,ast,re,shutil,zipfile,json

def package(package_root,skill_name,zip_path,install_to=None):
    root=Path(package_root).resolve();skill=root/skill_name
    front=(skill/'SKILL.md').read_text(encoding='utf-8').split('---',2)
    if len(front)!=3 or not re.search(r'^name: '+re.escape(skill_name)+r'$',front[1],re.M) or not re.search(r'^description: .+',front[1],re.M):raise RuntimeError('Invalid required frontmatter.')
    for p in skill.rglob('*.md'):
        for _,target in re.findall(r'\[([^\]]+)\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            if not target.startswith(('https://','http://')) and not (p.parent/target.split('#')[0]).exists():raise RuntimeError('Missing local reference: '+target)
    for p in (skill/'scripts').glob('*.py'):ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
    files=[p for p in skill.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    files += [root/name for name in ('Install.ps1','Install.py','Install.sh','SETUP.md','LICENSE') if (root/name).is_file()]
    if install_to:
        dest=Path(install_to).resolve()
        for p in files:
            if not p.is_relative_to(skill):continue
            target=dest/p.relative_to(skill);target.parent.mkdir(parents=True,exist_ok=True)
            if target!=p:shutil.copy2(p,target)
            if target.read_bytes()!=p.read_bytes():raise RuntimeError('Installed bytes differ.')
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
        for p in files:z.write(p,p.relative_to(root))
    with zipfile.ZipFile(zip_path) as z:
        for p in files:
            if z.read(p.relative_to(root).as_posix())!=p.read_bytes():raise RuntimeError('ZIP differs.')
    return {'skill_files':sum(p.is_relative_to(skill) for p in files),'installed_checked':bool(install_to),'zip_checked':True}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--package-root',required=True);p.add_argument('--skill-name',required=True)
    p.add_argument('--zip-path',required=True);p.add_argument('--install-to')
    a=p.parse_args();print(json.dumps(package(a.package_root,a.skill_name,a.zip_path,a.install_to)))

if __name__=='__main__':main()
