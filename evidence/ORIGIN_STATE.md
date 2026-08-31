# Audited origin state

Reproducibility record only; no source mirror. Audit date: 2026-08-31.

## Local WSL

- Gaussian-Garments `main` at `ceb66fc36598da05b3b3391f4562cdc54d2a2ed2`; modified Stage 2/3, scene/model, data and defaults files.
- ActorsHQ-for-Gaussian-Garments `main` at `46651f55030407ea25463ed070eed9f7e837a9af`; modified defaults and untracked mask tools.
- ContourCraft `main` at `d606432c2f7e96b05664e6a4ffb9d1cb98705baf`; custom fixed-size utilities present.
- GaussianWardrobe `main` at `af9ff485602b55f8125651e48803b1448b67c0b8`; CUDA/build changes and bridge artifacts present.

## cvlab-110

- ContourCraft at `d606432c2f7e96b05664e6a4ffb9d1cb98705baf`; modified defaults/mesh creation and Actor-specific runners.
- RTX 5090 32 GB and about 60 GiB system RAM.

## cvlab-111

- Gaussian-Garments detached at `ceb66fc36598da05b3b3391f4562cdc54d2a2ed2`; dirty Stage 2/3/model/data changes.
- ActorsHQ wrapper at `46651f55030407ea25463ed070eed9f7e837a9af`; dirty initialization/reconstruction and gs2mesh submodule.
- ContourCraft at `d606432c2f7e96b05664e6a4ffb9d1cb98705baf`; Actor-specific tooling present.
- RTX 5090 32 GB and about 60 GiB system RAM.

Dirty diffs are not embedded because they may contain third-party code, machine paths, or unreviewed work. Archive reviewed patches separately with commit, author and purpose.
