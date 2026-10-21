# Nástroje

Skripty, které sestavují a kontrolují tento balíček. Orca je nenačítá: manifest nedeklaruje žádný vstupní bod a jazykový balíček obsahuje pouze data.

| Skript | Co dělá |
|---|---|
| [`translation-menu.py`](translation-menu.py) | Interaktivní menu: kontrola aktuálnosti, příprava, prompt do schránky, dokončení překladu a výběr pracovní složky. Spouští se také přes kořenový `prepare-translation.bat`. |
| [`prepare-update.py`](prepare-update.py) | Jedním příkazem stáhne katalog a pravidla konkrétního vydání, uloží audit a vytvoří novou pracovní složku s bloky, promptem pro agenta a pokyny po překladu. |
| [`audit-pack.py`](audit-pack.py) | Audituje libovolný jazykový balíček Orca vůči konkrétnímu vydání Orca: zda engine katalog přijme, pokrytí, nepřeložené a zastaralé klíče, posun zástupných symbolů (placeholders). |
| [`prepare-waves.py`](prepare-waves.py) | Převede anglický katalog `en.json` na dílčí ploché překladové bloky (podle vln či po dávkách), odfiltruje chráněné klíče a připraví podklady pro překlad. |
| [`build.py`](build.py) | Sestavuje `locales/cs-CZ.json` z bloků překladu a ověřuje jej podle pravidel nejnovějšího stabilního vydání Orca. |
| [`release-check.py`](release-check.py) | Kontroluje shodu verze a všech počtů mezi manifestem, oběma soubory README a glosářem. Spouští se před vytvořením tagu. |

