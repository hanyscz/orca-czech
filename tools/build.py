#!/usr/bin/env python3
"""Sestavuje locales/cs-CZ.json z překladových bloků a validuje podle pravidel Orca.

Spuštění z kořenového adresáře repozitáře:

    python3 tools/build.py

Vyžaduje python3 a přihlášené CLI `gh`: pravidla ochrany a originální katalog
se přebírají z nejnovějšího stabilního vydání stablyai/orca. Pracovní adresář
s překladovými bloky je `.i18n-work/` (není sledován v gitu); jinou cestu
lze nastavit proměnnou prostředí ORCA_CS_WORK. Bez bloků sestavení pouze
překontroluje stávající katalog a zapíše jej beze změn.
"""
import json, re, glob, sys, os, subprocess, base64

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = os.environ.get('ORCA_CS_WORK') or os.environ.get('ORCA_RU_WORK') or os.path.join(ROOT, '.i18n-work')
TARGET = os.path.join(ROOT, 'locales', 'cs-CZ.json')
REPO = 'stablyai/orca'
EN_PATH = 'src/renderer/src/i18n/locales/en.json'
PROT = 'auto.components.settings.'
DANGEROUS = {'__proto__', 'prototype', 'constructor'}
RAW = ['-H', 'Accept: application/vnd.github.raw+json']

# Pravidlo ochrany bereme z NEJNOVĚJŠÍHO STABILNÍHO VYDÁNÍ Orca, nikoli z větve main.
# Zkušenost z v5.1.4: allow-list z PR #12455 byl sice v main, ale ještě ne ve vydání,
# a balíček s 34 povolenými klíči engine odmítl všem uživatelům na v1.4.168.
# Balíček musí fungovat na tom, co mají uživatelé nainstalováno.
CHROME = set()
_stable = subprocess.run(['gh', 'release', 'view', '--repo', REPO, '--json', 'tagName', '--jq', '.tagName'],
                         capture_output=True, text=True, encoding='utf-8', errors='replace').stdout.strip()
if _stable:
    _r = subprocess.run(['gh', 'api',
        f'repos/{REPO}/contents/src/shared/plugins/plugin-translatable-chrome.ts?ref={_stable}',
        '--jq', '.content'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if _r.returncode == 0 and _r.stdout.strip():
        src = base64.b64decode(_r.stdout).decode('utf-8')
        CHROME = set(re.findall(r"'(auto\.components\.settings\.[^']+)'", src))
    print(f'  pravidlo ochrany: vydání {_stable}, povolených výjimek: {len(CHROME)}')

def protected(path):
    if not path.startswith(PROT):
        return False
    if path in CHROME:
        return False
    return path[len(PROT):].lower().startswith('plugin')

def fetch_catalog(ref):
    # Přímý media type: pro soubor větší než 1 MiB vrací contents API prázdný obsah bez chyby.
    rc = subprocess.run(['gh', 'api', *RAW, f'repos/{REPO}/contents/{EN_PATH}?ref={ref}'],
                        capture_output=True, text=True, encoding='utf-8', errors='replace')
    return json.loads(rc.stdout) if rc.returncode == 0 and rc.stdout and rc.stdout.strip() else {}

# Katalog main: lokální snímek v pracovním adresáři, pokud existuje, jinak čerstvý z GitHubu.
_en_snapshot = os.path.join(SCRATCH, 'en.json')
if os.path.exists(_en_snapshot):
    en = json.load(open(_en_snapshot, encoding='utf-8'))
else:
    en = fetch_catalog('main')
    if not en:
        print('  ℹ katalog main z GitHubu není dostupný (offline režim nebo gh nepřihlášeno)')

# Katalog vydání — druhý zdroj pravdy. Balíček instalují lidé s vydáním, nikoli s main.
en_release = fetch_catalog(_stable) if _stable else {}
if not en and not en_release:
    # Pokud nemáme gh ani snapshot, zkusíme pracovat lokálně s existujícím souborem
    print('  ℹ běh v offline režimu bez validace proti vzdálenému en.json')

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

# Čeština vyžaduje tvary množného čísla, které v angličtině chybí (1, 2-4, 5+).
# i18next je vyhledává pro každé volání s parametrem count: ke klíči připojí příponu tvaru:
#   - `_few` a `_many` u rodiny, kde Orca má `<báze>_one` a `<báze>_other`;
#   - `_one`, `_few` a `_many` u řetězce volaného s počtem, ale uloženého vcelku
#     (`fileOther`, `connectedHostCount_other`, `transcriptsSkipped`).
# V současném stavu enginu bez #12505 se vybírá pouze mezi _one a ostatním,
# proto musí být základní řetězec či _other formulován neutrálně („uloženo větví: {{count}}“).
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

    if len(v) > 8192:
        errors.append(f'{k} je delší než 8 192 znaků')
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
if nodes[0] > 20000: errors.append(f'počet uzlů {nodes[0]} > 20 000')
if maxdepth[0] > 16: errors.append(f'hloubka {maxdepth[0]} > 16')
if size > 5 * 1024 * 1024: errors.append('soubor je větší než 5 MB')

print()
for w in warnings[:15]: print('  ⚠', w)
if len(warnings) > 15: print(f'  ⚠ … dalších varování: {len(warnings)-15}')
for e in errors: print('  ✗', e)

if errors:
    print(f'\n❌ {len(errors)} chyb — soubor nebyl zapsán')
    sys.exit(1)

open(TARGET, 'w', encoding='utf-8').write(raw)
print(f'\n✅ zapsán {TARGET}')
print(f'   řádků: {len(flat) - len(extra_forms)} (+{len(extra_forms)} doplňkových tvarů), '
      f'uzlů: {nodes[0]}/20000, hloubka: {maxdepth[0]}/16, velikost: {size} B / 5 MB')
