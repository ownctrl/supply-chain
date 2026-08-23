#!/usr/bin/env python3
"""Assert what this preset lets merge unattended.

`renovate-config-validator` checks that default.json is well formed. It does
not check what the rules *decide* -- it will happily accept a rule that grants
automerge to every package on npm, or one whose matcher never fires. Every
fault this preset has shipped was of that kind:

  * `^jest` unanchored matched every `jest-*` package on npm, a prefix nobody
    owns, and those automerged with the trust meant for Jest.
  * Per-tool rules sat after the anchored trust list and re-granted automerge
    through looser patterns, undoing the anchoring above them.
  * The GitHub Actions rule had no matchUpdateTypes, so it overrode
    "major: automerge false" and merged bare digest moves unattended.
  * `matchManagers: ["npm", "pnpm", "yarn"]` named two managers that do not
    exist, so a rule that looked like it covered three ecosystems covered one.

The validator passed all four. The cases below are those bugs, frozen.

LIMITATION, and it is not a small one: this reimplements Renovate's matching
rather than calling Renovate. It can drift from the real engine. Treat a
failure here as a reason to look, and a pass as weaker evidence than a Renovate
dry run. It exists because the alternative is checking nothing.
"""

import fnmatch
import json
import re
import sys
from pathlib import Path

CONFIG = Path(__file__).resolve().parent.parent / "default.json"


def _matches_name(pattern: str, name: str) -> bool:
    """Renovate matchPackageNames: exact, glob, or /regex/."""
    if pattern == "*":
        return True
    if len(pattern) > 1 and pattern.startswith("/") and pattern.endswith("/"):
        return re.search(pattern[1:-1], name) is not None
    if any(c in pattern for c in "*?["):
        return fnmatch.fnmatch(name, pattern)
    return pattern == name


def _rule_applies(rule, *, name, dep_type, manager, update_type, datasource):
    for key, value in (
        ("matchManagers", manager),
        ("matchDepTypes", dep_type),
        ("matchUpdateTypes", update_type),
        ("matchDatasources", datasource),
    ):
        if key in rule and value not in rule[key]:
            return False
    if "matchPackageNames" in rule:
        if not any(_matches_name(p, name) for p in rule["matchPackageNames"]):
            return False
    return True


def resolve(rules, key, **ctx):
    """Last matching rule wins, which is how Renovate layers packageRules."""
    value, source = None, "unset"
    for rule in rules:
        if _rule_applies(rule, **ctx) and key in rule:
            value, source = rule[key], rule.get("description", "")
    return value, source


# name, depType, manager, updateType, datasource, automerge expected
CASES = [
    # Trusted dev tooling merges unattended. That is the whole allowance.
    ("jest", "devDependencies", "npm", "patch", "npm", True),
    ("vitest", "devDependencies", "npm", "patch", "npm", True),
    ("oxlint", "devDependencies", "npm", "patch", "npm", True),
    ("typescript", "devDependencies", "npm", "patch", "npm", True),
    ("@biomejs/biome", "devDependencies", "npm", "patch", "npm", True),
    ("@types/node", "devDependencies", "npm", "patch", "npm", True),
    # Neighbours in unowned npm prefixes must NOT inherit that trust.
    ("jest-environment-foo", "devDependencies", "npm", "patch", "npm", False),
    ("vitest-fetch-mock", "devDependencies", "npm", "patch", "npm", False),
    ("oxlint-plugin-evil", "devDependencies", "npm", "patch", "npm", False),
    ("typescript-eslint-hijack", "devDependencies", "npm", "patch", "npm", False),
    # Production dependencies never merge unattended, whatever they are called.
    ("typescript", "dependencies", "npm", "patch", "npm", False),
    ("vitest", "dependencies", "npm", "patch", "npm", False),
    ("@biomejs/biome", "dependencies", "npm", "patch", "npm", False),
    ("express", "dependencies", "npm", "patch", "npm", False),
    ("serde", "dependencies", "cargo", "patch", "crate", False),
    ("django", "dependencies", "poetry", "patch", "pypi", False),
    # Watch-listed packages stay gated even as devDependencies.
    ("posthog-node", "dependencies", "npm", "patch", "npm", False),
    ("tinycolor2", "devDependencies", "npm", "patch", "npm", False),
    # CI actions: minor/patch only. A bare digest move on an unchanged tag is
    # the tj-actions/changed-files vector and must wait for a human.
    ("actions/checkout", None, "github-actions", "patch", "github-tags", True),
    ("actions/checkout", None, "github-actions", "minor", "github-tags", True),
    ("actions/checkout", None, "github-actions", "digest", "github-tags", False),
    ("actions/checkout", None, "github-actions", "major", "github-tags", False),
]


def main() -> int:
    config = json.loads(CONFIG.read_text())
    rules = config["packageRules"]
    failures = []

    for name, dep_type, manager, update_type, datasource, expected in CASES:
        got, source = resolve(
            rules,
            "automerge",
            name=name,
            dep_type=dep_type,
            manager=manager,
            update_type=update_type,
            datasource=datasource,
        )
        if bool(got) is not expected:
            failures.append(
                f"  {name} ({dep_type or manager}, {update_type}): "
                f"expected automerge={expected}, got {bool(got)} "
                f"from rule {source!r}"
            )

    # Lockfile refreshes are not covered by minimumReleaseAge, so automerging
    # one would pull every transitive dependency in unreviewed and ungated.
    if config["lockFileMaintenance"].get("automerge"):
        failures.append(
            "  lockFileMaintenance.automerge is true: minimumReleaseAge does "
            "not apply to lockfile refreshes, so this merges every transitive "
            "update with no age gate and no review"
        )

    # Renovate has no pnpm or yarn manager; the npm manager reads all three
    # lockfiles. A rule naming them looks broader than it is, and the schema
    # validator does not catch it.
    known = {
        "npm", "bun", "bun-version", "deno", "cargo", "gomod", "docker",
        "github-actions", "nix", "terraform", "ansible", "nuget", "composer",
        "bundler", "pub", "swift", "cocoapods", "kubernetes", "helmv3",
        "helm-values", "helm-requirements", "helmfile", "flux", "argocd",
        "gradle", "gradle-wrapper", "maven", "maven-wrapper", "sbt",
        "pip_requirements", "pip-compile", "poetry", "pep621", "pipenv",
        "setup-cfg",
    }
    for rule in rules:
        for manager in rule.get("matchManagers", []):
            if manager not in known:
                failures.append(
                    f"  unknown manager {manager!r} in rule "
                    f"{rule.get('description', '')!r} -- it matches nothing. "
                    f"If Renovate added it, add it to `known` here."
                )

    if failures:
        print(f"policy: {len(failures)} failure(s)\n")
        print("\n".join(failures))
        return 1

    print(f"policy: {len(CASES)} cases, lockfile gate and manager names all OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
