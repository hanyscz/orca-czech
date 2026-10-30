#!/usr/bin/env python3
"""Stáhne podklady jednoho vydání Orca a připraví složku pro překlad."""

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
REPO = 'stablyai/orca'
from engine_rules import load_rules


def run(command, env=None):
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                            encoding='utf-8', errors='replace')
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip()
                           or 'Příkaz selhal: ' + ' '.join(command))
    return result.stdout


def fetch(path, release):
    return run(['gh', 'api', '-H', 'Accept: application/vnd.github.raw+json',
                f'repos/{REPO}/contents/{path}?ref={release}'])


def prepare(release=None):
    if not shutil.which('gh'):
        raise RuntimeError('Chybí GitHub CLI (gh). Nainstalujte jej a spusťte gh auth login.')

    release = release or run(['gh', 'release', 'view', '--repo', REPO,
                                  '--json', 'tagName', '--jq', '.tagName']).strip()
    if not release:
        raise RuntimeError('Nepodařilo se zjistit vydání Orca.')
    print(f'Připravuji překlad pro Orca {release}…', flush=True)
    # Nový adresář zamezí přepsání rozpracovaných překladů i načtení starých bloků.
    scratch = ROOT / '.i18n-work'
    scratch.mkdir(exist_ok=True)
    safe_release = re.sub(r'[^a-zA-Z0-9._-]', '_', release)
    folder = Path(tempfile.mkdtemp(
        prefix=f'update-{safe_release}-{datetime.now():%Y%m%d-%H%M%S}-', dir=scratch))
    print(f'Pracovní složka: {folder}', flush=True)

    english = fetch('src/renderer/src/i18n/locales/en.json', release)
    json.loads(english)  # Nezapisujeme chybnou odpověď jako katalog.
    (folder / 'en.json').write_text(english, encoding='utf-8')
    rules = load_rules(release)
    (folder / 'plugin-translatable-chrome.ts').write_text(rules.chrome_source, encoding='utf-8')
    (folder / 'plugin-language-pack-artifact.ts').write_text(rules.artifact_source, encoding='utf-8')

    common = ['--release', release, '--en', str(folder / 'en.json'),
              '--chrome', str(folder / 'plugin-translatable-chrome.ts'),
              '--artifact', str(folder / 'plugin-language-pack-artifact.ts')]
    audit_result = subprocess.run([sys.executable, str(ROOT / 'tools/audit-pack.py'), *common, '--list'],
                                  cwd=ROOT, capture_output=True, encoding='utf-8', errors='replace')
    audit = audit_result.stdout + audit_result.stderr
    if audit_result.returncode and 'verdikt enginu:' not in audit_result.stdout:
        raise RuntimeError(audit.strip() or 'Audit selhal bez výsledku.')
    (folder / 'audit.txt').write_text(audit, encoding='utf-8')
    # Úplný seznam ponecháme v audit.txt, terminál zůstane přehledný.
    print('\n'.join(line for line in audit.splitlines()
                    if not line.startswith('    ')), flush=True)
    env = dict(os.environ, ORCA_CS_WORK=str(folder))
    output = run([sys.executable, str(ROOT / 'tools/prepare-waves.py'),
                  *common, '--untranslated'], env=env)
    (folder / 'prepare-log.txt').write_text(output, encoding='utf-8')

    prompt = f'''Přelož do češtiny všechny JSON bloky v {folder.as_posix()}/source/.
Nejprve přečti GLOSSARY.md a použij locales/cs-CZ.json jako vzor terminologie.
Překládej pouze hodnoty. Zachovej přesně sadu klíčů, zástupné symboly jako
{{{{name}}}} a {{{{count}}}}, značky, odkazy, příkazy a význam formátování.
Používej přirozenou češtinu; názvy produktů a identifikátory ponech podle glosáře.
Zdrojové soubory v source/ neměň. Přeložené kopie ulož přímo do
{folder.as_posix()}/ pod názvy wave01-cs-part01.json, wave01-cs-part02.json atd.
Výstupy musí být platný JSON v UTF-8, bez komentářů a Markdown obalu.
Ověř shodu klíčů a zástupných symbolů s originály a shrň případné nejasnosti.
Zatím neupravuj locales/cs-CZ.json ani manifest a nevytvářej vydání.
'''
    (folder / 'PROMPT.txt').write_text(prompt, encoding='utf-8')
    instructions = f'''Podklady pro Orca {release}

1. Předejte agentovi obsah PROMPT.txt. Originály jsou v source/.
2. Přeložené bloky patří přímo do této pracovní složky.
3. Spusťte prepare-translation.bat v kořeni repozitáře.
4. Zvolte 4 — Dokončení překladu. Aktivní složka musí být:
{folder}
Jinou složku lze vybrat volbou 5.

Sestavení a závěrečný audit používají nejnovější stabilní vydání.
Pokud mezitím vyjde další verze Orca, ověřte znovu podklady.
Audit.txt zachycuje stav před překladem proti {release}.
Filtr vybírá chybějící hodnoty a hodnoty s azbukou, nikoli změny EN textu
u již přeložených klíčů. Pracovní složka se necommituje.
'''
    (folder / 'POSTUP.txt').write_text(instructions, encoding='utf-8')
    (scratch / 'active-work.txt').write_text(folder.name, encoding='utf-8')
    blocks = sorted((folder / 'source').glob('*.json'))
    count = sum(len(json.loads(p.read_text(encoding='utf-8'))) for p in blocks)
    print(f'Hotovo: {count} textů v {len(blocks)} blocích. Český katalog se nezměnil.')
    print(f'Podklady: {folder / "source"}')
    print(f'Prompt pro agenta: {folder / "PROMPT.txt"}')
    print(f'Příkazy po překladu: {folder / "POSTUP.txt"}')
    return folder


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', help='Konkrétní značka vydání; jinak nejnovější stabilní')
    args = parser.parse_args()
    prepare(args.release)


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    try:
        main()
    except (RuntimeError, OSError, ValueError) as exc:
        print(f'CHYBA: {exc}', file=sys.stderr)
        sys.exit(1)
