# Third-party provenance and notices

This repository does not redistribute these projects or assets. Fetch official sources and retain their notices.

| Component | Upstream | Observed commit | Observed constraint |
|---|---|---|---|
| Gaussian-Garments | <https://github.com/eth-ait/Gaussian-Garments> | `ceb66fc36598da05b3b3391f4562cdc54d2a2ed2` | no top-level license found; do not redistribute without clarification |
| ActorsHQ-for-Gaussian-Garments | <https://github.com/hlimach/ActorsHQ-for-Gaussian-Garments> | `46651f55030407ea25463ed070eed9f7e837a9af` | no top-level license found; includes gs2mesh |
| gs2mesh | <https://github.com/yanivw12/gs2mesh> | local checkout `560f3e8a2349aaad24fe9444ef1ca2770aeec5ab`; submodule may differ | verify upstream and bundled licenses |
| ContourCraft | <https://github.com/Dolorousrtur/ContourCraft> | `d606432c2f7e96b05664e6a4ffb9d1cb98705baf` | MIT in audited checkout |
| GaussianWardrobe | <https://github.com/eth-ait/GaussianWardrobe> | `af9ff485602b55f8125651e48803b1448b67c0b8` | MIT in audited checkout |
| AnimatableGaussians | recorded in source checkout | `2b0f6e3` prefix | non-commercial scientific/educational/artistic terms and redistribution restrictions observed |
| 3D Gaussian Splatting | official Inria/MPI source/submodule | project-dependent | research/non-commercial terms observed |

Separate authorization is required for ActorsHQ, SMPL/SMPL-X, AMASS/CMU, GroundingDINO/SAM2 weights, and pretrained checkpoints. Their absence is intentional.

Before publishing a patch: record upstream and commit, include required attribution, exclude data/weights/generated subjects, review redistribution rights, and remove local paths, hostnames, credentials and personal information.
