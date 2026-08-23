#!/usr/bin/env bash
# Validate every preset in this repo.
#
# This mirrors what .github/workflows/validate.yml runs in CI. It exists so the
# gate still works when CI does not -- run it before pushing, or wire it up as
# a pre-push hook:
#
#   ln -s ../../tooling/validate.sh .git/hooks/pre-push
#
# It is a convenience, not an enforcement boundary: anyone can skip a local
# hook. CI remains the real gate.
set -euo pipefail

# renovate: datasource=npm depName=renovate
RENOVATE_VERSION="${RENOVATE_VERSION:-44.39.1}"

cd "$(dirname "$0")/.."

presets=(default.json renovate.json lockdown.json aggressive.json no-automerge.json)

missing=()
for f in "${presets[@]}"; do
  [[ -f "$f" ]] || missing+=("$f")
done
if [[ ${#missing[@]} -gt 0 ]]; then
  printf 'missing preset(s): %s\n' "${missing[*]}" >&2
  echo "if a preset was renamed, update this list and the CI workflow together" >&2
  exit 1
fi

echo "validating ${#presets[@]} presets against renovate@${RENOVATE_VERSION}"
npx --yes --package "renovate@${RENOVATE_VERSION}" -- \
  renovate-config-validator --strict "${presets[@]}"

# The validator checks that the rules are well formed, not what they decide.
# Every fault this preset has shipped passed it.
python3 tooling/test_policy.py
