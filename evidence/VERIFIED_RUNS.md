# Verified run evidence

## Actor08 shirt Stage 3 (`cvlab-110`)

- Log contained `Training complete`.
- Final artifacts included `epoch5/net.pt` and `epoch5/optm.pt`.
- A Blender atexit warning followed completion; checkpoint existence distinguished it from a failed loop.

## Actor08 shorts Stage 2 (`cvlab-111`)

- A 2,374-frame run was observed active around frame 2,065 after roughly 18 hours.
- This is execution/scale evidence, not a completion claim.
- Mask and mesh review remain required.

## Actor08 shirt ContourCraft fine-tune (`cvlab-110`)

- Actor-specific config used male SMPL-X, Stage4 registrations, pretrained checkpoint, AMASS loader, and `pinned_verts`.
- Observed interval was step 45,000 toward 46,000, checkpointing every 50 steps.
- It was still running at audit time; this is not completion evidence.

## Stage 1 example

- A 60-view, 30,000-iteration Gaussian run wrote `point_cloud/iteration_30000/point_cloud.ply`.
- Optimization took roughly nine minutes on RTX 5090; stereo, masking, TSDF and registration add time.

For every new run retain command, environment, Git commit/diff hash, config, timestamps, exit code, checkpoint hashes and visual-review decision.
