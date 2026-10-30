"""Regrese změn cest, ochranných pravidel a kontrol dokumentace."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import engine_rules as engine

ROOT = Path(__file__).resolve().parent.parent
CHROME = "'auto.components.settings.PluginHeader.title'"
ARTIFACT = """
export const PLUGIN_LANGUAGE_CATALOG_MAX_ENTRIES = 50_000
export const PLUGIN_LANGUAGE_CATALOG_MAX_DEPTH = 16
const PROTECTED_TRANSLATION_ROOT = 'auto.components.settings.'
const PROTECTED_TRANSLATION_MODULE = /^plugin/i
const PROTECTED_TRANSLATION_COMPONENTS = [
  'components.native-chat.approval',
  'auto.components.settings.PluginHeader.title'
]
"""


class EngineRulesTests(unittest.TestCase):
    def test_new_path_and_legacy_fallback(self):
        for paths in (engine.CHROME_PATHS, engine.ARTIFACT_PATHS):
            with self.subTest(paths=paths):
                with patch.object(engine, 'fetch_source', return_value='new') as fetch:
                    self.assertEqual(engine.fetch_first(paths, 'v1'), 'new')
                    fetch.assert_called_once_with(paths[0], 'v1')
                with patch.object(engine, 'fetch_source', side_effect=[RuntimeError('HTTP 404'), 'old']):
                    self.assertEqual(engine.fetch_first(paths, 'v1'), 'old')

    def test_missing_paths_and_authentication_errors_stop(self):
        with patch.object(engine, 'fetch_source', side_effect=RuntimeError('HTTP 404')):
            with self.assertRaisesRegex(RuntimeError, 'nebyl nalezen'):
                engine.fetch_first(engine.CHROME_PATHS, 'v1')
        with patch.object(engine, 'fetch_source', side_effect=RuntimeError('HTTP 401')) as fetch:
            with self.assertRaisesRegex(RuntimeError, '401'):
                engine.fetch_first(engine.CHROME_PATHS, 'v1')
            self.assertEqual(fetch.call_count, 1)

    def test_component_protection_overrides_allowlist_and_checks_boundaries(self):
        rules = engine.parse_rules(CHROME, ARTIFACT)
        self.assertEqual(rules.max_entries, 50000)
        self.assertTrue(rules.protected('components.native-chat.approval.allow'))
        self.assertTrue(rules.protected('auto.components.settings.PluginHeader.title'))
        self.assertTrue(rules.protected('auto.components.settings.PLUGINConsent.body'))
        self.assertFalse(rules.protected('components.native-chat.approvalExtra.title'))
        self.assertFalse(rules.protected('menu.file'))

    def test_old_release_without_components_and_empty_allowlist_are_valid(self):
        source = ARTIFACT[:ARTIFACT.index('const PROTECTED_TRANSLATION_COMPONENTS')]
        rules = engine.parse_rules('', source.replace('50_000', '20_000'))
        self.assertEqual(rules.protected_components, ())
        self.assertEqual(rules.max_entries, 20000)

    def test_unknown_changed_missing_and_unreadable_rules_stop(self):
        for source in (ARTIFACT + '\nconst PROTECTED_NEW_RULE = true',
                       ARTIFACT.replace('/^plugin/i', '/^trust/i'),
                       ARTIFACT.replace("const PROTECTED_TRANSLATION_ROOT", 'const RENAMED_ROOT'),
                       ARTIFACT.replace('50_000', 'calculateLimit()'),
                       ARTIFACT.replace("[\n  'components", "new Set(\n  'components")):
            with self.subTest(source=source):
                with self.assertRaises(RuntimeError):
                    engine.parse_rules(CHROME, source)

    def test_offline_mode_requires_engine_module(self):
        with self.assertRaisesRegex(RuntimeError, '--artifact'):
            engine.load_rules(chrome='does-not-matter')

    def test_offline_audit_rejects_component_and_waves_exclude_it(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'chrome.ts').write_text(CHROME, encoding='utf-8')
            (root / 'artifact.ts').write_text(ARTIFACT, encoding='utf-8')
            tree = {'components': {'native-chat': {'approval': {'allow': 'Allow'}}}, 'menu': {'file': 'File'}}
            (root / 'en.json').write_text(json.dumps(tree), encoding='utf-8')
            (root / 'cs.json').write_text(json.dumps(tree), encoding='utf-8')
            manifest = {'contributes': {'languagePacks': [{'path': 'cs.json', 'locale': 'cs-CZ'}]}}
            (root / 'orca-plugin.json').write_text(json.dumps(manifest), encoding='utf-8')
            args = ['--en', str(root / 'en.json'), '--chrome', str(root / 'chrome.ts'),
                    '--artifact', str(root / 'artifact.ts')]
            audit = subprocess.run([sys.executable, str(ROOT / 'tools/audit-pack.py'), str(root), *args],
                                   capture_output=True, encoding='utf-8')
            self.assertEqual(audit.returncode, 1, audit.stdout + audit.stderr)
            self.assertIn('ODMÍTNUT', audit.stdout)
            out = root / 'blocks'
            waves = subprocess.run([sys.executable, str(ROOT / 'tools/prepare-waves.py'),
                                    *args, '--out-dir', str(out)], capture_output=True, encoding='utf-8')
            self.assertEqual(waves.returncode, 0, waves.stdout + waves.stderr)
            self.assertEqual(json.loads(next(out.glob('*.json')).read_text(encoding='utf-8')),
                             {'menu.file': 'File'})

    def test_build_help_and_unknown_arguments_do_not_write_catalog(self):
        path = ROOT / 'locales/cs-CZ.json'
        before = path.read_bytes()
        for arg, code in (('--help', 0), ('--invalid', 1)):
            result = subprocess.run([sys.executable, str(ROOT / 'tools/build.py'), arg],
                                    capture_output=True, encoding='utf-8')
            self.assertEqual(result.returncode, code)
            self.assertEqual(path.read_bytes(), before)

    def test_release_check_catches_one_missing_count_site(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ('tools/release-check.py', 'README.md', 'GLOSSARY.md',
                         'orca-plugin.json', 'locales/cs-CZ.json'):
                dest = root / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, dest)
            readme = root / 'README.md'
            readme.write_text(readme.read_text(encoding='utf-8').replace('obsahuje ', 'nese '), encoding='utf-8')
            result = subprocess.run([sys.executable, str(root / 'tools/release-check.py')],
                                    capture_output=True, encoding='utf-8')
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn('nenalezeno povinné místo „popis katalogu“', result.stdout)


if __name__ == '__main__':
    unittest.main()
