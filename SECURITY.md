# Security policy

## Reporting

Report a problem with this preset through
[private vulnerability reporting](https://github.com/ownctrl/supply-chain/security/advisories/new),
not a public issue.

Worth reporting:

- a rule that lets something merge unattended when it should not
- a matcher that is broader than it reads — an unanchored pattern over a
  package prefix nobody owns is the fault this preset has shipped most often
- a package on the watch list that should not be, or one missing that should
- remediation text pointing somewhere a reader cannot follow

## What this preset is and is not

It decides **which dependency updates may land without a human looking at
them.** That is all. It does not scan code, detect compromise, or verify that a
published package matches its source.

It cannot protect a repository that has already installed a hostile version. It
gates *updates*, so a compromised package already in your lockfile is outside
its reach — check the lockfile directly and rotate anything the package could
have read.

## Known limitations

- `renovate-config-validator` does not validate manager names. A typo'd manager
  silently disables the rule containing it. `tooling/test_policy.py` checks the
  names this preset uses against a hardcoded list, which needs updating when
  Renovate adds a manager.
- `tooling/test_policy.py` reimplements Renovate's matching rather than calling
  Renovate. It can drift from the real engine. A failure is a reason to look; a
  pass is weaker evidence than a Renovate dry run.
- `minimumReleaseAge` does not apply to `pin`, `lockFileMaintenance`,
  `lockfileUpdate`, `rollback`, `bump` or `replacement`. This preset disables
  automerge for lockfile maintenance because of it.
- Renovate has a hosted app on GitHub.com only. On every other forge you run it
  yourself, and its token can write to all of your repositories.

## Supported versions

The latest tag. Older tags do not get fixes — move the pin.
