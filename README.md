# supply-chain

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Renovate enabled](https://img.shields.io/badge/renovate-enabled-brightgreen.svg)](https://renovatebot.com/)
![Ecosystems](https://img.shields.io/badge/ecosystems-10+-blue.svg)

**Shared supply-chain policy for dependency updates**

_Multi-ecosystem • Multi-forge • Review-gated by default_

</div>

---

## What this is

A Renovate preset that encodes one decision: **which dependency updates are
allowed to land without a human looking at them, and which are not.**

The answer is deliberately narrow. Trusted dev tooling and minor/patch CI
action bumps automerge. Production dependencies, lockfile refreshes and bare
digest moves do not — those are the paths a supply-chain attack travels.

It is not a JavaScript config. It covers Rust, Nix, Terraform, Ansible, Docker
and CI actions alongside the JS ecosystems, because the threat model does not
care what language you write.

### Why it exists

The Shai-Hulud 2.0 npm attack in November 2025 is the origin story, not the
scope. It prompted the first version and the 428-package watch list, but the
policy here is general: assume any dependency can turn hostile between one
release and the next, and make the blast radius a review instead of a merge.

The watch list still ships, gated behind dashboard approval. See
[dont-be-shy-hulud](https://github.com/miccy/dont-be-shy-hulud) for detection
and remediation.

## Shared preset

### 🎯 Features

- **7-day `minimumReleaseAge`**, set as a packageRule for npm so it actually
  applies — a top-level value is outranked by the inherited npm rule
- **`security:minimumReleaseAgeNpm`** — avoids freshly published and
  unpublished packages
- **No automerge for production deps** — only trusted dev tooling automerges
- Groups **all non-major** updates into one PR, majors stay separate
- Uses **Platform Automerge** (GitHub Native) for faster merging of approved PRs
- Automerges only **trusted dev tooling** (Biome, Oxlint, TypeScript, Vitest,
  Jest, ESLint, Prettier), matched on anchored names so neighbouring packages
  in unowned npm prefixes cannot inherit the trust
- Automatic **deduplication** for npm/pnpm/yarn lockfiles
- Weekly **lock file maintenance**, review required (`minimumReleaseAge` does
  not gate lockfile refreshes)
- **Semantic commits** enabled (`chore(deps): update package`)
- **Vulnerability alerts** with security labels
- **Pins GitHub Actions** to digests; automerges minor/patch only, never a bare
  digest move
- **428 known-compromised packages** gated behind dashboard approval
- Supports **npm, pnpm, yarn, Bun, Deno, Rust, Nix, Terraform, Ansible,
  Docker, GitHub Actions**

### 🛠️ Supported Ecosystems

<div align="center">

| Category            | Technologies                         |
| ------------------- | ------------------------------------ |
| **JavaScript/Node** | npm • pnpm • yarn • Bun • Deno       |
| **Systems**         | Rust (cargo)                         |
| **System & Infra**  | Nix • Terraform • Ansible            |
| **Containers**      | Docker                               |
| **CI/CD**           | GitHub Actions                       |
| **Languages**       | TypeScript • Python (pip) • Go (mod) |
| **Linting**         | Biome • Oxlint                       |
| **Testing**         | Vitest • Jest                        |

</div>

## How to use

Drop this file into a new repo and you are done:

```json
{ "extends": ["local>ownctrl/supply-chain"] }
```

That is the whole setup. The preset carries the schedule, grouping, automerge
policy and ecosystem coverage — there is nothing else to configure per repo.

The one prerequisite is that the **Mend Renovate App** is installed for the
account or org and has access to the repo.

### What to expect on a fresh repo

- **Nothing happens until Monday.** The schedule is `before 06:00 on monday`
  (Europe/Prague). This is not a misconfiguration — set `"schedule": ["at any
  time"]` in your repo if you want the first run immediately.
- **The Dependency Dashboard issue is the control surface.** Majors and
  known-compromised packages wait there for a click.
- **What automerges on its own:** trusted dev tooling (Biome, Oxlint,
  TypeScript, Vitest, Jest, ESLint, Prettier and their scopes) and minor/patch
  GitHub Action bumps. Everything else opens a PR and waits for you.

That last point is the deliberate trade-off: production dependencies, lockfile
refreshes and bare digest moves are the paths a supply-chain attack travels, so
they are review-gated by design. Expect a handful of clicks a week, not zero.

### `local>` and why it is not `github>`

`local>` resolves against whichever forge Renovate is currently running on, so
the same line works on GitHub, GitLab, Codeberg and self-hosted Forgejo,
provided the preset repo is mirrored there under the same path. Use
`github>ownctrl/supply-chain` only if you want to pin to GitHub specifically
from another forge.

Pin a release if you do not want your policy to change under you:

```json
{ "extends": ["local>ownctrl/supply-chain#v1.0"] }
```

### Using it under your own account

Copy this repo, then reference your own copy. Do **not** fork it per
organisation — inherit instead, so one security fix does not have to be applied
once per copy:

```json
{
  "extends": ["local>ownctrl/supply-chain"],
  "labels": ["dependencies", "yourbrand"]
}
```

The `Setup Owner` workflow rewrites the examples and LICENSE to the new owner
when you dispatch it manually.

### JavaScript runtimes and package managers

Renovate has three managers here, and the split is not the one you would guess:

- **`npm`** covers npm, pnpm **and** yarn. There is no separate `pnpm` or
  `yarn` manager — all three are the same manager reading different lockfiles.
- **`bun`** is its own manager (`bun.lock`, `bun.lockb`). Commit the lockfile.
- **`deno`** is its own manager (`deno.json`, `deno.jsonc`, `deno.lock`) and
  pulls from the npm, jsr and deno datasources.

`.bun-version` is picked up by the `bun-version` manager.

**Nub** needs nothing special. It reads and writes whichever lockfile the
project already has (`package-lock.json`, `pnpm-lock.yaml`, `bun.lock`), so
Renovate keeps using the matching manager and nub reads the result. Note that
lockfile refreshes are performed by the incumbent package manager, not by nub.

### Biome & Oxlint

- **Biome** (`@biomejs/*`) is treated as trusted dev tooling and grouped + automerged on non-major updates.
- **Oxlint** (`oxlint`, `@oxc-project/*`) follows the same pattern as Biome.

### Nix & NixOS

- **Nix Flakes** are supported via Renovate's `nix` manager. Commit your `flake.lock` file for reliable updates.
- Nix dependencies are grouped together with higher priority (`prPriority: 5`).
- Renovate will automatically update inputs in your `flake.lock` when new versions are available.

### Terraform & Ansible

- **Terraform** modules and providers are managed via the `terraform` manager. Works with `main.tf`, `versions.tf`, and other Terraform files.
- **Ansible** Galaxy roles and collections are supported via the `ansible` manager (looks for `requirements.yml` or `galaxy.yml`).
- Both are grouped separately with higher priority (`prPriority: 5`) for infrastructure changes.

### Socket.dev & Dependabot Compatibility

- **Socket.dev** works perfectly with Renovate - they complement each other. Socket provides supply chain security scanning, while Renovate handles updates. Socket can block problematic PRs from Renovate.
- **Dependabot Alerts** - keep them enabled for security notifications. Remove `.github/dependabot.yml` if you used Dependabot "version updates" to avoid duplicate PRs.

## Policy summary

| Setting | Value | Reason |
|---------|-------|--------|
| `minimumReleaseAge` | 7 days | Avoid freshly published packages (set as a packageRule for npm, which outranks the top-level value) |
| `security:minimumReleaseAgeNpm` | enabled | Avoid freshly published and unpublished packages |
| `rangeStrategy` | pin | Lock exact versions (npm, bun, deno) |
| `prConcurrentLimit` | 4 | Avoid PR storms |
| `schedule` | Mondays 06:00 | Weekly updates |
| `timezone` | Europe/Prague | Local timezone |
| `automerge` (prod deps) | ❌ disabled | Security review required |
| `automerge` (trusted dev) | ✅ enabled | Biome, TypeScript, Vitest, etc. |
| `vulnerabilityAlerts` | ✅ enabled | With security labels |
| `lockFileMaintenance` | ✅ weekly | Review required — the age gate does not apply here |

## Testing locally

You can test this config locally before deploying:

```bash
# Install Renovate CLI
npm install -g renovate

# Run in dry-run mode (no changes made)
LOG_LEVEL=debug renovate --platform=local --dry-run=true

# Or use npx without installing
npx renovate --platform=local --dry-run=true
```

## Presets

Each of these is a ready preset, not a snippet to copy. Reference it directly:

| Preset | Reference | What it changes |
| --- | --- | --- |
| base | `local>ownctrl/supply-chain` | the policy described above |
| lockdown | `local>ownctrl/supply-chain:lockdown` | nothing automerges, 14-day npm floor, every update waits for dashboard approval |
| no-automerge | `local>ownctrl/supply-chain:no-automerge` | automerge off, everything else unchanged |
| aggressive | `local>ownctrl/supply-chain:aggressive` | any time, no release-age floor, higher PR limit |

Reach for **lockdown** during an active supply-chain incident and **aggressive**
only when you are certain there is not one.

```json
{ "extends": ["local>ownctrl/supply-chain:lockdown"] }
```

Sub-presets extend the base themselves, so you do not list both.

### Custom timezone

For teams in different timezones:

```json
{
  "extends": ["local>ownctrl/supply-chain"],
  "timezone": "America/New_York",
  "schedule": ["before 09:00 on monday"]
}
```

## Shai-Hulud Affected Packages

This preset includes warnings for packages affected by the Shai-Hulud 2.0 attack. When Renovate proposes updates for these packages, the PR will include:

- ⚠️ Security warning banner
- Checklist for verification
- Links to IOC lists

**Currently monitored packages: 428**

Sourced from the Datadog IOC database. These are gated behind dashboard approval with a warning attached — not blocked, so fixed versions can still land.

For the complete list, see [dont-be-shy-hulud IOC database](https://github.com/miccy/dont-be-shy-hulud/blob/main/ioc/malicious-packages.json).

---

## Related Resources

- 🪱 [dont-be-shy-hulud](https://github.com/miccy/dont-be-shy-hulud) — Shai-Hulud 2.0 detection and remediation guide
- 🔒 [Socket.dev](https://socket.dev) — Supply chain security scanning
- 📊 [Datadog IOCs](https://github.com/DataDog/indicators-of-compromise/tree/main/shai-hulud-2.0) — Official IOC list

---

<div align="center">
  <p>🛠 Maintained by <a href="https://github.com/miccy">@miccy</a> with 💙</p>
  <p>© 2025 <a href="https://github.com/miccy">Miccy</a></p>
</div>
