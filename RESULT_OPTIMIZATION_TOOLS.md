# Result-optimization tools added around Gaussian-Garments and ContourCraft

This note separates reusable result-improvement methods from one-off recovery work caused by an incorrect command, environment, frame, gender, path, or camera mapping. The tools below wrap or prepare inputs for the audited upstream repositories; they are not claimed as upstream Gaussian-Garments or ContourCraft features.

The recent division of work was:

- `cvlab-110`: Actor08 shirt, including the frame-183 pipeline and ContourCraft shirt fine-tuning.
- `cvlab-111`: Actor08 shorts, including the frame-267 curved-hem pipeline and checkpoint comparisons.

The live servers should still be checked before reuse because their working trees were dirty and may no longer match the recovered local copies.

## 1. Curved hem trimming

### Problem

TSDF/Stage 1 meshes sometimes contain narrow downward spikes or “whiskers” along a shirt or shorts hem. Keeping only the largest connected component does not remove spikes that are connected to the main garment. A single horizontal plane can remove the spikes but makes a naturally curved hem unnaturally straight.

### Added method

The sanitized [`result_optimization/curved_hem_candidates.py`](result_optimization/curved_hem_candidates.py), derived from the Actor08 shorts frame-267 and shirt frame-183/506 experiments, performs a geometry-space curved clip:

1. Load the Stage 1 template without automatic mesh processing.
2. Keep the largest connected garment component.
3. Estimate the garment center and usable width.
4. Define an upward-opening parabolic cutoff, approximately `base + amplitude * normalized_x^2`.
5. Temporarily warp the mesh so the curved boundary becomes a plane.
6. Clip it with PyVista, triangulate and clean it.
7. Undo the warp and keep the largest resulting component.
8. Export several conservative `base`/`amplitude` candidates and a front/back/side contact sheet.
9. Install a candidate only after visual review.

This is a preprocessing operation, not a training loss. It changes the mesh topology, so it must happen before UV unwrap and the final Stage 2/3/Stage 4 runs. Downstream artifacts from the old topology must not be mixed with the curved-hem version.

### Supporting checks

- The curved-hem tool starts from the largest connected component, removing disconnected floating fragments before clipping.
- Candidate JSON files record the clip parameters, vertex/face counts and bounds.

### Status

The reusable part is the candidate-and-review method. Hard-coded coordinates for Actor08 are experiment data and should be parameterized before general reuse.

## 2. Selecting the correct mask and TSDF views

### Problem

A good DINO/SAM2 mask can still be assigned to the wrong reconstruction view. COLMAP/gs2mesh view indices are not guaranteed to equal camera IDs or lexical filename order. Poor, cropped, empty, border-touching or wrongly mapped masks contaminate TSDF and create body, shoe or fringe geometry.

### Added method

The review pipeline has three gates.

#### A. Establish the exact view-to-camera mapping

- [`result_optimization/derive_view_camera_mapping.py`](result_optimization/derive_view_camera_mapping.py) matches rendered camera positions in `camera_data.json` to Gaussian/COLMAP camera positions and requires a configurable near-zero position error.

The mapping is saved before any view whitelist is chosen. A numeric view such as `028` must never be interpreted directly as `Cam028`.

#### B. Generate and review DINO + SAM2 candidates

- [`result_optimization/review_dino_sam2_masks.py`](result_optimization/review_dino_sam2_masks.py) runs GroundingDINO followed by `SAM2ImagePredictor`, saves the RGB/mask/overlay and records score and mask area for every rendered view.
- Ambiguous Actor08 views were tested with reviewed positive and negative points plus DINO boxes. Those actor-specific coordinates are recorded in the provenance table but deliberately not shipped as generic defaults.
- [`result_optimization/install_reviewed_masks.py`](result_optimization/install_reviewed_masks.py) backs up existing masks and installs only the masks explicitly listed in a review manifest.

This stays within DINO + SAM2. HSV selection, closing, dilation, hole filling and other morphology are not part of this method.

#### C. Select TSDF views by quality, not by index range

- [`result_optimization/audit_tsdf_views.py`](result_optimization/audit_tsdf_views.py) measures mask area, border contact and focal length after the exact mapping is known, then emits an explicit `TSDF_valid` whitelist.

Observed candidate policy included:

- reject a view when the garment is absent or its reviewed mask is empty for a valid reason;
- reject masks touching the image border when the garment is severely cropped;
- reject implausibly large masks likely to contain body or another garment;
- optionally reject extreme focal/crop views;
- compare the resulting Stage 1 mesh from front, back and side before accepting the whitelist.

`TSDF_valid` and mask-aware TSDF are upstream-supported controls. The exact mapping audit, quality scoring, contact sheets and candidate comparison are the added tooling.

