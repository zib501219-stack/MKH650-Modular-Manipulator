from pathlib import Path
import json
import cadquery as cq
from cadquery import exporters


ROOT = Path(__file__).resolve().parent / "output"


def rounded_plate(length, width, thickness, radius=6):
    return cq.Workplane("XY").box(length, width, thickness).edges("|Z").fillet(radius)


def cut_cbore(shape, points, hole_d, cbore_d, cbore_depth):
    return (
        shape.faces(">Z").workplane()
        .pushPoints(points)
        .cboreHole(hole_d, cbore_d, cbore_depth)
    )


def add_ring(shape, x, y, z, outer_d, inner_d, height):
    ring = (
        cq.Workplane("XY", origin=(x, y, z))
        .circle(outer_d / 2).circle(inner_d / 2)
        .extrude(height)
    )
    return shape.union(ring)


def arm_plate(length, width, thickness, joint_d, centers, lightening):
    shape = rounded_plate(length, width, thickness, min(12, width / 5))
    shape = shape.faces(">Z").workplane().pushPoints(centers).hole(joint_d)
    if lightening:
        shape = shape.faces(">Z").workplane().pushPoints(lightening).hole(width * 0.38)
    for x, y in centers:
        shape = add_ring(shape, x, y, thickness / 2, joint_d + 22, joint_d, 5)
    return shape


def base_mounting_plate():
    s = rounded_plate(320, 320, 20, 15)
    s = cut_cbore(s, [(-125,-125),(125,-125),(125,125),(-125,125)], 14, 24, 7)
    s = s.faces(">Z").workplane().circle(92).circle(62).cutBlind(-8)
    s = add_ring(s, 0, 0, 10, 184, 124, 12)
    return s


def robot_gripper_finger():
    base = rounded_plate(70, 18, 12, 3)
    base = cut_cbore(base, [(-23,0),(-7,0)], 6.6, 11, 4)
    tip = cq.Workplane("XY", origin=(32,0,0)).box(22, 14, 18).edges("|Z").fillet(2)
    s = base.union(tip)
    for x in (26,31,36,41):
        groove = cq.Workplane("YZ", origin=(x,-8,-5)).rect(14,1.6).extrude(16)
        s = s.cut(groove)
    return s


def feeder_track():
    base = rounded_plate(600, 70, 12, 6)
    base = cut_cbore(base, [(-270,-23),(-270,23),(270,-23),(270,23)], 9, 16, 5)
    rail1 = cq.Workplane("XY", origin=(0,-27,9)).box(560,12,18).edges("|Z").fillet(2)
    rail2 = cq.Workplane("XY", origin=(0,27,9)).box(560,12,18).edges("|Z").fillet(2)
    s = base.union(rail1).union(rail2)
    s = s.faces(">Z").workplane().rect(520,34).cutBlind(-5)
    return s


def separator_mount():
    base = rounded_plate(120, 80, 10, 5)
    base = cut_cbore(base, [(-45,-25),(45,-25)], 7, 12, 4)
    upright = cq.Workplane("XZ", origin=(0,30,35)).box(120,10,70).edges("|Y").fillet(4)
    s = base.union(upright)
    s = s.faces(">Y").workplane().hole(18)
    for x in (-40, 40):
        rib = cq.Workplane("XZ", origin=(x,22,12)).polyline([(0,0),(0,35),(18,0)]).close().extrude(8)
        s = s.union(rib)
    return s


def v_locator():
    base = rounded_plate(100, 80, 16, 5)
    base = cut_cbore(base, [(-35,-25),(35,-25)], 7, 12, 4)
    base = base.faces(">Z").workplane().pushPoints([(0,30)]).hole(8)
    left = cq.Workplane("XY", origin=(0,-16,15)).box(76,18,20).rotate((0,0,0),(1,0,0),35)
    right = cq.Workplane("XY", origin=(0,16,15)).box(76,18,20).rotate((0,0,0),(1,0,0),-35)
    s = base.union(left).union(right)
    return s


