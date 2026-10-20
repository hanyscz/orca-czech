#!/usr/bin/env python3
"""Porovnává verzi a počty řetězců ve všech souborech balíčku. Spouštět PŘED otagováním.

Spuštění z kořenového adresáře repozitáře:

    python3 tools/release-check.py

Jediná ochrana proti nekonzistentním údajům a zastaralým číslům je kontrola před tagem.
Publikovaný tag již nelze posunout.

Kontrolují se pouze místa popisující AKTUÁLNÍ vydání balíčku.
"""
import json, re, sys, os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (regex s group(1) = hodnota, popis místa)
VERSION_SITES = [
    (r'badge/(?:verze|version)-(?:v)?([0-9.]+)-', 'odznak verze'),
    (r'(?:Verze balíčku|Package version) ([0-9.]+)', 'alt odznaku verze'),
    (r'orca-czech(?:\.git)?#v([0-9.]+)', 'řádek instalace'),
    (r'Aktuální k `v([0-9.]+)`', 'záhlaví glosáře'),
    (r'limitům enginu\*\* k v([0-9.]+)', 'rezerva limitů v glosáři'),
]

COUNT_SITES = [
    (r'badge/(?:řetězců|strings|строк)-(\d{2}[,\s%]?(?:20)?\d{3})-', 'odznak řetězců'),
    (r'alt="(\d{2}[,\s]\d{3}) (?:přeložených řetězců|přeložen\w+ řetězc\w*|translated strings)"', 'alt odznaku řetězců'),
    (r'\n\s*(\d{2}[,\s]\d{3}) (?:řetězců —|řetězc\w* —|strings —)', 'podnadpis'),
    (r'(?:katalog překladů|translation catalog), (\d{2}[,\s]\d{3})', 'strom souborů'),
    (r'přeloženo (\d{2}[,\s]\d{3}) řádků', 'záhlaví glosáře'),
]

DOCS = ['README.md', 'GLOSSARY.md']

EXTRA_SITES = [
    (r'a (\d+) doplňkov\w+ tvar\w* množného čísla', 'doplňkové tvary'),
    (r'and (\d+) extra plural forms', 'doplňkové tvary'),
]


def flat(o, p=''):
    out = {}
    for k, v in o.items():
        path = f'{p}.{k}' if p else k
        out.update({path: v} if isinstance(v, str) else flat(v, path))
    return out


manifest = json.load(open(os.path.join(ROOT, 'orca-plugin.json'), encoding='utf-8'))
version = manifest['version']
catalog_path = os.path.join(ROOT, 'locales', 'cs-CZ.json')
catalog = flat(json.load(open(catalog_path, encoding='utf-8')))

# Doplňkové tvary množného čísla
extra_forms = [k for k in catalog if re.search(r'_(few|many)$', k)
               or (k.endswith('_one') and k[:-4] + '_other' not in catalog)]
lines = len(catalog) - len(extra_forms)
print(f'manifest: v{version}, katalog: {lines} řádků (+{len(extra_forms)} doplňkových tvarů)')

ok_counts = {
    f'{lines:,}',
    f'{lines // 1000} {lines % 1000:03d}',
    f'{lines // 1000}%20{lines % 1000:03d}'
}


def norm(s):
    return s.replace('\xa0', ' ').replace(' ', ' ')


errors, checked, counts_checked = [], 0, 0
for rel in DOCS:
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        continue
    text = open(path, encoding='utf-8').read()
    for pattern, what in VERSION_SITES:
        for found in set(re.findall(pattern, text)):
            checked += 1
            if found != version:
                errors.append(f'{rel} ({what}): nalezeno {found} namísto {version}')
    for pattern, what in COUNT_SITES:
        for found in set(re.findall(pattern, text)):
            checked += 1
            counts_checked += 1
            if norm(found) not in ok_counts:
                errors.append(f'{rel} ({what}): nalezeno {found} namísto {lines}')

extra_checked = 0
for rel in DOCS:
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        continue
    text = open(path, encoding='utf-8').read()
    for pattern, what in EXTRA_SITES:
        for found in set(re.findall(pattern, text)):
            checked += 1
            extra_checked += 1
            if int(found) != len(extra_forms):
                errors.append(f'{rel} ({what}): nalezeno {found} namísto {len(extra_forms)}')

if extra_forms and not extra_checked:
    errors.append('v balíčku jsou doplňkové tvary množného čísla, ale dokumentace neuvádí jejich počet')

# Anglický zbytek: záhlaví sekce musí odpovídat součtu svých položek
REMAINDER = {
    'README.md': (
        r'(\d[\d\s\xa0]*) klíčů katalogu Orca v[\d.]+ zůstává v angličtině',
        r'\n- \*\*(\d[\d\s\xa0]*) (?:řetěz\w*|klíč\w*)\*\*',
        'Seznam se zkracuje'
    ),
}

headlines = {}
for rel, (head_re, item_re, stop) in REMAINDER.items():
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        continue
    text = open(path, encoding='utf-8').read()
    m = re.search(head_re, text)
    if not m or stop not in text[m.end():]:
        errors.append(f'{rel}: nebyla nalezena sekce anglického zbytku — vzor REMAINDER neodpovídá')
        continue
    checked += 1
    head = int(re.sub(r'\D', '', m.group(1)))
    body = text[m.end():text.index(stop, m.end())]
    total = sum(int(re.sub(r'\D', '', v)) for v in re.findall(item_re, body))
    headlines[rel] = head
    if total != head:
        errors.append(f'{rel}: v záhlaví zbytku je {head}, ale položky v součtu dávají {total}')

if not counts_checked:
    errors.append('nebylo nalezeno žádné počítadlo řádků — vzory COUNT_SITES neodpovídají')

for e in sorted(set(errors)):
    print('  ✗', e)

if errors:
    print(f'\n❌ {len(set(errors))} neshod na {checked} místech — tag nevytvářet')
    sys.exit(1)

print(f'\n✅ verze a počty jsou v souladu, zkontrolováno míst: {checked}')
