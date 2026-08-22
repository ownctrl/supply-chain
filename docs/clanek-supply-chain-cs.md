---
title: "Váš robot na aktualizace závislostí je taky cesta dovnitř"
perex: "Automatické aktualizace závislostí jsou dnes standard. Málokdo si přitom přečte, co přesně jeho konfigurace dovoluje sloučit bez lidského oka. Když jsme si to přečetli my, našli jsme čtyři díry — a tři z nich by nenašel nikdo, kdo jen následuje dokumentaci."
tags: [supply-chain, renovate, bezpečnost, open-source]
lang: cs
draft: true
---

## Útok, který nepotřebuje vaši chybu

V listopadu 2025 se npm ekosystémem prohnal Shai-Hulud 2.0. Nešlo o díru
v něčím kódu. Šlo o to, že se útočník dostal k publikačním právům legitimních
balíčků a vydal novou verzi — a všechno, co ten balíček používalo v rozsahu
semver, si ji samo stáhlo.

To je na tom to podstatné a je dobré si to říct nahlas: **vy jste neudělali
nic špatně.** Váš kód se nezměnil. Změnilo se něco, čemu jste se rozhodli
věřit, a ta důvěra byla vyjádřená stříškou ve `package.json`.

Obrana proti tomuhle není lepší kód. Je to politika. Konkrétně odpověď na
jedinou otázku:

> Které aktualizace závislostí smějí přistát, aniž se na ně někdo podívá?

Většina týmů na tuhle otázku nikdy vědomě neodpověděla. Odpověděl za ně
výchozí config jejich bota.

## Co je supply-chain

