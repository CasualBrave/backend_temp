# Project handoff

## 1. Purpose and deliverable

The project reconstructs a garment from synchronized multi-view ActorsHQ footage, registers it through a sequence, learns its appearance as Gaussian primitives, and can drive the garment with ContourCraft simulation. This handoff records the **observed working pipeline**, including local patches and operational caveats, without redistributing restricted inputs or large outputs.

## 2. Audited machines and source state

Audit date: 2026-08-31. Hostnames are aliases only; connection details and keys are intentionally excluded.

| Location | Repository | Branch / commit | Observed state |
|---|---|---|---|
| local WSL | Gaussian-Garments | `main` / `ceb66fc36598da05b3b3391f4562cdc54d2a2ed2` | dirty; Stage 2/3, dataset, model and defaults changes |
| local WSL | ActorsHQ-for-Gaussian-Garments | `main` / `46651f55030407ea25463ed070eed9f7e837a9af` | dirty; defaults plus mask utilities |
| local WSL | ContourCraft | `main` / `d606432c2f7e96b05664e6a4ffb9d1cb98705baf` | custom fixed-size utilities untracked |
| local WSL | GaussianWardrobe | `main` / `af9ff485602b55f8125651e48803b1448b67c0b8` | CUDA/build and bridge artifacts present |
| `cvlab-110` | ContourCraft | `main` / `d606432c2f7e96b05664e6a4ffb9d1cb98705baf` | dirty; Actor05/08 runners and configs |
| `cvlab-111` | Gaussian-Garments | detached / `ceb66fc36598da05b3b3391f4562cdc54d2a2ed2` | dirty; Stage 2/3 and model changes |
| `cvlab-111` | ActorsHQ-for-Gaussian-Garments | `main` / `46651f55030407ea25463ed070eed9f7e837a9af` | dirty; initialization/reconstruction and gs2mesh submodule |

Before reproducing work, run `git status --short --branch`, `git rev-parse HEAD`, and `git diff --stat` in every source repo. Do not assume two machines contain identical dirty patches.

## 3. End-to-end workflow

The verified route is:

1. ActorsHQ archive or organized sequence plus calibration.
2. GroundingDINO prompt selection and SAM2 masks; manually review every camera used by Stage 1.
3. Export a chosen template frame into COLMAP format.
4. Train 3D Gaussian Splatting (observed default: 30,000 iterations), stereo depth, mask, TSDF fusion and mesh cleanup.
5. Register the cleaned mesh to obtain `stage1/template.obj`.
6. Gaussian-Garments Stage 2 builds a template and registers all sequence frames.
7. UV unwrap if required, then Stage 3 learns appearance.
8. Convert Stage 2 registrations and SMPL-X to ContourCraft Stage 4 data.
9. Optionally fine-tune ContourCraft from its pretrained checkpoint, simulate a trajectory, and render with Gaussian-Garments inference.

See [PIPELINE.md](PIPELINE.md) for commands and contracts. Fixed-size ContourCraft work has its own required checks in [FIXED_SIZE.md](FIXED_SIZE.md).

## 4. Repository responsibilities

- **ActorsHQ-for-Gaussian-Garments**: input reorganization, calibration conversion, GroundingDINO/SAM2 masking, COLMAP export, gs2mesh reconstruction, Stage 1 registration.
- **Gaussian-Garments**: Stage 1 alternative initialization, Stage 2 template/sequence registration, Stage 3 appearance, inference.
- **ContourCraft**: Stage 4 conversion, garment dictionaries, fine-tuning and cloth simulation.
- **GaussianWardrobe / AnimatableGaussians**: inspected as adjacent integration experiments. They are not required by the verified Actor05/08 path.

Direct coupling is mainly through filesystem contracts and mutable `utils/defaults.py` values. The safer pattern is an isolated runner that assigns defaults at process start; examples are in `reference_runners/`.

## 5. Inputs and licensing

Required external inputs may include ActorsHQ, SMPL-X body models, AMASS CMU subsets, GroundingDINO weights, SAM2 weights, the Gaussian-Splatting dependencies, and a ContourCraft checkpoint. Obtain each from its official source under its own terms. Never commit them here. Exact expected schemas are in [DATA_FORMAT.md](DATA_FORMAT.md).

## 6. Configuration policy

