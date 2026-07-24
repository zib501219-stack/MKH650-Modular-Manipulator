from __future__ import annotations

import csv
from pathlib import Path


REPOS = {
    "AI-Vision-4Axis-Robot-Arm": {
        "zones": [
            ("worktable/frame", lambda x, y, z: z < 850),
            ("robot base/J1", lambda x, y, z: z < 1100 and abs(x) < 260 and abs(y) < 260),
            ("arm/joints", lambda x, y, z: z >= 1050 and abs(x) < 650),
            ("vision/safety", lambda x, y, z: True),
        ]
    },
    "Automatic-Feeding-Inspection-System": {
        "zones": [
            ("machine frame", lambda x, y, z: z < 850),
            ("feeding/separation", lambda x, y, z: z >= 850 and x < 250),
            ("inspection station", lambda x, y, z: z >= 850 and 200 <= x < 500),
            ("sorting/discharge", lambda x, y, z: z >= 700 and x >= 450),
            ("guard/control", lambda x, y, z: True),
        ]
    },
    "MKH650-Modular-Manipulator": {
        "zones": [
            ("foundation/J1", lambda x, y, z: z < 350),
            ("shoulder/J2", lambda x, y, z: z < 850 and x < 300),
            ("arm/J3", lambda x, y, z: x < 950),
            ("wrist/gripper", lambda x, y, z: True),
        ]
    },
}


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def classify(penetrations: list[float], exact_volume: float, bbox_volume: float):
    min_penetration = min(penetrations)
    fill_ratio = exact_volume / bbox_volume if bbox_volume else 0.0
    if min_penetration <= 1.0 and exact_volume < 5000:
        return (
            "possible fitted/contact interface",
            "Confirm intended fit/contact; suppress only after component names and nominal clearance are checked.",
        )
    if min_penetration >= 5.0 and fill_ratio >= 0.35:
        return (
            "probable construction-geometry overlap",
            "Open the named components, trim/fuse construction solids or reposition parts, then rerun exact interference.",
        )
    return (
        "ambiguous overlap",
        "Assign component identity and inspect section view; classify as intended interface or real interference.",
    )


def main():
    script = Path(__file__).resolve()
    local_repo = script.parents[2]
    if local_repo.name in REPOS:
        root = local_repo.parent
        selected = {local_repo.name: REPOS[local_repo.name]}
    else:
        root = script.parents[1] / "repo_sync"
        selected = REPOS
    for repo_name, config in selected.items():
        folder = root / repo_name / "native_sources" / "collision_validation"
        boxes = {
            int(row["solid_index"]): row
            for row in read_csv(folder / "solid_bounding_boxes.csv")
        }
        pairs = read_csv(folder / "overlap_pairs.csv")
        output_rows = []
        for rank, row in enumerate(pairs, 1):
            a = boxes[int(row["solid_a"])]
            b = boxes[int(row["solid_b"])]
            center = []
            for low, high in (("xmin", "xmax"), ("ymin", "ymax"), ("zmin", "zmax")):
                a_center = (float(a[low]) + float(a[high])) / 2
                b_center = (float(b[low]) + float(b[high])) / 2
                center.append((a_center + b_center) / 2)
            zone = next(name for name, rule in config["zones"] if rule(*center))
            penetrations = [
                float(row["bbox_overlap_x_mm"]),
                float(row["bbox_overlap_y_mm"]),
                float(row["bbox_overlap_z_mm"]),
            ]
            exact_volume = float(row["exact_common_volume_mm3"])
            bbox_volume = float(row["bbox_overlap_volume_mm3"])
            category, action = classify(penetrations, exact_volume, bbox_volume)
            priority = "P1" if exact_volume >= 100000 else "P2" if exact_volume >= 5000 else "P3"
            output_rows.append(
                {
                    "rank": rank,
                    "priority": priority,
                    "solid_a": row["solid_a"],
                    "solid_b": row["solid_b"],
                    "zone_inference": zone,
                    "pair_center_x_mm": round(center[0], 3),
                    "pair_center_y_mm": round(center[1], 3),
                    "pair_center_z_mm": round(center[2], 3),
                    "min_bbox_penetration_mm": round(min(penetrations), 3),
                    "exact_common_volume_mm3": round(exact_volume, 3),
                    "category_inference": category,
                    "required_action": action,
                    "review_status": "OPEN",
                }
            )
        fields = list(output_rows[0])
        with (folder / "overlap_classification_worklist.csv").open(
            "w", encoding="utf-8-sig", newline=""
        ) as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(output_rows)
        counts = {priority: sum(r["priority"] == priority for r in output_rows) for priority in ("P1", "P2", "P3")}
        report = f"""# 实体交叠分类与整改清单

## 当前统计

- 精确交叠对：{len(output_rows)}
- P1（共同体积不小于100,000 mm3）：{counts['P1']}
- P2（5,000至100,000 mm3）：{counts['P2']}
- P3（小于5,000 mm3）：{counts['P3']}

## 使用方法

`overlap_classification_worklist.csv` 按共同体积从大到小排列，并根据实体空间中心推测所在机构区域。`category_inference` 是几何启发式判断，不是最终审批结论。

整改时应先处理 P1：在原生装配中给 `solid_a`、`solid_b` 对应组件分配名称，打开剖视图，判断是预期配合、焊接/并体构造还是实际穿透。完成后将 `review_status` 改为 `ACCEPTED_INTERFACE`、`FIXED` 或 `FALSE_POSITIVE`，重新导出 STEP 并运行 `run_collision_screening.py`。只有所有真实干涉关闭后，才能声明装配通过干涉检查。
"""
        (folder / "overlap_classification_report.md").write_text(report, encoding="utf-8")
        print(repo_name, counts)


if __name__ == "__main__":
    main()
