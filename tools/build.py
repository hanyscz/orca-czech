#!/usr/bin/env python3
"""Sestavuje locales/cs-CZ.json z překladových bloků a validuje podle pravidel Orca.

Spuštění z kořenového adresáře repozitáře:

    python3 tools/build.py

Vyžaduje python3 a přihlášené CLI `gh`: pravidla ochrany a originální katalog
se přebírají z nejnovějšího stabilního vydání stablyai/orca. Pracovní adresář
s překladovými bloky je `.i18n-work/` (není sledován v gitu); jinou cestu
lze nastavit proměnnou prostředí ORCA_CS_WORK. Bez bloků sestavení pouze
ověří stávající katalog a odstraní zaniklé či nově chráněné klíče.
"""
import json, re, glob, sys, os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

if sys.argv[1:] in (['-h'], ['--help']):
    print(__doc__.strip())
    sys.exit(0)
if len(sys.argv) > 1:
    sys.exit('build.py se spouští bez argumentů; nápověda: --help')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = os.environ.get('ORCA_CS_WORK') or os.environ.get('ORCA_RU_WORK') or os.path.join(ROOT, '.i18n-work')
TARGET = os.path.join(ROOT, 'locales', 'cs-CZ.json')
EN_PATH = 'src/renderer/src/i18n/locales/en.json'
DANGEROUS = {'__proto__', 'prototype', 'constructor'}

# Zdrojová pravidla i katalogy jsou povinné; výpadek nesmí vyřadit platné překlady.
from engine_rules import latest_release, load_rules, fetch_source
try:
    _stable = latest_release()
    rules = load_rules(_stable)
    en = json.loads(fetch_source(EN_PATH, 'main'))
    en_release = json.loads(fetch_source(EN_PATH, _stable))
    if not en or not en_release:
        raise RuntimeError('Zdrojový katalog je prázdný.')
except (RuntimeError, OSError, ValueError) as exc:
    sys.exit(f'CHYBA: {exc}')
protected = rules.protected
print(f'  pravidla: {_stable}, výjimek {len(rules.allowed_chrome)}, '
      f'chráněných komponent {len(rules.protected_components)}, limit {rules.max_entries} uzlů')

def get(d, path):
    if not d:
        return None
    cur = d
    for p in path.split('.'):
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur if isinstance(cur, str) else None

def placeholders(s):
    return sorted(re.findall(r'\{\{[^}]*\}\}', s))

# Čeština používá _one pro 1, _few pro 2–4, _other pro ostatní celá čísla a _many pro zlomky.
# i18next je vyhledává pro každé volání s parametrem count: ke klíči připojí příponu tvaru:
#   - `_few` a `_many` u rodiny, kde Orca má `<báze>_one` a `<báze>_other`;
#   - `_one`, `_few` a `_many` u řetězce volaného s počtem, ale uloženého vcelku
#     (`fileOther`, `connectedHostCount_other`, `transcriptsSkipped`).
# Od Orca v1.4.243 (#12505) se používají pravidla deklarovaného jazyka.
# Neutrální základní text zůstává zálohou, pokud balíček potřebný tvar nemá.
PLURAL_EXTRA = re.compile(r'_(one|few|many)$')

def plural_family(k):
    m = PLURAL_EXTRA.search(k)
    return k[:m.start()] if m else None

def plural_sources(k):
    """Anglické vzory pro doplňkový tvar; prázdné, pokud je klíč běžný nebo nemá oporu."""
    base = plural_family(k)
    if base is None or get(en, k) is not None or get(en_release, k) is not None:
        return []
    return [s for cat in (en, en_release) for name in (base + '_other', base + '_one', base)
            if (s := get(cat, name)) is not None]

def plural_companions(k):
    """Klíče, bez kterých doplňkový tvar ztrácí smysl: rodina nebo samotný řetězec."""
    base = plural_family(k)
    if get(en, base + '_other') is not None or get(en_release, base + '_other') is not None:
        return [base + '_one', base + '_other']
    return [base]

# --- Základ: již existující katalog, aby bloky nemusely obsahovat vše ---
flat = {}
dupes = []
if os.path.exists(TARGET):
    def flatten(o, p=''):
        for k, v in o.items():
            path = f'{p}.{k}' if p else k
            if isinstance(v, str):
                flat[path] = v
            else:
                flatten(v, path)
    flatten(json.load(open(TARGET, encoding='utf-8')))
    print(f'  základ {os.path.basename(TARGET)}: {len(flat)} řádků')

# Bloky mají vždy přednost před základem.
# Za konflikt se považuje pouze rozpor mezi dvěma bloky.
from_block = {}
block_files = sorted(set(glob.glob(os.path.join(SCRATCH, 'wave*-cs-part*.json')) +
                         glob.glob(os.path.join(SCRATCH, 'wave*-part*.json'))))
for f in block_files:
    part = json.load(open(f, encoding='utf-8'))
    for k, v in part.items():
        if k in from_block and from_block[k] != v:
            dupes.append(k)
        from_block[k] = v
        flat[k] = v
    print(f'  + {os.path.basename(f)}: {len(part)} řádků')

