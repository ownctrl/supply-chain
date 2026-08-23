# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-08-23

### Added

- `tooling/test_policy.py` — asserts what the presets *decide*, not just that
  they are well formed. 22 cases over the automerge decision, plus guards on
  the lockfile gate and on manager names Renovate does not have. Every fault
  this preset has shipped passed the schema validator; these freeze them.
- `SECURITY.md` — where to report, what this preset does not do, and its known
  limitations.
- Biome runs in the gate, pinned to the version `biome.json` declares.
- README states what the preset does not do, documents the `Setup Owner`
  workflow, and gives the three adoption paths with the cost of each. A copy
  stops receiving fixes; that is now said out loud.

### Changed

- The custom manager keeps both pinned tools updated, not only renovate.
- JSON formatted by Biome. Verified to change no meaning.

## [1.0.1] - 2026-08-23

### Fixed

- Stopped linking readers to a repository they cannot open. `dont-be-shy-hulud`
  is not publicly reachable, and it was referenced five times — including in
  `prBodyNotes`, so every pull request for a watch-listed package handed the
  reader a dead link in place of a remediation step. Replaced with checks that
  can be performed without it, including credential rotation.
- Documentation now names `github>` consistently. The English README recommended
  `local>`, which resolves against the current forge and only pays off once the
  preset is mirrored to each of them.

### Changed

- Ecosystem table lists the managers actually configured, rather than naming
  Biome, Oxlint and Vitest as if they were ecosystems.

### Added

- Czech README (`README-cs.md`), linked from the English one.

## [1.0.0] - 2026-08-23

First tagged release. Renamed from `renovate-config` to `supply-chain`: the old
name described the tool, not the job.

### Fixed

Four faults, all live, none findable by reading the documentation:

- **The 7-day npm floor never applied.** `security:minimumReleaseAgeNpm` sets
  3 days through a `packageRule`, and a `packageRule` outranks the top-level
  value. npm ran on a 3-day floor while the README promised 7.
- **`^jest` matched an unowned namespace.** Unanchored, it matched every
  `jest-*` package on npm — a prefix anyone can publish into — and those
  automerged with the trust intended for Jest. Same for `^vitest` and
  `^oxlint`.
- **`lockFileMaintenance` bypassed the age gate entirely** and automerged.
  Renovate excludes it from `minimumReleaseAge`, along with `pin`,
  `lockfileUpdate`, `rollback`, `bump` and `replacement`.
- **`pnpm` and `yarn` are not managers.** The `npm` manager handles all three
  lockfiles. `bun` is separate and was missing from the pinning rule, so
  bun-only repos got no version pinning at all.

Also fixed: GitHub Actions automerged majors and bare digest moves, the
per-tool rules re-granted automerge after the anchored trust list, and command
injection in the `setup-owner` workflow.

### Added

- Sub-presets: `:lockdown`, `:no-automerge`, `:aggressive`. Previously copy-paste
  examples, now referenceable directly.
- Ecosystem coverage: Rust, Go, Python, JVM, .NET, PHP, Ruby, Dart, Swift,
  Kubernetes and Deno alongside the JS ecosystems, Nix, Terraform, Ansible and
  Docker.
- CI validation with `renovate-config-validator --strict`, and
  `tooling/validate.sh` so the same check runs locally. It caught a real error
  in one of the fixes above.
- Shai-Hulud 2.0 watch list expanded to 428 packages from the
  [Datadog IOC database](https://github.com/DataDog/indicators-of-compromise).
  Gated behind dashboard approval with automerge off; updates stay enabled so
  fixed versions can still land.

### Changed

- Grouping is universal. The non-major group carried a manager allowlist, so
  any ecosystem not named in it got a separate pull request per dependency.
- `packageRules` reordered so "never automerge production dependencies" and the
  Shai-Hulud gate evaluate last, overriding the permissive rules above them.
- Migrated deprecated configuration: `npm:unpublishSafe` →
  `security:minimumReleaseAgeNpm`, dropped `stabilityDays` and
  `transitiveRemediation`, `matchPackagePatterns` → `matchPackageNames`.

### Known limitations

- `renovate-config-validator` does not validate manager names.
  `matchManagers: ["npm", "pnpm", "yarn"]` passes clean and matches nothing.
  The gate covers schema, not semantics.
- Renovate has a hosted app on GitHub.com only. Every other forge needs it
  self-hosted.

[Unreleased]: https://github.com/ownctrl/supply-chain/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/ownctrl/supply-chain/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/ownctrl/supply-chain/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/ownctrl/supply-chain/releases/tag/v1.0.0
