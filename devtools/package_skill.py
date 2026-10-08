"""Validate and package approved release files; never installs or overwrites."""
from pathlib import Path, PurePosixPath
import argparse, ast, json, re, zipfile


def package(package_root, skill_name, zip_path):
    root = Path(package_root).resolve()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', skill_name):
        raise ValueError('Invalid skill name.')
    skill = root / skill_name
    destination = Path(zip_path).resolve()
    if destination.is_relative_to(skill):
        raise ValueError('Release archive must be outside the skill directory.')
    if destination.exists():
        raise FileExistsError('Release archive exists; choose a new filename.')
    entries = json.loads((root / 'devtools' / 'release-files.json').read_text(encoding='utf-8'))
    if not isinstance(entries, list) or not entries or any(not isinstance(e, str) for e in entries):
        raise ValueError('Release manifest must be a nonempty list of paths.')
    if len(set(entries)) != len(entries):
        raise ValueError('Duplicate release paths.')
    files = []
    for entry in entries:
        relative = PurePosixPath(entry)
        if relative.is_absolute() or '..' in relative.parts or '\\' in entry or ':' in entry:
            raise ValueError('Invalid release path: ' + entry)
        if relative.parts[0] != skill_name and entry not in ('Install.ps1', 'Install.py', 'Install.sh', 'SETUP.md', 'LICENSE'):
            raise ValueError('Release path outside approved roots: ' + entry)
        path = root / entry
        for part in [path, *path.parents]:
            if part != root and part.is_relative_to(root) and (part.is_symlink() or (hasattr(part, 'is_junction') and part.is_junction())):
                raise ValueError('Release links are not allowed: ' + entry)
        if not path.resolve().is_relative_to(root) or not path.is_file():
            raise ValueError('Missing or escaped release file: ' + entry)
        files.append((entry, path))
    shipped = set(entries)
    if skill_name + '/SKILL.md' not in shipped:
        raise ValueError('Skill entrypoint missing from release manifest.')
    front = (skill / 'SKILL.md').read_text(encoding='utf-8').split('---', 2)
    if len(front) != 3 or not re.search(r'^name: ' + re.escape(skill_name) + r'$', front[1], re.M) or not re.search(r'^description: .+', front[1], re.M):
        raise RuntimeError('Invalid required frontmatter.')
    for entry, path in files:
        if path.suffix == '.py':
            ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
        if path.suffix == '.md' and path.is_relative_to(skill):
            for _, target in re.findall(r'\[([^\]]+)\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
                if target.startswith(('https://', 'http://')):
                    continue
                resolved = (path.parent / target.split('#')[0]).resolve()
                if not resolved.is_relative_to(root) or resolved.relative_to(root).as_posix() not in shipped:
                    raise RuntimeError('Reference not shipped: ' + target)
    with destination.open('xb') as output:
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
            for entry, path in files:
                archive.write(path, entry)
    with zipfile.ZipFile(destination) as archive:
        if set(archive.namelist()) != shipped:
            raise RuntimeError('ZIP manifest differs.')
        for entry, path in files:
            if archive.read(entry) != path.read_bytes():
                raise RuntimeError('ZIP bytes differ: ' + entry)
    return {'skill_files': sum(p.is_relative_to(skill) for _, p in files), 'installed_checked': False, 'zip_checked': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-root', required=True)
    parser.add_argument('--skill-name', required=True)
    parser.add_argument('--zip-path', required=True)
    args = parser.parse_args()
    print(json.dumps(package(args.package_root, args.skill_name, args.zip_path)))


if __name__ == '__main__':
    main()
