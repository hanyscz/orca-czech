"""Společná pravidla jazykových balíčků načtená z konkrétního vydání Orca."""

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess

REPO = 'stablyai/orca'
EN_PATH = 'src/renderer/src/i18n/locales/en.json'
CHROME_PATHS = (
    'src/shared/plugins/languages/plugin-translatable-chrome.ts',
    'src/shared/plugins/plugin-translatable-chrome.ts',
)
ARTIFACT_PATHS = (
    'src/shared/plugins/artifacts/plugin-language-pack-artifact.ts',
    'src/shared/plugins/plugin-language-pack-artifact.ts',
)
PROTECTED_ROOT = 'auto.components.settings.'


def gh(*args):
    result = subprocess.run(['gh', *args], capture_output=True, encoding='utf-8', errors='strict')
    if result.returncode or not result.stdout.strip():
        raise RuntimeError(f'Volání gh selhalo: {result.stderr.strip() or "prázdná odpověď"}')
    return result.stdout


def latest_release():
    return gh('release', 'view', '--repo', REPO, '--json', 'tagName', '--jq', '.tagName').strip()


def fetch_source(path, release):
    return gh('api', '-H', 'Accept: application/vnd.github.raw+json',
              f'repos/{REPO}/contents/{path}?ref={release}')


def fetch_first(paths, release):
    """Další cestu zkoušíme pouze při 404; ostatní chyby nesmějí schovat výpadek API."""
    for path in paths:
        try:
            return fetch_source(path, release)
        except RuntimeError as exc:
            if 'HTTP 404' not in str(exc):
                raise
    raise RuntimeError(f'Ve vydání {release} nebyl nalezen soubor na cestách: {", ".join(paths)}')


@dataclass
class EngineRules:
    chrome_source: str
    artifact_source: str
    allowed_chrome: set
    protected_components: tuple
    max_entries: int
    max_depth: int
    max_value: int = 8192
    max_bytes: int = 5 * 1024 * 1024

    def protected(self, path):
        if any(path == c or path.startswith(c + '.') for c in self.protected_components):
            return True
        return (path.startswith(PROTECTED_ROOT) and path not in self.allowed_chrome
                and path[len(PROTECTED_ROOT):].lower().startswith('plugin'))


def parse_rules(chrome_source, artifact_source):
    known = {'PROTECTED_TRANSLATION_ROOT': "'auto.components.settings.'",
             'PROTECTED_TRANSLATION_MODULE': '/^plugin/i',
             'PROTECTED_TRANSLATION_COMPONENTS': None}
    declarations = dict(re.findall(r'\bconst (PROTECTED_[A-Z_]+)\s*=\s*([^\n]+)', artifact_source))
    unknown = set(declarations) - set(known)
    changed = {k for k, v in known.items() if v is not None
               and declarations.get(k, '').strip() != v}
    if unknown or changed:
        raise RuntimeError('Engine má neznámá nebo změněná pravidla ochrany: '
                           + ', '.join(sorted(unknown | changed)))
    components = re.search(r'PROTECTED_TRANSLATION_COMPONENTS\s*=\s*\[(.*?)\]', artifact_source, re.S)
    if 'PROTECTED_TRANSLATION_COMPONENTS' in declarations and not components:
        raise RuntimeError('Nelze přečíst seznam chráněných komponent.')
    limits = []
    for name in ('ENTRIES', 'DEPTH'):
        match = re.search(r'\bPLUGIN_LANGUAGE_CATALOG_MAX_' + name + r'\s*=\s*([\d_]+)\b', artifact_source)
        if not match:
            raise RuntimeError(f'Nelze přečíst limit enginu {name}.')
        limits.append(int(match.group(1).replace('_', '')))
    return EngineRules(chrome_source, artifact_source,
                       set(re.findall(r"'(auto\.components\.settings\.[^']+)'", chrome_source)),
                       tuple(re.findall(r"'([^']+)'", components.group(1))) if components else (),
                       *limits)


def load_rules(release=None, chrome=None, artifact=None):
    if not release and not (chrome and artifact):
        raise RuntimeError('Offline kontrola vyžaduje --chrome i --artifact; jinak zadejte vydání.')
    chrome_source = Path(chrome).read_text(encoding='utf-8') if chrome else fetch_first(CHROME_PATHS, release)
    artifact_source = Path(artifact).read_text(encoding='utf-8') if artifact else fetch_first(ARTIFACT_PATHS, release)
    return parse_rules(chrome_source, artifact_source)
