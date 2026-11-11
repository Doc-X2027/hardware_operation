#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python_bin="${AUBO_PYTHON:-$HOME/miniconda3/envs/lerobot/bin/python}"
if [[ ! -x "$python_bin" ]]; then
    echo '请将 AUBO_PYTHON 设置为 Python 3.12 解释器的完整路径' >&2
    exit 1
fi
script="${1:-control.py}"
if [[ $# -gt 0 ]]; then shift; fi
case "$script" in
    control.py|read_state.py|check_sdk.py) exec "$python_bin" "$script_dir/$script" "$@" ;;
    *) echo '用法: run.sh {control.py|read_state.py|check_sdk.py} [参数...]' >&2; exit 2 ;;
esac
