"""Release boundary regressions; offline and no host connection."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'fusion-360-mcp'/'scripts'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'devtools'))
import tempfile,unittest,zipfile,json
from pathlib import Path
from package_skill import package
from export_multipart import export
from security_audit import write_report

class ReleaseTests(unittest.TestCase):
    def test_repository_metadata_and_private_records_are_not_packaged(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);skill=root/'demo';skill.mkdir()
            (skill/'SKILL.md').write_text('---\nname: demo\ndescription: test\n---\nTest\n',encoding='utf-8')
            (root/'.git').mkdir();(root/'.git'/'private').write_text('secret')
            (root/'work').mkdir();(root/'work'/'private').write_text('secret')
            (root/'README.md').write_text('repository only')
            (root/'LICENSE').write_text('license')
            (root/'devtools').mkdir()
            (root/'devtools'/'release-files.json').write_text(json.dumps(['demo/SKILL.md','LICENSE']))
            (skill/'private.txt').write_text('must not ship')
            archive=root/'release.zip';package(root,'demo',archive)
            with zipfile.ZipFile(archive) as z:
                self.assertEqual(set(z.namelist()),{'demo/SKILL.md','LICENSE'})
            original=archive.read_bytes()
            with self.assertRaises(FileExistsError):package(root,'demo',archive)
            self.assertEqual(archive.read_bytes(),original)

    def test_manifest_escape_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'devtools').mkdir()
            manifest=root/'devtools'/'release-files.json'
            for entry in ('../secret.txt','demo/../../secret.txt','C:/secret.txt','demo\\secret.txt'):
                manifest.write_text(json.dumps([entry]))
                with self.subTest(entry=entry),self.assertRaises(ValueError):package(root,'demo',root/'release.zip')
                self.assertFalse((root/'release.zip').exists())

    def test_custom_writer_requires_explicit_opt_in_before_connecting(self):
        with self.assertRaisesRegex(ValueError,'explicit'):
            export(None,'Document',[],Path('not-created'))

    def test_report_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'inventory.json'
            write_report(path,{'original':True})
            with self.assertRaises(FileExistsError):write_report(path,{'original':False})
            self.assertEqual(json.loads(path.read_text()),{'original':True})

    def test_linked_release_input_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'demo').mkdir();(root/'devtools').mkdir()
            (root/'secret.txt').write_text('private')
            link=root/'demo'/'linked.txt'
            try:link.symlink_to(root/'secret.txt')
            except OSError:self.skipTest('Host does not permit symbolic links.')
            (root/'devtools'/'release-files.json').write_text(json.dumps(['demo/linked.txt']))
            with self.assertRaisesRegex(ValueError,'links'):package(root,'demo',root/'release.zip')
            self.assertFalse((root/'release.zip').exists())

if __name__=='__main__':unittest.main()