[`ownctrl/supply-chain`](https://github.com/ownctrl/supply-chain) je sdílený
preset pro [Renovate](https://renovatebot.com), který tu odpověď zapisuje
explicitně. Vezmete si ho jedním řádkem:

```json
{ "extends": ["local>ownctrl/supply-chain"] }
```

A to je celé nastavení. Žádný per-repo tuning.

Odpověď, kterou ten preset dává, je záměrně úzká:

**Sloučí se samo:** důvěryhodné vývojářské nástroje (Biome, Oxlint,
TypeScript, Vitest, Jest, ESLint, Prettier) a minor/patch aktualizace CI akcí.

**Počká na vás:** produkční závislosti, obnova lockfilu, holé změny digestu
a všechny major verze.

Ta druhá skupina není seznam nepohodlných výjimek. To jsou přesně cesty,
kterými se supply-chain útok šíří.

## Čtyři věci, které jsme našli ve vlastním configu

Preset jsme napsali jako reakci na Shai-Hulud. O devět měsíců později jsme si
ho pořádně přečetli. Tady je, co v něm bylo — a proč to jsou obecné pasti, ne
naše specifické hlouposti.

### 1. Sedmidenní odstup nikdy neplatil

V configu stálo `"minimumReleaseAge": "7 days"`. V README stálo, že čekáme
sedm dní, než balíček navrhneme. Obojí byla pravda o tom, co jsme napsali,
a lež o tom, co se dělo.

Preset totiž dědil `security:minimumReleaseAgeNpm`, který nastavuje **tři dny
přes `packageRule`**. A `packageRule` přebíjí hodnotu z nejvyšší úrovně. Takže
npm — ekosystém, kvůli kterému ten preset vůbec vznikl — jel na třech dnech.

To je past, do které spadne každý, kdo kombinuje vlastní hodnoty s děděnými
presety. **Nastavení na nejvyšší úrovni je slabší než pravidlo, ne silnější.**

### 2. `^jest` je celý cizí namespace

Měli jsme seznam „důvěryhodných" nástrojů, které se smějí slučovat samy.
Vypadal rozumně: `^jest`, `^vitest`, `^oxlint`.

Jenže to jsou regulární výrazy bez ukotvení konce. `^jest` neodpovídá balíčku
`jest`. Odpovídá **každému balíčku, jehož název začíná na `jest`** — a prefix
`jest-` na npm nikdo nevlastní. Může do něj publikovat kdokoli.

Kdokoli by tedy mohl vydat `jest-cokoli`, vy byste si to jednou přidali jako
vývojářskou závislost, a od té chvíle by se jeho aktualizace slučovaly bez
review. S důvěrou, kterou jste chtěli dát projektu Jest.

**Ukotvujte celý název**, pokud není ve scope, který vlastníte. `^jest$` ano.
`^@testing-library/` taky ano, protože npm scopes vlastníka mají. `^jest` ne.

### 3. Obnova lockfilu obchází všechny brzdy

Renovate umí týdně přegenerovat lockfile, aby stáhl nejnovější verze v rámci
existujících rozsahů. Měli jsme to zapnuté a slučovalo se to samo.

Ta funkce ale **nepodléhá `minimumReleaseAge`**. Renovate to říká ve vlastní
dokumentaci: kontrola stáří se nevztahuje na `pin`, `lockFileMaintenance`,
`lockfileUpdate`, `rollback`, `bump` ani `replacement`.

Takže každé pondělí ráno se každá tranzitivní závislost posunula na nejnovější
vyhovující verzi, bez jakéhokoli odstupu a bez review. Tranzitivní šíření
uvnitř semver rozsahů je přesně to, jak Shai-Hulud cestoval.

Vypnuli jsme to. Stojí to jeden klik týdně.

### 4. Validátor nechytá to, co byste čekali

Přidali jsme do CI `renovate-config-validator --strict`. Hned se to vyplatilo:
zachytil chybu v opravě, kterou jsme psali o commit dřív, a která by způsobila,
že Renovate celé pravidlo zahodí — díra by zůstala otevřená, ale vypadalo by to
opravené.

Jenže má hranice, které stojí za to znát. Config obsahoval
`matchManagers: ["npm", "pnpm", "yarn"]`. **`pnpm` ani `yarn` nejsou managery**
— všechny tři lockfily obsluhuje manager `npm`. Ty dva zápisy neodpovídaly
ničemu.

Validátor to pustil bez jediného varování. Ověřovali jsme to schválně.

Horší bylo, co z toho plynulo: manager `bun` je samostatný a v tom pravidle
chyběl. Repozitáře, které jedou výhradně na bunu, nedostávaly pinování verzí,
které jsme v README inzerovali jako základní vlastnost.

**Váš CI gate kontroluje schéma, ne význam.** Překlep v názvu manageru tiše
vypne celé pravidlo.

## Co to usnadňuje

Praktický zisk není „bezpečnost" jako abstraktní pocit. Je konkrétní:

- **Nové repo je hotové jedním řádkem.** Žádné kopírování konfigurace, žádné
  rozhodování, žádný per-projekt tuning.
- **Jedna oprava platí všude.** Když se objeví další Shai-Hulud, upravíte
  jeden soubor, ne dvacet repozitářů.
- **Politika je čitelná.** Můžete ji někomu ukázat. Můžete se o ní hádat.
  To o výchozím nastavení bota nejde.
- **Nezáleží na jazyce.** JavaScript, Rust, Go, Python, JVM, .NET, PHP, Ruby,
  Nix, Terraform, Docker, Kubernetes. Hrozba se o váš jazyk nezajímá, tak proč
  by se měla politika.

## Jak si ho vzít a upravit

### Základ

Do nového repozitáře stačí `renovate.json`:

```json
{ "extends": ["local>ownctrl/supply-chain"] }
```

Prefix `local>` je tu záměrně. Řekne Renovate, ať preset hledá na tom forge,
kde zrovna běží — takže tentýž řádek funguje na GitHubu, GitLabu, Codebergu
i na vlastním Forgejo, pokud je preset zrcadlený pod stejnou cestou.

### Když zrovna hoří

Při aktivním incidentu si přepněte do lockdownu. Nic se neslučuje samo,
čtrnáctidenní odstup, všechno čeká na schválení:

```json
{ "extends": ["local>ownctrl/supply-chain:lockdown"] }
```

### Když nehoří a spěcháte

Pro nekritické projekty:

```json
{ "extends": ["local>ownctrl/supply-chain:aggressive"] }
```

Žádný odstup, aktualizace kdykoli. Nepoužívejte to, když si nejste jistí, že
zrovna neprobíhá útok.

### Přepsání jednotlivostí

Cokoli z presetu jde přebít ve vlastním souboru. Ale pozor na past číslo 1 —
pokud přepisujete něco, co je v presetu nastavené jako `packageRule`, musíte
to taky napsat jako `packageRule`:

```json
{
  "extends": ["local>ownctrl/supply-chain"],
  "packageRules": [
    { "matchDatasources": ["npm"], "minimumReleaseAge": "14 days" }
  ]
}
```

Nastavení `"minimumReleaseAge": "14 days"` na nejvyšší úrovni by tady
nefungovalo. Přesně tak jsme si tu chybu vyrobili my.

### Pro vlastní organizaci

Repozitář si zkopírujte, ale **neforkujte ho pro každou značku zvlášť.**
Dědění je levnější:

```json
{
  "extends": ["local>ownctrl/supply-chain"],
  "labels": ["dependencies", "vaše-značka"]
}
```

Fork znamená opravit každou bezpečnostní vadu tolikrát, kolik máte kopií.
Ty čtyři výše bychom opravovali čtyřikrát.

Pokud nechcete, aby se vám politika měnila pod rukama, připněte si vydání:

```json
{ "extends": ["local>ownctrl/supply-chain#v1.0"] }
```

## Co si z toho odnést, i když náš preset nepoužijete

1. **Přečtěte si, co váš bot smí sloučit sám.** Ne co si myslíte, že smí.
2. **Ukotvujte vzory názvů**, pokud nejste vlastníkem prefixu nebo scope.
3. **Zjistěte, které typy aktualizací obcházejí vaše brzdy.** U Renovate to
   jsou `lockFileMaintenance`, `pin`, `bump`, `rollback` a `replacement`.
4. **Nezaměňujte validaci schématu za validaci významu.** Zelené CI neznamená,
   že vaše pravidla něčemu odpovídají.

Nic z toho není v dokumentaci označené jako past. Všechno to jsou důsledky
dvou pravidel, která dávají samostatně smysl a dohromady vás překvapí.

---

*Preset je pod MIT licencí. Chyby, nápady a nesouhlas vítáme —
[ownctrl/supply-chain](https://github.com/ownctrl/supply-chain).*
