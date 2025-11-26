# renovate-config

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Renovate enabled](https://img.shields.io/badge/renovate-enabled-brightgreen.svg)](https://renovatebot.com/)
![Ecosystems](https://img.shields.io/badge/ecosystems-9+-blue.svg)
[![GitHub stars](https://img.shields.io/github/stars/miccy/renovate-config?style=social)](https://github.com/miccy/renovate-config)

**🤖 Production-ready shared Renovate preset for automated dependency management**

_Multi-ecosystem • Safe defaults • Smart grouping • Automerge_

</div>

---

## Shared preset

### 🎯 Features

A shared Renovate preset for organizations and personal repos. It keeps noise low while staying safe:

- Groups **all non-major** updates into one PR (per repo), majors stay separate
- Uses **Platform Automerge** (GitHub Native) for faster merging
- Automerges **dev tooling** (Biome, Oxlint, TypeScript, testing libs) and **GitHub Actions** once checks pass
- Automatic **deduplication** for npm/pnpm/yarn lockfiles
- Waits **3 days** (`stabilityDays`) before proposing updates for stability
- Enables weekly **lock file maintenance** with automerge
- **Semantic commits** enabled (`chore(deps): update package`)
- **Vulnerability alerts** with security labels and transitive remediation
- Supports **Bun, npm, pnpm, yarn, Nix, Terraform, Ansible, Docker, GitHub Actions**
- **Pins GitHub Actions** to digests for security

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

1. Create a repository named **`renovate-config`** in your org (or personal account) and push this content.
2. In each target repository, add a minimal `renovate.json`:

```json
{ "extends": ["github>ORG_OR_USER/renovate-config"] }
```

Replace `ORG_OR_USER` with your org (e.g. `ownctrl`) or your username (`miccy`).

3. Install the **Mend Renovate App** for the org and select **All repositories**.

### Bun & Biome & Oxlint

- **Bun** is handled via Renovate's `bun` manager. Commit `bun.lock` (or `bun.lockb`) for reliable updates.
- **Biome** (`@biomejs/*`) is treated as dev tooling and grouped + automerged on non-major updates.
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

- Timezone: `Europe/Prague`, schedule: Mondays before 06:00
- `stabilityDays`: 3 days for stability
- `semanticCommits`: enabled for consistent commit messages
- `prCreation`: not-pending (creates PRs without waiting for checks)
- `rebaseWhen`: behind-base-branch (auto-rebase when behind)
- `prConcurrentLimit`: 4 to avoid PR storms
- `vulnerabilityAlerts`: enabled with security labels
- `lockFileMaintenance`: enabled weekly with automerge
- `ignorePaths`: node_modules, vendor, dist, build
- Groups: non-majors together, majors separate
- Automerge: GitHub Actions, dev tooling, Biome, Oxlint, TypeScript, testing tools
- Docker digests: grouped separately with high priority (manual review)

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

### More aggressive updates

For projects where you want faster updates ([example](./examples/renovate-aggressive.json)):

```json
{
  "extends": ["github>ORG_OR_USER/renovate-config"],
  "schedule": ["at any time"],
  "prConcurrentLimit": 10,
  "stabilityDays": 0
}
```

### Disable automerge

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

---



---

<div align="center">
  <p>🛠 Maintained by <a href="https://github.com/miccy">@miccy</a> with 💙</p>
  <p>© 2025 <a href="https://github.com/miccy">Miccy</a></p>
</div>
