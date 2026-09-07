#!/usr/bin/env bash
set -u
fail=0
check_cmd() {
  if command -v "$1" >/dev/null 2>&1; then
    echo "OK   $1 $(command -v "$1")"
  else
    echo "MISS $1"
    fail=1
  fi
}
check_cmd git
check_cmd python3
check_cmd ffmpeg
check_cmd nvidia-smi
for var in ACTORSHQ_REPO GG_REPO CONTOURCRAFT_REPO GG_DATA_ROOT GG_OUTPUT_ROOT; do
  value="${!var:-}"
  if [[ -z "$value" ]]; then
    echo "INFO $var not set"
  elif [[ -e "$value" ]]; then
    echo "OK   $var $value"
  else
    echo "MISS $var $value"
    fail=1
  fi
done
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
fi
exit "$fail"
