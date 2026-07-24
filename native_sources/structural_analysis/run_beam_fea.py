from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


OUTPUT = Path(__file__).resolve().parent


@dataclass
class Case:
    key: str
    title: str
    component: str
    material: str
    e_mpa: float
    yield_mpa: float
    length_mm: float
    width_mm: float
    depth_mm: float
    elements: int
    support: str
    load_type: str
    load_n: float
    design_basis: str
    allowable_deflection_mm: float

    @property
    def inertia_mm4(self) -> float:
        return self.width_mm * self.depth_mm**3 / 12.0

    @property
    def area_mm2(self) -> float:
        return self.width_mm * self.depth_mm


CASES = [
    Case(
        key="01_4axis_robot",
        title="四轴机器人上臂等效梁",
        component="J2-J3 上臂双侧板",
        material="6061-T6 铝合金",
        e_mpa=69000.0,
        yield_mpa=240.0,
        length_mm=230.0,
        width_mm=24.0,
        depth_mm=70.0,
        elements=20,
        support="cantilever",
        load_type="tip",
        load_n=47_700.0 / 230.0,
        design_basis="用已完成关节校核中的 47.7 N·m 设计弯矩折算端部载荷；两块 12 mm 侧板按总宽 24 mm 等效。",
        allowable_deflection_mm=0.50,
    ),
    Case(
        key="02_feeding_inspection",
        title="上料检测线导轨底板等效梁",
        component="600 mm 检测输送段底板",
        material="6061-T6 铝合金",
        e_mpa=69000.0,
        yield_mpa=240.0,
        length_mm=600.0,
        width_mm=70.0,
        depth_mm=12.0,
        elements=24,
        support="simply_supported",
        load_type="center",
        load_n=150.0,
        design_basis="150 N 中央集中载荷代表工件、滑台及冲击放大后的初步组合载荷；未计两侧导轨的增刚作用，偏保守。",
        allowable_deflection_mm=0.80,
    ),
    Case(
        key="03_mkh650",
        title="MKH650 大臂等效梁",
        component="J2-J3 大臂双侧板",
        material="Q355 钢",
        e_mpa=206000.0,
        yield_mpa=355.0,
        length_mm=520.0,
        width_mm=40.0,
        depth_mm=110.0,
        elements=26,
        support="cantilever",
        load_type="tip",
        load_n=1_552_000.0 / 520.0,
        design_basis="用已完成 J2 校核中的 1552 N·m 设计弯矩折算端部载荷；两块 20 mm 侧板按总宽 40 mm 等效。",
        allowable_deflection_mm=1.00,
    ),
]


def element_stiffness(e_mpa: float, i_mm4: float, length_mm: float) -> np.ndarray:
    l = length_mm
    return e_mpa * i_mm4 / l**3 * np.array(
        [
            [12, 6 * l, -12, 6 * l],
            [6 * l, 4 * l**2, -6 * l, 2 * l**2],
            [-12, -6 * l, 12, -6 * l],
            [6 * l, 2 * l**2, -6 * l, 4 * l**2],
        ],
        dtype=float,
    )


def solve(case: Case) -> dict:
    n = case.elements
    nodes = n + 1
    le = case.length_mm / n
    dofs = nodes * 2
    k_global = np.zeros((dofs, dofs))
    f_global = np.zeros(dofs)
    ke = element_stiffness(case.e_mpa, case.inertia_mm4, le)

    for element in range(n):
        idx = np.array([2 * element, 2 * element + 1, 2 * element + 2, 2 * element + 3])
        k_global[np.ix_(idx, idx)] += ke

    if case.load_type == "tip":
        f_global[2 * n] = -case.load_n
    elif case.load_type == "center":
        middle = n // 2
        f_global[2 * middle] = -case.load_n
    else:
        raise ValueError(case.load_type)

    if case.support == "cantilever":
        fixed = [0, 1]
    elif case.support == "simply_supported":
        fixed = [0, 2 * n]
    else:
        raise ValueError(case.support)

    free = np.setdiff1d(np.arange(dofs), fixed)
    displacement = np.zeros(dofs)
    displacement[free] = np.linalg.solve(
        k_global[np.ix_(free, free)], f_global[free]
    )
    reactions = k_global @ displacement - f_global

    node_x = np.linspace(0.0, case.length_mm, nodes)
    node_w = displacement[0::2]
    element_rows = []
    max_stress = 0.0
    for element in range(n):
        idx = np.array([2 * element, 2 * element + 1, 2 * element + 2, 2 * element + 3])
        internal = ke @ displacement[idx]
        moment_left = internal[1]
        moment_right = -internal[3]
        stress_left = abs(moment_left) * (case.depth_mm / 2.0) / case.inertia_mm4
        stress_right = abs(moment_right) * (case.depth_mm / 2.0) / case.inertia_mm4
        max_stress = max(max_stress, stress_left, stress_right)
        element_rows.append(
            {
                "element": element + 1,
                "x_start_mm": element * le,
                "x_end_mm": (element + 1) * le,
                "moment_start_nmm": moment_left,
                "moment_end_nmm": moment_right,
                "stress_start_mpa": stress_left,
                "stress_end_mpa": stress_right,
            }
        )

    safety_factor = case.yield_mpa / max_stress if max_stress else float("inf")
    return {
        "node_x": node_x,
        "node_w": node_w,
        "node_rotation": displacement[1::2],
        "reactions": reactions,
        "elements": element_rows,
        "max_abs_deflection_mm": float(np.max(np.abs(node_w))),
        "max_bending_stress_mpa": float(max_stress),
        "yield_safety_factor": float(safety_factor),
        "stress_pass": bool(safety_factor >= 1.5),
        "deflection_pass": bool(
            float(np.max(np.abs(node_w))) <= case.allowable_deflection_mm
        ),
    }


