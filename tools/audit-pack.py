#!/usr/bin/env python3
"""Audituje jazykový balíček Orca vůči jednomu vydání Orca.

    python3 tools/audit-pack.py                     # tento balíček, nejnovější stabilní vydání Orca
    python3 tools/audit-pack.py --release v1.4.224  # konkrétní vydání
    python3 tools/audit-pack.py cesta/k/balicku     # libovolný balíček s orca-plugin.json
    python3 tools/audit-pack.py --en en.json --chrome plugin-translatable-chrome.ts   # offline režim

Odpovídá na klíčové otázky po každém vydání aplikace Orca:

- Přijme engine tento katalog? Jediný chráněný klíč, příliš dlouhá hodnota nebo
  nebezpečný klíč způsobí, že Orca odmítne celý balíček a rozhraní zůstane tiše v angličtině.
- Které řetězce z vydání stále nejsou přeloženy a které klíče balíčku již vydání nedefinuje?
- Odpovídají zástupné symboly (placeholders) anglickému originálu?

Pravidla se načítají ze značky vydání (release tag), nikoli z větve main: balíček se instaluje
do vydání a pravidlo, které se dostalo teprve do main, zatím pro nikoho neplatí.
Vyžaduje python3 a přihlášené `gh` (pokud nejsou zadány parametry --en/--chrome).
Návratový kód je 1, pokud by engine odmítl alespoň jeden auditovaný balíček.
"""
import argparse, base64, json, os, re, subprocess, sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

REPO = 'stablyai/orca'
EN_PATH = 'src/renderer/src/i18n/locales/en.json'
CHROME_PATH = 'src/shared/plugins/plugin-translatable-chrome.ts'
PROTECTED_ROOT = 'auto.components.settings.'
DANGEROUS = {'__proto__', 'prototype', 'constructor'}
MAX_ENTRIES, MAX_DEPTH, MAX_VALUE, MAX_BYTES = 20_000, 16, 8192, 5 * 1024 * 1024
PLURAL = re.compile(r'_(zero|one|two|few|many|other)$')


