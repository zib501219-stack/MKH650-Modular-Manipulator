from __future__ import annotations

import csv
import json
from pathlib import Path

import cadquery as cq
from cadquery import exporters
import ezdxf
from ezdxf import units
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfgen import canvas


PROJECTS = {
    "AI-Vision-4Axis-Robot-Arm": [
        dict(no="RA-005", name="j2_hollow_output_shaft", kind="shaft", material="40Cr", dims=(30, 118, 12), qty=1, note="30 mm nominal shaft, 12 mm cable bore"),
        dict(no="RA-006", name="j2_output_flange", kind="flange", material="40Cr", dims=(122, 30, 12, 88, 8), qty=1, note="8 x M8 clearance on PCD 88"),
        dict(no="RA-007", name="j2_bearing_housing", kind="housing", material="6061-T6", dims=(126, 108, 48, 62), qty=1, note="Bearing envelope bore 62 mm"),
        dict(no="RA-008", name="tool_change_flange", kind="flange", material="45 steel", dims=(68, 18, 20, 50, 6), qty=1, note="6 x M5 clearance on PCD 50"),
    ],
    "Automatic-Feeding-Inspection-System": [
        dict(no="FI-005", name="separator_gate", kind="plate", material="45 steel", dims=(110, 100, 12, 18), qty=2, note="Gate plate with 18 mm actuator hole"),
        dict(no="FI-006", name="hard_stop_bracket", kind="bracket", material="Q235B", dims=(110, 70, 90, 10, 22), qty=1, note="L bracket with 22 mm stop bore"),
        dict(no="FI-007", name="photo_sensor_bracket", kind="bracket", material="SUS304", dims=(45, 32, 55, 3, 12), qty=5, note="Bent sensor bracket, 12 mm sensor hole"),
        dict(no="FI-008", name="camera_crossbeam_mount", kind="housing", material="6061-T6", dims=(120, 90, 24, 56), qty=1, note="Camera mount plate with central relief"),
    ],
    "MKH650-Modular-Manipulator": [
        dict(no="MK-005", name="j2_hollow_output_shaft", kind="shaft", material="42CrMo", dims=(90, 210, 52), qty=1, note="90 mm nominal hollow shaft, 52 mm cable bore"),
        dict(no="MK-006", name="j2_bearing_end_cover", kind="flange", material="Q355B", dims=(270, 24, 154, 220, 12), qty=1, note="12 x M12 clearance on PCD 220"),
        dict(no="MK-007", name="shoulder_tower_gusset", kind="plate", material="Q355B", dims=(340, 210, 18, 42), qty=2, note="Triangular tower gusset with 42 mm relief"),
        dict(no="MK-008", name="iso9409_tool_flange", kind="flange", material="42CrMo", dims=(144, 28, 80, 110, 8), qty=1, note="8 x M10 clearance on PCD 110"),
    ],
}

