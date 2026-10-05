#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCH_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PYTHON="$BENCH_DIR/.venv/bin/python"
TORCH_LIB="$($VENV_PYTHON -c 'from pathlib import Path; import torch; print(Path(torch.__file__).parent / "lib")')"

DYLD_LIBRARY_PATH="$TORCH_LIB${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}" \
OPENML_CACHE_DIR="$BENCH_DIR/.cache/openml" \
PYTHONDONTWRITEBYTECODE=1 \
OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}" \
OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}" \
PYTHONPATH="$BENCH_DIR/src${PYTHONPATH:+:$PYTHONPATH}" \
"$VENV_PYTHON" "$SCRIPT_DIR/quick_compare.py" "$@"
