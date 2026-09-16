#!/usr/bin/env python3
"""Experimentally transfer a GG template between SMPL-X poses, then optionally rigid-ICP it.

This is not an upstream Gaussian-Garments procedure. Prefer an upstream-style
template frame with a pose close to the sequence's first frame whenever possible.
"""

import argparse
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import open3d as o3d
import smplx
import trimesh


def load_params(path):
    if path.suffix == ".npz":
        return dict(np.load(path))
    with path.open("rb") as handle:
        return pickle.load(handle)


def cloud(path):
    geometry = o3d.io.read_point_cloud(str(path))
    if not geometry.has_points():
        mesh = o3d.io.read_triangle_mesh(str(path))
        geometry.points = mesh.vertices
    if not geometry.has_points():
        raise RuntimeError(f"no points in {path}")
    return geometry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gaussian-garments-root", type=Path, required=True)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--source-params", type=Path, required=True)
    parser.add_argument("--target-params", type=Path, required=True)
    parser.add_argument("--body-model-root", type=Path, required=True)
    parser.add_argument("--gender", choices=("male", "female", "neutral"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-cloud", type=Path)
    parser.add_argument("--target-cloud", type=Path)
    parser.add_argument("--icp-threshold", action="append", type=float,
                        default=[])
    parser.add_argument("--min-fitness", type=float, default=0.25)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if bool(args.source_cloud) != bool(args.target_cloud):
        raise ValueError("source-cloud and target-cloud must be supplied together")

    sys.path.insert(0, str(args.gaussian_garments_root.resolve()))
    from lbs import prepare_lbs

    source_params = load_params(args.source_params)
    target_params = load_params(args.target_params)
    model = smplx.create(
        str(args.body_model_root), model_type="smplx", gender=args.gender,
        use_pca=True, num_pca_comps=45, flat_hand_mean=False, batch_size=1,
    )
    mesh = trimesh.load(args.template, force="mesh", process=False,
                        maintain_order=True)
    vertices = np.asarray(mesh.vertices, dtype=np.float32)
    source_translation = np.asarray(source_params["transl"], dtype=np.float32)
    target_translation = np.asarray(target_params["transl"], dtype=np.float32)
    canonical, weights, nearest = prepare_lbs(
        model, source_params, vertices - source_translation, unpose=True
    )
    transferred, _, _ = prepare_lbs(
        model, target_params, canonical, blend_weights=weights, nn_ids=nearest
    )
    transferred = np.asarray(transferred) + target_translation

    icp_records = []
    transform = np.eye(4)
    if args.source_cloud:
        source = cloud(args.source_cloud)
        target = cloud(args.target_cloud)
        thresholds = args.icp_threshold or [0.05, 0.10, 0.20]
        candidates = []
        for threshold in thresholds:
            result = o3d.pipelines.registration.registration_icp(
                source, target, threshold, np.eye(4),
                o3d.pipelines.registration.TransformationEstimationPointToPoint(),
            )
            record = {"threshold": threshold, "fitness": result.fitness,
                      "inlier_rmse": result.inlier_rmse}
            icp_records.append(record)
            candidates.append((record, result.transformation))
        viable = [item for item in candidates if item[0]["fitness"] >= args.min_fitness]
        selected = min(viable or candidates,
                       key=lambda item: item[0]["inlier_rmse"]
                       if item[0]["fitness"] > 0 else float("inf"))
        transform = selected[1]
        homogeneous = np.c_[transferred, np.ones(len(transferred))]
        transferred = (homogeneous @ transform.T)[:, :3]

    output = trimesh.Trimesh(vertices=transferred, faces=np.asarray(mesh.faces),
                             process=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.export(args.output)
    report = {"method": "experimental_smplx_pose_transfer_then_optional_rigid_icp",
              "upstream_recommended": False, "vertices": len(output.vertices),
              "faces": len(output.faces), "icp": icp_records,
              "selected_transform": transform.tolist()}
    args.output.with_suffix(args.output.suffix + ".json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
