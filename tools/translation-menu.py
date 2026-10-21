#!/usr/bin/env python3
"""Interaktivní správa českého překladu Orca."""

import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / '.i18n-work'
spec = importlib.util.spec_from_file_location('prepare_update', ROOT / 'tools/prepare-update.py')
preparation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preparation)


def folders():
    if not WORK.exists():
        return []
    return sorted((p for p in WORK.glob('update-*') if p.is_dir()
                   and (p / 'PROMPT.txt').is_file() and (p / 'source').is_dir()),
                  key=lambda p: p.stat().st_mtime, reverse=True)


def active_folder():
    available = folders()
    state = WORK / 'active-work.txt'
    if state.is_file():
        name = state.read_text(encoding='utf-8').strip()
        for folder in available:
            if folder.name == name:
                return folder
    # Podpora složek vytvořených původním přípravným skriptem.
    return available[0] if available else None


def require_folder():
    folder = active_folder()
    if folder is None:
        raise RuntimeError('Nejdříve zvolte 2 — Příprava na překlad.')
    return folder


def choose_folder():
    available = folders()
    if not available:
        raise RuntimeError('Zatím nejsou připravené žádné podklady. Použijte volbu 2.')
    for index, folder in enumerate(available, 1):
        print(f'{index}. {folder.name}')
    value = input('Číslo pracovní složky (Enter = zpět): ').strip()
    if not value:
        return
    if not value.isdigit() or not 1 <= int(value) <= len(available):
        raise RuntimeError('Neplatné číslo složky.')
    folder = available[int(value) - 1]
    (WORK / 'active-work.txt').write_text(folder.name, encoding='utf-8')
    print(f'Vybráno: {folder}')


def copy_prompt():
    prompt = (require_folder() / 'PROMPT.txt').read_text(encoding='utf-8')
    print('\n' + prompt)
    # UTF-8 přenos přes stdin, žádné vkládání promptu do shellového příkazu.
    command = [
        'powershell.exe', '-NoProfile', '-NonInteractive', '-STA', '-Command',
        '[Console]::InputEncoding = New-Object System.Text.UTF8Encoding; '
        '$promptText = [Console]::In.ReadToEnd(); Set-Clipboard -Value $promptText',
    ]
    result = subprocess.run(command, input=prompt, encoding='utf-8', capture_output=True)
    if result.returncode:
        raise RuntimeError('Prompt je vypsaný výše, ale kopírování do schránky selhalo: '
                           + result.stderr.strip())
    print('Prompt byl zkopírován do schránky. Vložte ho agentovi pomocí Ctrl+V.')


def read_block(path):
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(data, dict) or any(not isinstance(v, str) for v in data.values()):
        raise RuntimeError(f'{path.name}: očekávám plochý JSON objekt s textovými hodnotami.')
    return data


def validate_blocks(folder):
    sources = sorted((folder / 'source').glob('wave*-part*.json'))
    if not sources:
        raise RuntimeError('Podklady neobsahují texty k překladu. Použijte kontrolu aktuálnosti.')
    expected = set()
    for source in sources:
        target = folder / source.name.replace('-part', '-cs-part')
        expected.add(target.name)
        if not target.is_file():
            raise RuntimeError(f'Chybí přeložený soubor {target.name}. '
                               'Agent ho musí uložit přímo do pracovní složky.')
        original, translated = read_block(source), read_block(target)
        if original.keys() != translated.keys():
            raise RuntimeError(f'{target.name}: sada klíčů se liší od originálu.')
        for key, value in translated.items():
            if not value.strip() and original[key].strip():
                raise RuntimeError(f'{target.name}: prázdný překlad klíče {key}.')
            if re.search(r'[\u0400-\u04ff]', value):
                raise RuntimeError(f'{target.name}: překlad {key} obsahuje azbuku.')
            tokens = lambda text: sorted(re.findall(r'\{\{[^}]*\}\}', text))
            if tokens(original[key]) != tokens(value):
                raise RuntimeError(f'{target.name}: změněné zástupné symboly u {key}.')
    actual = {p.name for pattern in ('wave*-cs-part*.json', 'wave*-part*.json')
              for p in folder.glob(pattern)}
    if actual != expected:
        raise RuntimeError('V pracovní složce jsou nečekané překladové bloky: '
                           + ', '.join(sorted(actual - expected)))


