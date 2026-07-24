from pathlib import Path
import csv
import json
import time

import cadquery as cq


SCRIPT_DIR = Path(__file__).resolve().parent
REPO = SCRIPT_DIR.parents[1]
OUT = SCRIPT_DIR
MODEL_BY_REPO = {
    "AI-Vision-4Axis-Robot-Arm": ("01_4axis_robot", "detailed_robot_workcell.step"),
    "Automatic-Feeding-Inspection-System": ("02_feeding_inspection", "automatic_feeding_inspection.step"),
    "MKH650-Modular-Manipulator": ("03_mkh650", "mkh650_manipulator.step"),
}


def bbox_tuple(shape):
    b = shape.BoundingBox()
    return (b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax)


def bbox_overlap(a,b,tol=0.05):
    dx=min(a[3],b[3])-max(a[0],b[0])
    dy=min(a[4],b[4])-max(a[1],b[1])
    dz=min(a[5],b[5])-max(a[2],b[2])
    return dx,dy,dz, dx>tol and dy>tol and dz>tol


def screen(slug,path):
    started=time.time()
    model=cq.importers.importStep(str(path))
    solids=model.solids().vals()
    boxes=[bbox_tuple(s) for s in solids]
    candidates=[]
    for i in range(len(solids)):
        for j in range(i+1,len(solids)):
            dx,dy,dz,overlap=bbox_overlap(boxes[i],boxes[j])
            if overlap:
                candidates.append((i,j,dx,dy,dz,dx*dy*dz))
    candidates.sort(key=lambda x:x[5],reverse=True)
    exact=[]
    failures=[]
    for i,j,dx,dy,dz,bbox_vol in candidates:
        try:
            common=solids[i].intersect(solids[j])
            vol=common.Volume() if common is not None else 0.0
            if vol>0.5:
                exact.append((i,j,dx,dy,dz,bbox_vol,vol))
        except Exception as exc:
            failures.append((i,j,repr(exc)))
    exact.sort(key=lambda x:x[6],reverse=True)
    folder=OUT/slug
    folder.mkdir(parents=True,exist_ok=True)
    with (folder/"solid_bounding_boxes.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.writer(f);w.writerow(["solid_index","xmin","ymin","zmin","xmax","ymax","zmax"])
        for idx,b in enumerate(boxes):w.writerow([idx,*b])
    with (folder/"overlap_pairs.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.writer(f);w.writerow(["solid_a","solid_b","bbox_overlap_x_mm","bbox_overlap_y_mm","bbox_overlap_z_mm","bbox_overlap_volume_mm3","exact_common_volume_mm3"])
        w.writerows(exact)
    summary={
        "source_step":str(path),
        "solid_count":len(solids),
        "bbox_candidate_pair_count":len(candidates),
        "exact_overlap_pair_count":len(exact),
        "exact_intersection_failures":len(failures),
        "exact_overlap_threshold_mm3":0.5,
        "runtime_seconds":round(time.time()-started,3),
        "largest_overlap_pairs":[
            {"solid_a":r[0],"solid_b":r[1],"common_volume_mm3":r[6]} for r in exact[:20]
        ],
    }
    (folder/"collision_screening_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    report=f"""# Detailed STEP solid-overlap screening

## Result

- Source: `{path.name}`
- Imported solid count: {len(solids)}
- Broad-phase bounding-box candidate pairs: {len(candidates)}
- Exact common-volume pairs above 0.5 mm3: {len(exact)}
- Exact intersection operation failures: {len(failures)}
- Runtime: {summary['runtime_seconds']} s

## Interpretation

This is a static geometry-overlap screen over every imported solid in the detailed STEP. Bounding boxes are used only for broad-phase filtering; listed overlap pairs were then checked with exact CAD common-volume operations.

An overlap is not automatically a design error. The portfolio STEP uses simplified primitives, and intended press fits, fasteners, embedded motors, welded interfaces and visual envelopes can overlap by construction. STEP import in this workflow does not preserve a reliable part-name mapping for every solid, so `solid_a` and `solid_b` are stable indices only within this exported file.

Use `solid_bounding_boxes.csv` and `overlap_pairs.csv` to investigate the largest pairs. Final interference approval requires a native assembly with component identity, suppression rules, intended-contact definitions and joint-position sweeps.
"""
    (folder/"collision_screening_report.md").write_text(report,encoding="utf-8")
    return summary


def main():
    slug, filename = MODEL_BY_REPO[REPO.name]
    target = REPO / "models" / filename
    all_results={}
    all_results[slug]=screen(".",target)
    print(slug,all_results[slug])
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"all_projects_collision_summary.json").write_text(json.dumps(all_results,indent=2),encoding="utf-8")


if __name__=="__main__":
    main()
