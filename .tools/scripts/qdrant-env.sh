# Shared env bootstrap for Qdrant CLIs (sourced by .qmd/bin/qdrant-*).
# Uses uv to create/sync .tools/venv-qdrant from .tools/pyproject.toml + uv.lock.
#
# shellcheck shell=bash

qdrant_tools_root() {
  # When sourced from .qmd/bin/*: this file is at .tools/scripts/qdrant-env.sh
  # Callers set ROOT to vault root before sourcing when possible.
  if [[ -n "${ROOT:-}" ]]; then
    printf '%s' "$ROOT"
    return
  fi
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
  printf '%s' "$here"
}

qdrant_venv_path() {
  printf '%s/.tools/venv-qdrant' "$(qdrant_tools_root)"
}

qdrant_ensure_uv() {
  if command -v uv >/dev/null 2>&1; then
    return 0
  fi
  printf 'uv not found on PATH. Install: https://docs.astral.sh/uv/\n' >&2
  printf '  curl -LsSf https://astral.sh/uv/install.sh | sh\n' >&2
  return 1
}

# Create/sync the project env with uv (idempotent).
qdrant_ensure_env() {
  local root venv tools
  root="$(qdrant_tools_root)"
  venv="${root}/.tools/venv-qdrant"
  tools="${root}/.tools"

  qdrant_ensure_uv || return 1

  if [[ ! -f "${tools}/pyproject.toml" ]]; then
    printf 'Missing %s/pyproject.toml\n' "$tools" >&2
    return 1
  fi

  # Prefer locked sync when uv.lock exists.
  export UV_PROJECT_ENVIRONMENT="$venv"
  if [[ -f "${tools}/uv.lock" ]]; then
    uv sync --directory "$tools" --frozen --no-dev 2>/dev/null \
      || uv sync --directory "$tools" --no-dev
  else
    uv sync --directory "$tools" --no-dev
  fi

  if [[ ! -x "${venv}/bin/python" ]]; then
    printf 'uv sync did not produce %s/bin/python\n' "$venv" >&2
    return 1
  fi
  return 0
}

qdrant_python() {
  printf '%s/bin/python' "$(qdrant_venv_path)"
}

# Usage: qdrant_exec script.py [args...]
qdrant_exec() {
  local script=$1
  shift
  qdrant_ensure_env || return 1
  exec "$(qdrant_python)" "$script" "$@"
}
