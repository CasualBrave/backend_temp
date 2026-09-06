# Fixed-size ContourCraft work

Fixed-size is a central experiment in this project, not a minor utility. It concerns running ContourCraft with a garment representation whose cloth-node/topology size is fixed for the selected experiment, so the rollout, garment dictionary, and checkpoint all agree on the same node layout.

## What must stay consistent

The following four items are one contract:

1. the source garment dictionary used to create the fixed-size experiment;
2. the fixed-size model/configuration and its node count;
3. the rollout/simulation configuration;
4. the checkpoint and any trajectory produced from that configuration.

Do not mix a fixed-size checkpoint with a garment dictionary from another actor, garment, topology, or revision. A successful Python start is not enough: shape mismatches can appear later as indexing errors, disconnected cloth, or apparently valid but incorrect motion.

## Garment dictionary checks

Before rollout, inspect and record:

- dictionary path and source commit;
- keys and tensor/array shapes (`rest_pos`, `faces`, `node_type`, `garment_id`, `center`, `coarse_edges`, and LBS fields when present);
- total garment node count and face count;
- whether `node_type` exists;
- unique `node_type` values and their counts;
- whether the intended pin class is actually present as value `3`;
- the vertex coordinates/region represented by those value-3 nodes.

For the previously discussed `00176 Lower` source, the important question is not merely whether rollout config says `pinned_verts: true`; the source garment dictionary must also contain the intended value-3 vertices. If it does not, enabling the flag cannot create waistband pins by itself.

## `pinned_verts` and rollout

`pinned_verts` is an experiment setting, not a universal repair switch. When enabled, it changes how designated garment nodes are constrained during rollout. Record:

```text
pinned_verts = true/false
node_type unique values = ...
count(node_type == 3) = ...
pin region = waistband / hem / other, with visual evidence
```

Use the same setting used during the checkpoint's intended training/rollout protocol. Compare frame 0 against the Stage 2 template before judging later frames; pinning cannot repair an incorrect template pose, body gender, camera mapping, or contaminated mask.

## Required validation images

For every fixed-size result, save a new review folder outside Git containing:

- garment-dictionary node-type visualization;
- frame-0 template versus SMPL/body overlay;
- front, back, and side rollout renders;
- first, middle, and late-frame renders;
- a log showing node count, face count, checkpoint, config and exit code.

Reject the result if the cloth changes topology unexpectedly, waistband pins are absent, shoes/body are absorbed, or the fixed-size mesh is visibly disconnected.

## Source-code handoff status

The audited WSL and server checkouts contained custom fixed-size ContourCraft utilities/scripts as uncommitted research work. The current Git handoff records the protocol and verification contract but does **not** copy those scripts because their exact filenames, dirty patches, machine paths and redistribution status were not safely verified in this audit. To make fixed-size directly runnable by classmates, add a separately reviewed patch containing:

- the exact runner filename and commit/diff hash;
- a sanitized sample config;
- a CPU shape-check script;
- one tiny synthetic garment dictionary (no real subject data);
- the command and expected node/face counts.

Do not upload the real `00176 Lower` dictionary, checkpoints, trajectories, SMPL-X/AMASS assets, or subject renders.
