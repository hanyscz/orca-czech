# Glosář lokalizace Orca (cs-CZ)

Pracovní dokument pro překlad `src/renderer/src/i18n/locales/en.json` (16 476 klíčů ve vydání
Orca v1.4.232; sestavení se ověřuje vůči sjednocení větve `main` a posledního vydání, viz „Známá omezení“).
Aktuální k `v0.1.0` (20. října 2026): přeloženo 16 296 řádků (pokrytí všech překladatelných klíčů) a 159 doplňkových tvarů množného čísla.
Ve vydání Orca v1.4.230 činil anglický zbytek — 316
(180 chráněných `settings.plugin*`, 3 CSS, 112 osiřelých klíčů sdílení dovedností, 9 osiřelých
klíčů vzdáleného prohlížeče z #15448, 1 nepoužívaný klíč automatizací z #16532 a 11 řetězců
shodných s originálem). Sdílení dovedností (`skills.*`, `settings.shareSkills.*`) přeloženo
ve v5.1.61: 262 řádků — obrazovka se dostala k uživatelům v Orca v1.4.187 spolu s re-landem #14934.
Blok kanálů sestavení (#15465) vyšel tamtéž a je zahrnut v balíčku: tři varování byla přepsána
pro běžná sestavení Windows, přidány `devChannelUnsupported*`, `downloadInstaller`
a `manualInstallHint`.
Katalog Orca roste o desítky řádků denně, proto se balíček přegenerovává podle
aktualizací upstreamu — viz „Známá omezení“.

## Obecná pravidla

1. **Neosobní tvary a přirozený tón.** „Vyberte jazyk“, „Nepodařilo se připojit“, nikoli „Můžete vybrat…“ nebo „Můžeš…“.
2. **Zástupné symboly (placeholders) se přenášejí doslovně:** `{{value0}}`, `{{path}}`, `{{hostName}}` — nepřekládat, neměnit velikost písmen, nepřemisťovat bez nutnosti; sada tokenů musí odpovídat anglickému originálu **u každého klíče zvlášť** (viz „Známá omezení“). Týká se 1 013 řádků.
   Jednoduché složené závorky jsou také zástupné symboly enginu Orca, nikoli překlep: `{basePrompt}`, `{prompt}`, `{count}`.
3. **Hybridní terminologie:** prvky rozhraní překládáme, příkazy gitu/CLI a názvy produktů ponecháváme v latince.
4. **Pravopis a diakritika:** důsledné dodržování spisovné češtiny včetně všech háčků a čárek.
5. **Výpustka (tři tečky) — znak `…`**, nikoli tři tečky. Uvozovky — české „dole a nahoře“, vnořené ‚jednoduché‘. Klíče-fragmenty s hodnotou `"` ověřujeme podle pořadí v JSX, nikoli v `en.json`: v katalogu je koncová uvozovka nezřídka zapsána dříve než počáteční (`SmartWorkspaceNameField`, `MobileEmulatorExamples`). Pokud jeden klíč obsluhuje obě strany, dáváme rovnou uvozovku `"` — tak tomu bylo u `GrabConfirmationSheet.eb98a0971a` do Orca v1.4.223, kde se objevila otevírací dvojice `accessibleNameOpenQuote`.
   Výjimka: uvnitř příkladů kódu, příkazů, URL a cest zůstává výpustka v ASCII —
   `orca://pair?code=...`, jinak řetězec přestává fungovat jako vzor ke zkopírování.
6. **Pomlčka — dlouhá „—“** s mezerami; spojovník ve složených výrazech je krátký bez mezer: „SSH-hostitel“, „QR-kód“.
7. **Řetězce začínající velkým písmenem (tlačítka, položky nabídek) si zachovávají velké písmeno.** Anglické titulky v Title Case překládáme běžnou větou: „Open Worktree Palette“ → „Otevřít paletu pracovních stromů“.
8. **Nepřekládáme:** CSS řetězce (247 ks) a `auto.components.settings.` + modul začínající na `plugin` — **predikát `/^plugin/i` nerozlišuje velikost písmen**, proto je zakázáno `settings.pluginError`, `settings.PluginSettingsRow` i `settings.PluginsSettingsSection` (214 ks). Jeden takový klíč způsobí odmítnutí celého balíčku.
9. **Interní identifikátory zůstávají v latince.** Hodnota může vypadat jako běžné slovo, ale vkládá se do `data-*`, `variant`, klíče stavu nebo cesty: `error`, `idle`, `loading`, `sending`, `working`, `destructive`, `default`, `compact`, `sheet`, `page`, `spinner`, `open`, `closed`, `resolved`, `paired`, `intro`, `pr`, `thread`, `comment`, `notes`, `pr-view`, `not-configured`, `not-authenticated`, `create_pr`, `MergeRequest`, `PULL_REQUEST`, `DRAFT_ISSUE`, `TABLE_LAYOUT`, `darwin`, `killAll`, a také kebab-case identifikátory tras (`settings`, `tasks`, `skills`, `automations`). Vodítko: řetězec se uživateli nezobrazuje jako věta a nemá velké počáteční písmeno tam, kde by v angličtině bylo.
10. **Anglické přípony množného čísla odstraňujeme.** `file{{value1}}`, `session{{value1}}`, `workspace{{value1}}` — `{{value1}}` dosazuje `s`. V češtině se plurál tvoří jinak, proto se zástupný symbol vypouští: „Dokončených relací: {{value0}}“. `build.py` na každý takový případ upozorňuje — varování je očekávané. Vypustit však lze pouze zástupný symbol připojený k anglickému slovu: samostatně stojící `{{value3}}` jsou data. V `ChecksPanel.f273f2271c` se takto ztratilo počítadlo selhání: #12150 vložil do řetězce nové číslo, překlad zůstal ze starého textu a varování zaniklo mezi očekávanými (`build.py` vypisuje jen prvních 15).
11. **Ukázková data prezentací** (přehled funkcí, snímky Orca Mobile): lidsky srozumitelné věty překládáme („Běží 12 testů“, „přepracovat tok ověřování“), zatímco názvy větví, souborů, testů, příkazy a výstupy nástrojů ponecháváme v původním stavu (`feat/mobile-page`, `login.spec.ts`, `pnpm playwright test`, `Read`, `Grep`, `Bash`).
12. **Názvy sekcí rozhraní v nápovědách** formátujeme v uvozovkách se šipkou: „Nastavení → Prohlížeč“, „Nastavení › Mobilní emulátor“. Sekce externích služeb ponecháváme v jazyce originálu: `Account → Security & Access` v Linear, `Personal Access Tokens` v Jira.

## Entity Orca

Čísla v poznámkách uvádějí, kolik řádků katalogu vydání Orca v1.4.224 obsahuje dané slovo v anglickém textu.

| Anglicky | Česky | Poznámka |
|---|---|---|
| workspace | pracovní prostor | klíčový pojem, 658 řádků |
| floating workspace | plovoucí pracovní prostor |  |
| active workspace | aktivní pracovní prostor |  |
| worktree | pracovní strom | 282 řádků; v příkazech `git worktree` — latinkou |
| worktree source | zdroj | odkud Orca načítá cizí pracovní stromy (`.claude/worktrees/*`, vlastní složka); „Sources“ → „Zdroje“. Neplést se `source control` (správa verzí) a `Source` = „Zdrojový kód“ |
| project | projekt |  |
| host | hostitel |  |
| execution host | hostitel běhu |  |
| remote host | vzdálený hostitel |  |
| SSH host | SSH hostitel |  |
| cloud VM | cloudový virtuální stroj (VM) |  |
| agent | agent |  |
| coding agent | programovací agent |  |
| AI agent | AI agent |  |
| session | relace | 314 řádků; „sezení“ nepoužíváme — pojem je sjednocen na „relace“ |
| agent session | relace agenta |  |
| orchestration | orchestrace |  |
| coordinator agent | koordinační agent |  |
| child workspace | podřízený pracovní prostor |  |
| parent worktree (`ComposerParentWorktreePicker`) | nadřazený pracovní strom | ([#15420](https://github.com/stablyai/orca/pull/15420)) výběr v rozšířeném nastavení vytváření pracovního prostoru: vnoří nový prostor do vybraného v postranním panelu, základní větev nemění. „No parent“ → „Bez nadřazeného“; toast o chybějícím nadřazeném prvku — „Pracovní prostor byl vytvořen bez vnoření do «{{value0}}»“ podle vzoru „Pracovní prostor byl vytvořen, ale…“ |
| handoff | předání práce | sloveso — „předat“ |
| nested worker depth (`OrchestrationPane.nestedWorkerDepth*`) | hloubka vnoření vykonavatelů (workerů) | ([#16669](https://github.com/stablyai/orca/pull/16669)) číselné pole v nastavení orchestrace — kolik generací vykonavatelů může spouštět vlastní vykonavatele. `worker` → „vykonavatel / worker“ a `dispatch` → „rozdělení / přidělení“ — podle klíčových slov hledání téhož panelu (`orchestration.search.741dfc03fa` / `eee028ae14`), proto „a coordinator dispatches workers“ → „koordinační agent rozděluje úkoly mezi vykonavatele“; „worker“ v balíčku zůstává pouze pro test-runnery (`WorkbenchAnimatedVisual`) |
| feature wall | přehled funkcí | interní název obrazovky (zeď funkcí) |
| workflow | pracovní postup / workflow | v přehledu funkcí — „pracovní postup“; `workflow run` v GitHub Actions — „spuštění workflow“ |
| onboarding | seznámení / úvodní průvodce | „Skip onboarding?“ → „Přeskočit úvodního průvodce?“ |
| tour | prohlídka |  |
| checklist | kontrolní seznam (checklist) |  |
| milestone | milník |  |
| tip | tip |  |
| pet | mazlíček | jména mazlíčků (Gremlin, Claudino) nepřekládáme |
| task | úkol | od [#15170](https://github.com/stablyai/orca/pull/15170) stojí vedle `issue` v popiscích palety Cmd+J (`matchLabel.task` — přiřazená pracovní položka Linear/Jira, `matchLabel.issue` — issue repozitáře). Shoda překladů je přijata: obě návěští označují identifikátor, který sám rozlišuje zdroj (`ENG-42` proti `#17`), a rozlišovat je slovy by vedlo k neohrabaným formulacím jako „pracovní položka“ |
| issue | úkol / issue | Linear / Jira / GitHub |
| skill | dovednost | 290 řádků |
| skill bundle | balíček dovedností | několik dovedností pod jedním odkazem; `bundle` v jiných kontextech (mazlíčci, protokoly) také „balíček“ |
| share (dovednosti) | sdílení / publikování | `Share skills` → „Publikovat dovednosti“, `Unshare` → „Zrušit sdílení“, `Shared links` → „Sdílené odkazy“. „Sdílet“ se používá podle kontextu, u publikace artefaktů též „Publikovat jako artefakt“ |
| immutable version | neměnná verze | verze balíčku, kterou po publikování nelze přepsat |
| revoke (odkaz) | odvolat | podle vzoru `Revoke access` → „Odvolat přístup“ |
| runnable / executable / binary file | spustitelný / spustitelný (program) / binární soubor | štítky souborů v kontrolním seznamu dovednosti; stojí vedle sebe, proto se překládají třemi různými výrazy |
| managed install | instalace přes Orca | dovednost nainstalovaná a sledovaná aplikací Orca, na rozdíl od ručně vložené složky |
| This share is unavailable / Enter an Orca skill share link (`skills.install.*`) | Toto sdílení není dostupné… / Zadejte odkaz na sdílenou dovednost Orca. | ([#16682](https://github.com/stablyai/orca/pull/16682)) chyby formulářů instalace dovednosti a změny verze; `share` zde znamená publikovanou dovednost. `Installation failed before Orca could verify…` → „Instalace byla přerušena dříve, než Orca stihla ověřit…“: Orca je v balíčku rodu ženského („Orca nemohla“); `The destination had already finished this installation` → „V cílovém umístění již tato instalace proběhla“; `managed installs` → „dovednosti nainstalované přes Orca“ |
| private bytes / committed / commit limit / paged out (`resource.memory.metric.*`) | privátní bajty / vyhrazená paměť / limit vyhrazené paměti / odloženo do stránkovacího souboru | ([#16589](https://github.com/stablyai/orca/pull/16589)) nápovědy k řádkům paměti ve Windows ve Správci prostředků: terminologie českých Windows (Správce úloh „Vyhrazeno“, Sledování prostředků „Privátní (kB)“, „Pracovní sada“). Tímtéž PR byl přepsán text `workingSetDescription` pod původním klíčem |
| automation | automatizace |  |
| automation destination | hostitel automatizace / cíl automatizace | toasty uložení formuláře ([#16552](https://github.com/stablyai/orca/pull/16552)): „Vybraný hostitel automatizace není připraven. Znovu jej připojte a zkuste to znovu“, „Vyberte projekt patřící vybranému hostiteli automatizace“. `destination` zde představuje položku vybranou v rozbalovacím seznamu „Vyberte hostitele automatizace“ (`AutomationProjectCombobox.chooseHost`) |
| authority (úložiště automatizací) | {authority} — nepřekládá se, popisek „Ukládání a plánování: {authority}.“ | ([#16532](https://github.com/stablyai/orca/pull/16532)) pod výběrem „Hostitel“ ve formuláři automatizace; `authority` označuje entitu, která ukládá záznam a řídí plánování (`Local Mac` nebo server), doplňuje se latinkou bez skloňování |
| View only (odznak hostitele) | Pouze pro prohlížení | ([#16532](https://github.com/stablyai/orca/pull/16532)) hostitel, ze kterého nelze automatizace upravovat ani spouštět; záměrně se liší od `Read-only` → „Jen pro čtení“ (`AutomationsPage.e059042585`) — oba odznaky existují na téže obrazovce |
| Update the Orca server on {hosts} (`createDestination.updateRequired`) | Aktualizujte server Orca na {hosts}, abyste zde mohli ukládat automatizace. | ([#16665](https://github.com/stablyai/orca/pull/16665), sloveso „store“ od [#16823](https://github.com/stablyai/orca/pull/16823)) popisek pod výběrem „Hostitel“, když je část nabízených hostitelů zakázána: jejich server Orca je starší než zavedení dělení automatizací podle hostitelů. `{hosts}` představuje názvy hostitelů oddělené čárkami v latince |
| move (automatizace mezi hostiteli) | přesun: „Automatizace byla přesunuta na {host}.“ | ([#16823](https://github.com/stablyai/orca/pull/16823)) úprava umožňuje změnit hostitele v rámci jedné autority; výběr formuláře je nyní „Host“ → „Hostitel“ při vytváření i úpravách. Varování `createDestination.move`: „Uložení vytvoří tuto automatizaci na {host} a odstraní originál včetně historie spuštění“ |
| Run history is unavailable from this host. This does not mean the automation failed or has no runs. (`AutomationRunHistory.historyUnavailable`) | Historie spuštění není z tohoto hostitele dostupná. To neznamená, že automatizace selhala nebo nebyla nikdy spuštěna. | ([#17284](https://github.com/stablyai/orca/pull/17284)) text pod prázdnou historií spuštění, když ji hostitel neposkytuje; druhá věta vyvrací mylný dojem „0 spuštění“: nedostupnost historie značí nekompatibilitu hostitele, nikoli selhání automatizace |
| Orca on this host needs an update before you can view run history or manage this automation. Scheduled runs may still continue on the host. (`capturedOwner.unfenced`) | Chcete-li zobrazit historii spuštění a spravovat tuto automatizaci, aktualizujte aplikaci Orca na tomto hostiteli. Naplánovaná spuštění na hostiteli mohou přesto pokračovat. | ([#17284](https://github.com/stablyai/orca/pull/17284)) blok akcí nad automatizací, jejíž hostitel neumí ohraničit (`fence`) vlastníka; vedle tlačítko `Update server` → „Aktualizovat server“ |
| Unreachable / Unavailable (odznaky hostitele) | Není spojení / Nedostupný | dvě nezávislé osy stavu hostitele automatizací: `authority.unavailable` — k úložišti se nelze připojit („Není spojení“), `execution.unavailable` — spouštěcí hostitel je odstraněn („Nedostupný“). Další popisky: `Up to date` → „Aktuální“, `Not refreshed` → „Neobnoveno“, `Connection unknown` → „Stav připojení neznámý“ |
| this host (`emptyState.unknownHost`) | tento hostitel | záložní popisek, když vybraný hostitel nemá záznam v katalogu; doplňuje se do „Na hostiteli {{hostLabel}} nejsou žádné automatizace“ apod. |
| {{times}} times (historie spuštění) | Opakování: {{times}} | řádek sbaleného běhu za několika shodnými výsledky; s datem — „Opakování: {{times}}, poslední — {{date}}“. Tvar bez nutnosti skloňování počtu, viz „Známá omezení“ |
| weekday (pole cronu) | den v týdnu | nadpis pátého pole cronu v `AutomationCustomCronPanel`; `Day` v téže řadě — „Den“ podle vzoru `AutomationSchedulePicker` |
| plugin | plugin |  |
| profile | profil |  |
| provider | poskytovatel |  |
| runtime | běhové prostředí |  |
| emulator | emulátor |  |
| Orca CLI, Orca Server, Orca Mobile | bez překladu | názvy produktů |
| Computer Use | Computer Use | název funkce, nepřekládáme |
| orca.yaml | orca.yaml |  |
| Caffeinate: On / Agent / Off | Zap. / Agent / Vyp. | režim `Agent` se do #13751 jmenoval `Auto`; klíč zůstal `.auto`, překládáme podle současného textu. Od [#14775](https://github.com/stablyai/orca/pull/14775) bere čip ve stavovém řádku popisky režimů i záhlaví z nastavení (`AgentAwakeSetting.*`), slovo `Caffeinate` z rozhraní zmizelo |
| external worktrees | externí pracovní stromy | vytvořené mimo Orca; nastavení viditelnosti v „Nastavení“ a v `RepositoryPane`. Neplést s `Non-Orca worktrees` = „Pracovní stromy mimo Orca“ |
| cleanup tier | úroveň vyčištění | nakolik je bezpečné odstranit pracovní prostor: `Ready` / `Needs review` / `Protected` → „Připraveno“ / „K revizi“ / „Chráněno“. Sloupec řazení se jmenuje `Safety` = „Bezpečnost“ |
| prunable | lze prořezat (prune) | příznak `git worktree list`: strom je registrován, ale `git worktree prune` jej odstraní. `prune` je příkaz gitu, zůstává latinkou |
| unlisted link | neveřejný odkaz | odkaz sdílení dovednosti: neindexuje se a není nikde uveden, samotný odkaz je vstupenkou. Podle vzoru `Unlisted toggles` → „Neveřejné přepínače“ |
| quick views (mapa agentů) | rychlé filtry | předvolby panelu správy mapy (`Everything`, `Needs me`, `Stuck`…), nikoli režimy zobrazení |
| artifact | artefakt | soubor HTML nebo Markdown publikovaný přes veřejný odkaz |
| Share as artifact | Publikovat jako artefakt | položka nabídky souboru; „share“ zde znamená publikaci, nikoli běžné sdílení |
| public link | veřejný odkaz |  |
| Generate link (`ArtifactPublishButton.sharePublicLink`) | Vytvořit odkaz | tlačítko publikování artefaktu; do [#17037](https://github.com/stablyai/orca/pull/17037) se jmenovalo `Share public link` → „Sdílet veřejný odkaz“. Podle vzoru `Generate Access Link` → „Vytvořit přístupový odkaz“: `generate` pro odkaz překládáme jako „vytvořit“, „vygenerovat“ ponecháváme pro texty generované AI a QR kódy |

## Git a správa verzí

| Anglicky | Česky | Poznámka |
|---|---|---|
| repository / repo | repozitář |  |
| branch | větev |  |
| base branch | výchozí větev |  |
| commits ahead of / behind {{ref}} | Commitů napřed / pozadu oproti {{ref}}: {{count}} | nápovědy počítadel `↑` / `↓` na řádku základny porovnání (`branch-context-stats.ts`, [#16358](https://github.com/stablyai/orca/pull/16358)); jednotné číslo — „O 1 commit napřed před {{ref}}“ / „O 1 commit pozadu za {{ref}}“. Tvar bez nutnosti skloňování počtu, viz „Známá omezení“ |
| files changed vs {{ref}} | Změněných souborů oproti {{ref}}: {{count}} | nápověda počítadla v záhlaví „Potvrzeno ve větvi“ (`branch-section.tsx`, #16358); jednotné číslo — „1 soubor změněn oproti {{ref}}“; `vs` zde znamená „oproti“, nikoli „proti“ |
| commit | commit |  |
| commit message | zpráva commitu |  |
| merge | sloučení / sloučit | „Sloučit pull request“, „Konflikt při sloučení“ |
| merge conflict | konflikt při sloučení |  |
| pull request | pull request | 110 řádků; zkratku PR nepřekládáme |
| merge request | merge request | GitLab; zkratky PR a MR nepřekládáme |
| PRs / MRs (záložky stránky úkolů) | Pull requesty / Merge requesty | popisky přepínače seznamu vedle „Úkoly“ a „Moje úkoly“ ([#15163](https://github.com/stablyai/orca/pull/15163)) — rozepisujeme; zkratky zůstávají pouze v odznacích `PR #12` / `MR !12` |
| GitLab MR link (`WorktreeMetaDialog.gitlabMR` / `gitlabPlaceholder` / `gitlabHelp` / `gitlabDescription`, `ChecksPanel.gitlabMoreActions` / `gitlabUnlink` / `gitlabLinkAnother`) | MR na GitLabu / Číslo MR nebo odkaz na GitLab / „Vložte odkaz na merge request…“ / „…úkoly a merge requesty…“ / Další akce s MR / Odpojit MR / Propojit jiný MR | GitLab protějšky řetězců z GitHubu ([#16906](https://github.com/stablyai/orca/pull/16906)): pole propojení pracovního prostoru s MR v dialogu úpravy podrobností pracovního stromu a nabídka „⋯“ nad MR v panelu kontrol |
| review | revize / review | 193 řádků; neplést s `checks` |
| reviewer | posuzovatel / revident / reviewer | 58 řádků |
| review thread | vlákno revize / diskuse k revizi |  |
| review note | poznámka k revizi | `notes` v editoru — „poznámky“ |
| assignee | řešitel / přiřazený |  |
| label | štítek | 61 řádků |
| draft | koncept |  |
| draft → ready for review (`HostedReviewActions.markReady` / `markingReady` / `readyToast` / `closeDraft` / `draftMoreActions`) | Označit jako připravené k revizi / Označuje se jako připravené… / „{{value0}} je označen jako připravený k revizi“ / Zavřít / Další akce: {{value0}} | tlačítko nad konceptem PR/MR v pravém panelu ([#16889](https://github.com/stablyai/orca/pull/16889)): ruší stav konceptu |
| Started the agent. Marked {{value0}} resolved, replied to {{value1}}, skipped {{value2}}, failed {{value3}}. / Started the agent, but could not resolve or reply on the selected comments. (`ChecksPanel.aa95b81a3a` / `f273f2271c` / `495b2f8c4b`) | Agent spuštěn. Označeno jako vyřešené: {{value0}}, zodpovězeno: {{value1}}, přeskočeno: {{value2}}, selhalo: {{value3}}. / Agent byl spuštěn, ale nepodařilo se označit vybrané komentáře jako vyřešené ani na ně odpovědět. | toast po odeslání vybraných komentářů revize agentovi v panelu kontrol ([#12150](https://github.com/stablyai/orca/pull/12150)): Orca odpovídá na komentáře a označuje vlákna jako vyřešená tam, kde to hostitel umožňuje. Pořadí čísel odpovídá originálu |
| checks | kontroly | stavy CI |
| check run | běh kontroly | `rerun` → „spustit znovu“ |
| annotation | anotace | výstup kontroly v diffu |
| auto-merge | automatické sloučení |  |
| merge queue | fronta pro sloučení |  |
| stacked pull requests | sada navazujících pull requestů (stack) | „Stack #12“ → „Stack #12“; stavy v mapě zásobníku překládáme — jsou viditelné uživateli |
| merge through #N | sloučit včetně #N | sloučí aktuální PR a vše, co je pod ním v zásobníku |
| squash and merge | sloučit se sloučením commitů (squash) |  |
| base ref | výchozí reference (base ref) | `head SHA` → „SHA vrcholového commitu (head)“ |
| fast-forward | posunout vpřed (fast-forward) | „Větev {{branch}} byla posunuta vpřed o {{count}} commitů“ |
| pipeline | pipeline / kanál | GitLab CI |
| job | úloha | uvnitř pipeline nebo kontroly |
| viewed | zkontrolováno / zobrazeno | stav souboru při revizi |
| inline / side by side | v řádku / vedle sebe | režimy zobrazení diffu |
| sparse checkout preset | předvolba částečného vycheckování (sparse checkout) | v rozhraní jednoduše „předvolba“ |
| symlink | symbolický odkaz |  |
| source control | správa verzí | „Git & Source Control“ → „Git a správa verzí“ |
| staged changes | připravené změny (staged) |  |
| uncommitted changes | nepotvrzené změny |  |
| fork (sloveso) | vytvořit fork / odštěpit | „This workspace cannot be forked…“ |
| rebase, stash, diff, checkout, fetch, pull, push | bez překladu | shodují se s příkazy gitu |
| remote (podst. jm.) | remote | v kontextu gitu; `remote host` → „vzdálený hostitel“ |

## Rozhraní

| Anglicky | Česky | Poznámka |
|---|---|---|
| pane | panel | s `panel` se v žádném řádku nekříží |
| terminal pane | panel terminálu |  |
| panel | panel |  |
| tab | karta |  |
| browser tab | karta prohlížeče |  |
| sidebar | postranní panel |  |
| left sidebar | levý postranní panel |  |
| status bar | stavový řádek |  |
| file tree | strom souborů |  |
| My Todos (GitLab) | Moje úkoly | karta seznamu úkolů na GitLabu; podle vzoru „Aktualizovat moje úkoly“ |
| Pull requests / GitHub list (back label) | Pull requesty / Seznam GitHubu | popisek tlačítka „‹ zpět“ nad stránkou PR nebo úkolu (`header.tsx`): 1. pád, slovo „Zpět“ tlačítko neobsahuje; pro Linear stejnou roli hrají „Projekt: {{value0}}“ / „Zobrazení: {{value0}}“ |
| command palette | paleta příkazů |  |
| terminal | terminál |  |
| daemon, terminal host, terminal service | démon terminálů | upstream označuje tentýž proces střídavě jako `daemon`, `terminal host` nebo `terminal service`; v balíčku používáme vždy „démon“ — slovo „hostitel“ je vyhrazeno pro SSH a vzdálené stroje |
| editor | editor |  |
| browser | prohlížeč |  |
| settings | nastavení |  |
| theme | motiv |  |
| folder | složka |  |
| directory | adresář |  |
| path | cesta |  |
| drawer / sheet | výsuvný panel / panel | prvky vysouvající se z boku |
| slash menu | nabídka lomítka (lomítkové příkazy) | nabídka editoru po stisku `/` |
| word wrap | zalamování řádků |  |
| front matter | front matter | nepřekládáme — ustálený termín z Markdownu |
| markup (screenshot) | anotace / značení | kreslení přes snímek obrazovky |
| dictation | diktování |  |
| release notes | poznámky k vydání |  |
| release channel | kanál vydání | `stable` / `preview` → „Stabilní“ / „Náhledový“ |
| applied filter chip | čip použitého filtru | řada čipů pod vyhledáváním na obrazovce čištění (#15300): každá aktivní podmínka je pojmenována a lze ji zrušit křížkem. Název čipu odpovídá popisku v panelu filtrů („Hostitel“, „Lze prořezat (prune)“, „Bezpečnost“) |
| connected peer | připojený protějšek | jiná instance Orca na druhém konci spojení (#16282). „Protějšek / strana“ podle `sshDisconnectedBlocker` („Vzdálená strana není dostupná“). `Update the older connected peer` → „Aktualizujte připojený protějšek se zastaralou verzí“ |
| Installation Target | Kam instalovat | záhlaví karty v okně instalace dovednosti ([#16380](https://github.com/stablyai/orca/pull/16380)): pod ním je výběr pracovního prostoru a agentů. Nikoli „Cíl instalace“ — „cíl“ je již obsazen pro adresy (SSH cíl apod.) |
| Standard Agents (Always Included) / Additional Agent Directories | Standardní agenti (vždy zahrnuti) / Další adresáře agentů | dvě poloviny rozbalovacího seznamu agentů (#16380): první se instalují vždy, druzí se volí zaškrtnutím. Proto `Deselect optional` → „Zrušit výběr volitelných“ |
| placement (skill delete) | složka / odkaz | ([#16357](https://github.com/stablyai/orca/pull/16357)) smazání dovednosti odstraní všechna její umístění: samotnou složku i symbolické odkazy z jiných složek |
| Removes {{parts}} across {{roots}} | Bude odstraněno {{parts}} — v {{roots}} | `roots` jsou návěští kořenů jako `Repo orca .claude`, nepřekládají se. Části s počtem jsou formulovány jako „složek: {{count}}“ |
| The skill itself stays at {{path}} | Samotná dovednost zůstane v {{path}} | dovednost, jejíž obsah leží mimo kořenové složky Orca, se maže pouze formou odkazů |
| Bundled with Orca — it would be restored | Součást instalace Orca — byla by obnovena | důvod blokování smazání |
| Not deletable | Nelze smazat | popisek řádku dovednosti, protějšek k `notShareable` = „Nelze publikovat“ |
| client-hosted (browser page) | hostováno na zařízení / zobrazuje se na tomto zařízení | ([#15448](https://github.com/stablyai/orca/pull/15448)) stránka vzdáleného pracovního prostoru, kterou vykresluje tento počítač, ale síťový provoz jde přes vzdáleného hostitele; protiklad k `streamed` → „streamováno / přenášeno“ |
| this device / this desktop / this machine | toto zařízení / tento počítač | v #15448 se tři výrazy střídají v témže významu. Přepínače „This device“ → „Toto zařízení“; `desktop` a `machine` → „počítač“ |
| paired desktop | spárovaný počítač | odpovídá pojmu „spárovaná zařízení“ v `MobilePane` |
| Browsing through {{host}} / Browsing on {{host}} | Procházení přes {{host}} / Procházení na {{host}} | indikátor přístupu k síti: „přes“ — provoz jde přes hostitele, stránka běží lokálně; „na“ — stránka běží na hostiteli a obraz se přenáší |
| Where browser traffic leaves from | Odkud odchází síťový provoz prohlížeče | popis řádku nastavení `SSH workspaces` |
| document preview / HTML preview (`HtmlDocPreview`) | náhled dokumentu / náhled HTML | ([#16679](https://github.com/stablyai/orca/pull/16679)) lokální vykreslení HTML dokumentů pracovního prostoru podle schématu `orca-preview`. `Preview options` → „Možnosti náhledu“, `Reload preview` → „Znovu načíst náhled“, `Open source file` → „Otevřít zdrojový soubor“, `Copy file path` → „Kopírovat cestu k souboru“, `Open Preview to the Side` → „Otevřít náhled vedle“ |
| `{{path}}` / `{{count}}` v poznámkách náhledu | „Soubor {{path}} je příliš velký…“ / „…několik souborů tohoto dokumentu ({{count}})“ | ([#16679](https://github.com/stablyai/orca/pull/16679)) `{{count}}` je vždy ≥ 2 bez tvarů pro jednotné číslo — uvádí se v závorce, aby nebylo nutné skloňovat |
| paired server (`file.preview.pairedOutsideWorktree`) | spárovaný server | ([#16679](https://github.com/stablyai/orca/pull/16679)) server Orca, se kterým je tento klient spárován. `Download & open with default app` → „Stáhnout a otevřít ve výchozí aplikaci“, `Downloads are disabled in document previews` → „Stahování souborů v náhledech dokumentů je zakázáno“ |
| Reopen on server | Znovu otevřít na serveru | nikoli „přeotevřít“: tlačítko vytvoří novou stránku na poslední adrese, stav se nepřenáší |
| See more (palette overflow) | Zobrazit další | tlačítko vedle nápovědy v paletě přechodu (#16533). Neplést se `showMore`/`showLess` pro rozbalení textu → „Zobrazit více“ / „Méně“ |
| Supported agents: (`NativeChatSupportedAgents`) | Podporovaní agenti: | ([#16830](https://github.com/stablyai/orca/pull/16830)) popisek u řady ikon agentů pod přepínačem „Rozhraní chatu“ v experimentálním nastavení. S Orca v1.4.224 přepsáno: `nativeChat.description` → „Otevírat nové podporované agenty v rozhraní chatu.“ |
| Use updated structured native chat / Toggle … / structuredCopy / structuredScope (`ExperimentalPane.nativeChat.structured*`) | Používat aktualizované strukturované rozhraní chatu / Přepnout aktualizované strukturované rozhraní chatu / „Připojuje strukturované běhové prostředí chatu pro Codex a Claude spravované hostitelem…“ / „Zatím pouze lokální relace…“ | ([#16729](https://github.com/stablyai/orca/pull/16729)) vnořený přepínač pod „Rozhraní chatu“. „native chat“ = „rozhraní chatu“, „structured“ → „strukturované“, `runtime` → „běhové prostředí“, `execution host` → „hostitel běhu“. V Orca v1.4.224 odstraněno — řádek ponechán pro historii |
| Orchestration paused / orchestrationPaused.message / `orca orchestration check` (`native-chat.orchestrationPaused.*`) | Orchestrace pozastavena / „Strukturovaný chat blokuje prompty a odesílání do terminálu. Zprávy orchestrace zůstávají ve frontě; přepněte se do terminálu a zkontrolujte příchozí zprávy Orca příkazem“ / orca orchestration check | (#16729) pruh ve strukturovaném chatu, dokud dispečer orchestrace čeká na odpověď |
| Message delivery is unconfirmed. / Message was not sent. / Retry (`NativeChatStructuredSession.1f772bb5d0` / `93ef441197` / `a5e7f14068`) | Doručení zprávy není potvrzeno. / Zpráva nebyla odeslána. / Opakovat | (#16729) řádek odchozích zpráv strukturovaného chatu s tlačítkem opakování |
| Could not open {{value0}} chat / Could not close this chat session / Starting {{value0}} chat… / «The terminal stayed open so the provider remains recoverable.» / {{value0}} bytes (`native-chat.structuredSession*`, `providerFrame.byteLength`) | Nepodařilo se otevřít chat {{value0}} / Nepodařilo se ukončit tuto relaci chatu / Spouštění chatu {{value0}}… / „Terminál zůstal otevřený, aby bylo možné poskytovatele obnovit.“ / {{value0}} bajtů | (#16729) toasty spuštění/ukončení strukturované relace (`provider` → „poskytovatel“ podle glosáře); velikost rámce v rozbalovacím bloku zprávy — „bajtů“ bez skloňování |
| The structured agent session is not available yet. Retry in a moment. (`activateAiVaultStructuredSession.unavailable`) | Strukturovaná relace agenta zatím není dostupná. Zkuste to za okamžik znovu. | (#16729) toast při přetažení relace z historie relací agenta; „za okamžik“ podle `worktreeNotReady` |
| Multi-task / Use Orca's browser / Turn on notifications / Choose your default agent / Enable Orca CLI / Connect integrations / Automate workspace setup / Start work in multiple repos (`feature.wall.setup.checklist.localized.copy.*`, názvy kroků) | Pracovat paralelně / Používat prohlížeč Orca / Zapnout oznámení / Zvolit výchozího agenta / Povolit Orca CLI / Připojit integrace / Automatizovat nastavení pracovního prostoru / Začít pracovat ve více repozitářích | ([#17108](https://github.com/stablyai/orca/pull/17108)) 8 kroků kontrolního seznamu průvodce nastavením (Setup Guide). Názvy jsou v infinitivu |
| Work in 2 different worktrees at once… / Browse your web app without leaving Orca… / Know the moment an agent finishes, needs attention, or gets blocked. / Register the Orca shell command and install agent skills for browser, computer, and orchestration workflows. / Run install and setup commands automatically… / Bring your key repos into Orca… (`feature.wall.setup.checklist.localized.copy.*`, popisy kroků) | „Pracujte současně ve 2 různých pracovních stromech. Každý je izolovaný (dokonce i v rámci jednoho projektu)…“ / „Procházejte svou webovou aplikaci, aniž byste opustili Orca…“ / „Dozvíte se okamžitě, jakmile agent dokončí práci, vyžaduje pozornost nebo je zablokován.“ / „Zaregistrujte příkaz prostředí Orca a nainstalujte dovednosti agentů pro pracovní postupy prohlížeče, počítače a orchestrace.“ / „Spouštějte instalační a konfigurační příkazy automaticky…“ / „Přidejte do Orca své klíčové repozitáře…“ | (#17108) 2. osoba množného čísla |
| Unlink {{value0}} from workspace / description (`HostedReviewUnlinkMenuItem`) | Odpojit {{value0}} od pracovního prostoru / „Orca skryje podrobnosti {{value0}} {{value1}} pro tento pracovní prostor. Samotný {{value0}} a větev v {{value2}} se nezmění.“ | ([#16898](https://github.com/stablyai/orca/pull/16898)) položka nabídky odpojení PR/MR; value0 = „PR“/„MR“, value1 = „#123“, value2 = poskytovatel |
| Pull request unlinked / Link PR #{{number}} / unlinkedPr.status (`checksPanel.unlinked.*`, `sourceControl.unlinkedPr`) | „Pull request byl odpojen“ / „Propojit PR #{{number}}“ / „PR #{{number}} je odpojen“ | ([#16898](https://github.com/stablyai/orca/pull/16898)) prázdný stav panelu kontrol po odpojení |
| {{count}} unresolved conflicts were excluded… (`CombinedDiffViewer.skippedConflictsExcluded`, `_one`/`_other`) | _one „{{count}} nevyřešený konflikt byl vyloučen z tohoto zobrazení diffu.“ / _other a výchozí „Z tohoto zobrazení diffu bylo vyloučeno nevyřešených konfliktů: {{count}}.“ | ([#17341](https://github.com/stablyai/orca/pull/17341)) první klíč upstreamu se skutečným parametrem `count`. Pro balíček se uplatňují pravidla náhradního chování pro angličtinu (#12106), proto je `_other` formulován nezávisle na počtu |
| Annotation intent / Edit annotation {{value0}} (`browser.page.annotation.tray`) | Účel anotace / Upravit anotaci {{value0}} | ([#17511](https://github.com/stablyai/orca/pull/17511)) aria popis přepínací skupiny a tlačítka s tužkou |
| Orca isn’t reachable on this host / restoring / checking / contact note (`RuntimeHostStatusRow`) | „Orca není na tomto hostiteli dostupná“ / „Orca se pokouší obnovit připojení“ / „Orca ověřuje, zda je tento hostitel dostupný“ / „Hostitel může stále běžet; nedostupné je pouze připojení Orca.“ | ([#17062](https://github.com/stablyai/orca/pull/17062)) podnabídka podrobností o selhání hostitele ve stavovém řádku |
| Filtering {{value0}} of {{value1}} team labels… / partial (`linear-issue-attribute-filter-*`) | „Filtruje se {{value0}} z {{value1}} štítků týmů — úkoly ostatních týmů nejsou zahrnuty.“ / odznak „částečně“ | ([#17376](https://github.com/stablyai/orca/pull/17376), [#17342](https://github.com/stablyai/orca/pull/17342)) varování o neúplném pokrytí filtrů Linear |
| This project is stored on a Windows drive / description (`repos.wslFilesystemBoundary*`) | „Tento projekt je uložen na disku Windows“ / „Git pro tento projekt běží v distribuci {{distro}} a k diskům Windows přistupuje přes most souborového systému WSL. Počítejte s tím, že git bude přibližně 20× pomalejší než na kopii uložené přímo uvnitř distribuce {{distro}}.“ | ([#17636](https://github.com/stablyai/orca/pull/17636)) varování po přidání projektu, jehož strom leží na disku Windows a git běží ve WSL |
| Update the remote runtime to unlink GitHub pull requests (`worktree.meta.persist.github.pr.suppression`) | Chcete-li odpojovat pull requesty GitHubu, aktualizujte vzdálené běhové prostředí | ([#16898](https://github.com/stablyai/orca/pull/16898)) `runtime` → „běhové prostředí“ |
| Orca unavailable / SSH transport is connected, but the Orca runtime is unavailable / did not answer (`SshStatusSegment.runtime_unavailable_transport_up`, `RuntimeHostStatusRow.runtime_unavailable*`, `RuntimeEnvironmentsPane.serverRuntimeUnavailable*`) | „Orca není dostupná“ / „Přenos přes SSH je připojen, ale běhové prostředí Orca není dostupné“ / „…neodpovědělo“ | ([#17710](https://github.com/stablyai/orca/pull/17710)) rozlišení živého transportu SSH od nedostupného běhového prostředí |
| View activity / Turn off activity view / Activity options (`dashboard.sidebar.openActivity`/`closeActivity`, `ActivityPrototypePage.activityOptions`) | Zobrazit aktivitu / Vypnout zobrazení aktivity / Možnosti aktivity | ([#18250](https://github.com/stablyai/orca/pull/18250)) zvonek v záhlaví postranního panelu přepíná panel do zobrazení „Agenti“ |
| Could not confirm whether Codex chat opened. Retry to check again. (`auto.lib.worktree.creation.flow.structured.launch.unknown`) | Nepodařilo se ověřit, zda se chat Codex otevřel. Zkuste to prověřit znovu. | ([#18248](https://github.com/stablyai/orca/pull/18248)) chyba na kartě vytváření pracovního stromu |
| No preview for this remote session — open the workspace to view the terminal. (`dashboardPopout.terminal.remotePreviewUnavailable`) | Pro tuto vzdálenou relaci není náhled k dispozici — otevřete pracovní prostor pro zobrazení terminálu. | ([#18403](https://github.com/stablyai/orca/pull/18403)) zástupný text náhledu terminálu v panelu agentů |
| Français (`settings.appearance.language.french`) | Francouzština | ([#16455](https://github.com/stablyai/orca/pull/16455)) položka přepínače jazyka rozhraní |
| Try Automatic Install Again (`LinuxPackageInstallRecoveryCard.3da99454c6`) / Orca couldn't confirm whether this terminal's previous session is still running… (`TerminalErrorToast.7ee11bc0db`) | Zkusit automatickou instalaci znovu / Orca nemohla ověřit, zda předchozí relace tohoto terminálu stále běží… | obě položky zmizely ve v1.4.197 a byly vyřazeny |
| There are terminals with running processes. / A remote host could not be reached, so Orca cannot tell whether work is still running there. Close the window anyway? (`Terminal.7958465754` / `Terminal.b7c1f0a934`) | Některé terminály obsahují běžící procesy. / Se vzdáleným hostitelem se nepodařilo spojit, takže Orca nemůže určit, zda na něm práce stále probíhá. Přesto okno zavřít? | ([#18593](https://github.com/stablyai/orca/pull/18593)) dialog potvrzení při zavírání okna |
| Your Orca account session expired. / Sign in again to use Orca Relay, or use LAN to pair over Tailscale or the same Wi‑Fi. (`MobileRelayMintFailureNotice.reconnectTitle` / `reconnectBody`) | Platnost relace účtu Orca vypršela. / Přihlaste se znovu pro používání Orca Relay, nebo použijte místní síť (LAN) pro spárování přes Tailscale či stejnou Wi‑Fi. | ([#18694](https://github.com/stablyai/orca/pull/18694)) oznámení o selhání vygenerování párovacího kódu |
| Worktree scan failed for {{value0}} / Retry scan / Existing worktrees are kept until a scan succeeds. Click to retry. (`sidebar.RepoScanUnavailableIndicator.*`) | Skenování pracovních stromů repozitáře {{value0}} selhalo / Opakovat skenování / Existující pracovní stromy zůstávají zachovány, dokud skenování neproběhne úspěšně. Klikněte pro opakování. | ([#18456](https://github.com/stablyai/orca/pull/18456)) žlutý trojúhelník v záhlaví repozitáře v postranním panelu |
| Terminal / Chat / Switching (`native-chat.handoff.mode.*`) / Switching session owner… / Switch after this turn / Stop turn and switch / Open agent TUI / Return after this turn / Return to chat / Switching after this turn / Returning after this turn / Cancel (`native-chat.handoff.*`) | Terminál / Chat / Přepínání / Změna vlastníka relace… / Přepnout po tomto tahu / Zastavit tah a přepnout / Otevřít TUI agenta / Vrátit se po tomto tahu / Vrátit se do chatu / Přepínání po tomto tahu / Návrat po tomto tahu / Zrušit | ([#18560](https://github.com/stablyai/orca/pull/18560)) pruh předání práce (`StructuredAgentSessionHandoffChrome`) nad strukturovaným chatem. `turn` → „tah“, `owner` → „vlastník“, `TUI` latinkou |
| Finishing chat session… / Finishing agent terminal… / Opening agent terminal… / Resuming chat session… / Verifying agent terminal… / Verifying chat session… / Recovering agent session… / Agent session needs recovery (`native-chat.handoff.stage.*`) / Agent is open in terminal on {{value0}}. / Agent is open in terminal. / Exit the agent terminal to continue in chat. / Retry proof / Retry / Details | Dokončování relace chatu… / Ukončování terminálu agenta… / Otevírání terminálu agenta… / Obnovování relace chatu… / Ověřování terminálu agenta… / Ověřování relace chatu… / Obnova relace agenta… / Relace agenta vyžaduje obnovu / Agent je otevřen v terminálu na {{value0}}. / Agent je otevřen v terminálu. / Pro pokračování v chatu ukončete terminál agenta. / Opakovat ověření / Opakovat / Podrobnosti | (#18560) stavy předání vyjádřené dějovými podstatnými jmény s výpustkou |
| Default Agent / Appearance / Windows Terminal / Notifications / Integrations (`components.onboarding.flow.stepTooltip.*`) | Výchozí agent / Vzhled / Windows Terminal / Oznámení / Integrace | ([#17992](https://github.com/stablyai/orca/pull/17992)) popisky bodů průběhu úvodního průvodce (onboardingu) |
| Add your first project / Continue / Opening Add Project... / Skip / No, keep going (`components.onboarding.flow.actions.*`, `components.onboarding.skipConfirmation.*`) | Přidat první projekt / Pokračovat / Otevírá se „Přidat projekt“… / Přeskočit / Ne, pokračovat | (#17992) tlačítka zápatí úvodního průvodce |
| Match OS / Easy on the eyes / Bright & crisp (`components.onboarding.theme.hints.*`) | Podle systému / Příjemné pro oči / Jasný a ostrý | (#17992) nápovědy pod kartami motivů |
| Start a workspace from any GitHub issue or pull request, prefilled with its title and context / Browse GitHub issues and pull requests in the Tasks view without leaving Orca / See issue state, review status, and CI checks on every worktree / Read, comment on, and merge pull requests without leaving Orca (`components.onboarding.integrations.capabilities.*`) | „Spouštějte pracovní prostor z libovolného úkolu nebo pull requestu GitHubu — s předvyplněným názvem a kontextem“ / „Procházejte úkoly a pull requesty GitHubu v zobrazení Úkoly, aniž byste opustili Orca“ / „Sledujte stav úkolu, stav revize a kontroly CI v každém pracovním stromu“ / „Čtěte, komentujte a slučujte pull requesty, aniž byste opustili Orca“ | (#17992) seznam schopností integrace |
| settings search keywords — runtime / agent location / permissions / spellcheck / red underline / diff base / sync fork / behind upstream / pop-out / in-window / kanban / ephemeral / sandbox / recipe / sign in / logout / share / publish / unlisted / revoke / wheel / trackpad… (`auto.components.settings.*.search.*`, `auto.components.settings.*.keyword*`, 154 klíčů) | běhové prostředí / umístění agentů / oprávnění / kontrola pravopisu / červené podtržení / základna diffu / synchronizovat fork / zpoždění za upstreamem / v samostatném okně / v okně / kanban / dočasné / sandbox / recept / přihlásit se / odhlásit se / sdílet / publikovat / neveřejný / odvolat / kolečko / trackpad… | ([#18040](https://github.com/stablyai/orca/pull/18040)) klíčová slova vyhledávání v nastavení |
| Split Chat Right / Split Chat Down / Open the active chat in a split pane to the right. / Open the active chat in a split pane below. (`cmd.j.quick.actions.splitChat*`) a vyhledávací slova | Rozdělit chat doprava / Rozdělit chat dolů / Otevřít aktivní chat v rozděleném panelu vpravo. / Otevřít aktivní chat v rozděleném panelu dole. / „rozdělit chat doprava“, „přesunout chat doprava“, „panel chatu vpravo“ | ([#18714](https://github.com/stablyai/orca/pull/18714)) akce palety Cmd+J |
| Reveal hidden workspace? / The active workspace is hidden in the sidebar. Revealing it will clear your sidebar filters. / Clear filters and reveal / Keep filters (`sidebar.revealFiltered.*`) | Zobrazit skrytý pracovní prostor? / Aktivní pracovní prostor je v postranním panelu skrytý. Jeho zobrazení vymaže filtry postranního panelu. / Vymazat filtry a zobrazit / Ponechat filtry | ([#18708](https://github.com/stablyai/orca/pull/18708)) potvrzovací dialog |
| Edited file / Added file / Deleted file / Renamed file / Copy diff / Lines not shown / Diff truncated (`native-chat.tool.editedFile` … `diffTruncated`) | Soubor upraven / Soubor přidán / Soubor smazán / Soubor přejmenován / Kopírovat diff / Řádky nejsou zobrazeny / Diff zkrácen | ([#18765](https://github.com/stablyai/orca/pull/18765)) karty úprav souborů v chatu agenta |
| Orca keeps failing to load / The app window stopped responding while reloading after a crash. / The app window crashed repeatedly and stopped reloading automatically. / Orca reloaded the window after a crash, but it never finished loading. / Orca tried to recover {{recoveryCount}} times in a row without success. / If that does not help, the cause is usually a graphics driver. / This is often a graphics-driver or installation problem. Reload to try again, or quit and relaunch Orca. / Reload / Copy Commands / Quit (`rendererRecovery.*`) | Aplikaci Orca se opakovaně nedaří načíst / Okno aplikace přestalo odpovídat při opětovném načítání po pádu. / Okno aplikace opakovaně spadlo a Orca zastavila automatické načítání. / Orca po pádu okno znovu načetla, ale načítání se nikdy nedokončilo. / Orca se neúspěšně pokusila o obnovení — neúspěšných pokusů za sebou: {{recoveryCount}}. / Pokud to nepomůže, příčinou bývá obvykle grafický ovladač. / Často se jedná o problém s grafickým ovladačem nebo instalací aplikace. Znovu načtěte pro další pokus, nebo ukončete a znovu spusťte Orca. / Znovu načíst / Kopírovat příkazy / Ukončit | ([#18466](https://github.com/stablyai/orca/pull/18466)) systémový dialog procesu main |
| Monitoring background tasks / Stop / Background agent / Background workflow / Background command / Background monitor / Background task / Running background tasks / Task details are unavailable for this session. (`native-chat.backgroundTasks.*`) | Sledování úkolů na pozadí / Zastavit / Agent na pozadí / Workflow na pozadí / Příkaz na pozadí / Monitor na pozadí / Úkol na pozadí / Běžící úkoly na pozadí / Podrobnosti o úkolech nejsou pro tuto relaci dostupné. | ([#18757](https://github.com/stablyai/orca/pull/18757)) pruh nad editorem zpráv nativního chatu |
| Structured chat isn't available / Orca tried to open a {{value0}} terminal instead. / Orca could not open a structured {{value0}} chat. See the logs for details. (`native-chat.structuredSessionFellBackToTerminal*`, `structuredSessionLaunchFailedDescription`) | Strukturovaný chat není dostupný / Orca se místo toho pokusila otevřít terminál {{value0}}. / Orca nemohla otevřít strukturovaný chat {{value0}}. Podrobnosti najdete v protokolech. | ([#18762](https://github.com/stablyai/orca/pull/18762)) toasty záložního otevření terminálu |
| Stop {{value0}} / Stop background tasks (`native-chat.backgroundTasks.stopTask`, `stopAll`) | Zastavit úkol „{{value0}}“ / Zastavit úkoly na pozadí | ([#18807](https://github.com/stablyai/orca/pull/18807)) aria popisky tlačítek zastavení |
| Thread list options, filters active / Show all hosts and projects / Clear notification (`activity.ActivityPrototypePage.threadListOptionsFiltered`, `ActivityScopeFilterControls.resetScope`, `ActivityThreadRow.clearNotification`) | Možnosti seznamu vláken, filtry aktivní / Zobrazit všechny hostitele a projekty / Odstranit oznámení | ([#18699](https://github.com/stablyai/orca/pull/18699)) zobrazení „Aktivita“ a karta „Agenti“ |
| Roadmap / Unsupported / Timeline zoom / Placed by {{value0}} / {{value0}} without dates / Today / Month / Quarter / Year / Item / No dates / Restricted item / {{value0}} — {{value1}} / This roadmap view has no date or iteration field to place items on, so Orca is listing them instead. / Switch to a Table or Roadmap view to work with this project in Orca. / Orca renders table and roadmap project views. This view uses a layout it cannot render yet. (`github.project.ProjectPickerPanels.*`, `ProjectRoadmap.*`, `ProjectRoadmapBar.*`, `ProjectViewStates.*`) | Plán (Roadmap) / Nepodporováno / Měřítko časové osy / Umístěno podle: {{value0}} / Bez dat: {{value0}} / Dnes / Měsíc / Čtvrtletí / Rok / Položka / Bez dat / Položka s omezeným přístupem / {{value0}} — {{value1}} / V tomto zobrazení plánu není žádné pole data ani iterace, podle kterého by bylo možné položky umístit, takže je Orca zobrazuje jako seznam. / Přepněte se na tabulkové zobrazení nebo plán, abyste s tímto projektem mohli v Orca pracovat. / Orca vykresluje zobrazení projektů v podobě tabulky a plánu. Toto zobrazení používá rozvržení, které zatím neumí vykreslit. | ([#17795](https://github.com/stablyai/orca/pull/17795)) zobrazení GitHub Projects typu Roadmap na časové ose |
| This chat is no longer on this host, so it cannot be reopened here. / This chat can't be reopened until Orca is updated. (`lib.activateAiVaultStructuredSession.gone`, `hostCannotOpen`) | Tento chat se již na tomto hostiteli nenachází, takže jej zde nelze znovu otevřít. / Tento chat nelze znovu otevřít, dokud nebude Orca aktualizována. | ([#18933](https://github.com/stablyai/orca/pull/18933)) toasty při opakovaném otevírání chatu z historie |
| Show link actions / Show available actions when you click a link in the terminal or a chat transcript. Turn this off to require {{modifier}}-click in the terminal. / chat (`BrowserTerminalLinkActionsSetting.title`, `.description`, `browser.search.terminalLinkActions.chat`) | Zobrazovat akce pro odkazy / Zobrazovat dostupné akce při kliknutí na odkaz v terminálu nebo v záznamu chatu. Vypněte, pokud má být v terminálu vyžadováno kliknutí s klávesou {{modifier}}. / chat | ([#19130](https://github.com/stablyai/orca/pull/19130)) vyskakovací nabídka akcí u odkazu |
| MiniMax endpoint / Overseas (platform.minimax.io) / China (platform.minimaxi.com) / Credentials not set / MiniMax API key / Forget key / Stored locally and sent to the selected MiniMax endpoint for usage refreshes. / Grok reported no usage percentage for this account. (`AccountsPane.f8a4b9d210`, `.endpointOverseas`, `.endpointChina`, `.credentialsNotSet`, `.83b6a1f7c4`, `.a7b1e3c5d2`, `.selectedEndpointStorage`, `GrokAccountsSection.a8f4139350`) | Koncový bod MiniMax / Mezinárodní (platform.minimax.io) / Čína (platform.minimaxi.com) / Přihlašovací údaje nejsou nastaveny / Klíč API MiniMax / Zapomenout klíč / Uloženo lokálně a odesíláno na vybraný koncový bod MiniMax pro aktualizaci údajů o využití. / Grok pro tento účet neohlásil procento využití. | ([#14929](https://github.com/stablyai/orca/pull/14929), [#17936](https://github.com/stablyai/orca/pull/17936)) podpora výběru regionu a klíče API |
| Orca could not confirm every agent session in this workspace has closed, so it stopped before deleting any files. Use Force Delete to remove it anyway. / This workspace still has running agent sessions that Orca could not close, so it stopped before deleting any files. Force Delete will discard any work they hold. (`sidebar.delete.worktree.toast.runningAgentSession`, `runningAgentSessionLive`) | Orca nemohla ověřit, zda byly ukončeny všechny relace agentů v tomto pracovním prostoru, a zastavila se před odstraněním jakýchkoli souborů. Chcete-li prostor přesto odstranit, použijte Vynucené smazání. / Tento pracovní prostor má stále běžící relace agentů, které Orca nemohla ukončit, proto se zastavila před odstraněním jakýchkoli souborů. Vynucené smazání zahodí veškerou neuloženou práci v těchto relacích. | ([#18827](https://github.com/stablyai/orca/pull/18827), [#19762](https://github.com/stablyai/orca/pull/19762)) důvody odmítnutí smazání pracovního prostoru |
| Wait for pending work and messages to finish before using this command. / Conversation operation was not confirmed. (`native-chat.conversationCommand.pendingWork`, `.unconfirmed`) | Před použitím tohoto příkazu počkejte na dokončení probíhající práce a odeslání čekajících zpráv. / Operace s konverzací nebyla potvrzena. | ([#19164](https://github.com/stablyai/orca/pull/19164)) chyby editoru zpráv chatu pro příkazy `/clear` a `/compact` |
| Resume in New Chat / Another chat is already holding this conversation. / Could not resume this session in a new chat. / This conversation's history could not be loaded, so it cannot be resumed in chat. (`AiVaultSessionRow.resumeInNewChat`, `AiVaultPanel.resumeInChatConflict`, `.resumeInChatFailed`, `.resumeInChatTranscriptMissing`) | Pokračovat v novém chatu / Tuto konverzaci již drží jiný chat. / Tuto relaci se nepodařilo obnovit v novém chatu. / Historii této konverzace se nepodařilo načíst, proto v ní nelze v chatu pokračovat. | ([#19176](https://github.com/stablyai/orca/pull/19176)) pokračování v relaci z historie agentů v novém nativním chatu |
| Sign-in expired / MiniMax API key expired. Replace it in Settings. / MiniMax session cookie expired. Replace it in Settings. (`status.bar.tooltip.minimax.expired.label`, `.apiKey`, `.cookie`) | Přihlášení vypršelo / Platnost klíče API MiniMax vypršela. Nahraďte jej v Nastavení. / Platnost cookie relace MiniMax vypršela. Nahraďte ji v Nastavení. | ([#19250](https://github.com/stablyai/orca/pull/19250)) stav vypršení platnosti přihlašovacích údajů |
| Interrupted / Working / Monitoring background tasks / Blocked / Waiting for input / Failed / Done / Idle / No recent update / Needs attention / Projects / Workspaces (`activity.ActivityPrototypePage.interrupted`, `.state.*`, `dashboard.sidebar.projects`, `.workspaces`) | Přerušeno / Pracuje / Sledování úkolů na pozadí / Zablokováno / Čeká na vstup / Selhalo / Hotovo / Nečinný / Žádná nedávná aktualizace / Vyžaduje pozornost / Projekty / Pracovní prostory | ([#18589](https://github.com/stablyai/orca/pull/18589)) stavy agenta v zobrazení „Aktivita“ |
| completed / working / idle / failed / stopped / unverifiable / {{value0}} working / {{value0}} idle / {{value0}} failed / {{value0}} stopped / {{value0}} unverifiable / Kicked off 1 subagent / Kicked off {{value0}} subagents / Ran 1 subagent / Ran {{value0}} subagents / {{value0}} tokens (`native-chat.subagents.*`) | dokončeno / pracuje / nečinný / chyba / zastaveno / neověřeno / {{value0}} pracuje / {{value0}} v nečinnosti / {{value0}} s chybou / {{value0}} zastaveno / {{value0}} neověřeno / Spuštěn 1 dílčí agent / Spuštěno dílčích agentů: {{value0}} / Proběhl 1 dílčí agent / Proběhlo dílčích agentů: {{value0}} / tokenů: {{value0}} | ([#18773](https://github.com/stablyai/orca/pull/18773)) řádek skupiny dílčích agentů Codexu ve strukturovaném chatu |
| Relay cell (`MobilePairingConnectionOptions.relayCell`) | Buňka Relay | ([#19307](https://github.com/stablyai/orca/pull/19307)) řádek „Relay cell: {host}“ v nastavení párování telefonu |
| Show search (`ActivityPrototypePage.showSearch`) | Zobrazovat vyhledávání | ([#19313](https://github.com/stablyai/orca/pull/19313)) zaškrtávací položka v nabídce možností aktivity postranního panelu |
| exit {{value0}} / {{value0}}ms (`native-chat.tool.exitCode`, `.milliseconds`) | návratový kód {{value0}} / `{{value0}}ms` — nepřekládá se | ([#19226](https://github.com/stablyai/orca/pull/19226)) neproporcionální shrnutí vpravo na řádku volání nástroje ve strukturovaném chatu (`NativeChatCommandMetadata`): návratový kód příkazu a jeho doba trvání |
| Context compacted / Plan / Details (`native-chat.notices.*`) | Kontext komprimován / Plán / Podrobnosti | ([#19228](https://github.com/stablyai/orca/pull/19228)) systémová oznámení ve strukturovaném chatu (`NativeChatNoticeRow`). `notices.contextCleared` → „Kontext vymazán“ |
| +{{value0}} more (`native-chat.tool.moreCalls`) | a ještě {{value0}} | ([#19372](https://github.com/stablyai/orca/pull/19372)) sbalené záhlaví série volání nástrojů ve strukturovaném chatu (`NativeChatToolRun`) |
| Create / Add project (`SidebarHeader.createMenu`, `.addProject`) | Vytvořit / Přidat projekt | ([#19375](https://github.com/stablyai/orca/pull/19375)) záhlaví postranního panelu: sloučené tlačítko „+“ s rozbalovací nabídkou |
| Color Contrast / Contrast target / Automatic / Off / Custom / Subtle / Strong (`settings.contrast.*`, `terminal.search.minimumContrast.*`) | Barevný kontrast / Cílový kontrast / Automaticky / Vypnuto / Vlastní / Jemný / Výrazný | ([#18126](https://github.com/stablyai/orca/pull/18126)) nastavení minimálního kontrastu terminálu |
| Filters / View (`activity.ActivityPrototypePage.filtersSection`, `.viewSection`) | Filtry / Zobrazení | ([#19547](https://github.com/stablyai/orca/pull/19547)) nabídka parametrů seznamu vláken v zobrazení „Aktivita“ |
| 1 changed file / {{count}} changed files / Partial diff / Totals from recorded edits in this turn. / Selected answer unavailable / Cancelled / Resolved / Answered on {{device}} / Cancelled on {{device}} (`components.native-chat.turnDiff.*`, `.receipt.*`) | 1 změněný soubor / Změněných souborů: {{count}} / Neúplný diff / Souhrn zaznamenaných úprav v tomto tahu. / Vybraná odpověď není dostupná / Zrušeno / Vyřešeno / Zodpovězeno na {{device}} / Zrušeno na {{device}} | ([#19229](https://github.com/stablyai/orca/pull/19229)) sbalení změn tahu a stvrzenka vyřešeného požadavku |
| Tasks / Completed / In progress / Pending / No tasks / {{completed}} of {{total}} tasks completed / Added {{task}} / Removed {{task}} / Started {{task}} / Completed {{task}} / Marked pending: {{task}} / Updated {{task}} / Tasks unchanged / Full task list (`components.native-chat.taskList.*`) | Úkoly / Dokončeno / Probíhá / Čeká / Žádné úkoly / Dokončeno {{completed}} z {{total}} úkolů / Přidáno: {{task}} / Odebráno: {{task}} / Zahájeno: {{task}} / Dokončeno: {{task}} / Vráceno do čekajících: {{task}} / Aktualizováno: {{task}} / Úkoly beze změny / Úplný seznam úkolů | ([#19230](https://github.com/stablyai/orca/pull/19230)) kontrolní seznam úkolů agenta v nativním chatu |
| 1 agent / {{value0}} agents / 1 shell / {{value0}} shells / 1 shell command / 1 monitor / {{value0}} monitors / 1 workflow / {{value0}} workflows / 1 task / {{value0}} tasks / {{value0}} background tasks / Agents / Shell / Monitors / Workflows / Tasks / working / monitoring / waiting / blocked / done / stopped / unverifiable / needs approval / no contact / failed (`native-chat.backgroundTasks.count*`, `.headerTotal`, `.group*`, `.state*`, `.reason*`) | 1 agent / Agentů: {{value0}} / 1 příkaz / Příkazů: {{value0}} / 1 příkaz shellu / 1 monitor / Monitorů: {{value0}} / 1 workflow / Workflow: {{value0}} / 1 úkol / Úkolů: {{value0}} / Úkolů na pozadí: {{value0}} / Agenti / Příkazy / Monitory / Workflow / Úkoly / pracuje / monitoruje / čeká / chyba / hotovo / zastaveno / bez odezvy / vyžaduje schválení / bez spojení / selhání | ([#19311](https://github.com/stablyai/orca/pull/19311)) pruh úkolů na pozadí nad editorem nativního chatu |
| needs input / working / stopped / finished (`notifications.agentStatus.*`) | čeká na vstup / pracuje / zastaven / dokončil práci | ([#19935](https://github.com/stablyai/orca/pull/19935)) stavová slova v systémovém oznámení o agentovi |
| You've been signed out / Dismiss / Sign in again to restore Artifact sharing, Orca Relay, and skill sharing. / Sign in again as {{value0}} to restore … / What you get back / Artifact sharing / Orca Relay / Skill sharing / Signing in… / Sign in to Orca (`UnexpectedSignoutCard.*`) | Byli jste odhlášeni / Skrýt / Přihlaste se znovu pro obnovení sdílení artefaktů, Orca Relay a sdílení dovedností. / Přihlaste se znovu jako {{value0}} pro obnovení … / Co získáte zpět / Sdílení artefaktů / Orca Relay / Sdílení dovedností / Probíhá přihlašování… / Přihlásit se do Orca | ([#19966](https://github.com/stablyai/orca/pull/19966)) karta v panelu oznámení při neočekávaném odhlášení |
| Reveal in Finder / Reveal in File Explorer / Open Containing Folder (`editor.EditorPanelHeader.*`, `right.sidebar.FileExplorerRow.*`, `tab.bar.EditorFileTabContextMenu.*`: `revealInFinder`, `revealInFileExplorer`, `openContainingFolder`) | Zobrazit ve Finderu / Zobrazit v Průzkumníku souborů / Otevřít nadřazenou složku | ([#20010](https://github.com/stablyai/orca/pull/20010)) zobrazení souboru podle platformy: macOS — Finder, Windows — Průzkumník souborů, Linux — Otevřít nadřazenou složku |
| Drop to attach to this chat / Files are added to your message as paths the agent can read. / Couldn't read the dropped files. / This workspace changed hosts while attaching — drop the files again. / Files can only be attached to their source workspace. / Orca couldn't read a path for the dropped files. (`native-chat.drop.*`, `native-chat.composer.attachment*`, `useGlobalFileDrop.nativeDropUnresolvedPaths*`) | Přetažením připojíte k tomuto chatu / Soubory budou přidány do zprávy jako cesty, které agent může číst. / Přetažené soubory se nepodařilo přečíst. / Během připojování změnil pracovní prostor hostitele — přetáhněte soubory znovu. / Soubory lze připojit pouze k jejich zdrojovému pracovnímu prostoru. / Orca nemohla načíst cestu k přetaženým souborům. | ([#20494](https://github.com/stablyai/orca/pull/20494), [#20561](https://github.com/stablyai/orca/pull/20561)) přetahování souborů do strukturovaného chatu |
| Trim Gutter on Copy / Drop the left gutter agent output is painted behind… (`settings.TerminalInteraction.copyTrimsGutter*`, `settings.terminal.clipboard.search.*`) | Oříznout levý okraj při kopírování / Nekopírovat levý okraj, za kterým se zobrazuje výstup agenta… | ([#20545](https://github.com/stablyai/orca/pull/20545)) nastavení terminálu: odstraňuje společné odsazení výstupu agenta |
| Default / Not reported / This view has no items yet. / Recently added items can take a while to appear. (`native-chat.composer.valueIsDefault`, `.valueNotReported`, `github.project.ProjectViewStates.3b9c1d5e47`, `.7e4a2f80c6`) | Výchozí / Nehlášeno / V tomto zobrazení zatím nejsou žádné položky. / Nedávno přidané položky se mohou objevit až po chvíli. | ([#20506](https://github.com/stablyai/orca/pull/20506), [#20588](https://github.com/stablyai/orca/pull/20588)) hodnoty režimu Fast a prázdný stav projektu |
| Failed to stage / unstage / discard / delete “{{value0}}” / {{value0}} in {{value1}} / Failed to copy notes / The text is too large to copy. (`right.sidebar.SourceControl.entry*Failed`, `.entryFailedInWorkspace`, `.diffCommentNotesCopyFailed`, `lib.clipboardWriteFailure.tooLarge`) | Nepodařilo se připravit (stage) „{{value0}}“ / Nepodařilo se odebrat z připravených „{{value0}}“ / Nepodařilo se zahodit změny v „{{value0}}“ / Nepodařilo se smazat „{{value0}}“ / {{value0}} v pracovním prostoru {{value1}} / Nepodařilo se zkopírovat poznámky / Text je pro zkopírování příliš velký. | ([#20423](https://github.com/stablyai/orca/pull/20423), [#20795](https://github.com/stablyai/orca/pull/20795)) chyby operací ve správě verzí |
| {{failureCount}} of {{count}} items could not be attached. / No longer at its original path. / Symbolic links cannot be attached. / Permission denied. / Unsupported file type. (`hooks.useComposerState.dropPartiallyAttached*`, `.attachSkip*`) | Nepodařilo se připojit položek: {{failureCount}} z {{count}}. / (_one) Nepodařilo se připojit {{failureCount}} z {{count}} položky. / Již se nenachází na původní cestě. / Symbolické odkazy nelze připojit. / Přístup odepřen. / Nepodporovaný typ souboru. | ([#20704](https://github.com/stablyai/orca/pull/20704)) toast při částečném selhání připojení přetažených souborů |
| No microphone was found… / Could not open the microphone. / Opened macOS Privacy & Security… / Microphone access is blocked… (`settings.VoiceMicrophoneSetting.*`) | Nebyl nalezen žádný mikrofon. Připojte jej a zkuste to znovu. / Mikrofon se nepodařilo otevřít. / Byla otevřena sekce Soukromí a zabezpečení v macOS. Povolte přístup k mikrofonu a zkuste to znovu. / Přístup k mikrofonu je blokován. Povolte jej v systémovém nastavení a zkuste to znovu. | ([#20801](https://github.com/stablyai/orca/pull/20801)) chybové hlášky přístupu k mikrofonu |
| Delete Anyway / Copy code / Your messages / Image attachment / Message / Loading subagents… / Retry / Account status unknown / Add or replace credentials (`sidebar.delete.worktree.failure.archive.waiver`, `native-chat.copyCode`, `native-chat.rail*`, `aiVault.subagents.*`, `common.retry`, `UsageAccountsCard.accountStatusUnknown`, `settings.bitbucket.integration.card.*`) | Přesto smazat / Kopírovat kód / Vaše zprávy / Přiložený obrázek / Zpráva / Načítání dílčích agentů… / Opakovat / Stav účtu neznámý / Přidat nebo nahradit přihlašovací údaje | ([#20153](https://github.com/stablyai/orca/pull/20153), [#20357](https://github.com/stablyai/orca/pull/20357), [#20719](https://github.com/stablyai/orca/pull/20719)) krátké popisky rozhraní |
| managed Orca server / relay / Move … to its managed server / Deploy server / Deploying… (`settings.managedServers.*`, `settings.sshHostServer.*`, `ssh.managedServerMove.*`, `settings.deltaMove.*`, `settings.keepServer.*`) | spravovaný server Orca / relay / přesunout… na spravovaný server, „Přesun“ / Nasadit server / Nasazování… | ([#24863](https://github.com/stablyai/orca/pull/24863)) spravovaný server Orca na SSH hostitelích |
| Forget… / Forget on this desktop / Keep linked / Not done: this server is the default host for new projects. Choose another one in Advanced before stopping it. / Orca couldn’t confirm that the managed server is answering. (`managedServers.row.forget*`, `.keepLinked`, `managedServers.outcome.activeServer`, `sshHostServer.notServing`) | Zapomenout… / Zapomenout na tomto počítači / Ponechat propojeno / „Nedokončeno: tento server je výchozím hostitelem pro nové projekty. Před jeho zastavením zvolte jiného v části Pokročilé.“ / „Orca nemohla ověřit, zda spravovaný server odpovídá.“ | ([#26847](https://github.com/stablyai/orca/pull/26847)) akce a hlášení u spravovaného serveru |
| Default host for new projects / Default for new projects (`RuntimeEnvironmentsPane.64b6bea541`, `.activeServerRowHelp`, `SidebarWorkspaceOptionsMenu.activeRuntimeHost`, `providerAccountScope.*`) | Výchozí hostitel pro nové projekty / Výchozí pro nové projekty | ([#27286](https://github.com/stablyai/orca/pull/27286)) nahrazuje dřívější označení Active Server |
| Permissions / Ask for approval / Accept edits / Approve for me / Full access (`native-chat.composer.permission*`, `settings.chat.permissionsTitle`) | Oprávnění / Žádat o schválení / Přijímat úpravy / Schvalovat za mě / Úplný přístup | ([#26116](https://github.com/stablyai/orca/pull/26116)) režimy oprávnění chatu u modelů Claude a Codex |
| WSL host / WSL distro / Orca server / Experimental / Idle (`settings.wslHosts*`, `sidebar.AddWslHostFormPanel.*`, `wslHostRowStatus.*`, `AddRepoHostSelector.addWslHost*`) | WSL hostitel / distribuce WSL / server Orca / Experimentální / Nečinný | ([#27934](https://github.com/stablyai/orca/pull/27934)) distribuce WSL jako hostitel projektů |
| Administrator mode / Run as administrator / Standard user / permissions (Windows) (`settings.terminal.windows.*`) | Režim správce / Spustit jako správce / Běžný uživatel / oprávnění | ([#28073](https://github.com/stablyai/orca/pull/28073)) spuštění s právy správce ve Windows |
| Worktrees / Recent worktrees (paleta přechodu, `WorktreeJumpPalette.worktreesHeader`, `.recentWorktreesHeader`, `.27f10cca63`, `.2770f02910`) | Pracovní prostory / Nedávné pracovní prostory | ([#28175](https://github.com/stablyai/orca/pull/28175)) paleta Cmd/Ctrl+J |
| scoped API token / Has Workspace / Resolution / Story Points / transition (`jira.connect.*`, `jira.statusFilters.*`, `TaskPage.jiraColumn*`, `jira.transitions.*`) | token API s omezeným rozsahem / S pracovním prostorem / řešení / Story Points (body) / přechod stavu | ([#28604](https://github.com/stablyai/orca/pull/28604)) integrace Jira |
| Note / Tip / Important / Warning / Caution (`components.markdown-callout.*`) | Poznámka / Tip / Důležité / Varování / Upozornění | ([#26255](https://github.com/stablyai/orca/pull/26255)) záhlaví bloků Markdown `[!NOTE]` … `[!CAUTION]` |
| Hand Off to Another Agent (`agentSessionContinuation.handOffToAnotherAgent`, `.dialogTitle`) | Předat jinému agentovi | ([#26375](https://github.com/stablyai/orca/pull/26375)) položka nabídky a dialog předání práce |
| Resuming chats {{value0}}/{{value1}} / Resumed {{value0}} of {{value1}} chats / Waiting for a reply / Starting / Waiting to start / Resumed / All / In progress / Need you / Running {{value0}} (`NativeChatResumeRunPanel.*`, `NativeChatResumeRunStatusIcon.*`, `NativeChatResumeRunSummary.*`, `NativeChatResumeStatusSegment.resumingProgress*`) | Obnovování chatů {{value0}}/{{value1}} / Obnoveno chatů: {{value0}} z {{value1}} / Čekání na odpověď / Spouštění / Čeká na spuštění / Obnoveno / Vše / Běží / Vyžadují vás / Běží {{value0}} | ([#26361](https://github.com/stablyai/orca/pull/26361)) panel obnovení chatů po restartu |
| Select all chats / Select all / Select all chats on {{value0}} / Select all chats in {{value0}} / {{value0}} of {{value1}} selected (`NativeChatResumeOnRestartModal.select*`, `.collapseNode`, `.expandNode`, `.sshHost`) | Vybrat všechny chaty / Vybrat vše / Vybrat všechny chaty na {{value0}} / Vybrat všechny chaty v {{value0}} / Vybráno: {{value0}} z {{value1}} | ([#25652](https://github.com/stablyai/orca/pull/25652)) stromový výběr chatů k obnovení |
| {{agent}} is not signed in. / Claude isn't signed in. Run `{{loginCommand}}`, or choose an account in Claude Accounts settings. / Sign in to {{agent}} with `{{loginCommand}}` on the computer running this chat. / Then send your message again. (`native-chat.failureWords.*NotSignedIn`, `.thenSendAgain`, `.cliMissing`) | „{{agent}}: nejste přihlášeni.“ / „V Claude nejste přihlášeni. Spusťte `{{loginCommand}}` nebo zvolte účet v nastavení Účty Claude.“ / „Přihlaste se k {{agent}} příkazem `{{loginCommand}}` na počítači, kde tento chat běží.“ / „Poté zprávu odešlete znovu.“ | ([#25666](https://github.com/stablyai/orca/pull/25666)) hlášení o nepřihlášeném agentovi |
| The agent is still working. / Run /{{command}} when it's done. / Answer the agent's question or approval, then run /clear. (`native-chat.writeNotice.agentStillWorking`, `.run*WhenDone`, `.*AfterAnswer`, `.*AfterRetry`, `.*AfterSending`, `failureWords.runCommandWhenDone`, `.commandAfterAnswer`) | „Agent stále pracuje.“ / „Jakmile dokončí práci, spusťte /{{command}}.“ / „Odpovězte na otázku nebo schválení agenta, poté spusťte /clear.“ | ([#25704](https://github.com/stablyai/orca/pull/25704)) odmítnutí lomítkových příkazů při vytížení agenta |
| Native chat got an upgrade / New / Manage Chat UI in + Settings → Experimental (`featureTips.nativeChatUpgrade.*`) | Nativní chat byl vylepšen / Nové / „Rozhraní chatu lze spravovat v části Nastavení → Experimentální“ | ([#26710](https://github.com/stablyai/orca/pull/26710)) tip k vylepšenému rozhraní |
| Usage display is now compact / One headline metric per provider. Choose `<detailed>Detailed</detailed>` in the Usage menu to show more limits. (`status.bar.StatusBarUsageChangeNotices.compact*`) | Zobrazení využití je nyní kompaktní / „Jedna hlavní metrika na poskytovatele. Chcete-li zobrazit více limitů, zvolte `<detailed>Podrobně</detailed>` v nabídce Využití.“ | ([#26726](https://github.com/stablyai/orca/pull/26726)) přechod na kompaktní režim využití |
| Browser / Editor / Terminal (`tabHoverCard.*`) | Prohlížeč / Editor / Terminál | ([#26811](https://github.com/stablyai/orca/pull/26811)) karta náhledu záložky |
| From (`native-chat.queuedMessages.fromSender`) | Od | ([#26357](https://github.com/stablyai/orca/pull/26357)) odesílatel ve frontě zpráv: „Od agenta“ |
| Find in chat / No results / Previous match / Next match (`native-chat.find.*`) | Hledat v chatu / Žádné výsledky / Předchozí shoda / Další shoda | ([#26517](https://github.com/stablyai/orca/pull/26517)) hledání v konverzaci |
| Orca on {{machine}} restarted for an update / was closed / stopped unexpectedly while this response was in progress. / You can continue in this conversation. / Continue (`native-chat.notices.orcaStop*`, `native-chat.interruptedContinue.*`) | „Orca na {{machine}} se restartovala z důvodu aktualizace / byla ukončena / neočekávaně se zastavila během generování této odpovědi.“ / „V této konverzaci můžete pokračovat.“ / Pokračovat | ([#25675](https://github.com/stablyai/orca/pull/25675)) hlášení přerušené odpovědi |
| Linked work / Add reference / Unlink from workspace / Seen in {{label}} / Target: {{branch}} (`workspace.links.*`, `workspace.attachments.updateRuntime*`) | Propojená práce / Přidat odkaz / Odpojit od pracovního prostoru / Viděno v kartě „{{label}}“ / Cílová větev: {{branch}} | ([#26429](https://github.com/stablyai/orca/pull/26429)) propojení pracovního prostoru s PR, MR a úkoly |
| Add to chat (`native-chat.addSelectionToChat`) | Přidat do chatu | ([#26018](https://github.com/stablyai/orca/pull/26018)) vložení citace označeného textu do vstupu |
| Inline visuals / Visualization unavailable / Loading visualization / Open in new tab (`settings.nativeChat.inlineVisuals*`, `native-chat.visual*`) | Vložené vizualizace / Vizualizace není dostupná / Načítání vizualizace / Otevřít v nové kartě | ([#26103](https://github.com/stablyai/orca/pull/26103)) vizualizace v odpovědích agenta |
| Orca-managed Node / Allow this host's orca CLI to control Orca / Quit {{appName}} (`settings.SshTargetCard.hostNode*`, `settings.SshTargetForm.allowRemoteCliControl*`, `menu.quitApp`) | Node spravovaný Orca / Povolit orca CLI tohoto hostitele ovládat Orca / Ukončit {{appName}} | ([#26483](https://github.com/stablyai/orca/pull/26483)) nastavení SSH hostitele a ukončení aplikace |
| Extra agent arguments / Extra arguments / Use fresh sessions (`automations.extraAgentArgs.*`) | Dodatečné argumenty agenta / Dodatečné argumenty / Použít nové relace | ([#26659](https://github.com/stablyai/orca/pull/26659)) argumenty spuštění agenta v automatizacích |
| Stopped manually (`native-chat.notices.stoppedBeforeStart`) | Zastaveno ručně | ([#26381](https://github.com/stablyai/orca/pull/26381)) stav zastavení před spuštěním |
| Orca is retrying automatically. This terminal will resume if the connection returns. (`terminal.pane.TerminalRemoteRuntimeReconnectBanner.retryingBody`) | Orca se automaticky pokouší o obnovení. Tento terminál bude pokračovat, jakmile se spojení obnoví. | ([#26847](https://github.com/stablyai/orca/pull/26847)) pruh opětovného připojení terminálu |
| The remote browser is unavailable. Check its setup on the server. (`BrowserPane.streamBrowserUnavailable`) | Vzdálený prohlížeč není dostupný. Zkontrolujte jeho nastavení na serveru. | ([#26573](https://github.com/stablyai/orca/pull/26573)) hlášení nedostupnosti streamovaného prohlížeče |

## Akce

| Anglicky | Česky | | Anglicky | Česky |
|---|---|---|---|---|
| Open | Otevřít | | Install | Instalovat / Nainstalovat |
| Close | Zavřít | | Connect | Připojit |
| Copy | Kopírovat | | Disconnect | Odpojit |
| Add | Přidat | | Enable / Disable | Povolit / Zakázat |
| Create | Vytvořit | | Show / Hide | Zobrazit / Skrýt |
| Delete | Smazat / Odstranit | | Choose / Select | Vybrat |
| Remove | Odebrat | | Search | Hledat / Hledání |
| Save | Uložit | | Import / Export | Importovat / Exportovat |
| Cancel | Zrušit | | Run | Spustit |
| Retry | Opakovat | | Start / Stop | Spustit / Zastavit |
| Refresh | Obnovit | | Restart | Restartovat |
| Update | Aktualizovat | | Reload | Znovu načíst |
| Reset | Resetovat / Obnovit výchozí | | Switch | Přepnout |
| Set up / Setup | Nastavit / nastavení | | Collapse / Expand | Sbalit / Rozbalit |
| Hand off | Předat | | Equalize | Vyrovnat |

**Rozbalení oříznutého textu:** `Show more` → „Zobrazit více“, `Show less` → „Méně“ —
tlačítko vrací zbytek řádku oříznutého pomocí `line-clamp` (popis dovednosti, prompt automatizace).
Nejde o `Expand / Collapse`: tam se sbaluje celý blok, zatímco zde viditelná část textu zůstává.

**Přípustná homonymie:** `refresh` i `update` se v kontextu rozhraní překládají jako „Obnovit“ / „Aktualizovat“, `run` a `start` — „Spustit“. Kontexty se nekříží, uměle je oddělovat není nutné.

**Kill / End (relace a terminály):** obojí → „Ukončit“ (`Kill session` → „Ukončit relaci“,
`Kill all sessions` → „Ukončit všechny relace“, `Couldn’t kill session` → „Nepodařilo se ukončit relaci“,
22 řádků). Slovo „Zabít“ se v rozhraní nepoužívá. Upstream v
[#16976](https://github.com/stablyai/orca/pull/16976) přejmenoval tlačítko sledování prostředků
`Kill {{value0}} orphan terminals` → `End {{value0}} orphan terminals` beze změny klíčů
(`ResourceUsageStatusSegment.c7e3b1a0d9f2`/`d8f4c2b1e0a3`) — český text zůstává shodný.

## Stavy a statusy

| Anglicky | Česky |
|---|---|
| failed | selhalo (na začátku věty) / chyba (v záhlaví) |
| could not … | nepodařilo se … |
| Quit canceled: the session snapshot could not be saved | Ukončení práce zrušeno: nepodařilo se uložit snímek relace — „ukončení“, jako `tray.quit` → „Ukončit“, nikoli „konec“ ([#16497](https://github.com/stablyai/orca/pull/16497)) |
| unavailable | nedostupné |
| available | dostupné |
| no longer available | již není dostupné |
| active | aktivní |
| current | aktuální |
| default | výchozí |
| loading | načítání |
| saved | uloženo |
| pending | čeká na vyřízení |
| running | běží |
| idle | nečinný |
| too large | příliš velký |
| seen (o dokončení práce agenta) | zobrazeno — „Done, seen“ → „Hotovo, zobrazeno“; dvojice k `unread`/`unseen` = „nepřečteno“ („Unread agent completion“ → „Nepřečtené dokončení agenta“) |

## Technické termíny

| Anglicky | Česky |
|---|---|
| API key | klíč API |
| endpoint | koncový bod |
| API token | token API |
| access token | přístupový token |
| token | token |
| API budget | rozpočet API |
| usage | využití / čerpání |
| context | kontext |
| prompt | prompt |
| environment variables | proměnné prostředí |
| setup script | konfigurační/instalační skript |
| pairing code | párovací kód |
| pair (sloveso) | spárovat |
| access link | přístupový odkaz |
| QR code | QR kód |
| relay | Relay (název služby Orca) |
| LAN | místní síť (LAN) |
| firewall | brána firewall |
| Full Disk Access | úplný přístup k disku |
| distro | distribuce (WSL) |
| telemetry | telemetrie |
| temporary storage | dočasné úložiště |
| rate limit | limit četnosti požadavků |
| fallback | záložní řešení |
| ultra (úroveň úsilí) | Ultra — vyšší stupeň než `max` = „Maximální“, proto nesklonný název stupně |
| font weight | tloušťka písma — `Bold Font Weight` → „Tloušťka tučného písma“ podle dvojice s `Bold Text` = „Tučný text“ |
| font face | řez písma — konkrétní forma písma; `font family` — „rodina písem“. Rozlišovat je nutné: v [#14368](https://github.com/stablyai/orca/pull/14368) je několik hodnot tloušťky sloučeno do jednoho řezu |
| passkey | přístupový klíč (passkey) — termín Apple a Google v českých rozhraních |
| security key | bezpečnostní klíč — hardwarový autentizátor, nikoli samotný účet. V [#14687](https://github.com/stablyai/orca/pull/14687) stojí oba termíny vedle sebe (`Choose a passkey` / `…with this security key`) |
| keyring | klíčenka / svazek klíčů; `login keyring` — „přihlašovací klíčenka“ |
| app-bound encryption | šifrování vázané na aplikaci — režim Chrome, kvůli kterému Orca nemůže číst cizí cookies |
| account | účet — jednotná volba v celém balíčku |
| backup tool | zálohovací nástroj — v [#15046](https://github.com/stablyai/orca/pull/15046) stojí vedle antiviru |
| one-click run | spuštění na jedno kliknutí — zavedeno v [#15011](https://github.com/stablyai/orca/pull/15011) |
| Run (popisek, nikoli tlačítko) | spuštění — podle vzoru `AutomationRunHistory` („Run“ → „Spuštění“). Tlačítko „Run“ zůstává „Spustit“ |
| `{{day}}s at {{time}}` (popisek plánu) | „Týdně: {{day}}, {{time}}“ — zavedeno v [#15884](https://github.com/stablyai/orca/pull/15884) |
| `Speaking` / `Listening` (indikátor diktování) | „Mluvení“ / „Poslouchám“ — popisek `DictationIndicator` podle úrovně signálu mikrofónu |
| probe (zjišťování agentů) | zjišťování / hledání — „the probe may have timed out“ → „vypršel časový limit zjišťování“ ([#16043](https://github.com/stablyai/orca/pull/16043)) |
| console (limit Git Bash) | konzole — „128-console limit“ → „limit 128 konzolí“ ([#16045](https://github.com/stablyai/orca/pull/16045)) |
| site-partition (cookie) | oddělení podle webu — klíč, podle kterého Chromium rozděluje cookies podle webu nejvyšší úrovně ([#15030](https://github.com/stablyai/orca/pull/15030)) |
| directory access (banner náhledu HTML) | „Tento náhled požaduje čtení souborů v {{path}}“ / tlačítka „Povolit složku“ a „Povolit složky ({{count}})“ |
| Open link to {{host}}? (externí odkaz z náhledu) | „Otevřít odkaz na {{host}}?“, tlačítko `Open link` → „Otevřít odkaz“, `Cancel` → „Zrušit“ ([#16920](https://github.com/stablyai/orca/pull/16920)) |
| Hidden experimental settings / Terminal render diagnostics (`HiddenExperimentalGroup`) | „Skrytá experimentální nastavení“ / „Diagnostika vykreslování terminálu“ ([#16868](https://github.com/stablyai/orca/pull/16868)) |
| rich editing limit / Open anyway (`editor.richMarkdown.*`) | „Soubor překračuje limit formátovaného editoru ({{limit}}). Zobrazen režim zdrojového kódu.“ / „Přesto otevřít“ ([#16971](https://github.com/stablyai/orca/pull/16971)) |
| Working… / Thinking / Worked for {{value0}} (živý stav tahu, `native-chat.status.*`) | „Pracuje…“ / „Přemýšlí“ / „Pracoval {{value0}}“ — řádek stavu tahu agenta ve strukturovaném chatu ([#17597](https://github.com/stablyai/orca/pull/17597)) |
| CLI, API, SSH, WSL, URL, PATH, REST, GraphQL | bez překladu |
| cookie, diff, middleware, hex | bez překladu |
| GitHub, GitLab, Linear, Jira, Azure DevOps, Bitbucket, Gitea | bez překladu |
| Claude, Codex, Gemini, OpenCode, Kimi, MiniMax, Ghostty, Tailscale | bez překladu |

## Známá omezení

- **Množné číslo v současné verzi enginu nefunguje optimálně.** Balíček se připojuje pod syntetickým kódem `plugin<hex>`, který i18next nepřiřazuje k pravidlům CLDR pro daný jazyk, proto se aplikují výchozí pravidla: pouze dva tvary namísto českých tří. Ověřeno na živém katalogu:

  | Jazyk | 1 | 2 | 5 |
  |---|---|---|---|
  | `cs` | oprávnění | oprávnění | oprávněn**í** ✅ |
  | `plugin<hex>` | oprávnění | oprávnění | oprávněn**í** ❌ (pouze 2 tvary) |

  Proto se k tvarům `_few` / `_many` engine v současnosti nedostane. V `_other` používáme formulace bez nutnosti skloňování počtu — např. „Souborů: {{count}}“ namísto „{{count}} soubory“. Omezení je popsáno v [stablyai/orca#12106](https://github.com/stablyai/orca/issues/12106); udržovatel podpořil prototyp, který je otevřen jako [PR #12505](https://github.com/stablyai/orca/pull/12505) — resolver získá deklarovanou lokalitu balíčku namísto syntetické značky. Dokud PR nebude sloučen, zůstávají formulace nezávislé na čísle v `_other` povinné.

  **Doplňkové tvary jsou připraveny předem (od v5.1.158).** i18next hledá tvar pro každé volání s parametrem `count`: ke klíči volanému komponentou se připojí přípona tvaru a teprve poté se vyhledá samotný klíč. Proto balíček nese 159 doplňkových tvarů dvou druhů:
  - `_few` a `_many` pro 18 rodin, které v katalogu Orca mají `_one` a `_other` (36 tvarů);
  - `_one`, `_few` a `_many` pro 41 řetězců, které Orca volá s počítadlem, ale ukládá jako jediný text: `fileOther`, `connectedHostCount_other`, `transcriptsSkipped` (123 tvarů). Samotný klíč zůstává záložní variantou.

  Dnes se na obrazovce mění jediné: jednička u řetězců bez samostatného klíče — „1 agent“ namísto „Agentů: 1“. Ostatní tvary začnou fungovat po sloučení #12505.

  Pravidla pro nové řetězce s počítadlem:
  - Tvary vyžaduje řetězec, který stojí na obrazovce samostatně: věta, tlačítko, popisek. Část vkládaná do jiného řetězce zůstává nezávislá na počtu.
  - Tvar `_one` musí obsahovat `{{count}}`, nikoli napevno „1“ nebo „jeden“ — **pokud `{{count}}` obsahuje už anglický originál**: podle slovanských pravidel připadá i na 21, 101 atd. Kde má anglický `_one` napevno „1“ (`1 uncommitted or untracked change`, `Delete 1 Workspace`, `Hiding 1 discovered worktree`), `{{count}}` se **nepřidává** a tvar se překládá bez počítadla: „Nepotvrzená nebo nesledovaná změna“, „Smazat pracovní prostor“, „Skrývá se nalezený pracovní strom“.
  - Zástupné symboly se porovnávají **po jednotlivých klíčích, nikoli po rodině tvarů**: `tools/translation-menu.py` (`validate_blocks`, volba 4) žádá u každého klíče přesně tytéž tokeny `{{…}}` jako v jeho anglické hodnotě a rozdíl u jediného klíče sestavení zastaví. `_one` proto nikdy nepřebírá `{{count}}` jen proto, že ho má sesterský `_other`. Ověřeno ve vydání Orca v1.4.243 u `DeleteWorktreeDirtyChangeHint.changeCount_one`, `SetupScriptPromptCard.savedWithSkippedFields_one` a `workspaceBatchActionLabels.*Count_one`.
  - `_few` a `_many` píšeme přirozenou větou s číslem na svém místě. Základní řetězec zůstává neutrální k počtu.
  - Bez parametru `count` ve volání jsou tvary neúčinné, ať se klíč jmenuje jakkoli.
  - Neskloňované výrazy neměníme („{{count}} PR“), stejně jako popisky bez podstatného jména („Vybráno: {{count}}“).
  - Skript `tools/build.py` přijímá doplňkový tvar pouze tehdy, dokud v katalogu Orca existuje jeho opora. Do počítadla řádků a pokrytí se doplňkové tvary nezapočítávají.
- **Chráněná zóna.** 180 řetězců `auto.components.settings.` + `plugin*` (bez ohledu na velikost písmen) zůstává v angličtině — jejich přepsání engine z bezpečnostních důvodů zakazuje. Bylo jich 214, dokud [PR #12455](https://github.com/stablyai/orca/pull/12455) nevyjmul 34 klíčů rozhraní (nadpisy, prázdné stavy, formulář vývoje): ty nenesou rozhodnutí o důvěryhodnosti. Platí od Orca v1.4.169.
- **Anglické slovo předané jako parametr.** `install.agentsCountLabel` je deklarován jako
  `{{count}} {{label}}`, ale `label` dosazuje komponenta sama — literály `agent` / `agents`
  ([SkillInstallAgentPicker.tsx](https://github.com/stablyai/orca/blob/main/src/renderer/src/components/skills/SkillInstallAgentPicker.tsx)),
  které se do katalogu nedostanou. Překládáme bez tohoto zástupného symbolu — „Agentů: {{count}}“:
  `build.py` na vynechaný `{{label}}` jemně upozorní, což je očekávaný stav.
- **Limit délky řetězce.** 8 192 znaků. Dva řetězce CSS animací přehledu funkcí (9 691 a 9 965 znaků) se fyzicky do balíčku nevejdou a zůstávají v angličtině; třetí (7 055) je čisté CSS, kde není co překládat.
- **Rezerva vůči limitům enginu** k v0.1.0: 18 154 uzlů z 20 000, hloubka 12 z 16, velikost ~1,4 MB z 5 MB.
- **Katalog upstreamu se mění.** `build.py` sám vyřazuje klíče, které zmizely z `en.json`,
  a upozorní pouze v případě, že zastaralý klíč přišel z překladového bloku. Po aktualizaci Orca
  stačí vyměnit `.i18n-work/en.json` a provést nové sestavení.