Copy `configs/sample_pipeline.yaml` to an ignored local config. Paths should point outside this repository. Keep separate output roots per actor, garment, template frame, and experiment, for example `Actor08_shirt_tf000000`; never switch actors by permanently editing a shared `utils/defaults.py` without recording the diff.

Record actor, sequence, garment type, gender, template frame, camera list, mask revision, source commits, checkpoint identity, resume frame, ICP, foreground loss, pinning, collision and AMASS settings.

## 7. Local modifications that matter

Observed modifications affect results and must be reviewed before reuse:

- Gaussian-Garments: resume behavior, temporal state, collision scheduling, mask loading, isolated defaults, Actor-specific inference wrappers, and CUDA/model compatibility.
- ActorsHQ wrapper: Stage 1 frame selection, CPU COLMAP compatibility, garment-specific reconstruction/masking and TSDF cleanup.
- ContourCraft: isolated data roots, male SMPL-X selection, `pinned_verts`, missing `lookup` compatibility, and cuDF-to-NumPy compatibility on RTX 5090.

Do not copy entire dirty repos into this handoff. Preserve the actual change set in a separately reviewed patch with `git diff --binary > patch-name.patch` only after removing machine paths and confirming third-party redistribution rights.

## 8. Validation gates

- Masks: contact sheet of all selected views; reject skin, shoes, other garments, holes, and empty/misaligned views.
- Stage 1: render front/back/left/right; inspect waist, cuffs, hem, collar, disconnected components and body contamination.
- Stage 2: overlay template and registered meshes on early/middle/late frames; check topology and pose alignment.
- Stage 3: inspect held-out views and RGBA/foreground behavior; look for dirty color transfer and edge artifacts.
- ContourCraft: inspect frame 0 before long simulation; verify fixed-size node/face counts, waistband pins and `node_type` for trousers. Follow [FIXED_SIZE.md](FIXED_SIZE.md).
- Inference: verify the requested source pose and camera sequence, then encode MP4.

## 9. Performance observations

These measured examples are not guarantees.

| Task | Hardware | Example observation |
|---|---|---|
| Stage 1 GS training, 30k | RTX 5090 | about 9 minutes for one 60-view run; stereo/TSDF adds time |
| Stage 2 full sequence | RTX 5090 | many hours; one 2,374-frame run was active after ~18 h |
| Stage 3 appearance | RTX 5090 | roughly 1.5 h per epoch; five epochs completed in one run |
| ContourCraft fine-tune | RTX 5090 | multi-day in the observed 45k-to-46k experiment |

Local WSL had an 8 GB RTX 5070 Laptop GPU and 11 GiB RAM; both servers had 32 GB RTX 5090 GPUs and 60 GiB RAM. Avoid simultaneous heavy jobs on the same GPU.

## 10. Known risks and failure modes

- A correct-looking mask can still map to the wrong COLMAP view; preserve view-to-camera mapping.
- Changing template frame requires corresponding masks, calibration and images.
- Shared mutable defaults can silently direct outputs to another actor.
- Stage 1 body/shoe contamination propagates into later stages.
- A gender mismatch changes registration and requires rebuilding dependent results.
- Pinning cannot repair a source-pose alignment error; inspect frame 0 first.
- A Blender atexit warning followed `Training complete` in one run; confirm checkpoints before treating it as harmless.
- SAM2 optional-extension warnings can fall back to slower kernels; distinguish warnings from a traceback.

## 11. Handoff checklist

- [ ] Source commits and dirty diffs archived separately
- [ ] Licensed data acquired by each authorized user
- [ ] Local config created outside version control
- [ ] Environment check passes
- [ ] Mask contact sheet approved
- [ ] Stage 1 four-view render approved
- [ ] Stage 2 projection samples approved
- [ ] Stage 3 checkpoint and visual samples approved
- [ ] ContourCraft frame 0 and pinning inspected
- [ ] Fixed-size dictionary/config/checkpoint contract verified, if applicable
- [ ] Inference MP4 and exact command recorded
- [ ] No credentials, datasets, checkpoints, or large output in Git

## 12. Minimal verification

```bash
python3 scripts/smoke_test.py
bash scripts/check_environment.sh
EXECUTE=0 bash scripts/run_stage1.sh
```

The smoke test checks only this handoff's structure and tiny synthetic fixtures. It does not prove CUDA compatibility or scientific quality.
