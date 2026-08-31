#!/usr/bin/env bash
set -euo pipefail
: "${GG_REPO:?set GG_REPO}"
: "${ACTOR:?set ACTOR}"
: "${SEQUENCE:=Sequence1}"
: "${TEMPLATE_FRAME:=0}"
: "${START_FROM:=0}"
template=(python s2_registration.py -s "$ACTOR" -so "$ACTOR" -q "$SEQUENCE" -tf "$TEMPLATE_FRAME" --only_foreground_loss)
sequence=(python s2_registration.py -s "$ACTOR" -so "$ACTOR" -q "$SEQUENCE" -t Template --start_from "$START_FROM" --only_foreground_loss)
printf '%q ' "${template[@]}"; echo
printf '%q ' "${sequence[@]}"; echo
if [[ "${EXECUTE:-0}" == 1 ]]; then cd "$GG_REPO" && "${template[@]}" && "${sequence[@]}"; fi
