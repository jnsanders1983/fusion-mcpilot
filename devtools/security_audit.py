"""Local inventory, package hashes and evidence-based advisory applicability.
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'fusion-360-mcp'/'scripts'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'devtools'))

No uploads or automatic network requests. Advisory records are external reviewed
data, not a permanent vulnerability database embedded in the skill.
"""
import argparse,ast,datetime,hashlib,json,platform,re,ssl,sys,pyexpat,zlib
from pathlib import Path
from safe_data import strict_json


def numeric_version(value):
    match=re.fullmatch(r'(?:expat_)?(\d+)\.(\d+)\.(\d+)',value)
    if not match:raise ValueError('Unsupported version syntax; manual applicability review required.')
    return tuple(int(part) for part in match.groups())


def inventory(skill_dir):
    root=Path(skill_dir).resolve();files=[]
    for path in sorted(root.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts or path.suffix=='.pyc':continue
        if path.suffix=='.py':ast.parse(path.read_text(encoding='utf-8'))
        files.append({'path':path.relative_to(root).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size})
    openssl=re.search(r'OpenSSL (\d+\.\d+\.\d+)',ssl.OPENSSL_VERSION)
    return {'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'components':[
        {'name':'python','version':platform.python_version(),'scope':'agent helper runtime'},
        {'name':'expat','version':'.'.join(map(str,pyexpat.version_info)),'scope':'3MF XML parser'},
        {'name':'openssl','version':openssl.group(1) if openssl else ssl.OPENSSL_VERSION,'scope':'HTTPS connections'},
        {'name':'zlib','version':zlib.ZLIB_RUNTIME_VERSION,'scope':'3MF ZIP compression'},
        {'name':'fusion-mcp-server','version':None,'scope':'Separate installed server; dependencies and patch provenance unknown'}],
        'third_party_python_dependencies':'No third-party imports required by packaged agent helpers; native Fusion APIs run inside Autodesk.',
        'files':files,'scope':'Local inventory with file hashes, not a complete server SBOM or security certification.'}


def assess(data,advisories):
    if not isinstance(advisories,list):raise ValueError('Advisory ledger must be a list.')
    components={row['name']:row for row in data['components']};results=[]
    for advisory in advisories:
        if not isinstance(advisory,dict) or not re.fullmatch(r'CVE-\d{4}-\d{4,}',advisory.get('cve','')) or not advisory.get('source','').startswith('https://') or not advisory.get('reviewed_at'):
            raise ValueError('Each advisory needs a CVE, authoritative HTTPS source and review date.')
        component=components.get(advisory['component']);status='unknown_component'
        if component:
            try:
                version=numeric_version(component['version']) if component['version'] else None
                fixed=numeric_version(advisory['fixed_version'])
                if version is None:status='unknown_version'
                elif version>=fixed:status='outside_recorded_affected_range'
                elif advisory.get('affected_min') and version<numeric_version(advisory['affected_min']):status='outside_recorded_affected_range'
                else:status='affected_by_recorded_version_range'
            except (ValueError,TypeError):status='manual_version_review_required'
        results.append({**advisory,'installed_version':component.get('version') if component else None,'status':status,'exploitability':'Not established by version matching; inspect conditions, reachability and vendor backports.'})
    return results


def write_report(path, result):
    with Path(path).open('x',encoding='utf-8') as report:
        report.write(json.dumps(result,indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill-dir',default=str(Path(__file__).resolve().parents[1]/'fusion-360-mcp'))
    parser.add_argument('--advisories',help='External JSON ledger of independently reviewed exact-component advisories.')
    parser.add_argument('--report',required=True)
    args=parser.parse_args();result=inventory(args.skill_dir)
    ledger=strict_json(Path(args.advisories).read_text(encoding='utf-8')) if args.advisories else []
    result['advisory_assessments']=assess(result,ledger)
    assessed={row['component'] for row in result['advisory_assessments']}
    result['unassessed_components']=[row['name'] for row in result['components'] if row['name'] not in assessed]
    result['coverage']='Only supplied reviewed advisories; an empty list or absent match does not mean no vulnerabilities.'
    write_report(args.report,result)
    print(json.dumps({'components':result['components'],'assessments':result['advisory_assessments'],'unassessed_components':result['unassessed_components'],'report':str(Path(args.report).resolve())},indent=2))

if __name__=='__main__':main()
