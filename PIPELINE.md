# Pipeline and commands

## Flow

```text
ActorsHQ RGB JPEG + foreground PNG + calibration
  -> data_preparation.py: GroundingDINO boxes -> SAM2 -> reviewed garment PNG
  -> mesh_initialization.py --ff FRAME: COLMAP TXT/PLY scene
  -> mesh_reconstruction.py / gs2mesh: 3DGS PLY -> depth NPY -> TSDF/clean mesh PLY
  -> registration: stage1/template.obj
  -> s2_registration.py: Stage2 template OBJ + per-frame OBJ meshes
  -> s3_appearance.py: Stage3 net.pt / optm.pt
  -> inference.py: RGB/RGBA PNG
       or GauGarConverter: Stage4 SMPL-X NPZ + registrations/garment PKL
          -> ContourCraft train/simulation: checkpoint + trajectory PKL
          -> Gaussian-Garments inference: PNG sequence -> MP4
```

## A. Data preparation and masks

Entrypoint: `ActorsHQ-for-Gaussian-Garments/data_preparation.py`.

```bash
python data_preparation.py \
  --subject Actor08 --sequence Sequence1 --resolution 4x \
  --masker_prompt "plaid shirt" --gender male
```

It uses GroundingDINO and `SAM2ImagePredictor`. Observed defaults were box threshold 0.35 and text threshold 0.25. Do not add HSV, morphology, hole filling, closing, or dilation unless a separate experiment records it. Review all camera masks. `--skip_masking`, `--skip_reorg`, `--skip_smplx`, and `--skip_json` skip only named steps; existing outputs must match the selected frame.

## B. Template frame export

Entrypoint: `ActorsHQ-for-Gaussian-Garments/mesh_initialization.py`.

```bash
python mesh_initialization.py \
  --subject Actor08 --sequence Sequence1 --resolution 4x \
  --ff 0 --no_gpu
```

`--ff` chooses the template frame. It exports multiview images and calibration into COLMAP. CPU COLMAP 3.9.1 worked in one environment. Inspect camera count and image/view mapping.

## C. Stage 1: gs2mesh reconstruction

Entrypoint: `mesh_reconstruction.py`; worker: `gs2mesh/run_single.py`.

```bash
python mesh_reconstruction.py \
  --subject Actor08 --sequence Sequence1 \
  --garment_type upper --masker_prompt "plaid shirt"
```

The observed output root encoded `iterations30000`. The process trains splats, renders stereo depth, propagates masks, fuses TSDF, cleans the mesh, and registers it. When using reviewed masks, verify the wrapper skips automatic masking and maps each mask to the correct COLMAP view. For shorts, inspect both leg openings before accepting TSDF cleanup.

Outputs include an iteration-30k `point_cloud.ply`, depth/occlusion files, fused and cleaned PLY meshes, and `stage1/template.obj`.

## D. Stage 2 registration

Entrypoint: `Gaussian-Garments/s2_registration.py`.

```bash
# Template
python s2_registration.py -s Actor08 -so Actor08 -q Sequence1 \
  -tf 0 --only_foreground_loss

# Sequence
python s2_registration.py -s Actor08 -so Actor08 -q Sequence1 \
  -t Template --start_from 0 --only_foreground_loss
```

Observed source defaults were approximately 10k first-template iterations, 15k first cross-scene iterations, 5k later-frame iterations, and 2k collision iterations. Local patches alter resume/state behavior, so record the exact diff. Use `--use_icp` only for a verified initialization gap.

Outputs include `stage2/Template/template.obj`, `local_point_cloud.ply`, and per-frame registered meshes/renders. Resume only from verified contiguous frames.

## E. UV unwrap

UV unwrap bridged registration and appearance training. Preserve the original mesh and save UV output separately. Verify vertex/face counts before and after. No single upstream command was verified consistently across all machines, so this handoff does not invent one.

## F. Stage 3 appearance

Entrypoint: `Gaussian-Garments/s3_appearance.py`.

```bash
python s3_appearance.py -s Actor08 -so Actor08 --only_foreground_loss
```

Relevant settings include SH degree 3, texture resolution 512, texture margin 5, and epochs. The observed upstream default was 3 epochs; an Actor08 run used 5. Outputs are `stage3/epochN/net.pt`, `optm.pt`, and debug renders.

## G. Stage 4 and ContourCraft

`ContourCraft/utils/gaugar.py` contains `GauGarConverter`, which converts Stage 2 registrations and SMPL-X into Stage 4 data and a garment dictionary.

```bash
python train.py config=finetune/Actor08
```

One Actor08 job loaded pretrained `contourcraft.pth`, ran from step 45,000 toward 46,000, saved every 50 steps, selected male SMPL-X, and enabled `pinned_verts`. This is experiment-specific. For trousers, verify `node_type == 3` exists at intended waistband vertices.

## H. Simulation, inference, and MP4

Confirm the first simulated pose matches the actor/template pose before a full run.

```bash
ffmpeg -framerate 30 -start_number 0 -i renders/%04d.png \
  -vf 'scale=trunc(iw/2)*2:trunc(ih/2)*2' \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart output.mp4
```

## I. Transparency, frontend, and API status

Rasterizer experiments expose alpha/opacity outputs and losses, which can support RGBA integration. No complete transparent-garment stage was verified. No production frontend conversion, HTTP API, upload service, or publishing pipeline was found; bridge directories were artifact exchanges, not an API.
