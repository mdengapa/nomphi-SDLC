#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 TARGET_REPO --name NAME --id ID [--type TYPE]" >&2
  exit 2
fi

TARGET="$1"; shift
NAME=""; ID=""; TYPE="other"
while [ $# -gt 0 ]; do
  case "$1" in
    --name) NAME="$2"; shift 2;;
    --id) ID="$2"; shift 2;;
    --type) TYPE="$2"; shift 2;;
    *) echo "Unknown option: $1" >&2; exit 2;;
  esac
done

[ -n "$NAME" ] && [ -n "$ID" ] || { echo "--name and --id are required" >&2; exit 2; }
TARGET="$(cd "$TARGET" && pwd)"
HERE="$(cd "$(dirname "$0")" && pwd)"

if [ -e "$TARGET/.nomphi/core" ]; then
  echo "Refusing to overwrite existing $TARGET/.nomphi/core" >&2
  exit 3
fi

mkdir -p "$TARGET/.nomphi" "$TARGET/.opencode" "$TARGET/scripts"
cp -R "$HERE/.nomphi/core" "$TARGET/.nomphi/core"
cp -R "$HERE/.nomphi/project" "$TARGET/.nomphi/project"
mkdir -p "$TARGET/.nomphi/tasks"
cp -R "$HERE/.opencode/agents" "$TARGET/.opencode/agents"
cp "$HERE/scripts/nomphi.py" "$TARGET/scripts/nomphi.py"
cp "$HERE/scripts/activate_opencode_agents.py" "$TARGET/scripts/activate_opencode_agents.py"
cp "$HERE/AGENTS.nomphi.md" "$TARGET/AGENTS.nomphi.md"
cp "$HERE/opencode.jsonc.example" "$TARGET/opencode.jsonc.example"

python3 "$TARGET/scripts/nomphi.py" project-init --id "$ID" --name "$NAME" --type "$TYPE"

echo "Installed Nomphi core into $TARGET"
echo "Next: complete $TARGET/.nomphi/project/ before the first real task."
echo "AGENTS.nomphi.md is intentionally not merged into an existing AGENTS.md automatically."
