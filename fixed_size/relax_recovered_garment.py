#!/usr/bin/env python3
"""Relax a recovered garment and write a new dictionary without modifying input."""

import argparse
import copy
import pickle
import sys
from pathlib import Path


def dump_new(value, path):
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        pickle.dump(value, handle)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contourcraft-root", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--body-model-root", type=Path, required=True)
    parser.add_argument("--input-garment-dict", type=Path, required=True)
    parser.add_argument("--output-garment-dict", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--trajectory-output", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--gender", choices=("male", "female", "neutral"), required=True)
    args = parser.parse_args()

    for output in (args.output_garment_dict, args.trajectory_output):
        if output.exists():
            raise FileExistsError(f"Refusing to overwrite: {output}")
    if args.input_garment_dict.resolve() == args.output_garment_dict.resolve():
        raise ValueError("Input and output garment dictionaries must be different")

    sys.path.insert(0, str(args.contourcraft_root.resolve()))
    from utils.defaults import DEFAULTS
    from utils.mesh_creation import GarmentCreator

    DEFAULTS.project_dir = str(args.contourcraft_root.resolve())
    DEFAULTS.data_root = str(args.data_root.resolve())
    DEFAULTS.aux_data = str((args.data_root / "aux_data").resolve())
    DEFAULTS.experiment_root = str((args.data_root / "experiments").resolve())

    with args.input_garment_dict.open("rb") as handle:
        source_garment = copy.deepcopy(pickle.load(handle))
    dump_new(source_garment, args.output_garment_dict)

    creator = GarmentCreator(
        str(args.output_garment_dict.parent),
        str(args.body_model_root),
        "smplx",
        args.gender,
        collect_lbs=True,
        n_samples_lbs=0,
        coarse=False,
        swap_axes=False,
    )
    # ContourCraft's relax_zeropos writes back to the dictionary it receives.
    # It is deliberately pointed at the newly created output copy.
    trajectory = creator.relax_zeropos(
        args.output_garment_dict.stem, str(args.checkpoint), n_steps=args.steps
    )
    dump_new(trajectory, args.trajectory_output)

    with args.output_garment_dict.open("rb") as handle:
        garment = pickle.load(handle)
    metadata = garment.setdefault("recovery_metadata", {})
    metadata["relaxed"] = True
    metadata["relaxation_steps"] = args.steps
    metadata["relaxation_trajectory"] = str(args.trajectory_output.resolve())
    metadata["unrelaxed_source"] = str(args.input_garment_dict.resolve())
    with args.output_garment_dict.open("wb") as handle:
        pickle.dump(garment, handle)
    print(f"Input preserved: {args.input_garment_dict}")
    print(f"Relaxed garment copy: {args.output_garment_dict}")
    print(f"Relaxation trajectory: {args.trajectory_output}")


if __name__ == "__main__":
    main()
