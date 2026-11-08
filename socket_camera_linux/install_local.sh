#!/usr/bin/env bash
# Ubuntu 22.04 x86_64: download distro libraries without sudo.
set -euo pipefail
camera_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$camera_root/lib"
cd "$camera_root/lib"
apt-get download gir1.2-aravis-0.8 libaravis-0.8-0
for package in ./*.deb; do
  dpkg-deb -x "$package" .
done
