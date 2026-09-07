#!/usr/bin/env bash
set -euo pipefail
: "${CONTOURCRAFT_REPO:?set CONTOURCRAFT_REPO}"
: "${CC_CONFIG:?set CC_CONFIG, for example finetune/Actor08}"
cmd=(python train.py "config=$CC_CONFIG")
printf '%q ' "${cmd[@]}"; echo
if [[ "${EXECUTE:-0}" == 1 ]]; then cd "$CONTOURCRAFT_REPO" && "${cmd[@]}"; fi
