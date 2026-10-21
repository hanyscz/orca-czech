"""Kontroly pracovních složek a dokončení bez změn skutečného katalogu."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('translation_menu',
                                             Path(__file__).with_name('translation-menu.py'))
menu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(menu)


class TranslationMenuTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.work = self.root / '.i18n-work'
        self.folder = self.work / 'update-test'
        (self.folder / 'source').mkdir(parents=True)
        (self.folder / 'PROMPT.txt').write_text('Přelož {{name}}.', encoding='utf-8')
        self.source = self.folder / 'source/wave01-part01.json'
        self.source.write_text(json.dumps({'test': 'Hello {{name}}'}), encoding='utf-8')
        self.target = self.folder / 'wave01-cs-part01.json'
        self.target.write_text(json.dumps({'test': 'Ahoj {{name}}'}), encoding='utf-8')
        self.addCleanup(patch.stopall)
        patch.object(menu, 'ROOT', self.root).start()
        patch.object(menu, 'WORK', self.work).start()

    def test_legacy_folder_and_persisted_selection(self):
        self.assertEqual(menu.active_folder(), self.folder)
        other = self.work / 'update-other'
        (other / 'source').mkdir(parents=True)
        (other / 'PROMPT.txt').write_text('prompt', encoding='utf-8')
        (self.work / 'active-work.txt').write_text(self.folder.name, encoding='utf-8')
        self.assertEqual(menu.active_folder(), self.folder)

    def test_missing_block_prevents_build(self):
        self.target.unlink()
        with patch.object(menu.preparation, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, 'Chybí přeložený'):
                menu.finish(self.folder)
            run.assert_not_called()

    def test_bad_keys_placeholders_and_unexpected_blocks(self):
        for data in ({'other': 'Ahoj'}, {'test': 'Ahoj'}, {'test': ''}):
            with self.subTest(data=data):
                self.target.write_text(json.dumps(data), encoding='utf-8')
                with self.assertRaises(RuntimeError):
                    menu.validate_blocks(self.folder)
        self.target.write_text(json.dumps({'test': 'Ahoj {{name}}'}), encoding='utf-8')
        (self.folder / 'wave99-part01.json').write_text('{}', encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError, 'nečekané'):
            menu.validate_blocks(self.folder)

    def test_finish_sets_environment_and_saves_reports(self):
        report = ('pokrytí: 1/1 = 100.00 %; 0 chybí\n'
                  'zástupné symboly, které anglický originál nemá: 0\n')
        with patch.object(menu.preparation, 'run', side_effect=['build ok', 'diff', 'stat']) as run:
            with patch.object(menu.subprocess, 'run', return_value=
                              subprocess.CompletedProcess([], 0, report, '')):
                with contextlib.redirect_stdout(io.StringIO()):
                    menu.finish(self.folder)
        self.assertEqual(run.call_args_list[0].kwargs['env']['ORCA_CS_WORK'], str(self.folder))
        self.assertEqual((self.folder / 'audit-after.txt').read_text(encoding='utf-8'), report)
        self.assertEqual((self.folder / 'changes.diff').read_text(encoding='utf-8'), 'diff')

    def test_incomplete_coverage_is_not_reported_as_success(self):
        with patch.object(menu.preparation, 'run', return_value='ok'):
            with patch.object(menu.subprocess, 'run', return_value=
                              subprocess.CompletedProcess([], 0, 'pokrytí: 1/2; 1 chybí', '')):
                with contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaisesRegex(RuntimeError, 'úplné pokrytí'):
                        menu.finish(self.folder)

    def test_prompt_is_sent_to_clipboard_as_input(self):
        with patch.object(menu.subprocess, 'run', return_value=
                          subprocess.CompletedProcess([], 0, '', '')) as run:
            with contextlib.redirect_stdout(io.StringIO()):
                menu.copy_prompt()
        self.assertEqual(run.call_args.kwargs['input'], 'Přelož {{name}}.')
        self.assertNotIn('Přelož', ' '.join(run.call_args.args[0]))


if __name__ == '__main__':
    unittest.main()
