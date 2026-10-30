#!/usr/bin/env python3
"""Připravuje dílčí ploché JSON soubory (překladové bloky / vlny) z anglického katalogu.

Spuštění z kořenového adresáře repozitáře:

    python3 tools/prepare-waves.py                    # vygeneruje bloky po 500 klíčích do .i18n-work/source/
    python3 tools/prepare-waves.py --chunk-size 1000  # bloky po 1 000 klíčích
    python3 tools/prepare-waves.py --by-domain        # rozdělení podle logických oblastí rozhraní
    python3 tools/prepare-waves.py --untranslated     # pouze klíče, které v cs-CZ.json ještě obsahují azbuku či chybí
    python3 tools/prepare-waves.py --with-ref         # vytvoří i referenční soubory (EN originál + RU reference)

Zdrojový katalog hledá v `.i18n-work/en.json` (případně stáhne z GitHubu).
Vygenerované soubory v `.i18n-work/source/` slouží jako podklad pro překlad do češtiny.
Po přeložení se uloží do `.i18n-work/wave*-cs-part*.json`, odkud je `tools/build.py`
zkompiluje a sloučí do výsledného `locales/cs-CZ.json`.
"""

import argparse
import json
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = os.environ.get('ORCA_CS_WORK') or os.path.join(ROOT, '.i18n-work')
TARGET = os.path.join(ROOT, 'locales', 'cs-CZ.json')
REPO = 'stablyai/orca'
EN_PATH = 'src/renderer/src/i18n/locales/en.json'
DANGEROUS = {'__proto__', 'prototype', 'constructor'}
RAW = ['-H', 'Accept: application/vnd.github.raw+json']
CYRILLIC = re.compile(r'[\u0400-\u04FF]')


from engine_rules import latest_release, load_rules


def flatten(tree, prefix=''):
    out = {}
    for k, v in tree.items():
        path = f'{prefix}.{k}' if prefix else k
        if isinstance(v, dict):
            out.update(flatten(v, path))
        elif isinstance(v, str):
            out[path] = v
    return out


