#!/usr/bin/env bash
# Install optional git hooks for the Bible Vault wiki maintenance gate.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if [[ ! -d .git ]]; then
  echo "Not a git repository: $ROOT" >&2
  exit 1
fi

mkdir -p .githooks
HOOK_SRC="$ROOT/.githooks/pre-commit"
if [[ ! -f "$HOOK_SRC" ]]; then
  echo "Missing $HOOK_SRC" >&2
  exit 1
fi

git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
echo "Installed git hooksPath=.githooks"
echo "Pre-commit will run: wiki_tool build, lint, source-lint, lint_wiki"
