# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Security:** Expanded the Shai-Hulud 2.0 watch list to the complete set of 428 compromised packages, gated behind dashboard approval with automerge disabled (updates stay enabled so fixed versions can still land) sourced directly from the official [Datadog IOC database](https://github.com/DataDog/indicators-of-compromise).

### Changed
- **Security:** Reordered `packageRules` in `default.json` to ensure the "Never automerge production dependencies" and the "SHAI-HULUD" gate rules are evaluated last, correctly overriding any prior permissive rules (such as dev-tooling whitelists).
- **Code Health:** Upgraded Biome configuration to the latest schema using `biome migrate`.
- **Code Health:** Formatted all JSON files in the repository to ensure consistency.

### Fixed
- Fixed a logic bug where generic automerge rules could have potentially applied to production dependencies due to sequential evaluation in Renovate.
