# Exact-pose ContourCraft configuration note

The Actor08 reconstruction was captured in the sequence's original SMPL-X pose.
For its from-any-pose ContourCraft rollout, the useful change was to preserve
that pose instead of applying the optional arm-separation preprocessing:

```python
dataloader = create_fromanypose_dataloader(
    "body_model",
    sequence_path,
    garment_template,
    sequence_loader="cmu_npz_smplx",
    model_type="smplx",
    gender=gender,
    body_model_root=body_model_root,
    obstacle_dict_file=None,
    n_coarse_levels=4,
    separate_arms=False,
    pinned_verts=use_pins,
)
```

This is an experiment setting, not a universal improvement. Compare frame 0 of
the body and garment before a full rollout. It cannot repair a template made
with the wrong gender, frame, topology or SMPL-X parameters.