def assign_domain(key):
    """Zařadí klíč do tematické oblasti rozhraní."""
    if key.startswith(('menu.', 'app.', 'sidebar.', 'tray.', 'browser.', 'updates.', 'notifications.',
                       'osDocumentOpen.', 'fileExplorer.', 'quickOpen.', 'dashboard.', 'common.')):
        return 'wave01-core-ui'
    if key.startswith(('editor.', 'terminal.', 'workspace.', 'workspaceDeletion.', 'workspaceSpace.',
                       'worktree.', 'worktreeJumpPalette.', 'csv.', 'sessionHistory.', 'sessionSearch.',
                       'sparsePreset.', 'rendererRecovery.', 'runtimeRpc.', 'mediaPreview.', 'tabHoverCard.')):
        return 'wave02-editor-workspace'
    if key.startswith(('sourceControl.', 'githubChecks.', 'checksPanel.', 'jira.', 'projectBoard.',
                       'projectBoardCard.', 'projectField.', 'projectViews.', 'auto.components.GitHubItemDialog.',
                       'auto.components.GitLabItemDialog.', 'auto.components.PullRequestPage.',
                       'auto.components.linear.', 'auto.components.github.')):
        return 'wave03-git-integrations'
    if key.startswith(('aiVault.', 'agentsSidebarIntro.', 'auto.components.right.', 'auto.components.artifacts.',
                       'auto.components.automations.', 'auto.components.skills.', 'auto.components.TaskPage.',
                       'auto.components.NewWorkspaceComposerCard.')):
        return 'wave04-ai-chat-assistant'
    if key.startswith(('accounts.', 'settings.', 'auto.components.settings.')):
        return 'wave05-settings-accounts'
    return 'wave06-components-ui'


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--en', default=None, help='Cesta k en.json (výchozí: .i18n-work/en.json)')
    parser.add_argument('--release', help='Značka vydání pro katalog a pravidla ochrany (výchozí: nejnovější stabilní)')
    parser.add_argument('--chrome', help='Lokální plugin-translatable-chrome.ts daného vydání')
    parser.add_argument('--artifact', help='Lokální modul plugin-language-pack-artifact.ts daného vydání')
    parser.add_argument('--chunk-size', type=int, default=500, help='Počet klíčů v jednom souboru (výchozí: 500)')
    parser.add_argument('--by-domain', action='store_true', help='Rozdělit do vln podle funkčních oblastí rozhraní')
    parser.add_argument('--untranslated', action='store_true', help='Generovat pouze klíče, které v cs-CZ.json obsahují azbuku nebo chybí')
    parser.add_argument('--with-ref', action='store_true', help='Vytvořit i referenční soubory se srovnáním EN originálu a RU překladu')
    parser.add_argument('--out-dir', default=None, help='Cílová složka pro dílčí soubory (výchozí: .i18n-work/source/)')
    parser.add_argument('--direct', action='store_true', help='Uložit přímo do .i18n-work/ s názvy wave*-cs-part*.json pro okamžité použití v build.py')
    args = parser.parse_args()

    # Jedna sada pravidel pro celý běh; bez úplných pravidel se bloky nevytvářejí.
    try:
        stable_tag = args.release or (None if args.en and args.chrome and args.artifact else latest_release())
        rules = load_rules(stable_tag, args.chrome, args.artifact)
    except (RuntimeError, OSError, ValueError) as exc:
        sys.exit(f'CHYBA: {exc}')

    # 1. Načtení en.json
    en_file = args.en or os.path.join(SCRATCH, 'en.json')
    if not os.path.exists(en_file):
        print(f'Soubor {en_file} nebyl nalezen. Zkouším stáhnout z GitHubu...')
        r = subprocess.run(
            ['gh', 'api', *RAW, f'repos/{REPO}/contents/{EN_PATH}?ref={stable_tag}'],
            capture_output=True, text=True, encoding='utf-8', errors='replace'
        )
        if r.returncode != 0 or not r.stdout.strip():
            sys.exit(f'Nepodařilo se načíst en.json z {en_file} ani z GitHubu.')
        os.makedirs(os.path.dirname(en_file), exist_ok=True)
        with open(en_file, 'w', encoding='utf-8') as f:
            f.write(r.stdout)
        print(f'Uložen stažený en.json: {en_file}')

    with open(en_file, 'r', encoding='utf-8') as f:
        en_tree = json.load(f)
    en_flat = flatten(en_tree)
    print(f'Načten en.json: {len(en_flat)} klíčů')

    # 2. Načtení stávajícího katalogu pro kontrolu azbuky a referenci
    cs_flat = {}
    if os.path.exists(TARGET):
        with open(TARGET, 'r', encoding='utf-8') as f:
            cs_flat = flatten(json.load(f))
        print(f'Načten referenční {os.path.basename(TARGET)}: {len(cs_flat)} klíčů')

    print(f'Pravidla pro {stable_tag or "lokální podklady"}: '
          f'{len(rules.allowed_chrome)} výjimek, {len(rules.protected_components)} chráněných komponent')

    # 4. Filtrace translatabilních klíčů
    filtered_keys = []
    skipped_protected = 0
    skipped_length = 0
    skipped_dangerous = 0

    for k, v in sorted(en_flat.items()):
        if rules.protected(k):
            skipped_protected += 1
            continue
        if len(v) > rules.max_value:
            skipped_length += 1
            continue
        if k in DANGEROUS or any(part in DANGEROUS for part in k.split('.')):
            skipped_dangerous += 1
            continue

        # Filtr nepřeložených, pokud byl zadán parametr --untranslated
        if args.untranslated:
            cur_val = cs_flat.get(k)
            # Chybějící nebo obsahující azbuku
            if cur_val is None or CYRILLIC.search(cur_val):
                filtered_keys.append(k)
        else:
            filtered_keys.append(k)

    print(f'Klíče k přípravě: {len(filtered_keys)} (vynecháno {skipped_protected} chráněných, {skipped_length} dlouhých)')

    # 5. Cílový adresář
    if args.direct:
        out_dir = SCRATCH
    elif args.out_dir:
        out_dir = args.out_dir
    else:
        out_dir = os.path.join(SCRATCH, 'source')
    os.makedirs(out_dir, exist_ok=True)

    ref_dir = os.path.join(SCRATCH, 'reference') if args.with_ref else None
    if ref_dir:
        os.makedirs(ref_dir, exist_ok=True)

    # 6. Dělení do souborů
    files_created = []

    if args.by_domain:
        # Skupiny podle domén
        domains = {}
        for k in filtered_keys:
            dom = assign_domain(k)
            domains.setdefault(dom, []).append(k)

        for dom, dom_keys in sorted(domains.items()):
            chunks = [dom_keys[i:i + args.chunk_size] for i in range(0, len(dom_keys), args.chunk_size)]
            for idx, chunk in enumerate(chunks, 1):
                fname = f'{dom}-part{idx:02d}.json'
                if args.direct:
                    fname = f'{dom}-cs-part{idx:02d}.json'
                fpath = os.path.join(out_dir, fname)

                data = {k: en_flat[k] for k in chunk}
                with open(fpath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                files_created.append((fpath, len(data)))

                if args.with_ref:
                    ref_data = {
                        k: {
                            'en': en_flat[k],
                            'ru_reference': cs_flat.get(k, '')
                        } for k in chunk
                    }
                    ref_path = os.path.join(ref_dir, fname.replace('.json', '.ref.json'))
                    with open(ref_path, 'w', encoding='utf-8') as f:
                        json.dump(ref_data, f, ensure_ascii=False, indent=2)
    else:
        # Sekvenční číslování vln a částí
        chunks = [filtered_keys[i:i + args.chunk_size] for i in range(0, len(filtered_keys), args.chunk_size)]
        total_chunks = len(chunks)
        print(f'Rozdělení do {total_chunks} souborů po max {args.chunk_size} klíčích...')

        for idx, chunk in enumerate(chunks, 1):
            fname = f'wave01-cs-part{idx:02d}.json' if args.direct else f'wave01-part{idx:02d}.json'
            fpath = os.path.join(out_dir, fname)

            data = {k: en_flat[k] for k in chunk}
            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            files_created.append((fpath, len(data)))

            if args.with_ref:
                ref_data = {
                    k: {
                        'en': en_flat[k],
                        'ru_reference': cs_flat.get(k, '')
                    } for k in chunk
                }
                ref_path = os.path.join(ref_dir, fname.replace('.json', '.ref.json'))
                with open(ref_path, 'w', encoding='utf-8') as f:
                    json.dump(ref_data, f, ensure_ascii=False, indent=2)

    print(f'\nÚspěšně vygenerováno {len(files_created)} dílčích souborů do: {out_dir}')
    if ref_dir:
        print(f'Referenční soubory uloženy do: {ref_dir}')
    print('\nPrvní 5 vytvořených souborů:')
    for p, count in files_created[:5]:
        print(f'  - {os.path.basename(p)} ({count} klíčů)')
    if len(files_created) > 5:
        print(f'  … a dalších {len(files_created) - 5} souborů.')

    print('\nPostup překladu:')
    print('  1. Vezměte dílčí soubor (např. z .i18n-work/source/ nebo podle domény).')
    print('  2. Přeložte anglické hodnoty do češtiny (dodržujte GLOSSARY.md a zachovejte zástupné symboly jako {{count}}).')
    print('  3. Přeložený soubor uložte do .i18n-work/ s názvem wave*-cs-part*.json (např. .i18n-work/wave01-cs-part01.json).')
    print('  4. Spusťte `python tools/build.py` pro sloučení do locales/cs-CZ.json.')
    print('  5. Spusťte `python tools/audit-pack.py` pro ověření integrity balíčku.')


if __name__ == '__main__':
    main()
