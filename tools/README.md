# Nástroje

Skripty, které sestavují a kontrolují tento balíček. Orca je nenačítá: manifest nedeklaruje žádný vstupní bod a jazykový balíček obsahuje pouze data.

| Skript | Co dělá |
|---|---|
| [`translation-menu.py`](translation-menu.py) | Interaktivní menu: kontrola aktuálnosti, příprava, prompt do schránky, dokončení překladu a výběr pracovní složky. Spouští se také přes kořenový `prepare-translation.bat`. |
| [`prepare-update.py`](prepare-update.py) | Jedním příkazem stáhne katalog a pravidla konkrétního vydání, uloží audit a vytvoří novou pracovní složku s bloky, promptem pro agenta a pokyny po překladu. |
| [`audit-pack.py`](audit-pack.py) | Audituje libovolný jazykový balíček Orca vůči konkrétnímu vydání Orca: zda engine katalog přijme, pokrytí, nepřeložené a zastaralé klíče, posun zástupných symbolů (placeholders). |
| [`prepare-waves.py`](prepare-waves.py) | Převede anglický katalog `en.json` na dílčí ploché překladové bloky (podle vln či po dávkách), odfiltruje chráněné klíče a připraví podklady pro překlad. |
| [`build.py`](build.py) | Sestavuje `locales/cs-CZ.json` z bloků překladu a ověřuje jej podle pravidel nejnovějšího stabilního vydání Orca. |
| [`engine_rules.py`](engine_rules.py) | Sdílené načítání pravidel vydání: nové i původní cesty, chráněné komponenty, allow-list a limity. |
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

Dokončení překladu (volba 4) nejprve ověří bloky **po jednotlivých klíčích**: stejnou sadu klíčů, neprázdné překlady, žádnou azbuku a přesně tytéž zástupné symboly `{{…}}` jako v anglické hodnotě téhož klíče. Rozdíl u jediného klíče sestavení zastaví — i u tvaru `_one`, kde sesterský `_other` `{{count}}` má; viz pravidla pro řetězce s počítadlem v [glosáři](../GLOSSARY.md#známá-omezení).

## Audit balíčku

```bash
python3 tools/audit-pack.py                      # tento balíček, nejnovější stabilní vydání Orca
python3 tools/audit-pack.py --release v1.4.224   # konkrétní vydání
python3 tools/audit-pack.py cesta/k/jinemu-packu # libovolný adresář s orca-plugin.json
python3 tools/audit-pack.py --list               # všechny chybějící a zastaralé klíče
```

```
Orca v1.4.245: 18316 klíčů v katalogu, 17791 lze přeložit (525 chráněných, 34 povolených výjimek, 8 chráněných komponent).

hanyscz.czech v0.5.0 — cs-CZ, locales/cs-CZ.json, enginy >=1.4.243
  verdikt enginu: PŘIJAT (ACCEPTED)
  velikost: 17047/50000 položek, hloubka 12/16, přibližně 1,1 MB
  pokrytí: 14932/17791 = 83.93 %; 2859 chybí
  zastaralé klíče nedefinované ve vydání: 0
  doplňkové tvary množného čísla: 72
  zástupné symboly, které anglický originál nemá: 0
```

Návratový kód (exit status) je 1, pokud by engine balíček odmítl, takže skript může sloužit jako kontrolní brána (gate) před vydáním.

Verdikt zrcadlí kontroly, které Orca provádí nad jazykovým balíčkem při instalaci:

- **Chráněné komponenty.** `PROTECTED_TRANSLATION_COMPONENTS` v modulu enginu chrání celé oblasti bez výjimek; v1.4.245 jich má osm. Neznámá ochranná pravidla nebo chybějící modul kontrolu zastaví.
- **Chráněné cesty (Protected paths).** Vše pod `auto.components.settings.plugin*` jsou texty souhlasu a důvěryhodnosti, s výjimkou cest uvedených v `plugin-translatable-chrome.ts`. Stačí jeden chráněný klíč a Orca bez jakékoliv zprávy odmítne celý katalog; rozhraní pak jednoduše zůstane v angličtině.
- **Limity.** Počet položek a hloubka se čtou z modulu enginu cílového vydání. Orca v1.4.245 povoluje 50 000 položek, starší podporovaná vydání 20 000. Hloubka je 16, délka hodnoty 8 192 znaků, velikost souboru 5 MB. Před překročením staršího limitu je nutné zvýšit `engines.orca` a ověřit balíček také vůči jeho minimálnímu vydání.
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

Základem je verzovaný katalog. Na něj se aplikují překladové bloky: ploché soubory JSON pojmenované `wave*-cs-part*.json` v pracovním adresáři `.i18n-work/` (není sledován gitem; jinou cestu lze nastavit proměnnou `ORCA_CS_WORK`), kde každý mapuje tečkový klíč na svůj překlad. I bez bloků sestavení znovu ověří katalog a odstraní zaniklé či nově chráněné klíče.

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

## Zdrojová pravidla a offline kontrola

Všechny nástroje používají `engine_rules.py`. Allow-list hledá nejprve v `src/shared/plugins/languages/plugin-translatable-chrome.ts`, poté na původní cestě `src/shared/plugins/plugin-translatable-chrome.ts`. Modul enginu hledá v `src/shared/plugins/artifacts/plugin-language-pack-artifact.ts` a `src/shared/plugins/plugin-language-pack-artifact.ts`. Na další cestu přejde pouze při 404; chyby přihlášení nebo připojení se nesmějí vydávat za prázdná pravidla.

`prepare-update.py` ukládá oba moduly do pracovní složky a předává je auditu i přípravě vln. Audit odmítnutého starého balíčku se uloží a příprava opravy pokračuje; chyba samotného auditu ji zastaví.

```bash
python tools/audit-pack.py --en en.json --chrome plugin-translatable-chrome.ts --artifact plugin-language-pack-artifact.ts
python tools/prepare-waves.py --en en.json --chrome plugin-translatable-chrome.ts --artifact plugin-language-pack-artifact.ts
```

Offline kontrola vyžaduje všechny tři soubory ze stejného vydání. Sestavení vždy stahuje čerstvý `main` i aktuální stabilní vydání a při neúplných podkladech nic nezapíše. `python tools/build.py --help` pouze vypíše nápovědu; neznámé argumenty jsou chyba.

Od Orca v1.4.243 fungují tvary podle českého locale: `_one` pro 1, `_few` pro celá čísla 2–4, `_other` pro ostatní celá čísla a `_many` pro necelá čísla. Kontrola před tagem vyžaduje každé jednotlivé očekávané místo s verzí i počtem; změna formulace tedy nesmí údaj tiše vyřadit z kontroly.

Regresní kontroly: `python tools/test-engine-rules.py` a `python tools/test-translation-menu.py`.