def finish(folder):
    print(f'Kontroluji překlady ve složce {folder}…', flush=True)
    validate_blocks(folder)
    env = dict(os.environ, ORCA_CS_WORK=str(folder))
    build = preparation.run([sys.executable, str(ROOT / 'tools/build.py')], env=env)
    (folder / 'build-log.txt').write_text(build, encoding='utf-8')
    print(build, flush=True)
    # Auditní zprávu uložíme i při odmítnutí katalogu enginem.
    audit = subprocess.run([sys.executable, str(ROOT / 'tools/audit-pack.py'), '--list'],
                           cwd=ROOT, capture_output=True, encoding='utf-8', errors='replace')
    report = audit.stdout + audit.stderr
    (folder / 'audit-after.txt').write_text(report, encoding='utf-8')
    print('\n'.join(line for line in report.splitlines() if not line.startswith('    ')))
    diff = preparation.run(['git', '--no-pager', 'diff', '--', 'locales/cs-CZ.json'])
    (folder / 'changes.diff').write_text(diff, encoding='utf-8')
    print(preparation.run(['git', 'diff', '--stat', '--', 'locales/cs-CZ.json']))
    if audit.returncode:
        raise RuntimeError('Závěrečný audit selhal. Podrobnosti jsou v audit-after.txt.')
    missing = re.search(r'; (\d+) chybí', report)
    if missing is None or int(missing.group(1)):
        raise RuntimeError('Katalog byl sestaven, ale audit nepotvrdil úplné pokrytí. '
                           'Projděte audit-after.txt; případně připravte podklady nové verze.')
    placeholders = re.search(r'zástupné symboly, které anglický originál nemá: (\d+)', report)
    if placeholders is None or int(placeholders.group(1)):
        raise RuntimeError('Audit nepotvrdil správnost zástupných symbolů. Projděte audit-after.txt.')
    print('Překlad byl sestaven a audit potvrdil úplné pokrytí. Vyzkoušejte ho v Orce.')
    print(f'Audit a změny jsou v {folder} (audit-after.txt, changes.diff).')
    print('Verze balíčku, commit ani vydání se automaticky nevytvářejí.')


def main():
    while True:
        folder = active_folder()
        print('\n=== Čeština pro Orca ===')
        print(f'Aktivní složka: {folder.name if folder else "zatím žádná"}')
        print('1 — Kontrola aktuálnosti překladu')
        print('2 — Příprava na překlad')
        print('3 — Vypsat prompt a zkopírovat do schránky')
        print('4 — Dokončení překladu (sestavení a audit)')
        print('5 — Vybrat jinou pracovní složku')
        print('6 — Otevřít pracovní složku v Průzkumníku')
        print('0 — Konec')
        choice = input('Vyberte akci: ').strip()
        if choice == '0':
            return
        try:
            if choice == '1':
                print('Kontroluji nejnovější stabilní vydání Orca…', flush=True)
                print(preparation.run([sys.executable, str(ROOT / 'tools/audit-pack.py')]))
            elif choice == '2':
                preparation.prepare()
                print('Nyní zvolte 3 pro zkopírování promptu agentovi.')
            elif choice == '3':
                copy_prompt()
            elif choice == '4':
                finish(require_folder())
            elif choice == '5':
                choose_folder()
            elif choice == '6':
                os.startfile(require_folder())
            else:
                print('Vyberte číslo z nabídky.')
        except (RuntimeError, OSError, ValueError) as exc:
            print(f'CHYBA: {exc}')
        input('\nEnter = návrat do nabídky…')


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print('\nUkončeno.')