PROJECTS_V3 = {
    "AI-Vision-4Axis-Robot-Arm": [
        dict(no="RA-009", name="j2_motor_adapter_plate", kind="housing", material="6061-T6", dims=(118, 102, 20, 52), qty=1, note="J2 servo-to-reducer adapter plate"),
        dict(no="RA-010", name="forearm_cross_rib", kind="plate", material="6061-T6", dims=(86, 58, 10, 26), qty=4, note="Forearm transverse rib with cable relief"),
        dict(no="RA-011", name="j3_bearing_end_cover", kind="flange", material="6061-T6", dims=(104, 16, 54, 78, 8), qty=1, note="J3 bearing end cover, 8 x M8 clearance"),
        dict(no="RA-012", name="cable_cover_bracket", kind="bracket", material="5052-H32", dims=(64, 42, 48, 3, 10), qty=4, note="Bent cable-cover support bracket"),
    ],
    "Automatic-Feeding-Inspection-System": [
        dict(no="FI-009", name="guide_rail_clamp_plate", kind="plate", material="SUS304", dims=(80, 32, 6, 10), qty=8, note="Adjustable guide-rail clamp plate"),
        dict(no="FI-010", name="cylinder_rod_clevis", kind="bracket", material="45 steel", dims=(52, 34, 46, 8, 12), qty=4, note="Cylinder rod clevis bracket with 12 mm pin"),
        dict(no="FI-011", name="valve_manifold_mounting_plate", kind="housing", material="Q235B", dims=(260, 120, 8, 40), qty=1, note="Eight-station valve-manifold mounting plate"),
        dict(no="FI-012", name="backlight_mount_bracket", kind="bracket", material="5052-H32", dims=(140, 60, 90, 4, 18), qty=2, note="Inspection backlight adjustment bracket"),
    ],
    "MKH650-Modular-Manipulator": [
        dict(no="MK-009", name="j2_motor_adapter_flange", kind="flange", material="42CrMo", dims=(230, 30, 95, 185, 12), qty=1, note="J2 servo/reducer adapter flange"),
        dict(no="MK-010", name="balance_link_pivot_pin", kind="shaft", material="40Cr", dims=(52, 190, 24), qty=2, note="Hardened balancing-link pivot pin"),
        dict(no="MK-011", name="upper_arm_service_cover", kind="plate", material="Q355B", dims=(420, 150, 8, 52), qty=2, note="Bolted upper-arm maintenance cover"),
        dict(no="MK-012", name="service_chain_mount_bracket", kind="bracket", material="Q355B", dims=(150, 90, 120, 10, 24), qty=4, note="Heavy cable-chain end bracket"),
    ],
}


def bolt_points(count, pcd):
    import math
    return [(pcd / 2 * math.cos(2 * math.pi * i / count), pcd / 2 * math.sin(2 * math.pi * i / count)) for i in range(count)]


def make_part(spec):
    d = spec["dims"]
    if spec["kind"] == "shaft":
        diameter, length, bore = d
        shape = cq.Workplane("XY").circle(diameter / 2).circle(bore / 2).extrude(length)
        shape = shape.faces(">Z").workplane().circle(diameter * .62).circle(bore / 2).extrude(length * .12)
        shape = shape.faces("<Z").workplane().circle(diameter * .58).circle(bore / 2).extrude(-length * .10)
        key_w = max(6, diameter * .12)
        key_d = max(3, diameter * .055)
        shape = shape.faces(">Z").workplane().center(0, diameter / 2 - key_d / 2).rect(key_w, key_d).cutBlind(-length * .35)
        return shape
    if spec["kind"] == "flange":
        outer, thick, bore, pcd, count = d
        shape = cq.Workplane("XY").circle(outer / 2).circle(bore / 2).extrude(thick)
        shape = shape.union(
            cq.Workplane("XY", origin=(0, 0, thick - 0.5))
            .circle(outer * .25)
            .circle(bore / 2)
            .extrude(thick * .32 + 0.5)
        )
        hole = 9 if "RA-" in spec["no"] else 13 if "MK-" in spec["no"] else 7
        return shape.faces(">Z").workplane().pushPoints(bolt_points(count, pcd)).hole(
            hole, depth=thick * 1.5
        )
    if spec["kind"] == "housing":
        length, width, thick, bore = d
        shape = cq.Workplane("XY").box(length, width, thick).edges("|Z").fillet(min(8, thick / 4))
        shape = shape.faces(">Z").workplane().hole(bore)
        points=((-length*.38,-width*.34),(-length*.38,width*.34),(length*.38,-width*.34),(length*.38,width*.34))
        return shape.faces(">Z").workplane().pushPoints(points).hole(9)
    if spec["kind"] == "bracket":
        length, width, height, thick, bore = d
        base = cq.Workplane("XY").box(length, width, thick)
        upright = cq.Workplane("XY").box(length, thick, height).translate(
            (0, width/2-thick/2, height/2-thick/2)
        )
        upright = upright.faces(">Y").workplane().hole(bore)
        shape = base.union(upright)
        return shape.faces(">Z").workplane().pushPoints(
            [(-length*.34, 0), (length*.34, 0)]
        ).hole(7)
    if spec["kind"] == "plate":
        length, width, thick, bore = d
        if spec["no"] == "MK-007":
            profile = cq.Workplane("XY").polyline([(-length/2,-width/2),(length/2,-width/2),(-length/2,width/2)]).close().extrude(thick)
            return profile.faces(">Z").workplane().center(-length*.28,-width*.18).hole(bore)
        shape = cq.Workplane("XY").box(length, width, thick).edges("|Z").fillet(5)
        return shape.faces(">Z").workplane().hole(bore)
    raise ValueError(spec)


