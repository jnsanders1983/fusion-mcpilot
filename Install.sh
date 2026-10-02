#!/bin/sh
# macOS/Linux agent-side installation. Autodesk Fusion itself requires a supported host.
set -eu
script_directory=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "${PYTHON:-python3}" "$script_directory/Install.py" "$@"
