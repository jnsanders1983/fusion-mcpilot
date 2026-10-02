"""Test the portable installer against isolated disposable trees."""
import importlib.util,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('portable_installer',Path(__file__).resolve().parents[1]/'Install.py')
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)

class InstallerTests(unittest.TestCase):
    def test_copy_verify_no_overwrite_and_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'source';source.mkdir()
            (source/'SKILL.md').write_text('original')
            result=installer.install(source,root/'skills')
            self.assertEqual(result['files_checked'],1)
            with self.assertRaises(FileExistsError):installer.install(source,root/'skills')
            (source/'SKILL.md').write_text('updated')
            result=installer.install(source,root/'skills',True)
            self.assertEqual((Path(result['backup'])/'SKILL.md').read_text(),'original')
            self.assertEqual((Path(result['installed'])/'SKILL.md').read_text(),'updated')
    def test_source_overlap_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp);(source/'SKILL.md').write_text('test')
            with self.assertRaises(ValueError):installer.install(source,source/'nested')

if __name__=='__main__':unittest.main()
