# Čeština pro Orca IDE

Tento repozitář je jazykový balíček, který přidává české rozhraní do Orca IDE. Obsahuje hotový český katalog a metadata, podle kterých Orca balíček rozpozná a nabídne k instalaci. Překladové skripty slouží autorům balíčku; Orca je při běhu nespouští.

![Verze balíčku 0.5.0](https://img.shields.io/badge/verze-0.5.0-blue)
![14 932 přeložených řetězců](https://img.shields.io/badge/řetězců-14%20932-brightgreen)

Katalog je ověřen proti Orca v1.4.245: obsahuje 14 932 překladatelných řádků a 72 českých doplňkových tvarů množného čísla. Audit této verze hlásí 83,93% pokrytí povolených klíčů (2 859 překladů chybí), žádné zakázané ani zastaralé klíče a žádné nadbytečné zástupné symboly.

## Co je v repozitáři

- [`locales/cs-CZ.json`](locales/cs-CZ.json) — vlastní překlad. Hierarchický JSON katalog, který Orca načítá pro locale `cs-CZ`.
- [`orca-plugin.json`](orca-plugin.json) — manifest balíčku: identifikátor, vydavatel, verze, minimální podporovaná verze Orca a cesta ke katalogu. Orca podle něj balíček instaluje.
- [`orca-marketplace.json`](orca-marketplace.json) — záznam v seznamu pluginů vydavatele; odkazuje na tento repozitář a zařazuje češtinu do kategorie jazyků.
- [`GLOSSARY.md`](GLOSSARY.md) — terminologie, překladatelská pravidla, technické poznámky a známá omezení katalogu.
- [`tools/`](tools/README.md) — dokumentace a pomocné skripty pro přípravu překladů, sestavení, audit a kontrolu před vydáním.
- [`.gitignore`](.gitignore) — vylučuje pracovní překladové podklady `.i18n-work/`, osobní `task.md` a systémový soubor `.DS_Store`.

## Jak spolu soubory souvisejí

Orca potřebuje hlavně `orca-plugin.json` a soubor uvedený v jeho `contributes.languagePacks`. V tomto projektu je to `locales/cs-CZ.json`. Marketplace soubor umožňuje najít a instalovat plugin. Glosář a obsah `tools/` jsou určeny lidem a automatizovaným agentům, kteří překlad udržují.

Katalog je velký, proto se při práci může rozdělit na menší ploché JSON bloky s klíči v tečkové notaci. Ty patří do dočasného adresáře `.i18n-work/`, který není součástí verzovaného balíčku. `tools/build.py` je sloučí do výsledného katalogu. Po dokončení práce stačí v repozitáři uchovávat hotový `locales/cs-CZ.json`; zdrojové vlny a reference lze znovu vytvořit nástrojem `tools/prepare-waves.py`.

## Kontrola překladu

Z kořenového adresáře spusťte:

```bash
python tools/audit-pack.py
```

Audit ověří, zda katalog odpovídá pravidlům Orca, porovná překladatelné klíče, hledá chybějící a zastaralé položky a kontroluje zástupné symboly jako `{{name}}`. Podrobnosti a další příkazy jsou v [`tools/README.md`](tools/README.md).

Před vytvořením vydání lze spustit také:

```bash
python tools/release-check.py
```

Tato kontrola porovnává verzi a počty v dokumentaci s manifestem a katalogem.

## Postup překladu po vydání nové Orcy

Dvojklikem spusťte **[`prepare-translation.bat`](prepare-translation.bat)**. Veškeré kroky jsou v jednom menu; není potřeba ručně zadávat cesty ani nastavovat proměnné. Potřebujete Python 3.8+ a přihlášené GitHub CLI (`gh auth login`) s přístupem k `stablyai/orca`. Menu lze otevřít také příkazem `python tools/translation-menu.py`.

| Volba | Co udělá |
|---|---|
| **1 — Kontrola aktuálnosti překladu** | Porovná český katalog s nejnovějším stabilním vydáním Orca a vypíše pokrytí, chybějící a zastaralé klíče i případné problémy. |
| **2 — Příprava na překlad** | Stáhne anglický katalog a pravidla vydání, uloží audit a vytvoří novou pracovní složku s bloky k překladu. Zapamatuje si ji jako aktivní. |
| **3 — Vypsat prompt a zkopírovat do schránky** | Zobrazí prompt s cestami k aktivním podkladům a zkopíruje jej do schránky. Stačí Ctrl+V do konverzace s agentem v tomto repozitáři. |
| **4 — Dokončení překladu** | Zkontroluje přeložené bloky, sloučí je do `locales/cs-CZ.json`, provede audit a uloží přehled změn. |
| **5 — Vybrat jinou pracovní složku** | Umožní pokračovat ve starším rozpracovaném překladu. |
| **6 — Otevřít pracovní složku** | Otevře aktivní složku v Průzkumníku. |
| **0 — Konec** | Zavře menu. |

### Běžný postup

1. Zvolte **1** pro kontrolu, co chybí.
2. Zvolte **2** pro přípravu podkladů.
3. Zvolte **3** a vložte prompt agentovi pomocí Ctrl+V. Prompt mu určí, kam uložit hotové překlady.
4. Po dokončení práce agenta zvolte **4**. Menu můžete mezitím zavřít a znovu otevřít; aktivní složku si pamatuje. Pokud máte více rozpracovaných překladů, správnou složku vyberte volbou **5**.
5. Vyzkoušejte výslednou češtinu v Orce.

Volba 4 nejprve ověří, že jsou přeloženy všechny připravené bloky, mají stejné klíče i zástupné symboly jako originály a neobsahují prázdné překlady nebo azbuku. Pokud něco chybí, sestavení se nespustí. Kontrola nenahrazuje jazykovou revizi. Sestavení a závěrečný audit používají nejnovější stabilní vydání; pokud během překladu vyjde další verze Orca, může být potřeba připravit další podklady.

### Co najdete v pracovní složce

Každá příprava vytvoří novou složku `.i18n-work/update-…/`, aby nepřepsala rozpracované překlady. Obsahuje:

- `source/` — originální anglické bloky, nejvýše 500 položek v jednom souboru.
- `en.json`, `plugin-translatable-chrome.ts` a `plugin-language-pack-artifact.ts` — katalog, povolené výjimky a pravidla ochrany i limity konkrétního vydání Orca.
- `PROMPT.txt` — prompt pro agenta, který menu umí zkopírovat do schránky.
- `POSTUP.txt` — stručný postup pro dokončení přes menu.
- `audit.txt` a `prepare-log.txt` — audit před překladem a záznam přípravy.

Agent uloží hotové překlady přímo do pracovní složky pod názvy `wave01-cs-part01.json` atd.; originály v `source/` ponechá beze změny. Po dokončení přibudou `build-log.txt`, `audit-after.txt` a `changes.diff`. U starších složek vytvořených před zavedením menu mohou být v `POSTUP.txt` ještě ruční příkazy; i tyto složky lze dokončit volbou 4. Pokud dosud není zapamatovaná aktivní složka, menu nabídne jako aktivní nejnovější připravenou složku s promptem.

Filtr přípravy vybírá chybějící hodnoty a hodnoty obsahující azbuku; změny anglického textu u již přeloženého klíče neodhaluje. Verdikt auditu `PŘIJAT (ACCEPTED)` sám o sobě nezaručuje úplné pokrytí — sledujte i počet chybějících klíčů a chyby zástupných symbolů. Zastaralé klíče projděte podle auditu; sestavení automaticky odstraňuje ty, které chybějí v obou jeho referenčních katalozích.

Menu nevytváří commit ani vydání a nemění verzi balíčku. Před vydáním aktualizujte verzi a údaje o katalogu v dokumentaci a spusťte `python tools/release-check.py`. Pracovní složka `.i18n-work/` se necommituje; výsledným překladem je `locales/cs-CZ.json`.

Samostatná příprava bez menu zůstává dostupná přes `python tools/prepare-update.py`, případně s `--release v1.4.237` pro konkrétní vydání.

## Anglické texty a chráněné klíče

525 klíčů katalogu Orca v1.4.245 zůstává v angličtině

- **525 klíčů** jsou chráněné texty pluginů a dalších komponent pro souhlas, oprávnění a důvěryhodnost; Orca je jazykovým balíčkem nepovoluje překládat. Seznam se čte z modulu enginu cílového vydání. Přepsání jediného chráněného klíče způsobí odmítnutí celého balíčku.

Vedle chráněných klíčů zatím chybí 2 859 povolených překladů; ty rovněž používají anglickou zálohu.

Seznam se zkracuje s tím, jak Orca zpřístupňuje další části katalogu k překladu. Některé hodnoty shodné s angličtinou jsou názvy, příkazy nebo jiné výrazy, u kterých je stejný zápis záměrný.

## Překladatelská pravidla

Při úpravách zachovávejte klíče, strukturu, interpunkci i zástupné symboly. Používejte termíny z glosáře. Výsledný JSON sestavte a ověřte pomocí skriptů v `tools/`; nepřidávejte do něj chráněné klíče ani texty, které daná verze Orca nezná.
