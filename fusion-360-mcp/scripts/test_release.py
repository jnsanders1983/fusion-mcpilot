"""Release boundary regressions; offline and no host connection."""
import tempfile,unittest,zipfile
from pathlib import Path
from package_skill import package
from export_multipart import export

class ReleaseTests(unittest.TestCase):
    def test_repository_metadata_and_private_records_are_not_packaged(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);skill=root/'demo';skill.mkdir()
            (skill/'SKILL.md').write_text('---\nname: demo\ndescription: test\n---\nTest\n',encoding='utf-8')
            (root/'.git').mkdir();(root/'.git'/'private').write_text('secret')
            (root/'work').mkdir();(root/'work'/'private').write_text('secret')
            (root/'README.md').write_text('repository only')
            (root/'LICENSE').write_text('license')
            archive=root/'release.zip';package(root,'demo',archive)
            with zipfile.ZipFile(archive) as z:
                self.assertEqual(set(z.namelist()),{'demo/SKILL.md','LICENSE'})

    def test_custom_writer_requires_explicit_opt_in_before_connecting(self):
        with self.assertRaisesRegex(ValueError,'explicit'):
            export(None,'Document',[],Path('not-created'))

if __name__=='__main__':unittest.main()
