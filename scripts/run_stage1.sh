#!/usr/bin/env bash
set -euo pipefail
: "${ACTORSHQ_REPO:?set ACTORSHQ_REPO}"
: "${ACTOR:?set ACTOR}"
: "${SEQUENCE:=Sequence1}"
: "${GARMENT_TYPE:?set GARMENT_TYPE}"
: "${MASK_PROMPT:?set MASK_PROMPT}"
cmd=(python mesh_reconstruction.py --subject "$ACTOR" --sequence "$SEQUENCE" --garment_type "$GARMENT_TYPE" --masker_prompt "$MASK_PROMPT")
echo "Repository: $ACTORSHQ_REPO"
printf '%q ' "${cmd[@]}"
echo
if [[ "${EXECUTE:-0}" == 1 ]]; then cd "$ACTORSHQ_REPO" && "${cmd[@]}"; fi