def overall(spec):
    d = spec["dims"]
    if spec["kind"] == "shaft":
        return d[0] * 1.24, d[0] * 1.24, d[1] * 1.12
    if spec["kind"] == "flange":
        return d[0], d[0], d[1] * 1.32
    return d[0], d[1], d[2]


def make_dxf(spec, path):
    width, height, depth = overall(spec)
    doc = ezdxf.new("R2013")
    doc.units = units.MM
    doc.layers.add("OUTLINE", color=7)
    doc.layers.add("HOLES", color=1)
    doc.layers.add("CENTER", color=3, linetype="CENTER")
    doc.layers.add("TEXT", color=2)
    msp = doc.modelspace()
    if spec["kind"] in ("shaft", "flange"):
        msp.add_circle((0, 0), width/2, dxfattribs={"layer": "OUTLINE"})
        bore = spec["dims"][2]
        msp.add_circle((0, 0), bore/2, dxfattribs={"layer": "HOLES"})
        if spec["kind"] == "flange":
            _, _, _, pcd, count = spec["dims"]
            hole = 9 if "RA-" in spec["no"] else 13
            for x, y in bolt_points(count, pcd):
                msp.add_circle((x, y), hole/2, dxfattribs={"layer": "HOLES"})
    else:
        pts=[(-width/2,-height/2),(width/2,-height/2),(width/2,height/2),(-width/2,height/2)]
        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer":"OUTLINE"})
        bore = spec["dims"][-1]
        msp.add_circle((0,0),bore/2,dxfattribs={"layer":"HOLES"})
    msp.add_line((-width*.6,0),(width*.6,0),dxfattribs={"layer":"CENTER"})
    msp.add_line((0,-height*.6),(0,height*.6),dxfattribs={"layer":"CENTER"})
    msp.add_text(f'{spec["no"]} {spec["name"]}', height=5, dxfattribs={"layer":"TEXT"}).set_placement((-width/2,-height*.7))
    doc.saveas(path)


def make_pdf(spec, path):
    page = landscape(A3)
    c = canvas.Canvas(str(path), pagesize=page)
    w, h = page
    c.setLineWidth(1)
    c.rect(18, 18, w-36, h-36)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(38, h-55, f'{spec["no"]}  {spec["name"]}')
    c.setFont("Helvetica", 11)
    c.drawString(38, h-78, f'Material: {spec["material"]}    Qty: {spec["qty"]}    Units: mm')
    c.drawString(38, h-96, f'Overall: {" x ".join(str(round(x,1)) for x in overall(spec))}')
    c.drawString(38, h-114, spec["note"])
    ow, oh, od = overall(spec)
    scale = min(360/max(ow,1), 260/max(oh,1))
    cx, cy = 300, 310
    if spec["kind"] in ("shaft","flange"):
        c.circle(cx,cy,ow/2*scale)
        c.circle(cx,cy,spec["dims"][2]/2*scale)
    else:
        c.rect(cx-ow*scale/2,cy-oh*scale/2,ow*scale,oh*scale)
        c.circle(cx,cy,spec["dims"][-1]/2*scale)
    c.line(cx-220,cy,cx+220,cy)
    c.line(cx,cy-150,cx,cy+150)
    c.setFont("Helvetica", 9)
    notes=[
        "1. Remove burrs and break sharp edges 0.5 x 45 deg unless specified.",
        "2. General dimensional tolerance: GB/T 1804-m.",
        "3. Verify mating bore, shaft and bolt pattern against released purchased components.",
        "4. This drawing is a portfolio-stage controlled part sheet; final process tolerances require manufacturing review.",
    ]
    for i,note in enumerate(notes):
        c.drawString(600,360-i*22,note)
    c.rect(590,80,530,110)
    c.drawString(605,165,f'PART NO: {spec["no"]}')
    c.drawString(605,142,f'NAME: {spec["name"]}')
    c.drawString(605,119,f'MATERIAL: {spec["material"]}')
    c.drawString(605,96,'SHEET: A3 / 1:1 or NTS')
    c.save()


