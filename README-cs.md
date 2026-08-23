# supply-chain

**Sdílená supply-chain politika pro aktualizace závislostí**

_Více ekosystémů • Více forgí • Ve výchozím stavu čeká na review_

> English version: [README.md](./README.md)

---

## Co to je

Renovate preset, který zapisuje jediné rozhodnutí: **které aktualizace
závislostí smějí přistát, aniž se na ně někdo podívá.**

Odpověď je záměrně úzká. Důvěryhodné vývojářské nástroje a minor/patch
aktualizace CI akcí se sloučí samy. Produkční závislosti, obnova lockfilu
a holé změny digestu ne — to jsou cesty, kterými se šíří supply-chain útok.

Není to konfigurace pro JavaScript. Vedle JS ekosystémů pokrývá Rust, Nix, Go,
Python, Docker, Terraform, Ansible i CI akce, protože hrozbu nezajímá, v čem
píšeš.

### Proč vznikl

Útok Shai-Hulud 2.0 na npm z listopadu 2025 je původní příběh, ne rozsah.
Vyvolal první verzi a seznam 428 balíčků, ale politika je obecná: počítej
s tím, že se libovolná závislost může mezi dvěma vydáními obrátit proti tobě,
a udělej z toho review místo merge.

Seznam kompromitovaných balíčků se pořád dodává, s podmínkou schválení
v dashboardu. Zasažené rozsahy verzí jsou v
[databázi IOC od Datadogu](https://github.com/DataDog/indicators-of-compromise/tree/main/shai-hulud-2.0).

## Jak to použít

Do nového repozitáře stačí `renovate.json`:

```json
{ "extends": ["github>ownctrl/supply-chain"] }
```

To je celé nastavení. Preset nese schedule, grupování, automerge politiku
i pokrytí ekosystémů — per repo se nekonfiguruje nic.

Pokud nechceš, aby se ti politika měnila pod rukama, připni si vydání:

```json
{ "extends": ["github>ownctrl/supply-chain#v1.0.0"] }
```

### Předpoklady

Dva, oba jednorázové:

1. **Renovate na to repo dosáhne.** Na GitHub.com to znamená nainstalovanou
   Mend Renovate App. Na každém jiném forge si Renovate hostuješ sám — viz níž.
2. **Auto-merge je povolený v nastavení repozitáře.** Preset nastavuje
   `platformAutomerge`, který používá nativní auto-merge GitHubu. S vypnutým
   nastavením Renovate tiše spadne na vlastního bota — funguje to, ale jinak,
   než tenhle preset popisuje.

### Kde Renovate běží

Preset je jen JSON, funguje všude, kde funguje Renovate. Liší se to, jak
Renovate rozjet — a bez práce to je jen na GitHub.com:

| Forge | Jak Renovate běží |
| --- | --- |
| GitHub.com | Mend Renovate App — hostovaná, zdarma, nic nespouštíš |
| GitLab | self-hosted; CI šablona [`renovate-runner`](https://gitlab.com/renovate-bot/renovate-runner) ho pouští jako scheduled pipeline |
| Codeberg / Forgejo / Gitea | self-hosted; Renovate CLI na plánovači |
| Bitbucket | self-hosted |

Je to vlastnost Renovate ekosystému, ne tohoto presetu — narazíš na to
s jakýmkoli presetem i bez něj.

### Co čekat na novém repu

- **Do pondělí se nestane nic.** Schedule je `before 06:00 on monday`
  (Europe/Prague). Není to chyba nastavení — když chceš první běh hned, nastav
  si v repu `"schedule": ["at any time"]`.
- **Dependency Dashboard issue je ovládací panel.** Major verze a známé
  kompromitované balíčky tam čekají na klik.
- **Co se sloučí samo:** důvěryhodné vývojářské nástroje (Biome, Oxlint,
  TypeScript, Vitest, Jest, ESLint, Prettier a jejich scopes) a minor/patch
  aktualizace GitHub akcí. Všechno ostatní otevře PR a počká na tebe.

Poslední bod je záměrný kompromis: produkční závislosti, obnova lockfilu
a holé změny digestu jsou cesty supply-chain útoku, takže na ně review sedí
schválně. Počítej s několika kliky týdně, ne s nulou.

## Presety

Každý z nich je hotový preset, ne úryvek ke kopírování:

| Preset | Reference | Co mění |
| --- | --- | --- |
| base | `github>ownctrl/supply-chain` | politika popsaná výš |
| lockdown | `github>ownctrl/supply-chain:lockdown` | nic se neslučuje samo, 14denní odstup u npm, všechno čeká na schválení |
| no-automerge | `github>ownctrl/supply-chain:no-automerge` | automerge vypnutý, zbytek beze změny |
| aggressive | `github>ownctrl/supply-chain:aggressive` | kdykoli, bez odstupu, vyšší limit PR |

Po **lockdownu** sáhni při aktivním supply-chain incidentu, po **aggressive**
jen když si jsi jistý, že žádný neprobíhá.

Sub-presety dědí base samy, takže se neuvádějí oba.

## Souhrn politiky

| Nastavení | Hodnota | Důvod |
| --- | --- | --- |
| `minimumReleaseAge` | 7 dní | vyhýbá se čerstvě vydaným balíčkům (jako packageRule pro npm, který přebíjí hodnotu z nejvyšší úrovně) |
| `security:minimumReleaseAgeNpm` | zapnuto | vyhýbá se čerstvě vydaným a odpublikovaným balíčkům |
| `rangeStrategy` | pin | přesné verze (npm, bun, deno) |
| `prConcurrentLimit` | 4 | proti záplavě PR |
| `schedule` | pondělí 06:00 | týdenní aktualizace |
| `timezone` | Europe/Prague | místní čas |
| `automerge` (produkční) | ❌ vypnuto | vyžaduje bezpečnostní review |
| `automerge` (důvěryhodné dev) | ✅ zapnuto | Biome, TypeScript, Vitest a spol. |
| `vulnerabilityAlerts` | ✅ zapnuto | s bezpečnostními štítky |
| `lockFileMaintenance` | ✅ týdně | review nutné — odstup se sem nevztahuje |

## JS runtimy a package managery

Renovate tu má tři managery a to rozdělení není to, co bys čekal:

- **`npm`** pokrývá npm, pnpm **i** yarn. Samostatný `pnpm` ani `yarn` manager
  neexistuje — jsou to tři lockfily jednoho manageru.
- **`bun`** je vlastní manager (`bun.lock`, `bun.lockb`). Lockfile commituj.
- **`deno`** je vlastní manager (`deno.json`, `deno.jsonc`, `deno.lock`)
  a čerpá z datasources npm, jsr a deno.

`.bun-version` obsluhuje manager `bun-version`.

**Nub** nepotřebuje nic zvláštního. Čte a zapisuje ten lockfile, který projekt
už má (`package-lock.json`, `pnpm-lock.yaml`, `bun.lock`), takže Renovate dál
používá odpovídající manager a nub si výsledek přečte. Obnovu lockfilu ale
provádí ten původní package manager, ne nub.

## Lokální validace

```bash
./tooling/validate.sh
```

Stejný seznam presetů, jaký kontroluje CI. Jako pre-push hook:

```bash
ln -s ../../tooling/validate.sh .git/hooks/pre-push
```

Lokální hook je pohodlí, ne hranice — dá se přeskočit. Skutečný gate zůstává
CI.

Pozor na jedno omezení: **`renovate-config-validator` nevaliduje názvy
managerů.** `matchManagers: ["npm", "pnpm", "yarn"]` projde čistě a nematchuje
nic. Gate pokrývá schéma, ne význam.

### Co gate kontroluje

`validate.sh` pouští dvě věci a ta druhá je důležitější:

- `renovate-config-validator --strict` — presety jsou správně zapsané
- `tooling/test_policy.py` — presety **rozhodují** to, co mají

Validátor kontroluje tvar, ne význam. Každá chyba, kterou tenhle preset vydal,
jím prošla: neukotvený vzor dávající důvěru namespace, který nikdo nevlastní,
pravidlo zařazené tak, že rušilo to nad sebou, dva neexistující názvy managerů.
Policy test je má zmrazené jako případy a spadne, kdyby obnova lockfilu zase
dostala automerge.

Renovate matching reimplementuje, místo aby volal Renovate, takže se od
skutečného enginu může rozejít. Selhání je důvod se podívat; průchod je slabší
důkaz než dry run.

## Tři způsoby, jak si to vzít, a co který stojí

**Jen dědit.** Opravy k tobě dorazí ve chvíli, kdy vzniknou. Nic neudržuješ.

```json
{ "extends": ["github>ownctrl/supply-chain"] }
```

**Dědit a přebít.** Totéž plus vlastní doplňky. Tohle použij pro druhou značku
nebo tým místo forku — jedna bezpečnostní oprava by se neměla dělat tolikrát,
kolik máš kopií.

```json
{
  "extends": ["github>ownctrl/supply-chain"],
  "labels": ["dependencies", "tvoje-značka"]
}
```

**Vzít si kopii.** Tenhle repozitář je GitHub template. Sáhni po něm, když
politiku potřebuješ vlastnit — odstřižené prostředí, požadavek na compliance,
nesouhlas s nějakým rozhodnutím tady.

Ale ber to s cenovkou: **kopie přestane dostávat opravy.** V tomhle presetu
se našly čtyři vady, na které by nikdo nepřišel čtením dokumentace, a kopie
vzatá před kteroukoli z nich si ji nechala. U bezpečnostní politiky je tohle
ten drahý směr.

Když chceš vlastní adresu **i** opravy, ať tvoje kopie dědí odsud:

```json
{
  "extends": ["github>ownctrl/supply-chain"],
  "packageRules": [ /* jen tvoje odchylky */ ]
}
```

Workflow `Setup Owner` po ručním spuštění přepíše reference a LICENSE na
nového vlastníka.

## Co to nedělá

Preset rozhoduje, které aktualizace závislostí smějí přistát bez lidského
pohledu. To je celý jeho rozsah a stojí za to říct natvrdo, kde končí:

- **Hlídá aktualizace, ne to, co už máš.** Hostilní verze, která ti už leží
  v lockfilu, je mimo jeho dosah. Zkontroluj lockfile přímo a rotuj všechno, na
  co ten balíček mohl dosáhnout.
- **Není to skener.** Neprohlíží obsah balíčků, neověřuje, že vydaný artefakt
  odpovídá zdrojáku, ani nedetekuje kompromitaci. Kombinuj ho s něčím, co to
  umí.
- **Odstup není záruka.** `minimumReleaseAge` kupuje čas, aby si někdo jiný
  všiml špatného vydání. Nemusí si všimnout nikdo. Shai-Hulud zůstal
  u některých balíčků nepovšimnutý déle než sedm dní.
- **Watch list je snímek.** 428 balíčků známých z jednoho útoku v listopadu
  2025. O tom příštím neříká nic.
- **Policy test reimplementuje Renovate matching**, místo aby volal Renovate,
  takže se od skutečného enginu může rozejít.

Poskytováno tak, jak je, bez záruky, pod [licencí MIT](./LICENSE). Rozhodnutí,
co smí tvůj projekt sloučit bez dozoru, je tvoje; tenhle preset je výchozí bod
s odůvodněním, ne náhrada za to rozhodnutí.

## Workflow `Setup Owner`

`.github/workflows/setup-owner.yml` je tu pro cestu s kopií. Po ručním
spuštění přepíše reference presetu a copyright v LICENSE na nového vlastníka
a pak sám sebe smaže.

Běží s `contents: write` a pushuje na výchozí větev, což k té práci potřebuje.
Je jen `workflow_dispatch` — nic ho nespouští automaticky. Když preset dědíš
místo kopírování, nikdy ho nepustíš.

## Verzování

`main` je to, co dostane každý, kdo si nepinnul `github>ownctrl/supply-chain` —
ten má každý merge okamžitě. Tagy jsou pro ty, kdo pinnuli. Mergovat můžeš, jak
často chceš; tag řež, až má pinnutý konzument důvod se pohnout.

Není tu žádné API k verzování. Konzument z presetu dostává jedinou věc —
**co se sloučí, aniž se na to podívá** — a to je to, co číslo sleduje.

| | Význam | Příklad |
| --- | --- | --- |
| **MAJOR** | něco se nově slučuje samo, co dřív čekalo, nebo přestane fungovat existující config | přidání balíčku mezi důvěryhodné; přejmenování sub-presetu |
| **MINOR** | nové pokrytí, které nic neuvolňuje | nový ekosystém, nový sub-preset, další balíčky na watch listu |
| **PATCH** | o slučování se nemění nic | dokumentace, text v PR, náš vlastní pin nástrojů |

Ta asymetrie je záměrná. **Utažení je minor, uvolnění je major**, i když je diff
stejně velký. Když něco přestane automergovat, nejhorší následek je pár kliků
navíc. Když něco začne automergovat, obešel jsi důvod, proč si ten člověk pin
dal — pin je příslib, že se posture nezmění pod rukama.

Takže přidat jeden balíček mezi důvěryhodné je major, i kdyby to byl jeden
řádek.

## Odkazy

- 🔒 [Socket.dev](https://socket.dev) — skenování supply chain
- 📊 [Datadog IOC](https://github.com/DataDog/indicators-of-compromise/tree/main/shai-hulud-2.0) — oficiální IOC seznam

<div align="right">
  <a href="#top"><img src="https://img.shields.io/badge/%E2%96%B2_Scroll-Top_%E2%96%B2-white?style=plastic&labelColor=black&color=white" alt="Scroll Top"/></a>
</div>

---

<div align="center">
  <a href="https://github.com/miccy"><img src="https://img.shields.io/badge/%F0%9F%A9%B7_Maintained%20by-%40miccy-white?style=plastic&labelColor=black&color=white" alt="Maintained by @miccy"/></a>
  <a href="https://github.com/ownctrl"><img src="https://img.shields.io/badge/%C2%A92026-ownCTRL%E2%84%A2-white?style=plastic&labelColor=black&color=white" alt="© 2026 ownCTRL™"/></a>
</div>
