#!/usr/bin/env bash
set -euo pipefail
: "${GG_REPO:?set GG_REPO}"
: "${ACTOR:?set ACTOR}"
cmd=(python s3_appearance.py -s "$ACTOR" -so "$ACTOR" --only_foreground_loss)
printf '%q ' "${cmd[@]}"; echo
if [[ "${EXECUTE:-0}" == 1 ]]; then cd "$GG_REPO" && "${cmd[@]}"; fi