## 3. Fine-tuning data split

### Weak baseline

The first Actor08 shirt preparation used one contiguous training interval, frames `0..1898`, and one contiguous validation tail, frames `1899..2373`. This is simple and valid, but it gives weak evidence about generalization because neighboring frames are highly correlated and most training samples come from one continuous motion range.

### Improved split used for Actor08 shorts

The original Actor08 script created nine 150-frame training clips distributed across the sequence and one separate 150-frame validation clip. Its reusable implementation is [`result_optimization/prepare_stratified_finetune.py`](result_optimization/prepare_stratified_finetune.py):

Training windows, Python half-open convention:

```text
[0,150), [184,334), [334,484), [645,795), [795,945),
[1100,1250), [1525,1675), [1939,2089), [2089,2239)
```

Validation:

```text
[1250,1400)
```

This produces 1,350 training frames and 150 validation frames while sampling early, middle and late motion. The unselected gaps reduce near-duplicate leakage around the validation clip.

Preparation also verifies the complete contract before training:

- 2,374 Stage 2 meshes and matching SMPL-X poses;
- identical registration/template topology;
- male body model;
- expected vertex and face counts;
- 24 reviewed waistband pins with `node_type == 3` for shorts;
- LBS fields present;
- hashes and split windows written to a manifest.

## 4. Other legitimate result-improvement tools

These are separate from the three main methods but are also genuine experiment additions:

- **Experimental SMPL-X pose transfer before Stage 2 registration**: [`result_optimization/experimental_smplx_pose_transfer.py`](result_optimization/experimental_smplx_pose_transfer.py) unposes a template with LBS, poses it to the target frame, then can apply a residual rigid ICP transform. This is a local experiment, not a procedure recommended by the Gaussian-Garments paper or repository. Upstream instead advises choosing a template frame whose pose is similar to the first sequence frame, and its optional `--use_icp` path performs rigid point-to-point ICP without SMPL-X pose transfer.
- **Boundary/topology audit**: [`result_optimization/repair_mesh_boundaries.py`](result_optimization/repair_mesh_boundaries.py) identifies boundary loops and can fill small unintended holes while preserving a configured number of real garment openings. It must be visually reviewed and rerun through downstream topology-dependent stages.
- **Shorts waistband pins**: [`result_optimization/pin_boundary_loop.py`](result_optimization/pin_boundary_loop.py) finds the highest boundary loop, samples evenly spaced waist vertices and assigns `node_type == 3`. This prevents waistband drop during ContourCraft rollout; it cannot repair a wrong initial pose or contaminated mesh.
- **Exact-pose ContourCraft inference**: [`result_optimization/exact_pose_contourcraft.md`](result_optimization/exact_pose_contourcraft.md) records the `separate_arms=False` setting used to keep the captured SMPL-X arm rotations so frame 0 agrees with the reconstructed garment.

## 5. Excluded: corrections for runs that did not follow the intended repo contract

The following are not presented as optimization methods or research contributions:

- installing or importing SAM2/GroundingDINO after launching from the wrong Python environment;
- adding paths only to repair `ModuleNotFoundError`;
- changing `gdown` versions or manually supplying a missing SMPL-X model;
- using a wrong gender, wrong template frame, mismatched frame mask, or stale Stage 1/2 output;
- interpreting render-view indices as camera IDs or installing reviewed masks in the wrong order;
- running with only an arbitrary “trusted 60” camera subset without a recorded quality criterion;
- editing a shared `utils/defaults.py` to switch actors and accidentally retaining another actor's paths;
- applying `--skip_masking` before verifying that the reviewed masks exist and match the render order;
- restarting or resuming from an incompatible optimizer/checkpoint state;
- compatibility-only patches for missing `lookup`, cuDF/Numba conversion, RTX 5090 kernels, Blender shutdown warnings or process supervision.

Outputs produced under one of those conditions should be treated as invalid or diagnostic. The useful artifact is the audit/gate that prevents recurrence, not the mistaken run or its emergency repair command.

## 6. Recommended reusable workflow

```text
official DINO + SAM2 candidates
  -> full mapped RGB/mask/overlay review
  -> explicit reviewed mask set
  -> TSDF view-quality candidates
  -> Stage 1 front/back/side gate
  -> optional curved-hem candidate selection
  -> UV + Stage 2/3 rerun on the accepted topology
  -> Stage 4 contract checks
  -> stratified finetune split
  -> finetune and review held-out renders plus rollout stability
```

Every accepted run should record actor, garment, gender, template frame, exact view-to-camera mapping, reviewed mask revision, TSDF whitelist, topology counts, pin indices, split windows, checkpoint hashes and visual-review decision.
