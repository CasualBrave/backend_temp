#!/usr/bin/env python3
"""Prepare and simulate a fixed-size upper garment without patching ContourCraft."""

from __future__ import annotations

import argparse
import copy
import pickle
import sys
from pathlib import Path

import numpy as np


def load_pickle(path: Path):
    with path.open("rb") as handle:
        return pickle.load(handle)


def dump_pickle(value, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    with path.open("wb") as handle:
        pickle.dump(value, handle)


def load_betas(path: Path, index: int, key: str = "betas") -> np.ndarray:
    suffix = path.suffix.lower()
    if suffix == ".npy":
        value = np.load(path)
    elif suffix == ".npz":
        archive = np.load(path)
        if key not in archive:
            raise KeyError(f"{path} does not contain key {key!r}; keys={archive.files}")
        value = archive[key]
    elif suffix in {".pkl", ".pickle"}:
        value = load_pickle(path)
        if isinstance(value, dict):
            if key not in value:
                raise KeyError(f"{path} does not contain key {key!r}; keys={list(value)}")
            value = value[key]
    else:
        raise ValueError(f"Unsupported beta file: {path}")

    value = np.asarray(value)
    if value.ndim == 1:
        betas = value
    elif value.ndim == 2:
        betas = value[index]
    else:
        raise ValueError(f"Expected beta array with 1 or 2 dimensions, got {value.shape}")
    if betas.shape[0] < 10:
        raise ValueError(f"Expected at least 10 beta values, got {betas.shape}")
    return np.asarray(betas[:10], dtype=np.float32)


def add_contourcraft_to_path(root: Path) -> None:
    root = root.resolve()
    if not (root / "datasets" / "ccraft.py").is_file():
        raise FileNotFoundError(f"Not a ContourCraft checkout: {root}")
    sys.path.insert(0, str(root))


def make_body_model(body_model_root: Path, model_type: str, gender: str):
    import smplx

    return smplx.create(
        str(body_model_root), model_type=model_type, gender=gender, use_pca=False
    )


def prepare(args: argparse.Namespace) -> None:
    add_contourcraft_to_path(args.contourcraft_root)
    import torch
    from scipy import spatial
    from smplx.lbs import blend_shapes

    source_dict = load_pickle(args.source_garment_dict)
    source_lbs = source_dict["lbs"]
    source_betas = load_betas(
        args.source_betas, args.source_beta_index, args.source_betas_key
    )
    target_betas = load_betas(
        args.target_sequence, args.target_beta_index, args.target_betas_key
    )

    source_gender = args.source_gender or source_dict.get("gender") or args.target_gender
    target_model = make_body_model(args.body_model_root, args.model_type, args.target_gender)

    source_v = torch.as_tensor(source_lbs["v"], dtype=torch.float32)
    source_shapedirs = torch.as_tensor(source_lbs["shapedirs"], dtype=torch.float32)
    beta_tensor = torch.as_tensor(source_betas[None], dtype=torch.float32)
    fixed_vertices = (source_v[None] + blend_shapes(beta_tensor, source_shapedirs))[0]

    target_beta_tensor = torch.as_tensor(target_betas[None], dtype=torch.float32)
    with torch.no_grad():
        target_vertices = target_model(betas=target_beta_tensor).vertices[0]

    tree = spatial.cKDTree(target_vertices.detach().cpu().numpy())
    distances, target_vertex_ids = tree.query(
        fixed_vertices.detach().cpu().numpy(), k=1
    )

    n_posedirs = target_model.posedirs.shape[0]
    target_posedirs = (
        target_model.posedirs.reshape(n_posedirs, -1, 3)[:, target_vertex_ids]
        .reshape(n_posedirs, -1)
        .detach()
        .cpu()
        .numpy()
    )
    target_weights = target_model.lbs_weights[target_vertex_ids].detach().cpu().numpy()

    output_dict = copy.deepcopy(source_dict)
    output_lbs = output_dict["lbs"]
    output_lbs["v"] = fixed_vertices.detach().cpu().numpy()
    output_lbs["shapedirs"] = np.zeros_like(source_lbs["shapedirs"], dtype=np.float32)
    output_lbs["posedirs"] = target_posedirs.astype(np.float32)
    output_lbs["lbs_weights"] = target_weights.astype(np.float32)
    output_lbs["f"] = np.asarray(source_lbs.get("f", source_dict["faces"]))
    output_dict["gender"] = args.target_gender
    output_dict["fixed_size_metadata"] = {
        "source_garment_dict": str(args.source_garment_dict.resolve()),
        "source_betas": source_betas,
        "target_betas": target_betas,
        "source_gender": source_gender,
        "target_gender": args.target_gender,
        "model_type": args.model_type,
        "binding": "nearest target shaped-body vertex",
        "mean_binding_distance": float(np.mean(distances)),
        "max_binding_distance": float(np.max(distances)),
    }

    dump_pickle(output_dict, args.output_garment_dict)
    print(f"Wrote fixed-size garment dict: {args.output_garment_dict}")
    print(
        "Binding distance: "
        f"mean={np.mean(distances):.6f} m, max={np.max(distances):.6f} m"
    )


def configure_defaults(contourcraft_root: Path, data_root: Path) -> None:
    from utils.defaults import DEFAULTS

    DEFAULTS.project_dir = str(contourcraft_root.resolve())
    DEFAULTS.data_root = str(data_root.resolve())
    DEFAULTS.aux_data = str((data_root / "aux_data").resolve())
    DEFAULTS.experiment_root = str((data_root / "experiments").resolve())


def simulate(args: argparse.Namespace) -> None:
    add_contourcraft_to_path(args.contourcraft_root)
    configure_defaults(args.contourcraft_root, args.ccraft_data_root)

    import torch
    from utils.arguments import load_params
    from utils.common import move2device
    from utils.validation import (
        _load_runner_from_state_dict,
        apply_material_params,
        create_postcvpr_one_sequence_dataloader,
    )

    garment_dict = args.garment_dict.resolve()
    if not garment_dict.is_file():
        raise FileNotFoundError(garment_dict)
    checkpoint = args.checkpoint.resolve()
    if not checkpoint.is_file():
        raise FileNotFoundError(checkpoint)
    if args.output_trajectory.exists():
        raise FileExistsError(f"Refusing to overwrite existing file: {args.output_trajectory}")

    modules, config = load_params(
        "contourcraft", config_dir=str(args.contourcraft_root / "configs")
    )
    material = {
        "density": args.density,
        "lame_mu": args.lame_mu,
        "lame_lambda": args.lame_lambda,
        "bending_coeff": args.bending_coeff,
    }
    config = apply_material_params(config, material)
    checkpoint_state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    _, runner = _load_runner_from_state_dict(modules, config, checkpoint_state)
    runner = runner.to(args.device)

    dataloader = create_postcvpr_one_sequence_dataloader(
        str(args.target_sequence.resolve()),
        garment_dict.stem,
        config="contourcraft",
        sequence_loader=args.sequence_loader,
        obstacle_dict_file=(
            str(args.obstacle_dict.resolve()) if args.obstacle_dict else None
        ),
        gender=args.target_gender,
        garment_dicts_dir=str(garment_dict.parent),
        body_model_root=str(args.body_model_root.resolve()),
        separate_arms=args.separate_arms,
    )
    sequence = move2device(next(iter(dataloader)), args.device)
    trajectory = dict(
        runner.valid_rollout(
            sequence,
            bare=True,
            n_steps=args.n_steps,
            safecheck=not args.disable_safecheck,
        )
    )

    trajectory["garment_names"] = [args.gaussian_garment_name]
    trajectory["fixed_size_metadata"] = load_pickle(garment_dict).get(
        "fixed_size_metadata", {}
    )
    dump_pickle(trajectory, args.output_trajectory)
    print(f"Wrote trajectory: {args.output_trajectory}")


def path(value: str) -> Path:
    return Path(value).expanduser()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prep = subparsers.add_parser("prepare", help="Create a new fixed-size garment dictionary")
    prep.add_argument("--contourcraft-root", type=path, required=True)
    prep.add_argument("--body-model-root", type=path, required=True)
    prep.add_argument("--source-garment-dict", type=path, required=True)
    prep.add_argument("--output-garment-dict", type=path, required=True)
    prep.add_argument("--source-betas", type=path, required=True)
    prep.add_argument("--source-betas-key", default="betas")
    prep.add_argument("--source-beta-index", type=int, default=0)
    prep.add_argument("--target-sequence", type=path, required=True)
    prep.add_argument("--target-betas-key", default="betas")
    prep.add_argument("--target-beta-index", type=int, default=0)
    prep.add_argument("--model-type", choices=("smpl", "smplx"), default="smpl")
    prep.add_argument("--source-gender", choices=("male", "female", "neutral"))
    prep.add_argument(
        "--target-gender", choices=("male", "female", "neutral"), required=True
    )
    prep.set_defaults(func=prepare)

    run = subparsers.add_parser("simulate", help="Run official ContourCraft checkpoint")
    run.add_argument("--contourcraft-root", type=path, required=True)
    run.add_argument("--ccraft-data-root", type=path, required=True)
    run.add_argument("--body-model-root", type=path, required=True)
    run.add_argument("--garment-dict", type=path, required=True)
    run.add_argument("--target-sequence", type=path, required=True)
    run.add_argument("--checkpoint", type=path, required=True)
    run.add_argument("--output-trajectory", type=path, required=True)
    run.add_argument("--gaussian-garment-name", required=True)
    run.add_argument("--sequence-loader", default="cmu_npz_smpl")
    run.add_argument(
        "--target-gender", choices=("male", "female", "neutral"), required=True
    )
    run.add_argument("--obstacle-dict", type=path)
    run.add_argument("--n-steps", type=int, default=200)
    run.add_argument("--device", default="cuda:0")
    run.add_argument(
        "--separate-arms", action=argparse.BooleanOptionalAction, default=True
    )
    run.add_argument("--disable-safecheck", action="store_true")
    run.add_argument("--density", type=float, default=0.20022)
    run.add_argument("--lame-mu", type=float, default=23600.0)
    run.add_argument("--lame-lambda", type=float, default=44400.0)
    run.add_argument("--bending-coeff", type=float, default=3.962e-5)
    run.set_defaults(func=simulate)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
