# Gaussian Garments project handoff

This repository is a **documentation and reproducibility handoff**, not a dataset or model release. It describes the pipeline actually used across a local WSL workstation and the `cvlab-110` / `cvlab-111` servers as audited on 2026-08-31.

Start with [HANDOFF.md](HANDOFF.md), then read [PIPELINE.md](PIPELINE.md), [DATA_FORMAT.md](DATA_FORMAT.md), and the central fixed-size protocol in [FIXED_SIZE.md](FIXED_SIZE.md). Third-party provenance and redistribution constraints are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Safe quick start

```bash
python3 scripts/smoke_test.py
bash scripts/check_environment.sh
cp configs/sample_pipeline.yaml configs/local_pipeline.yaml
# Edit only configs/local_pipeline.yaml; keep datasets and checkpoints outside this repo.
```

The stage scripts are dry-run by default. Set `EXECUTE=1` only after checking every printed path and command.

## What is intentionally absent

- ActorsHQ images, masks, calibration archives, or other licensed datasets
- SMPL/SMPL-X/AMASS assets
- GroundingDINO, SAM2, Gaussian-Garments, or ContourCraft checkpoints
- SSH keys, credentials, host IP addresses, API keys, and user-specific configs
- training outputs, point clouds, meshes, renders, videos, and optimizer states
- copies of third-party source trees

## Verified scope

- ActorsHQ preparation and mask generation
- COLMAP / gs2mesh Stage 1 mesh initialization
- Gaussian-Garments Stage 2 registration and Stage 3 appearance training
- Stage 4 conversion and ContourCraft fine-tuning/simulation
- Gaussian-Garments inference/rendering

No production frontend, HTTP API, or publishing service was found in the audited directories.
