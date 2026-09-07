#!/usr/bin/env bash
set -euo pipefail

: "${CCRAFT_ENV_PREFIX:?set CCRAFT_ENV_PREFIX to the fixed-size environment}"
: "${CONTOURCRAFT_ROOT:?set CONTOURCRAFT_ROOT to the ContourCraft checkout}"

export CONDA_PREFIX="$CCRAFT_ENV_PREFIX"
export CUDA_HOME="$CCRAFT_ENV_PREFIX"
export PATH="$CCRAFT_ENV_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="${WSL_CUDA_LIB:-/usr/lib/wsl/lib}:$CCRAFT_ENV_PREFIX/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PYTHONPATH="$CONTOURCRAFT_ROOT${PYTHONPATH:+:$PYTHONPATH}"
export TORCH_CUDA_ARCH_LIST="${TORCH_CUDA_ARCH_LIST:-12.0}"

exec "$CCRAFT_ENV_PREFIX/bin/python" \
  "$(dirname "$0")/contourcraft_fixed_size_upper.py" "$@"
