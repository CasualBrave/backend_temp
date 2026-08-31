# Data formats

Paths are logical examples; real datasets stay outside Git.

## ActorsHQ sequence

```text
ActorXX/Sequence1/
  cameras.json
  Cam001/
    rgb_images/Cam001_rgb000000.jpg
    foreground_masks/Cam001_mask000000.png
    garment_masks/Cam001_rgb000000.png
```

Observed sequences had up to 160 camera entries. Frames use six digits. `cameras.json` is keyed by `CamNNN`:

| Field | Shape/type |
|---|---|
| `ids` | integer |
| `intrinsics` | 3 x 3 float matrix |
| `extrinsics` | 3 x 4 float matrix |
| `shape` | 2 integers |

Do not transpose or invert matrices based on guesses; validate by reprojection.

## COLMAP and gs2mesh

COLMAP scenes contain `images/` plus `sparse/0/{cameras,images,points3D}` TXT/BIN/PLY. `viewNNN` order is not guaranteed to equal `CamNNN`; preserve a TSV mapping of view index, COLMAP image id, and source filename.

gs2mesh produces binary PLY splats, `.npy` depth/disparity/occlusion arrays plus PNG previews, fused/cleaned PLY meshes, and a registered OBJ.

## Gaussian-Garments Stage 1-3

```text
ActorXX/
  stage1/template.obj
  stage1/point_cloud.ply
  stage2/Template/template.obj
  stage2/Template/local_point_cloud.ply
  stage2/Sequence1/meshes/frame_00000.obj
  stage3/epochN/net.pt
  stage3/epochN/optm.pt
```

Keep OBJ topology stable through UV unwrap. PyTorch `.pt` files and Python pickle can execute code: load only trusted artifacts.

## Stage 4 SMPL-X NPZ

An observed Actor08 `Sequence1.npz` contained 2,374 frames:

| Key | Shape | dtype |
|---|---:|---|
| `betas` | `(F, 10)` | float32 |
| `expression` | `(F, 10)` | float32 |
| `trans` | `(F, 3)` | float32 |
| `root_orient` | `(F, 3)` | float32 |
| `pose_body` | `(F, 63)` | float32 |
| `pose_hand` | `(F, 90)` | float32 |
| `pose_jaw` | `(F, 3)` | float32 |
| `pose_eye` | `(F, 6)` | float32 |
| `mocap_frame_rate` | scalar | int64 |

## Registrations PKL

An observed Actor08 dictionary contained:

| Key | Shape |
|---|---:|
| `vertices` | `(F, 7964, 3)` |
| `faces` | `(15624, 3)` |
| `uv_coords` | `(F, 10014, 2)` |
| `uv_faces` | `(15624, 3)` |
| `pred` | `(F, 7964, 3)` |
| `cloth_faces` | `(15624, 3)` |

## Garment dictionary and simulation

Observed dictionaries contain fields such as `rest_pos`, `faces`, `node_type`, `garment_id`, `center`, `coarse_edges`, and LBS data. Fields vary by version. For waistband pinning, confirm value `3` in `node_type` and inspect those vertices visually. Simulation trajectories are normally PKL; pair them with frame rate, pose source, gender, and checkpoint metadata.
