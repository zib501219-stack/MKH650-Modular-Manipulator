from pathlib import Path
import csv
import math

import matplotlib.pyplot as plt
import numpy as np


OUT = Path(__file__).resolve().parent / "output"


def write_csv(path, headers, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerows(rows)


def four_axis():
    folder = OUT / "01_4axis_robot"
    folder.mkdir(parents=True, exist_ok=True)
    l1, l2, tool = 230.0, 190.0, 70.0
    rows = []
    xs, zs, singular = [], [], []
    for j2 in np.linspace(-20, 105, 51):
        for j3 in np.linspace(-120, 120, 61):
            t2, t23 = math.radians(j2), math.radians(j2 + j3)
            x = l1 * math.cos(t2) + (l2 + tool) * math.cos(t23)
            z = l1 * math.sin(t2) + (l2 + tool) * math.sin(t23)
            r = math.hypot(x, z)
            near_sing = abs(math.sin(math.radians(j3))) < 0.0872
            self_clear = not (x < 80 and z < -80)
            rows.append([j2,j3,x,z,r,near_sing,self_clear])
            xs.append(x); zs.append(z); singular.append(near_sing)
    write_csv(folder / "workspace_samples.csv",
              ["J2_deg","J3_deg","x_from_shoulder_mm","z_from_shoulder_mm","radius_mm","near_planar_singularity","coarse_base_clearance"], rows)
    arr = np.array(singular)
    xs, zs = np.array(xs), np.array(zs)
    fig, ax = plt.subplots(figsize=(9,7))
    ax.scatter(xs[~arr],zs[~arr],s=4,c="#2b78e4",alpha=.45,label="sampled workspace")
    ax.scatter(xs[arr],zs[arr],s=7,c="#cc3333",alpha=.75,label="near straight/folded singularity")
    ax.axhline(0,color="#555",lw=.8); ax.axvline(0,color="#555",lw=.8)
    ax.set_aspect("equal"); ax.grid(alpha=.25)
    ax.set_xlabel("X from shoulder (mm)"); ax.set_ylabel("Z from shoulder (mm)")
    ax.set_title("Four-axis robot planar workspace sample")
    ax.legend(loc="best"); fig.tight_layout()
    fig.savefig(folder / "workspace_map.png", dpi=180); plt.close(fig)
    valid_r = [r[4] for r in rows if r[6]]
    report = f"""# Four-axis robot motion-envelope validation

## Inputs

- Upper-arm joint distance: 230 mm
- Forearm joint distance: 190 mm
- Tool offset: 70 mm
- J2 sample range: -20 to 105 degrees
- J3 sample range: -120 to 120 degrees
- Sample count: {len(rows)}

## Results

- Maximum sampled shoulder-relative radius: {max(valid_r):.1f} mm
- Minimum sampled shoulder-relative radius: {min(valid_r):.1f} mm
- The 490 mm theoretical straight reach is reproduced by the sampled model.
- Samples with `abs(sin(J3)) < 0.0872` are flagged as near planar straight/folded singularities.
- A coarse base-clearance flag rejects only poses with X below 80 mm and Z below -80 mm; it is a screening rule, not solid-body collision detection.

## Interpretation

The map is suitable for explaining reach, elbow-up/elbow-down posture and why motion planning should avoid fully straight or folded configurations. J1 and J4 rotations are not included in this planar map. Final collision validation requires the native assembly, tooling, cables, workbench and safety guarding.
"""
    (folder / "motion_validation_report.md").write_text(report, encoding="utf-8")


def feeding():
    folder = OUT / "02_feeding_inspection"
    folder.mkdir(parents=True, exist_ok=True)
    phases = [
        ("feed_confirm",0.0,1.0,"feeder on; part reaches escapement"),
        ("separate",1.0,1.8,"rear gate closed before front gate opens"),
        ("transfer_out",1.8,3.0,"transfer cylinder extends"),
        ("inspect",3.0,4.0,"part clamped; camera trigger"),
        ("return_buffer",4.0,5.0,"transfer returns; next part buffers"),
    ]
    write_csv(folder / "cycle_timeline.csv",
              ["phase","start_s","end_s","duration_s","action"],
              [[n,s,e,e-s,a] for n,s,e,a in phases])
    interlocks = [
        ["transfer_extend","part_present AND separator_closed AND nest_clear","camera_trigger, transfer_retract","prevent double feed and motion blur"],
        ["camera_trigger","transfer_extended AND clamp_confirmed","transfer_retract","inspection only at stable position"],
        ["transfer_retract","inspection_complete OR reject_timeout","transfer_extend","return before next feed"],
        ["front_gate_open","rear_gate_closed AND transfer_home","rear_gate_open","release one part only"],
        ["rear_gate_open","front_gate_closed","front_gate_open","refill escapement pocket"],
    ]
    write_csv(folder / "interlock_matrix.csv",
              ["command","required_conditions","mutually_exclusive_with","purpose"], interlocks)
    samples=[]
    for t in np.linspace(0,5,51):
        phase=next((p[0] for p in phases if p[1] <= t < p[2]),"cycle_complete")
        sep = 1 if 1.0 <= t < 1.8 else 0
        transfer = 0 if t < 1.8 else min(1,(t-1.8)/1.2) if t<3 else 1 if t<4 else max(0,1-(t-4))
        inspect = 1 if 3 <= t < 4 else 0
        samples.append([round(t,2),phase,sep,round(transfer,3),inspect])
    write_csv(folder / "cycle_state_samples.csv",
              ["time_s","phase","separator_active","transfer_normalized_position","inspection_active"],samples)
    fig,ax=plt.subplots(figsize=(10,4.5))
    colors=["#4e79a7","#f28e2b","#59a14f","#e15759","#b07aa1"]
    for idx,(name,start,end,action) in enumerate(phases):
        ax.barh(0,end-start,left=start,height=.5,color=colors[idx],label=name)
        ax.text((start+end)/2,0,name,ha="center",va="center",fontsize=9,color="white")
    ax.set_xlim(0,5); ax.set_yticks([]); ax.set_xlabel("Cycle time (s)")
    ax.set_title("Automatic feeding system - 5 second cycle allocation")
    ax.grid(axis="x",alpha=.25); fig.tight_layout()
    fig.savefig(folder/"cycle_timeline.png",dpi=180); plt.close(fig)
    report = """# Feeding-system sequence and interlock validation

## Result

The proposed sequence closes in exactly 5.0 seconds, matching the 12 parts/min target. The generated state table samples the sequence every 0.1 seconds.

The critical logical rules are:

- rear gate closes before the front gate releases a part;
- transfer extension requires part presence, separator confirmation and a clear nest;
- camera trigger requires transfer-extended and clamp confirmation;
- the next feed cannot start until transfer-home is true.

## Boundary

This is an offline sequence model, not a PLC simulation. Valve switching time, cylinder cushioning, sensor debounce, image-processing time, reject handling and fault recovery must be commissioned on the selected hardware. The 5-second cycle remains a design target until measured.
"""
    (folder/"motion_validation_report.md").write_text(report,encoding="utf-8")


def mkh650():
    folder = OUT / "03_mkh650"
    folder.mkdir(parents=True, exist_ok=True)
    l1,l2,tool=520.0,480.0,180.0
    horizontal_static = 9.81 * (
        38*0.26
        +24*(0.52+0.24)
        +18*(0.52+0.57)
        +20*(0.52+0.66)
    )
    dynamic_service=1552/horizontal_static
    rows=[]; xs=[]; zs=[]; util=[]; sing=[]
    for j2 in np.linspace(-60,120,61):
        for j3 in np.linspace(-135,135,73):
            t2=math.radians(j2); t23=math.radians(j2+j3)
            x=l1*math.cos(t2)+(l2+tool)*math.cos(t23)
            z=l1*math.sin(t2)+(l2+tool)*math.sin(t23)
            static=9.81*(
                38*0.26*math.cos(t2)
                +24*(0.52*math.cos(t2)+0.24*math.cos(t23))
                +18*(0.52*math.cos(t2)+0.57*math.cos(t23))
                +20*(0.52*math.cos(t2)+0.66*math.cos(t23))
            )
            equiv=abs(static)*dynamic_service
            u=equiv/1552
            near=abs(math.sin(math.radians(j3)))<0.0872
            rows.append([j2,j3,x,z,math.hypot(x,z),static,equiv,u,near])
            xs.append(x);zs.append(z);util.append(u);sing.append(near)
    write_csv(folder/"workspace_load_samples.csv",
              ["J2_deg","J3_deg","x_from_shoulder_mm","z_from_shoulder_mm","radius_mm","static_J2_moment_Nm","factored_equivalent_Nm","design_torque_utilization","near_planar_singularity"],rows)
    xs=np.array(xs);zs=np.array(zs);util=np.array(util);sing=np.array(sing)
    fig,ax=plt.subplots(figsize=(9,7))
    sc=ax.scatter(xs,zs,c=util,s=5,cmap="viridis",vmin=0,vmax=1)
    ax.scatter(xs[sing],zs[sing],facecolors="none",edgecolors="#d62728",s=15,lw=.5,label="near singularity")
    ax.set_aspect("equal");ax.grid(alpha=.25)
    ax.set_xlabel("X from shoulder (mm)");ax.set_ylabel("Z from shoulder (mm)")
    ax.set_title("MKH650 sampled workspace and J2 torque utilization")
    fig.colorbar(sc,ax=ax,label="factored J2 torque / 1552 N.m")
    ax.legend(loc="best");fig.tight_layout()
    fig.savefig(folder/"workspace_load_map.png",dpi=180);plt.close(fig)
    report=f"""# MKH650 motion-envelope and pose-load validation

## Inputs and assumptions

- Upper arm: 520 mm; forearm: 480 mm; tool offset: 180 mm
- Assumed J2 sample range: -60 to 120 degrees
- Assumed J3 sample range: -135 to 135 degrees
- Sample count: {len(rows)}
- Mass model: 38 kg upper arm, 24 kg forearm, 18 kg tool and 20 kg payload
- Static moment is multiplied by {dynamic_service:.3f} so the horizontal reference pose aligns with the 1552 N.m design baseline.

## Results

- Maximum sampled radius: {max(r[4] for r in rows):.1f} mm
- Maximum sampled factored J2 torque: {max(r[6] for r in rows):.1f} N.m
- Maximum sampled utilization of the 1552 N.m baseline: {max(r[7] for r in rows):.3f}
- Near-singularity samples use `abs(sin(J3)) < 0.0872`.

## Interpretation

The horizontal extended posture remains the governing J2 load region. Folded and straight elbow configurations are highlighted for motion-planning caution. The map supports portfolio-level posture and load reasoning, but it does not include J1 rotation, 3D wrist orientation, gearbox inertia, structural flexibility, collision solids or controller acceleration limits.
"""
    (folder/"motion_validation_report.md").write_text(report,encoding="utf-8")


def main():
    four_axis()
    feeding()
    mkh650()
    print("motion validation generated")


if __name__=="__main__":
    main()
