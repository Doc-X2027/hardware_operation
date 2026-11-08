#!/usr/bin/env bash
set -euo pipefail
camera_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
camera_lib="$camera_root/lib/usr/lib/x86_64-linux-gnu"
if [[ -d "$camera_lib" ]]; then
  export GI_TYPELIB_PATH="$camera_lib/girepository-1.0${GI_TYPELIB_PATH:+:$GI_TYPELIB_PATH}"
  export LD_LIBRARY_PATH="$camera_lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi
exec /usr/bin/python3 "$camera_root/stream.py" "$@"
