#!/bin/sh
# Install and upgrade the Nix flake package in a disposable profile.
set -eu
task_store=${1:?usage: test-nix-package.sh STORE-OUTPUT}
task_gui=${2:-}
case "$task_gui" in ''|--gui) ;; *) echo 'usage: test-nix-package.sh STORE-OUTPUT [--gui]' >&2; exit 2 ;; esac
task_checks=$(CDPATH= cd -P "$(dirname "$0")" && pwd)
task_root=$(CDPATH= cd -P "$task_checks/.." && pwd)
command -v nix >/dev/null || { echo 'Nix package manager is required.' >&2; exit 2; }
task_store=$(readlink -f "$task_store")
[ -x "$task_store/bin/jarvis" ] || { echo 'Nix output has no jarvis launcher.' >&2; exit 2; }
case "$(uname -m)" in
    x86_64) task_system=x86_64-linux ;;
    aarch64) task_system=aarch64-linux ;;
    *) echo 'Nix profile smoke supports x86_64 and AArch64.' >&2; exit 2 ;;
esac
task_flake="$task_root#packages.$task_system.jarvis-assistant"
task_xdg_store=$(nix-store -qR "$task_store" | grep -- '-xdg-utils-' | head -n 1)
[ -n "$task_xdg_store" ] || { echo 'Nix output has no xdg-utils runtime dependency.' >&2; exit 2; }
grep -F "$task_xdg_store/bin" "$task_store/bin/jarvis" >/dev/null
test -x "$task_xdg_store/bin/xdg-open"
grep -F 'Copyright (c) 2025 opencode' "$task_store/share/licenses/jarvis/opencode-MIT.txt" >/dev/null
grep -F 'Permission is hereby granted' "$task_store/share/licenses/jarvis/opencode-MIT.txt" >/dev/null
[ -x "$task_store/lib/jarvis/runtime/bin/python3" ] || {
    echo 'Nix output has no bound Python runtime.' >&2
    exit 2
}
task_tmp=$(mktemp -d)
trap 'rm -rf "$task_tmp"' EXIT HUP INT TERM
task_profile=$task_tmp/profile
task_data=$task_tmp/data
export XDG_DATA_HOME=$task_data PYTHONDONTWRITEBYTECODE=1
mkdir -p "$task_data/jarvis"
printf '%s\n' preserved > "$task_data/jarvis/package-test"

nix --extra-experimental-features 'nix-command flakes' profile install \
    --profile "$task_profile" "$task_flake"
test "$(readlink -f "$task_profile/bin/jarvis")" = "$task_store/bin/jarvis"
"$task_profile/bin/jarvis" --doctor
test "$("$task_store/lib/jarvis/bin/opencode" --version)" = 1.18.23
"$task_store/lib/jarvis/runtime/bin/python3" - <<'PY'
import importlib
for name in ('faster_whisper', 'piper', 'mcp', 'httpx', 'dbus_next'):
    importlib.import_module(name)
print('Nix Python runtime imports passed')
PY
test "$(cat "$task_data/jarvis/package-test")" = preserved

nix --extra-experimental-features 'nix-command flakes' profile upgrade \
    --profile "$task_profile" --all
test "$(readlink -f "$task_profile/bin/jarvis")" = "$task_store/bin/jarvis"
"$task_profile/bin/jarvis" --doctor
test "$(cat "$task_data/jarvis/package-test")" = preserved

if [ "$task_gui" = --gui ]; then
    [ -x "$task_store/bin/jarvis-overlay" ] || {
        echo 'Nix output has no jarvis-overlay launcher.' >&2
        exit 2
    }
    python3 "$task_checks/test-overlay-instance.py" "$task_store/bin/jarvis-overlay"
fi

nix --extra-experimental-features 'nix-command flakes' profile remove \
    --profile "$task_profile" "$task_store"
test ! -e "$task_profile/bin/jarvis"
test "$(cat "$task_data/jarvis/package-test")" = preserved
printf '%s\n' 'PASS: Nix profile install/upgrade, runtime imports, removal and user data preservation'