def write_case(case: Case, result: dict) -> None:
    folder = OUTPUT
    folder.mkdir(parents=True, exist_ok=True)

    with (folder / "nodal_results.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["node", "x_mm", "deflection_mm", "rotation_rad"])
        writer.writeheader()
        for index, (x, w, rotation) in enumerate(
            zip(result["node_x"], result["node_w"], result["node_rotation"])
        ):
            writer.writerow(
                {
                    "node": index + 1,
                    "x_mm": x,
                    "deflection_mm": w,
                    "rotation_rad": rotation,
                }
            )

    with (folder / "element_results.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(result["elements"][0]))
        writer.writeheader()
        writer.writerows(result["elements"])

    x_mid = np.array([(r["x_start_mm"] + r["x_end_mm"]) / 2 for r in result["elements"]])
    stress = np.array(
        [max(r["stress_start_mpa"], r["stress_end_mpa"]) for r in result["elements"]]
    )
    fig, axes = plt.subplots(2, 1, figsize=(9, 7), constrained_layout=True)
    axes[0].plot(result["node_x"], result["node_w"], marker="o", ms=3)
    axes[0].axhline(0, color="black", lw=0.7)
    axes[0].set(xlabel="Position (mm)", ylabel="Deflection (mm)", title="Beam FE deflection")
    axes[0].grid(alpha=0.3)
    axes[1].plot(x_mid, stress, color="#b33", marker="o", ms=3)
    axes[1].axhline(case.yield_mpa / 1.5, color="#e99400", ls="--", label="yield / 1.5")
    axes[1].set(xlabel="Position (mm)", ylabel="Bending stress (MPa)", title="Element surface stress")
    axes[1].grid(alpha=0.3)
    axes[1].legend()
    fig.suptitle(f"{case.key} representative beam")
    fig.savefig(folder / "beam_fea_results.png", dpi=180)
    plt.close(fig)

    summary = {
        "analysis_method": "1D Euler-Bernoulli beam finite element method",
        "elements": case.elements,
        "material": case.material,
        "elastic_modulus_mpa": case.e_mpa,
        "yield_strength_mpa": case.yield_mpa,
        "length_mm": case.length_mm,
        "equivalent_width_mm": case.width_mm,
        "equivalent_depth_mm": case.depth_mm,
        "section_area_mm2": case.area_mm2,
        "second_moment_mm4": case.inertia_mm4,
        "support": case.support,
        "load_type": case.load_type,
        "load_n": case.load_n,
        "design_basis": case.design_basis,
        "max_abs_deflection_mm": result["max_abs_deflection_mm"],
        "allowable_deflection_mm": case.allowable_deflection_mm,
        "max_bending_stress_mpa": result["max_bending_stress_mpa"],
        "yield_safety_factor": result["yield_safety_factor"],
        "stress_pass_sf_1_5": result["stress_pass"],
        "deflection_pass": result["deflection_pass"],
    }
    (folder / "analysis_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    verdict = "通过初步筛查" if result["stress_pass"] and result["deflection_pass"] else "需优化后复核"
    report = f"""# {case.title}结构分析报告

## 结论

本算例按一维 Euler-Bernoulli 梁有限元计算，结论为：**{verdict}**。

- 最大弯曲应力：{result['max_bending_stress_mpa']:.2f} MPa
- 屈服安全系数：{result['yield_safety_factor']:.2f}
- 最大挠度：{result['max_abs_deflection_mm']:.3f} mm
- 本次挠度限值：{case.allowable_deflection_mm:.2f} mm

## 建模输入

- 代表部件：{case.component}
- 材料：{case.material}，弹性模量 {case.e_mpa / 1000:.1f} GPa，屈服强度 {case.yield_mpa:.0f} MPa
- 等效截面：{case.width_mm:.0f} mm × {case.depth_mm:.0f} mm
- 梁长：{case.length_mm:.0f} mm；单元数：{case.elements}
- 支承：{case.support}；载荷：{case.load_n:.1f} N（{case.load_type}）
- 载荷依据：{case.design_basis}

## 适用边界

这是用于作品集设计闭环的**简化梁有限元**，不是 NX/ANSYS 三维实体分析。它可以复核整体弯曲刚度和名义应力，但不能代表孔边、焊缝、圆角、轴承座、接触、螺栓预紧、板壳屈曲和瞬态冲击处的局部结果。正式加工前，应在原生装配清理干涉后，以真实材料、连接和载荷进行三维网格收敛分析，并对最大应力区域做局部细化。
"""
    (folder / "structural_analysis_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    aggregate = []
    repo_name = OUTPUT.parents[1].name
    key_by_repo = {
        "AI-Vision-4Axis-Robot-Arm": "01_4axis_robot",
        "Automatic-Feeding-Inspection-System": "02_feeding_inspection",
        "MKH650-Modular-Manipulator": "03_mkh650",
    }
    selected_key = key_by_repo[repo_name]
    for case in [item for item in CASES if item.key == selected_key]:
        result = solve(case)
        write_case(case, result)
        row = {
            "project": case.key,
            "max_abs_deflection_mm": result["max_abs_deflection_mm"],
            "max_bending_stress_mpa": result["max_bending_stress_mpa"],
            "yield_safety_factor": result["yield_safety_factor"],
            "stress_pass_sf_1_5": result["stress_pass"],
            "deflection_pass": result["deflection_pass"],
        }
        aggregate.append(row)
        print(row)
    (OUTPUT / "all_projects_structural_summary.json").write_text(
        json.dumps(aggregate, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
