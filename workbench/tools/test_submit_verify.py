"""Offline ZIP comparison regressions; never invoke a submission CLI command."""
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SUBMIT = ROOT / 'tools' / 'submit.js'
ENGINE_PYTHON = ROOT.parent / 'battlecode/work/bc127/bin/python3.13'
BOT = {
    'bot.toml': '[project]\nlanguage = "c++"\ninclude = ["*.cpp", "*.hpp"]\n',
    'main.cpp': 'int main() { return 0; }\n',
    'helper.hpp': '#pragma once\n',
    'sonar_codec.hpp': '#pragma once\n// sonar\n',
}


class SubmitVerify(unittest.TestCase):
    def setUp(self):
        self.inside = self.enterContext(tempfile.TemporaryDirectory(prefix='submit-test-', dir=ROOT / 'data/codex'))
        self.outside = self.enterContext(tempfile.TemporaryDirectory(prefix='submit-test-'))
        self.dirs = [Path(self.inside) / '봇 folder', Path(self.outside) / '봇 folder']
        for folder in self.dirs:
            folder.mkdir()
            for name, content in {**BOT, '.gitignore': '.unswbc-build/\n'}.items():
                (folder / name).write_text(content)
            for cache in ('.unswbc-build', 'build', '__pycache__', '__MACOSX'):
                (folder / cache).mkdir()
                (folder / cache / 'ignored').write_text('cache')

    def archive(self, entries):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as z:
            for name, content in entries.items():
                z.writestr(name, content)
        return buffer.getvalue()

    def compare(self, folder, blob, legacy=False):
        zip_path = Path(self.outside) / 'copy.zip'
        zip_path.write_bytes(blob)
        script = '''
const fs = require('fs'), path = require('path');
const { compareZip, files } = require(process.argv[1]);
const diff = compareZip(process.argv[2], fs.readFileSync(process.argv[3]));
if (process.argv[4] === 'legacy') {
  const want = files(process.argv[2]);
  const missingHidden = Object.keys(want).filter(f => path.basename(f).startsWith('.'));
  console.log(JSON.stringify({ diff, missingHidden }));
} else console.log(JSON.stringify(diff));
'''
        result = subprocess.run(['node', '-e', script, str(SUBMIT), str(folder), str(zip_path),
                                 'legacy' if legacy else ''], cwd=ROOT, text=True, capture_output=True)
        if result.returncode:
            raise RuntimeError(result.stderr.strip())
        return json.loads(result.stdout)

    def test_inside_outside_hidden_file_false_mismatch(self):
        for folder in self.dirs:
            with self.subTest(folder=str(folder)):
                result = self.compare(folder, self.archive(BOT), legacy=True)
                self.assertEqual(result, {'diff': [], 'missingHidden': ['.gitignore']})

    def test_relative_dotdot_and_symlink_folder(self):
        link = Path(self.inside) / 'alias'
        link.symlink_to(self.dirs[1], target_is_directory=True)
        for folder in (os.path.relpath(self.dirs[1], ROOT), link):
            self.assertEqual(self.compare(folder, self.archive(BOT)), [])

    def test_changed_missing_and_extra_files(self):
        for folder in self.dirs:
            for entries, expected in (
                ({**BOT, 'main.cpp': 'different'}, ['main.cpp']),
                ({k: v for k, v in BOT.items() if k != 'helper.hpp'}, ['helper.hpp']),
                ({**BOT, 'extra.cpp': 'extra'}, ['extra.cpp']),
            ):
                with self.subTest(folder=str(folder), expected=expected):
                    self.assertEqual(self.compare(folder, self.archive(entries)), expected)

    def test_hidden_server_files_are_ignored_like_check(self):
        self.assertEqual(self.compare(self.dirs[1], self.archive({**BOT, '.server-note': 'note'})), [])

    def test_nested_file_paths(self):
        for folder in self.dirs:
            (folder / 'include').mkdir()
            (folder / 'include/nested.hpp').write_text('nested')
            self.assertEqual(self.compare(folder, self.archive({**BOT, 'include/nested.hpp': 'nested'})), [])

    def test_invalid_zip_is_verification_error(self):
        with self.assertRaisesRegex(RuntimeError, 'server zip could not be extracted'):
            self.compare(self.dirs[1], b'not a zip')

    @unittest.skipUnless(ENGINE_PYTHON.exists(), 'installed official engine unavailable')
    def test_official_zip_inside_outside_has_same_four_entries(self):
        archives = []
        for folder in self.dirs:
            result = subprocess.run([str(ENGINE_PYTHON), '-B', '-c',
                                     'import sys; from unswbc.project import Project; '
                                     'from unswbc.submit import _zip; '
                                     'p=Project.from_dir(sys.argv[1]); p.collect_sources(); '
                                     'sys.stdout.buffer.write(_zip(p))', str(folder)],
                                    cwd=ROOT, capture_output=True, check=True)
            with zipfile.ZipFile(io.BytesIO(result.stdout)) as z:
                self.assertEqual(sorted(z.namelist()), sorted(BOT))
                archives.append({name: z.read(name) for name in z.namelist()})
                self.assertFalse(any('..' in Path(name).parts or Path(name).is_absolute() for name in z.namelist()))
            self.assertEqual(self.compare(folder, result.stdout), [])
        self.assertEqual(archives[0], archives[1])


if __name__ == '__main__':
    unittest.main()
