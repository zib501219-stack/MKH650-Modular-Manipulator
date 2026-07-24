from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path


MODEL_FILE = {
    "AI-Vision-4Axis-Robot-Arm": "detailed_robot_workcell.py",
    "Automatic-Feeding-Inspection-System": "automatic_feeding_inspection.py",
    "MKH650-Modular-Manipulator": "mkh650_manipulator.py",
}


def load_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def capture_parts(model_path):
    model_dir = model_path.parent
    sys.path.insert(0, str(model_dir))
    try:
        module_name = "component_map_" + model_path.parent.parent.name.replace("-", "_")
        spec = importlib.util.spec_from_file_location(module_name, model_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        captured = {}
        module.assembly = lambda parts, name: captured.update(parts=parts, name=name) or parts
        module.gen_step()
        return captured["parts"]
    finally:
        sys.path.pop(0)


def flatten(parts):
    rows = []
    index = 0
    for component_order, part in enumerate(parts, 1):
        solids = list(part.solids())
        for child_order, solid in enumerate(solids, 1):
            box = solid.bounding_box()
            rows.append(
                {
                    "solid_index": index,
                    "component_order": component_order,
                    "component_name": part.label,
                    "component_child_solid": child_order,
                    "component_solid_count": len(solids),
                    "xmin": box.min.X,
                    "ymin": box.min.Y,
                    "zmin": box.min.Z,
                    "xmax": box.max.X,
                    "ymax": box.max.Y,
                    "zmax": box.max.Z,
                }
            )
            index += 1
    return rows


def main():
    script = Path(__file__).resolve()
    possible_repo = script.parents[2]
    if possible_repo.name in MODEL_FILE:
        repos = [possible_repo]
    else:
        root = script.parents[1] / "repo_sync"
        repos = [root / name for name in MODEL_FILE]
    for repo in repos:
        collision = repo / "native_sources" / "collision_validation"
        exported = load_rows(collision / "solid_bounding_boxes.csv")
        mapped = flatten(capture_parts(repo / "models" / MODEL_FILE[repo.name]))
        if len(exported) != len(mapped):
            raise RuntimeError(f"{repo.name}: solid count mismatch {len(mapped)} != {len(exported)}")
        max_error = 0.0
        for generated, step_row in zip(mapped, exported):
            for field in ("xmin", "ymin", "zmin", "xmax", "ymax", "zmax"):
                max_error = max(max_error, abs(generated[field] - float(step_row[field])))
        verified = max_error <= 0.001
        if not verified:
            raise RuntimeError(f"{repo.name}: STEP order/bbox mismatch, max error {max_error}")
        fields = list(mapped[0])
        with (collision / "solid_component_map.csv").open(
            "w", encoding="utf-8-sig", newline=""
        ) as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(mapped)
        map_by_index = {str(r["solid_index"]): r["component_name"] for r in mapped}
        worklist = load_rows(collision / "overlap_classification_worklist.csv")
        new_fields = list(worklist[0])
        insert_at = new_fields.index("solid_b") + 1
        for field in ("component_a", "component_b"):
            if field not in new_fields:
                new_fields.insert(insert_at, field)
                insert_at += 1
        for row in worklist:
            row["component_a"] = map_by_index[row["solid_a"]]
            row["component_b"] = map_by_index[row["solid_b"]]
        with (collision / "overlap_classification_worklist.csv").open(
            "w", encoding="utf-8-sig", newline=""
        ) as f:
            writer = csv.DictWriter(f, fieldnames=new_fields)
            writer.writeheader()
            writer.writerows(worklist)
        report = f"""# STEP实体与部件名称映射

- 映射实体数：{len(mapped)}
- 参数化源码部件数：{len(parts := capture_parts(repo / 'models' / MODEL_FILE[repo.name]))}
- STEP包围盒最大匹配误差：{max_error:.9f} mm
- 映射状态：{'VERIFIED' if verified else 'FAILED'}

映射方法是在不修改参数化源码的前提下捕获其有标签的部件列表，按每个部件包含的实体展开，并逐项与导出STEP的实体包围盒核对。只有实体数量一致且六个包围盒坐标最大误差不超过0.001 mm时才写入结果。

`solid_component_map.csv` 现在可把 `solid_index` 追溯到 `component_name`；`overlap_classification_worklist.csv` 也已增加 `component_a` 和 `component_b`，后续干涉整改不再只依赖数字编号。
"""
        (collision / "solid_component_mapping_report.md").write_text(report, encoding="utf-8")
        print(repo.name, len(mapped), max_error)


if __name__ == "__main__":
    main()
