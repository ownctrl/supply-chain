# renovate-config

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Renovate enabled](https://img.shields.io/badge/renovate-enabled-brightgreen.svg)](https://renovatebot.com/)
![Ecosystems](https://img.shields.io/badge/ecosystems-9+-blue.svg)
[![GitHub stars](https://img.shields.io/github/stars/miccy/renovate-config?style=social)](https://github.com/miccy/renovate-config)

**🤖 Production-ready shared Renovate preset for automated dependency management**

_Multi-ecosystem • Security-hardened • Smart grouping • Supply chain protection_

</div>

---

## ⚠️ Security Notice: Shai-Hulud 2.0

> **This preset has been hardened in response to the Shai-Hulud 2.0 npm supply chain attack (November 2025).**

Key security measures included:
- 🛡️ **7-day stability period** before updates are proposed
- 🔒 **No automerge for production dependencies**
- ⚠️ **Warnings on known compromised packages**
- 📋 **Dashboard approval required for majors**
- 🔗 **`npm:unpublishSafe`** preset to avoid unpublished packages

For more information, see [dont-be-shy-hulud](https://github.com/miccy/dont-be-shy-hulud).

---

## Shared preset

### 🎯 Features

A shared Renovate preset for organizations and personal repos. Security-first with smart defaults:

- **7-day `stabilityDays`** and `minimumReleaseAge` for supply chain protection
- **No automerge for production deps** — only trusted dev tooling automerges
- **`npm:unpublishSafe`** preset — avoids packages that might be unpublished
- Groups **all non-major** updates into one PR, majors stay separate
- Uses **Platform Automerge** (GitHub Native) for faster merging of approved PRs
- Automerges only **trusted dev tooling** (Biome, Oxlint, TypeScript, Vitest, ESLint, Prettier)
- Automatic **deduplication** for npm/pnpm/yarn lockfiles
- Weekly **lock file maintenance**, review required (`minimumReleaseAge` does not gate lockfile refreshes)
- **Semantic commits** enabled (`chore(deps): update package`)
- **Vulnerability alerts** with security labels
- **Pins GitHub Actions** to digests; automerges minor/patch only, never a bare digest move
- **Warnings on Shai-Hulud affected packages**
- Supports **Bun, npm, pnpm, yarn, Nix, Terraform, Ansible, Docker, GitHub Actions**

### 🛠️ Supported Ecosystems

<div align="center">

| Category            | Technologies                         |
| ------------------- | ------------------------------------ |
| **JavaScript/Node** | npm • pnpm • yarn • Bun              |
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
{ "extends": ["github>miccy/renovate-config"] }
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

### Using it under your own account

Fork or copy this repo, then reference your own copy
(`github>ORG_OR_USER/renovate-config`). The `Setup Owner` workflow rewrites the
examples and LICENSE to the new owner when you dispatch it manually.

### Bun & Biome & Oxlint

- **Bun** is handled via Renovate's `bun` manager. Commit `bun.lock` (or `bun.lockb`) for reliable updates.
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
| `npm:unpublishSafe` | enabled | Avoid unpublished packages |
| `rangeStrategy` | pin | Lock exact versions |
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

## Common overrides

See practical examples in [`examples/`](./examples/) directory.

### 🔒 Lockdown Mode (Active Threats)

For maximum security during active supply chain attacks ([example](./examples/renovate-lockdown.json)):

```json
{
  "extends": ["github>ORG_OR_USER/renovate-config"],
  "stabilityDays": 14,
  "minimumReleaseAge": "14 days",
  "prConcurrentLimit": 2,
  "dependencyDashboardApproval": true,
  "packageRules": [
    {
      "matchPackagePatterns": ["*"],
      "automerge": false
    }
  ]
}
```

### 🛡️ Security-Hardened (Recommended)

Balanced security without too much friction ([example](./examples/renovate-security-hardened.json)):

```json
{
  "extends": ["github>ORG_OR_USER/renovate-config"],
  "stabilityDays": 7,
  "minimumReleaseAge": "7 days",
  "packageRules": [
    {
      "matchDepTypes": ["dependencies"],
      "automerge": false
    }
  ]
}
```

### More aggressive updates

For non-critical projects where you want faster updates ([example](./examples/renovate-aggressive.json)):

```json
{
  "extends": ["github>ORG_OR_USER/renovate-config"],
  "schedule": ["at any time"],
  "prConcurrentLimit": 10,
  "stabilityDays": 0
}
```

⚠️ **Warning**: Not recommended during active supply chain threats!

### Disable automerge completely

For critical projects requiring manual review ([example](./examples/renovate-no-automerge.json)):

```json
{
  "extends": ["github>ORG_OR_USER/renovate-config"],
  "packageRules": [
    {
      "matchPackagePatterns": ["*"],
      "automerge": false
    }
  ]
}
```

### Custom timezone

For teams in different timezones:

```json
{
  "extends": ["github>ORG_OR_USER/renovate-config"],
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