def transfer_bracket():
    base = rounded_plate(140, 90, 10, 6)
    base = cut_cbore(base, [(-50,-25),(50,-25)], 7, 12, 4)
    upright = cq.Workplane("XZ", origin=(0,35,45)).box(140,10,90)
    s = base.union(upright)
    bore = cq.Workplane("XZ", origin=(0,50,45)).circle(11).extrude(-30)
    s = s.cut(bore)
    return s


def foundation_flange():
    s = cq.Workplane("XY").circle(180).circle(60).extrude(30)
    pts = [(130,0),(-130,0),(0,130),(0,-130),(92,92),(-92,92),(92,-92),(-92,-92)]
    s = cut_cbore(s, pts, 18, 30, 8)
    boss = cq.Workplane("XY", origin=(0,0,30)).circle(105).circle(60).extrude(18)
    s = s.union(boss)
    for angle in range(0,360,45):
        x = 82 * __import__("math").cos(__import__("math").radians(angle))
        y = 82 * __import__("math").sin(__import__("math").radians(angle))
        rib = cq.Workplane("XY", origin=(x,y,30)).box(35,10,18).rotate((0,0,0),(0,0,1),angle)
        s = s.union(rib)
    return s


def joint_output_flange():
    s = cq.Workplane("XY").circle(110).circle(40).extrude(28)
    s = cut_cbore(s, [(70,0),(-70,0),(0,70),(0,-70)], 14, 24, 7)
    boss = cq.Workplane("XY", origin=(0,0,28)).circle(72).circle(40).extrude(22)
    seal = cq.Workplane("XY", origin=(0,0,50)).circle(58).circle(48).extrude(4)
    return s.union(boss).union(seal)


def heavy_finger():
    base = rounded_plate(180, 42, 28, 5)
    base = cut_cbore(base, [(-66,0),(-30,0)], 14, 24, 8)
    jaw = cq.Workplane("XY", origin=(78,0,12)).box(45,36,52).edges("|Z").fillet(4)
    s = base.union(jaw)
    s = s.faces(">Z").workplane().rect(70,22).cutBlind(-6)
    for x in (66,74,82,90,98):
        groove = cq.Workplane("YZ", origin=(x,-19,28)).rect(38,2.2).extrude(24)
        s = s.cut(groove)
    return s


MODELS = {
    "01_4axis_robot": {
        "base_mounting_plate": base_mounting_plate,
        "upper_arm_side_plate": lambda: arm_plate(230,70,12,32,[(-95,0),(95,0)],[(-48,0),(0,0),(48,0)]),
        "forearm_side_plate": lambda: arm_plate(190,60,10,28,[(-77,0),(77,0)],[(-38,0),(0,0),(38,0)]),
        "modular_gripper_finger": robot_gripper_finger,
    },
    "02_feeding_inspection": {
        "linear_feeder_track": feeder_track,
        "separator_cylinder_mount": separator_mount,
        "v_locator_base": v_locator,
        "transfer_cylinder_bracket": transfer_bracket,
    },
    "03_mkh650": {
        "foundation_flange": foundation_flange,
        "upper_arm_side_plate": lambda: arm_plate(520,110,20,65,[(-215,0),(215,0)],[(-130,0),(-65,0),(0,0),(65,0),(130,0)]),
        "joint_output_flange": joint_output_flange,
        "heavy_gripper_finger": heavy_finger,
    },
}


def main():
    report = {"status": "started", "files": [], "errors": []}
    for project, models in MODELS.items():
        folder = ROOT / project
        folder.mkdir(parents=True, exist_ok=True)
        for name, factory in models.items():
            try:
                shape = factory()
                step = folder / f"{name}_enhanced.step"
                stl = folder / f"{name}_enhanced.stl"
                exporters.export(shape, str(step))
                exporters.export(shape, str(stl), tolerance=0.05, angularTolerance=0.1)
                report["files"].append({
                    "project": project, "name": name,
                    "step": str(step), "stl": str(stl),
                    "step_bytes": step.stat().st_size,
                    "stl_bytes": stl.stat().st_size,
                })
            except Exception as exc:
                report["errors"].append({"project": project, "name": name, "error": repr(exc)})
    report["status"] = "complete" if not report["errors"] else "partial"
    (ROOT / "generation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
