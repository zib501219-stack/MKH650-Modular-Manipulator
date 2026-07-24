from pathlib import Path
import csv


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def decide(a, b):
    text = f"{a} {b}".lower()
    if "bolt" in text or "anchor" in text:
        return "EXPECTED_FASTENER_ENGAGEMENT", "Confirm hole/fastener identity and exclude only the engaged fastener pair in the native interference rules."
    envelope_words = ("envelope", "bearing", "reducer", "servo", "motor", "housing", "shaft")
    if sum(word in text for word in envelope_words) >= 2:
        return "EXPECTED_ENVELOPE_OVERLAP", "Replace nested visual envelopes with separate named purchased components or suppress the documented envelope pair."
    construction_words = ("frame", "rail", "rib", "plate", "pedestal", "tower", "bin", "guard", "cabinet", "flange")
    if any(word in text for word in construction_words):
        return "CONSTRUCTION_GEOMETRY_REMODEL", "Trim, fuse or reposition the construction geometry; rerun exact common-volume screening before closure."
    return "MANUAL_SECTION_REVIEW", "Open a section view in the native assembly and determine intended contact versus real interference."


def main():
    script = Path(__file__).resolve()
    possible_repo = script.parents[2]
    if (possible_repo / "native_sources" / "collision_validation").exists():
        repos = [possible_repo]
    else:
        repos = list((script.parents[1] / "repo_sync").glob("*"))
    for repo in repos:
        folder = repo / "native_sources" / "collision_validation"
        source = folder / "overlap_classification_worklist.csv"
        if not source.exists():
            continue
        rows = [row for row in read(source) if row["priority"] == "P1"]
        output = []
        for row in rows:
            disposition, action = decide(row["component_a"], row["component_b"])
            output.append(
                {
                    "rank": row["rank"],
                    "solid_a": row["solid_a"],
                    "component_a": row["component_a"],
                    "solid_b": row["solid_b"],
                    "component_b": row["component_b"],
                    "zone": row["zone_inference"],
                    "common_volume_mm3": row["exact_common_volume_mm3"],
                    "engineering_disposition": disposition,
                    "required_action": action,
                    "owner": "mechanical_design",
                    "closure_evidence": "named native assembly section view + rerun report",
                    "status": "DECISION_RECORDED_OPEN",
                }
            )
        fields = list(output[0])
        with (folder / "p1_interference_disposition.csv").open(
            "w", encoding="utf-8-sig", newline=""
        ) as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(output)
        counts = {}
        for row in output:
            counts[row["engineering_disposition"]] = counts.get(row["engineering_disposition"], 0) + 1
        lines = "\n".join(f"- {key}: {value}" for key, value in sorted(counts.items()))
        report = f"""# P1干涉处理决定

P1总数：{len(output)}

{lines}

每个P1对已经有部件名称、工程处理类型、整改动作、责任角色和关闭证据要求。状态统一保留为 `DECISION_RECORDED_OPEN`，因为记录处理决定不等于几何已经修改。

只有满足以下条件才能关闭：

1. 在带零件名称的原生装配中完成剖视确认；
2. 对构造重叠完成修剪、并体或重新定位；
3. 对包络件/紧固件建立明确的干涉排除规则；
4. 重新导出STEP并运行精确共同体积筛查；
5. 保存关闭前后截图和复查报告。
"""
        (folder / "p1_interference_disposition_report.md").write_text(report, encoding="utf-8")
        print(repo.name, len(output), counts)


if __name__ == "__main__":
    main()
