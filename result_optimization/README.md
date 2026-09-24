# Result-optimization utilities

These are sanitized, parameterized versions of tools developed around the
Actor08 experiments. They are not upstream Gaussian-Garments or ContourCraft
commands. Dataset images, masks, body models, checkpoints and generated meshes
must stay outside Git.

Python pickle and PyTorch checkpoint files can execute code. Only load trusted
inputs.

## Tools

- `curved_hem_candidates.py`: generate curved clipping candidates and a
  front/back/side comparison sheet for connected hem spikes.
- `derive_view_camera_mapping.py`: match renderer view indices to source camera
  names using camera positions rather than filename order.
- `review_dino_sam2_masks.py`: run GroundingDINO + SAM2ImagePredictor over
  rendered views and produce RGB/mask/overlay review sheets.
- `install_reviewed_masks.py`: install an explicit review manifest, with backup,
  into the renderer view folders.
- `audit_tsdf_views.py`: score mapped masks using area, border contact and focal
  length and emit an explicit TSDF view whitelist.
- `prepare_stratified_finetune.py`: slice full Stage 4 pose/registration data
  into explicit train and validation windows with a manifest.
- `repair_mesh_boundaries.py`: fill unintended small boundary loops while
  preserving a requested number of real garment openings.
- `pin_boundary_loop.py`: copy a garment dictionary and mark evenly spaced
  vertices on its highest boundary loop as pinned (`node_type == 3`).
- `experimental_smplx_pose_transfer.py`: experimental LBS pose transfer with an
  optional residual rigid ICP. This is not an upstream-recommended GG step.
- `exact_pose_contourcraft.md`: configuration note for preserving the captured
  SMPL-X pose during a from-any-pose rollout.

## Provenance mapping

| Sanitized tool | Recovered experiment scripts |
|---|---|
| `curved_hem_candidates.py` | `make_actor08_shorts_tf267_curvedhem_candidates.py`, `make_actor08_tf183_hem_cleanup_candidates.py`, `make_actor08_shirt_tf506_curvedhem_candidates.py` |
| `derive_view_camera_mapping.py` | `derive_actor08_tf183_render_mapping.py`, `audit_actor08_mask_mapping.py` |
| `review_dino_sam2_masks.py` | `review_new_stage1_masks.py`, `refine_selected_masks.py` |
| `install_reviewed_masks.py` | `install_refined_masks.py` |
| `audit_tsdf_views.py` | `audit_actor08_tf183_tsdf_views.py`, `run_actor08_tf183_tsdf_candidates.py` |
| `prepare_stratified_finetune.py` | `prepare_actor08_shorts_tf267_paper150_finetune.py`, `finalize_actor08_shorts_tf267_paper150_preparation.py` |
| `repair_mesh_boundaries.py` | `repair_actor08_shirt_tf183_topology.py` |
| `pin_boundary_loop.py` | `prepare_actor08_shorts_tf267_curvedhem_ccraft.py` |
| `experimental_smplx_pose_transfer.py` | `run_110_actor08_shirt_tf183_posetransfer_test.py` |

Actor-specific positive/negative SAM2 point coordinates are deliberately not
published as generic defaults. Store reviewed decisions in a separate manifest
and keep source data outside Git.
