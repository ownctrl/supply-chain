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
v dashboardu. Detekci a nápravu řeší
[dont-be-shy-hulud](https://github.com/miccy/dont-be-shy-hulud).

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

## Pod vlastním účtem

Repozitář si zkopíruj, ale **neforkuj ho pro každou organizaci zvlášť.**
Dědění je levnější:

```json
{
  "extends": ["github>ownctrl/supply-chain"],
  "labels": ["dependencies", "tvoje-značka"]
}
```

Fork znamená opravit každou bezpečnostní vadu tolikrát, kolik máš kopií.

## Odkazy

- 🪱 [dont-be-shy-hulud](https://github.com/miccy/dont-be-shy-hulud) — detekce a náprava Shai-Hulud 2.0
- 🔒 [Socket.dev](https://socket.dev) — skenování supply chain
- 📊 [Datadog IOC](https://github.com/DataDog/indicators-of-compromise/tree/main/shai-hulud-2.0) — oficiální IOC seznam