Vyžadují `python3` verze 3.8 nebo novější a autentizované CLI [`gh`](https://cli.github.com/). Spouštějte je z kořenového adresáře repozitáře.

Všechny skripty `audit-pack.py`, `prepare-waves.py`, `build.py` a `release-check.py` mají výstupy i komentáře v češtině, stejně jako glosář: představují vlastní pracovní postup (workflow) tohoto českého balíčku.

## Příprava aktualizace překladu

Pro celý postup spusťte `prepare-translation.bat` v kořeni repozitáře nebo `python tools/translation-menu.py`. Menu si pamatuje pracovní složku, zkopíruje prompt do schránky a po překladu nastaví prostředí, sestaví katalog a provede audit. Ruční příkazy pro jednotlivé kroky zůstávají dostupné:

```powershell
python tools/prepare-update.py                    # nejnovější stabilní vydání
python tools/prepare-update.py --release v1.4.237 # konkrétní vydání
```

Výstup patří do nové složky `.i18n-work/update-…/`. Agentovi předejte tamní `PROMPT.txt`; po překladu zvolte v menu dokončení. Zdrojové bloky zůstávají v `source/`, hotové překlady se ukládají přímo do pracovní složky. Katalog `locales/cs-CZ.json` se při přípravě nemění. Podrobný postup je v hlavním [README](../README.md#postup-překladu-po-vydání-nové-orcy).

## Audit balíčku

```bash
python3 tools/audit-pack.py                      # tento balíček, nejnovější stabilní vydání Orca
python3 tools/audit-pack.py --release v1.4.224   # konkrétní vydání
python3 tools/audit-pack.py cesta/k/jinemu-packu # libovolný adresář s orca-plugin.json
python3 tools/audit-pack.py --list               # všechny chybějící a zastaralé klíče
```

```
Orca v1.4.232: 16476 catalog keys, 16296 a pack may translate (180 protected, 0 over 8192 characters, 34 allow-listed).

hanys.czech v0.1.0 — cs-CZ, locales/cs-CZ.json, engines >=1.4.169
  engine verdict: ACCEPTED
  size: 18485/20000 entries, depth 12/16, 1191198 bytes
  coverage: 16296/16296 = 100.00 % of what a pack may translate; 0 missing
  stale keys the release does not define: 0
  extra plural forms: 159 — `_few` and `_many` stay unreachable until stablyai/orca#12505
  identical to English: 1320
  placeholders the English source does not have: 0
```

Návratový kód (exit status) je 1, pokud by engine balíček odmítl, takže skript může sloužit jako kontrolní brána (gate) před vydáním.

Verdikt zrcadlí kontroly, které Orca provádí nad jazykovým balíčkem při instalaci:

- **Chráněné cesty (Protected paths).** Vše pod `auto.components.settings.plugin*` jsou texty souhlasu a důvěryhodnosti, s výjimkou cest uvedených v `plugin-translatable-chrome.ts`. Stačí jeden chráněný klíč a Orca bez jakékoliv zprávy odmítne celý katalog; rozhraní pak jednoduše zůstane v angličtině.
- **Limity.** 20 000 položek, hloubka zanoření 16, 8 192 znaků na hodnotu, 5 MB na soubor.
- **Nebezpečné klíče (Unsafe keys).** Prázdné klíče, klíče s tečkou nebo řídicím znakem, `__proto__`, `prototype`, `constructor`.

### Proč se pravidla načítají z vydání (release), nikoli z větve `main`

Balíček se instaluje do konkrétního vydání aplikace. Pravidlo, které se dostalo teprve do větve `main`, zatím pro nikoho neplatí.

U balíčku v5.1.4 se na to přišlo tvrdou cestou: vydal 34 řetězců, které seznam povolených výjimek (allow-list) právě zpřístupnil v `main`, ale aktuální vydání je stále chránilo, a jazyk se všem uživatelům na tomto vydání přestal načítat. Ze stejného důvodu je nastaveno `engines.orca` na `>=1.4.169`, což je první vydání, které seznam povolených výjimek obsahuje.

## Příprava překladových vln a dílčích bloků

```bash
python3 tools/prepare-waves.py                    # připraví bloky po 500 klíčích do .i18n-work/source/
python3 tools/prepare-waves.py --by-domain        # rozdělí katalog logicky podle oblastí rozhraní
python3 tools/prepare-waves.py --chunk-size 1000  # nastavení velikosti dávky na 1 000 klíčů
python3 tools/prepare-waves.py --untranslated     # vygeneruje pouze klíče, které v cs-CZ.json chybí nebo mají azbuku
python3 tools/prepare-waves.py --with-ref         # vytvoří i srovnávací soubory (.ref.json s EN originálem i RU referencí)
```

Skript provede:
- Zploštění hierarchického stromu `en.json` do tečkových cest (`menu.file`, `editor.tabs...`).
- Odfiltrování všech chráněných klíčů (`auto.components.settings.plugin*` mimo allow-list) a nepřípustných délek.
- Rozdělení do přehledných dávek vhodných pro překlad (např. v LLM či překladači).
- Přeložené soubory se ukládají jako `.i18n-work/wave*-cs-part*.json`.

## Sestavení (Building)

```bash
python3 tools/build.py
```

Základem je verzovaný katalog. Na něj se aplikují překladové bloky: ploché soubory JSON pojmenované `wave*-cs-part*.json` v pracovním adresáři `.i18n-work/` (není sledován gitem; jinou cestu lze nastavit proměnnou `ORCA_CS_WORK`), kde každý mapuje tečkový klíč na svůj překlad. Bez bloků sestavení pouze znovu zvaliduje katalog a zapíše jej beze změn zpět.

Sestavení následně:

- odstraní klíč, který nedefinuje ani nejnovější vydání, ani větev `main`, a selže, pokud takový klíč pochází z překladového bloku;
- selže při výskytu chráněného klíče, zástupného symbolu (placeholderu), který anglický originál neobsahuje, nebo při překročení jakéhokoli limitu enginu;
- přijme tvar množného čísla, který v angličtině chybí (`_few` a `_many` pro skupinu množného čísla; `_one`, `_few` a `_many` u řetězce, který Orca volá s počtem), pouze pokud je řetězec, který rozšiřuje, stále aktivní v katalogu Orca a přeložený v balíčku;
- varuje před hodnotou bez české diakritiky (či latinky), nebo před vynechaným zástupným symbolem (což bývá obvykle anglické množné číslo `s`).

Při selhání jakékoli kontroly se nic nezapíše.

## Před vytvořením tagu (Before tagging)

```bash
python3 tools/release-check.py
```

Publikovaný tag se již nikdy nemění, proto jedinou ochranou proti zastaralým údajům je kontrola před otagováním. Skript porovná verzi z manifestu a počet řetězců v katalogu se všemi místy v dokumentaci, kde jsou uvedeny, a zkontroluje, zda celkový součet „ponechaných v angličtině“ odpovídá součtu jednotlivých položek svého rozpisu.
