# Fixed-size tools

These are sanitized copies or minimal patches derived from the fixed-size experiment found in the local WSL workspace. They contain no garment dictionaries, body models, checkpoints, trajectories, renders, or machine-specific paths.

## Files

- `contourcraft_fixed_size_upper.py`: bind an existing garment topology to target body-shape LBS data, then run a ContourCraft checkpoint without patching its source tree.
- `recover_resize_upper_garment.py`: fit SMPL-X to a Gaussian-Garments resize trajectory and recover a new garment dictionary.
- `relax_recovered_garment.py`: relax a recovered dictionary while preserving the input and writing a separate output copy.
- `inspect_garment_dict.py`: report topology, `node_type`, and value-3 pin counts.
- `run_contourcraft_fixed_size.sh`: environment wrapper with all machine paths supplied through variables.
- `inference_fixed_size_views.patch`: small patch against the audited Gaussian-Garments `inference.py`; it adds fixed front/back/left/right views, distance, frame limit, and render-only ground lift.

Python pickle and PyTorch checkpoints can execute code. Use only trusted inputs.

## 1. Inspect the source dictionary

```bash
python fixed_size/inspect_garment_dict.py /outside/git/source_garment.pkl
```

Record vertex/face counts, `node_type` values, and `pinned_value_3_count`. Enabling `pinned_verts` in a rollout config does not create value-3 vertices.

## 2. Prepare fixed-size dictionary

```bash
python fixed_size/contourcraft_fixed_size_upper.py prepare \
  --contourcraft-root /path/to/ContourCraft \
  --body-model-root /outside/git/body_models \
  --source-garment-dict /outside/git/source.pkl \
  --output-garment-dict /outside/git/fixed_size_new.pkl \
  --source-betas /outside/git/source_betas.npz \
  --target-sequence /outside/git/target_sequence.npz \
  --source-gender female --target-gender female --model-type smpl
```

The output path must not already exist. Inspect the new dictionary before simulation.

## 3. Simulate

```bash
python fixed_size/contourcraft_fixed_size_upper.py simulate \
  --contourcraft-root /path/to/ContourCraft \
  --ccraft-data-root /outside/git/ccraft_data \
  --body-model-root /outside/git/body_models \
  --garment-dict /outside/git/fixed_size_new.pkl \
  --target-sequence /outside/git/target_sequence.npz \
  --checkpoint /outside/git/contourcraft.pth \
  --output-trajectory /outside/git/trajectory_new.pkl \
  --gaussian-garment-name ActorXX_upper \
  --target-gender female --n-steps 200
```

## 4. Recover and relax a resized garment

`recover_resize_upper_garment.py` refuses to overwrite its fit and dictionary outputs. The sanitized relaxation tool also requires distinct input and output dictionaries:

```bash
python fixed_size/relax_recovered_garment.py \
  --contourcraft-root /path/to/ContourCraft \
  --data-root /outside/git/ccraft_data \
  --body-model-root /outside/git/body_models \
  --input-garment-dict /outside/git/recovered_unrelaxed.pkl \
  --output-garment-dict /outside/git/recovered_relaxed.pkl \
  --checkpoint /outside/git/contourcraft.pth \
  --trajectory-output /outside/git/relaxation_trajectory.pkl \
  --gender female --steps 30
```

## 5. Fixed-view Gaussian-Garments inference

Apply the patch only to the audited Gaussian-Garments commit and review it first:

```bash
cd /path/to/Gaussian-Garments
git apply --check --unidiff-zero /path/to/handoff/fixed_size/inference_fixed_size_views.patch
git apply --unidiff-zero /path/to/handoff/fixed_size/inference_fixed_size_views.patch
```

Prefer applying it on a new branch or disposable checkout. The patch modifies source and is not run automatically by this handoff.

## Provenance and limitations

The original local tools came from the audited WSL ContourCraft and Gaussian-Garments working trees; machine-specific locations have been removed from the runnable wrapper. The patch was measured as 35 insertions and 6 deletions relative to the audited `inference.py`. No scientific equivalence across other commits is claimed.
