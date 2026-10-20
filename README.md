# Čeština pro Orca IDE

Tento repozitář je jazykový balíček, který přidává české rozhraní do Orca IDE. Obsahuje hotový český katalog a metadata, podle kterých Orca balíček rozpozná a nabídne k instalaci. Překladové skripty slouží autorům balíčku; Orca je při běhu nespouští.

![Verze balíčku 0.1.0](https://img.shields.io/badge/verze-0.1.0-blue)
![16 296 přeložených řetězců](https://img.shields.io/badge/řetězců-16%20296-brightgreen)

Katalog vychází z Orca v1.4.232: obsahuje 16 296 překladatelných řádků a 159 českých doplňkových tvarů množného čísla. Audit této verze hlásí 100% pokrytí klíčů, které jazykový balíček smí překládat.

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

## Anglické texty a chráněné klíče

180 klíčů katalogu Orca v1.4.232 zůstává v angličtině

- **180 klíčů** jsou chráněné texty pluginů pro souhlas a důvěryhodnost; Orca je jazykovým balíčkem nepovoluje překládat.

Seznam se zkracuje s tím, jak Orca zpřístupňuje další části katalogu k překladu. Některé hodnoty shodné s angličtinou jsou názvy, příkazy nebo jiné výrazy, u kterých je stejný zápis záměrný.

## Překladatelská pravidla

Při úpravách zachovávejte klíče, strukturu, interpunkci i zástupné symboly. Používejte termíny z glosáře. Výsledný JSON sestavte a ověřte pomocí skriptů v `tools/`; nepřidávejte do něj chráněné klíče ani texty, které daná verze Orca nezná.