errors, warnings = [], []
for k in dupes:
    errors.append(f'klíč {k} je v blocích definován odlišně')

# --- Porovnání s anglickým katalogem (pokud je k dispozici) ---
if en or en_release:
    retired = [k for k in flat
               if get(en, k) is None and get(en_release, k) is None and not plural_sources(k)]
    for k in retired:
        if k in from_block:
            errors.append(f'klíč {k} neexistuje v en.json — odstraňte jej z překladového bloku')
        else:
            warnings.append(f'{k}: zmizel z katalogu Orca, vyřazen z balíčku')
        del flat[k]

    for k in [k for k in flat if protected(k)]:
        if k not in from_block:
            warnings.append(f'{k}: chráněn ve vydání {_stable or "?"}, vyřazen z balíčku')
            del flat[k]

extra_forms = []
for k, v in flat.items():
    extra = plural_sources(k)
    if extra:
        extra_forms.append(k)
        for companion in plural_companions(k):
            if companion not in flat:
                errors.append(f'{k}: v balíčku chybí {companion} — doplňkový tvar bez své opory')
    src = get(en, k) or get(en_release, k) or (extra[0] if extra else None)

    if (en or en_release) and src is None:
        errors.append(f'klíč {k} neexistuje ani v main, ani ve vydání')
        continue

    if src is not None:
        variants = extra or [s for s in (get(en, k), get(en_release, k)) if s is not None]
        known = {p for s in variants for p in placeholders(s)}
        if not extra and (base := plural_family(k)) and any(
                '{{count}}' in (get(cat, base + '_other') or '') for cat in (en, en_release)):
            known.add('{{count}}')
        extra_ph = [p for p in placeholders(v) if p not in known]
        dropped = [p for p in placeholders(src) if p not in placeholders(v)]
        if extra_ph:
            errors.append(f'v {k} se objevil zástupný symbol, který není v originále: {extra_ph}')
        if dropped:
            warnings.append(f'{k}: vynechán {dropped} — ověřte, zda jde o plurálový sufix s, nikoli data')

    if len(v) > rules.max_value:
        errors.append(f'{k} je delší než {rules.max_value} znaků')
    if protected(k):
        errors.append(f'{k} — chráněný klíč, balíček by byl kompletně odmítnut')

    # Kontrola zbytků azbuky z původního ruského balíčku
    if re.search(r'[а-яА-ЯёЁ]', v):
        warnings.append(f'{k} obsahuje azbuku (ruština): {v!r}')

# release-check.py počítá doplňkové tvary: `_few` a `_many` vždy, `_one` pokud chybí `_other`
_by_shape = {k for k in flat if re.search(r'_(few|many)$', k)
             or (k.endswith('_one') and k[:-4] + '_other' not in flat)}
if (en or en_release) and _by_shape != set(extra_forms):
    odd = sorted(_by_shape ^ set(extra_forms))
    errors.append(f'doplňkové tvary byly dvěma způsoby spočítány odlišně: {odd[:5]}')

# --- Sestavení stromové struktury ---
tree = {}
for k, v in sorted(flat.items()):
    parts = k.split('.')
    cur = tree
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
        if not isinstance(cur, dict):
            errors.append(f'konflikt struktury na {k}')
            break
    else:
        cur[parts[-1]] = v

# --- Limity enginu Orca ---
nodes = [0]
maxdepth = [0]
def walk(o, path='', depth=0):
    maxdepth[0] = max(maxdepth[0], depth)
    for k, v in o.items():
        nodes[0] += 1
        if not k or len(k) > 128 or k in DANGEROUS or '.' in k or any(ord(c) <= 31 for c in k):
            errors.append(f'nebezpečný klíč {k}')
        if isinstance(v, dict):
            walk(v, f'{path}.{k}', depth + 1)
walk(tree)

raw = json.dumps(tree, ensure_ascii=False, indent=2) + '\n'
size = len(raw.encode('utf-8'))
if nodes[0] > rules.max_entries: errors.append(f'počet uzlů {nodes[0]} > {rules.max_entries}')
if maxdepth[0] > rules.max_depth: errors.append(f'hloubka {maxdepth[0]} > {rules.max_depth}')
if size > rules.max_bytes: errors.append('soubor je větší než 5 MB')

print()
for w in warnings[:15]: print('  ⚠', w)
if len(warnings) > 15: print(f'  ⚠ … dalších varování: {len(warnings)-15}')
for e in errors: print('  ✗', e)

if errors:
    print(f'\n❌ {len(errors)} chyb — soubor nebyl zapsán')
    sys.exit(1)

open(TARGET, 'w', encoding='utf-8', newline='\n').write(raw)
print(f'\n✅ zapsán {TARGET}')
print(f'   řádků: {len(flat) - len(extra_forms)} (+{len(extra_forms)} doplňkových tvarů), '
      f'uzlů: {nodes[0]}/{rules.max_entries}, hloubka: {maxdepth[0]}/{rules.max_depth}, velikost: {size} B / 5 MB')