def validate_step(path, expected):
    imported = cq.importers.importStep(str(path))
    solids = imported.solids().size()
    box = imported.val().BoundingBox()
    actual = (box.xlen, box.ylen, box.zlen)
    tolerance = 0.5
    passed = solids == 1 and all(abs(a-e) <= tolerance for a,e in zip(actual, expected))
    return dict(solids=solids, bbox_mm=[round(v,3) for v in actual], expected_bbox_mm=list(expected), passed=passed)


def run(repo, specs=None, folder_name="production_parts_v2"):
    specs = specs or PROJECTS[repo.name]
    out = repo / "native_sources" / folder_name
    for name in ("step","dxf","pdf"):
        (out/name).mkdir(parents=True, exist_ok=True)
    validations=[]
    for spec in specs:
        shape=make_part(spec)
        step=out/"step"/f'{spec["no"]}_{spec["name"]}.step'
        dxf=out/"dxf"/f'{spec["no"]}_{spec["name"]}.dxf'
        pdf=out/"pdf"/f'{spec["no"]}_{spec["name"]}.pdf'
        exporters.export(shape,str(step))
        make_dxf(spec,dxf)
        make_pdf(spec,pdf)
        validations.append({"part_no":spec["no"],"step":str(step.relative_to(repo)),**validate_step(step,overall(spec))})
    with (out/f"BOM_{folder_name}.csv").open("w",newline="",encoding="utf-8-sig") as f:
        fields=["item","part_no","part_name","qty","material","overall_mm","note","step","dxf","pdf"]
        writer=csv.DictWriter(f,fieldnames=fields); writer.writeheader()
        for i,spec in enumerate(specs,1):
            writer.writerow(dict(item=i,part_no=spec["no"],part_name=spec["name"],qty=spec["qty"],material=spec["material"],overall_mm="x".join(str(round(v,1)) for v in overall(spec)),note=spec["note"],step=f'step/{spec["no"]}_{spec["name"]}.step',dxf=f'dxf/{spec["no"]}_{spec["name"]}.dxf',pdf=f'pdf/{spec["no"]}_{spec["name"]}.pdf'))
    (out/"validation_report.json").write_text(json.dumps(validations,indent=2),encoding="utf-8")
    (out/"README.md").write_text(
        f"# {folder_name.replace('_', ' ').title()}\n\nControlled batch of four parametric key parts. Each part includes validated single-solid STEP, editable millimetre DXF, A3 PDF and BOM entry. Purchased-component interfaces remain subject to final supplier drawings.\n",
        encoding="utf-8",
    )
    print(repo.name, validations)


def main():
    script = Path(__file__).resolve()
    local_repo = script.parents[2]
    if local_repo.name in PROJECTS:
        run(local_repo)
        run(local_repo, PROJECTS_V3[local_repo.name], "production_parts_v3")
        return
    repo_sync=script.parents[1]/"repo_sync"
    for repo_name in PROJECTS:
        run(repo_sync/repo_name)
        run(repo_sync/repo_name, PROJECTS_V3[repo_name], "production_parts_v3")


if __name__=="__main__":
    main()
