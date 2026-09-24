#!/usr/bin/env python3
"""Dependency-light structural smoke test for this handoff."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md", "HANDOFF.md", "PIPELINE.md", "DATA_FORMAT.md",
    "THIRD_PARTY_NOTICES.md", "configs/sample_pipeline.yaml",
    "examples/cameras.example.json", "examples/tiny_template.obj",
    "fixed_size/README.md", "fixed_size/inspect_garment_dict.py",
    "RESULT_OPTIMIZATION_TOOLS.md", "result_optimization/README.md",
    "result_optimization/curved_hem_candidates.py",
    "result_optimization/derive_view_camera_mapping.py",
    "result_optimization/review_dino_sam2_masks.py",
    "result_optimization/install_reviewed_masks.py",
    "result_optimization/audit_tsdf_views.py",
    "result_optimization/prepare_stratified_finetune.py",
    "result_optimization/repair_mesh_boundaries.py",
    "result_optimization/pin_boundary_loop.py",
    "result_optimization/experimental_smplx_pose_transfer.py",
    "result_optimization/exact_pose_contourcraft.md",
]

def parse_obj(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    vertices = sum(line.startswith("v ") for line in lines)
    faces = sum(line.startswith("f ") for line in lines)
    assert vertices >= 3 and faces >= 1
    return vertices, faces

def validate_camera(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data
    for name, camera in data.items():
        assert name.startswith("Cam")
        assert len(camera["intrinsics"]) == 3
        assert all(len(row) == 3 for row in camera["intrinsics"])
        assert len(camera["extrinsics"]) == 3
        assert all(len(row) == 4 for row in camera["extrinsics"])
        assert len(camera["shape"]) == 2
    return len(data)

def main():
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    if missing:
        raise SystemExit("Missing required files: " + repr(missing))
    vertices, faces = parse_obj(ROOT / "examples/tiny_template.obj")
    cameras = validate_camera(ROOT / "examples/cameras.example.json")
    print(f"PASS: {len(REQUIRED)} files; OBJ {vertices}v/{faces}f; {cameras} camera")

if __name__ == "__main__":
    main()