def gh(*args):
    result = subprocess.run(['gh', *args], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0 or not result.stdout.strip():
        sys.exit(f'Volání gh {" ".join(args[:2])} selhalo: {result.stderr.strip() or "prázdná odpověď"}')
    return result.stdout


def flatten(tree, prefix=''):
    out = {}
    for key, value in tree.items():
        path = f'{prefix}.{key}' if prefix else key
        if isinstance(value, dict):
            out.update(flatten(value, path))
        else:
            out[path] = value
    return out


def shape(tree, depth=0):
    """Položky, maximální hloubka a nebezpečné klíče počítané tak, jak engine prochází katalog."""
    entries, deepest, unsafe = 0, depth, []
    for key, value in tree.items():
        entries += 1
        if not key or len(key) > 128 or key in DANGEROUS or '.' in key or any(ord(c) <= 31 for c in key):
            unsafe.append(key)
        if isinstance(value, dict):
            child_entries, child_depth, child_unsafe = shape(value, depth + 1)
            entries += child_entries
            deepest = max(deepest, child_depth)
            unsafe += child_unsafe
    return entries, deepest, unsafe


def placeholders(text):
    return set(re.findall(r'\{\{[^}]*\}\}', text))


parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
parser.add_argument('packs', nargs='*', help='adresáře balíčků (výchozí: repozitář, kde se nachází tento skript)')
parser.add_argument('--release', help='značka vydání Orca (výchozí: nejnovější stabilní vydání)')
parser.add_argument('--en', help='lokální soubor en.json daného vydání namísto stahování z GitHubu')
parser.add_argument('--chrome', help='lokální soubor plugin-translatable-chrome.ts daného vydání')
parser.add_argument('--list', action='store_true', help='vypsat všechny chybějící a zastaralé klíče, nikoli jen ukázku')
args = parser.parse_args()

release = args.release
if not release and not (args.en and args.chrome):
    release = gh('release', 'view', '--repo', REPO, '--json', 'tagName', '--jq', '.tagName').strip()
if args.en:
    english = flatten(json.load(open(args.en, encoding='utf-8')))
else:
    # Přímý media type pro soubory nad 1 MiB
    english = flatten(json.loads(gh('api', '-H', 'Accept: application/vnd.github.raw+json',
                                    f'repos/{REPO}/contents/{EN_PATH}?ref={release}')))
if args.chrome:
    chrome_source = open(args.chrome, encoding='utf-8').read()
else:
    chrome_source = base64.b64decode(gh('api', f'repos/{REPO}/contents/{CHROME_PATH}?ref={release}',
                                        '--jq', '.content')).decode('utf-8')
allowed_chrome = set(re.findall(r"'(auto\.components\.settings\.[^']+)'", chrome_source))


def protected(path):
    """Pravidlo enginu: settings.plugin* jsou texty souhlasu a důvěry s výjimkou explicitního allow-listu."""
    if not path.startswith(PROTECTED_ROOT) or path in allowed_chrome:
        return False
    return path[len(PROTECTED_ROOT):].lower().startswith('plugin')


translatable = {k for k, v in english.items() if not protected(k) and len(v) <= MAX_VALUE}
print(f'Orca {release or "(lokální katalog)"}: {len(english)} klíčů v katalogu, {len(translatable)} lze přeložit '
      f'({sum(1 for k in english if protected(k))} chráněných, '
      f'{sum(1 for v in english.values() if len(v) > MAX_VALUE)} delších než {MAX_VALUE} znaků, '
      f'{len(allowed_chrome)} povolených výjimek v allow-listu).\n')

rejected = False
default_pack = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for root in args.packs or [default_pack]:
    manifest = json.load(open(os.path.join(root, 'orca-plugin.json'), encoding='utf-8'))
    for pack in manifest['contributes']['languagePacks']:
        path = os.path.join(root, pack['path'])
        tree = json.load(open(path, encoding='utf-8'))
        catalog = flatten(tree)
        entries, depth, unsafe = shape(tree)
        size = os.path.getsize(path)

        reasons = []
        blocked = sorted(k for k in catalog if protected(k))
        too_long = sorted(k for k, v in catalog.items() if isinstance(v, str) and len(v) > MAX_VALUE)
        not_text = sorted(k for k, v in catalog.items() if not isinstance(v, str))
        if blocked: reasons.append(f'{len(blocked)} chráněných klíčů, první: {blocked[0]}')
        if too_long: reasons.append(f'{len(too_long)} hodnot delších než {MAX_VALUE} znaků, první: {too_long[0]}')
        if not_text: reasons.append(f'{len(not_text)} hodnot, které nejsou řetězce, první: {not_text[0]}')
        if unsafe: reasons.append(f'{len(unsafe)} nebezpečných klíčů, první: {unsafe[0]!r}')
        if entries > MAX_ENTRIES: reasons.append(f'{entries} položek, limit je {MAX_ENTRIES}')
        if depth > MAX_DEPTH: reasons.append(f'hloubka {depth}, limit je {MAX_DEPTH}')
        if size > MAX_BYTES: reasons.append(f'{size} bajtů, limit je {MAX_BYTES}')
        rejected = rejected or bool(reasons)

        text = {k: v for k, v in catalog.items() if isinstance(v, str)}
        covered = [k for k in text if k in translatable]
        missing = sorted(translatable - set(text))
        def family(key):
            base = PLURAL.sub('', key)
            return [english[k] for k in (base + '_other', base + '_one', base) if k in english]

        extra_plural = sorted(k for k in text if k not in english and PLURAL.search(k) and family(k))
        stale = sorted(k for k in text if k not in english and k not in extra_plural)
        same = [k for k in covered if text[k] == english[k]]
        def known_placeholders(key):
            sources = [english[key]] if key in english else family(key)
            found = set().union(*map(placeholders, sources)) if sources else set()
            if key in english and PLURAL.search(key) and '{{count}}' in english.get(PLURAL.sub('', key) + '_other', ''):
                found.add('{{count}}')
            return sources, found

        surplus = sorted(k for k in text
                         if (known := known_placeholders(k))[0] and placeholders(text[k]) - known[1])

        print(f'{manifest.get("publisher")}.{manifest.get("id")} v{manifest.get("version")} — '
              f'{pack.get("locale")}, {pack["path"]}, enginy {manifest.get("engines", {}).get("orca")}')
        print(f'  verdikt enginu: {"PŘIJAT (ACCEPTED)" if not reasons else "ODMÍTNUT (REJECTED) — " + "; ".join(reasons)}')
        print(f'  velikost: {entries}/{MAX_ENTRIES} položek, hloubka {depth}/{MAX_DEPTH}, {size} bajtů')
        print(f'  pokrytí: {len(covered)}/{len(translatable)} = {100 * len(covered) / len(translatable):.2f} % '
              f'toho, co může balíček přeložit; {len(missing)} chybí')
        print(f'  zastaralé klíče nedefinované ve vydání: {len(stale)}')
        print(f'  doplňkové tvary množného čísla: {len(extra_plural)}'
              + (' — tvary `_few` a `_many` zůstávají neaktivní do stablyai/orca#12505' if extra_plural else ''))
        print(f'  shodné s angličtinou: {len(same)}')
        print(f'  zástupné symboly, které anglický originál nemá: {len(surplus)}')
        for label, keys in (('chybějící', missing), ('zastaralé', stale), ('nadbytečný zástupný symbol', surplus)):
            for key in keys if args.list else keys[:5]:
                print(f'    {label}: {key}')
            if not args.list and len(keys) > 5:
                print(f'    … dalších {len(keys) - 5} položek ({label}, použijte --list)')
        print()

sys.exit(1 if rejected else 0)
