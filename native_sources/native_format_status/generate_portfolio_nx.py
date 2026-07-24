import json
import os
import sys
import traceback

import NXOpen


def expression(part, name, value):
    part.Expressions.CreateExpression("Number", "%s=%s" % (name, value))


def bodies(part):
    return [body for body in part.Bodies if body.IsSolidBody]


def block(part, origin, lengths, target=None):
    builder = part.Features.CreateBlockFeatureBuilder(NXOpen.Features.Feature.Null)
    builder.Type = NXOpen.Features.BlockFeatureBuilder.Types.OriginAndEdgeLengths
    builder.SetOriginAndLengths(
        NXOpen.Point3d(*origin),
        str(lengths[0]),
        str(lengths[1]),
        str(lengths[2]),
    )
    if target is not None:
        builder.SetBooleanOperationAndTarget(
            NXOpen.Features.Feature.BooleanType.Unite, target
        )
    feature = builder.CommitFeature()
    builder.Destroy()
    return feature


def cylinder(part, origin, direction, height, diameter, target=None, subtract=False):
    builder = part.Features.CreateCylinderBuilder(NXOpen.Features.Feature.Null)
    builder.Type = NXOpen.Features.CylinderBuilder.Types.AxisDiameterAndHeight
    builder.Origin = NXOpen.Point3d(*origin)
    builder.Direction = NXOpen.Vector3d(*direction)
    builder.Height.RightHandSide = str(height)
    builder.Diameter.RightHandSide = str(diameter)
    if target is not None:
        operation = (
            NXOpen.GeometricUtilities.BooleanOperation.BooleanType.Subtract
            if subtract
            else NXOpen.GeometricUtilities.BooleanOperation.BooleanType.Unite
        )
        builder.BooleanOption.SetBooleanOperationAndBody(operation, target)
    feature = builder.CommitFeature()
    builder.Destroy()
    return feature


def export_step(session, part_path, step_path, description):
    creator = session.DexManager.CreateStep214Creator()
    creator.ExportFrom = NXOpen.Step214Creator.ExportFromOption.DisplayPart
    creator.InputFile = part_path
    creator.OutputFile = step_path
    creator.SettingsFile = r"D:\Program Files\Siemens\NX 12.0\STEP214UG\ugstep214.def"
    creator.FileSaveFlag = False
    creator.LayerMask = "1-256"
    creator.Author = "Liu Zibin portfolio"
    creator.Company = "Student mechanical design portfolio"
    creator.Description = description
    creator.ValidationProperties = False
    creator.Commit()
    creator.Destroy()


def save_and_export(session, part, folder, name, description):
    part_path = os.path.join(folder, name + ".prt")
    step_path = os.path.join(folder, name + ".step")
    status = part.Save(
        NXOpen.BasePart.SaveComponents.TrueValue,
        NXOpen.BasePart.CloseAfterSave.FalseValue,
    )
    if status is not None:
        status.Dispose()
    export_step(session, part_path, step_path, description)
    return {
        "prt": part_path,
        "step": step_path,
        "solid_bodies": len(bodies(part)),
        "features": len(list(part.Features.GetFeatures())),
        "prt_bytes": os.path.getsize(part_path),
        "step_bytes": os.path.getsize(step_path),
    }


def new_part(session, folder, name, params):
    path = os.path.join(folder, name + ".prt")
    for ext in (".prt", ".step"):
        candidate = os.path.join(folder, name + ext)
        if os.path.exists(candidate):
            os.remove(candidate)
    part = session.Parts.NewDisplay(path, NXOpen.Part.Units.Millimeters)
    session.Parts.SetWork(part)
    session.Parts.SetDisplay(part, False, False)
    for key, value in params.items():
        expression(part, key, value)
    return part


def plate_with_holes(session, folder, spec):
    part = new_part(session, folder, spec["name"], spec["params"])
    main = block(part, (0, 0, 0), spec["size"])
    target = bodies(part)[0]
    for hole in spec.get("holes", []):
        cylinder(
            part,
            hole["origin"],
            hole.get("direction", (0, 0, 1)),
            hole["height"],
            hole["diameter"],
            target,
            True,
        )
    for boss in spec.get("bosses", []):
        cylinder(
            part,
            boss["origin"],
            boss.get("direction", (0, 0, 1)),
            boss["height"],
            boss["diameter"],
            target,
            False,
        )
    return save_and_export(
        session, part, folder, spec["name"], spec["description"]
    )


def flange(session, folder, spec):
    part = new_part(session, folder, spec["name"], spec["params"])
    cylinder(part, (0, 0, 0), (0, 0, 1), spec["thickness"], spec["diameter"])
    target = bodies(part)[0]
    if spec.get("center_hole"):
        cylinder(
            part,
            (0, 0, -1),
            (0, 0, 1),
            spec["thickness"] + 2,
            spec["center_hole"],
            target,
            True,
        )
    for x, y, d in spec.get("holes", []):
        cylinder(
            part,
            (x, y, -1),
            (0, 0, 1),
            spec["thickness"] + 2,
            d,
            target,
            True,
        )
    return save_and_export(
        session, part, folder, spec["name"], spec["description"]
    )


def layout_part(session, folder, project):
    name = project["layout_name"]
    part = new_part(session, folder, name, project["layout_params"])
    for item in project["layout"]:
        if item["kind"] == "block":
            block(part, item["origin"], item["size"])
        else:
            cylinder(
                part,
                item["origin"],
                item.get("direction", (0, 0, 1)),
                item["height"],
                item["diameter"],
            )
    return save_and_export(
        session,
        part,
        folder,
        name,
        project["title"] + " native NX multi-body layout",
    )


def project_data():
    return [
        {
            "slug": "01_4axis_robot",
            "title": "2 kg four-axis robot arm",
            "layout_name": "4axis_robot_native_layout",
            "layout_params": {
                "rated_payload": 2,
                "upper_arm_joint_distance": 230,
                "forearm_joint_distance": 190,
                "tool_offset": 70,
                "theoretical_reach": 490,
            },
            "parts": [
                {
                    "type": "plate",
                    "name": "base_mounting_plate",
                    "description": "Four-axis robot base mounting plate",
                    "params": {"length": 320, "width": 320, "thickness": 20, "hole_dia": 14},
                    "size": ("length", "width", "thickness"),
                    "holes": [
                        {"origin": (35, 35, -1), "height": 22, "diameter": "hole_dia"},
                        {"origin": (285, 35, -1), "height": 22, "diameter": "hole_dia"},
                        {"origin": (35, 285, -1), "height": 22, "diameter": "hole_dia"},
                        {"origin": (285, 285, -1), "height": 22, "diameter": "hole_dia"},
                    ],
                },
                {
                    "type": "plate",
                    "name": "upper_arm_side_plate",
                    "description": "Four-axis robot 230 mm upper arm side plate",
                    "params": {"joint_distance": 230, "plate_width": 70, "thickness": 12, "joint_hole": 32},
                    "size": ("joint_distance", "plate_width", "thickness"),
                    "holes": [
                        {"origin": (20, 35, -1), "height": 14, "diameter": "joint_hole"},
                        {"origin": (210, 35, -1), "height": 14, "diameter": "joint_hole"},
                    ],
                },
                {
                    "type": "plate",
                    "name": "forearm_side_plate",
                    "description": "Four-axis robot 190 mm forearm side plate",
                    "params": {"joint_distance": 190, "plate_width": 60, "thickness": 10, "joint_hole": 28},
                    "size": ("joint_distance", "plate_width", "thickness"),
                    "holes": [
                        {"origin": (18, 30, -1), "height": 12, "diameter": "joint_hole"},
                        {"origin": (172, 30, -1), "height": 12, "diameter": "joint_hole"},
                    ],
                },
                {
                    "type": "plate",
                    "name": "modular_gripper_finger",
                    "description": "60 N modular gripper finger",
                    "params": {"length": 70, "width": 18, "thickness": 12, "mount_hole": 6.6},
                    "size": ("length", "width", "thickness"),
                    "holes": [
                        {"origin": (12, 9, -1), "height": 14, "diameter": "mount_hole"},
                        {"origin": (28, 9, -1), "height": 14, "diameter": "mount_hole"},
                    ],
                },
            ],
            "layout": [
                {"kind": "block", "origin": (-160, -160, 0), "size": (320, 320, 20)},
                {"kind": "cylinder", "origin": (0, 0, 20), "height": 240, "diameter": 180},
                {"kind": "block", "origin": (0, -35, 240), "size": (230, 70, 60)},
                {"kind": "block", "origin": (230, -30, 255), "size": (190, 60, 45)},
                {"kind": "block", "origin": (420, -20, 245), "size": (70, 40, 70)},
            ],
        },
        {
            "slug": "02_feeding_inspection",
            "title": "Automatic feeding and inspection system",
            "layout_name": "feeding_system_native_layout",
            "layout_params": {
                "workpiece_length": 60,
                "workpiece_diameter": 20,
                "target_rate_per_min": 12,
                "cycle_time_s": 5,
                "air_pressure_mpa": 0.5,
            },
            "parts": [
                {
                    "type": "plate",
                    "name": "linear_feeder_track",
                    "description": "Linear feeder track for diameter 20 by 60 mm workpiece",
                    "params": {"length": 600, "width": 70, "thickness": 12, "mount_hole": 9},
                    "size": ("length", "width", "thickness"),
                    "holes": [
                        {"origin": (30, 12, -1), "height": 14, "diameter": "mount_hole"},
                        {"origin": (30, 58, -1), "height": 14, "diameter": "mount_hole"},
                        {"origin": (570, 12, -1), "height": 14, "diameter": "mount_hole"},
                        {"origin": (570, 58, -1), "height": 14, "diameter": "mount_hole"},
                    ],
                },
                {
                    "type": "plate",
                    "name": "separator_cylinder_mount",
                    "description": "Adjustable mount for 16 mm bore separator cylinder",
                    "params": {"length": 120, "width": 80, "thickness": 10, "cylinder_hole": 18},
                    "size": ("length", "width", "thickness"),
                    "holes": [
                        {"origin": (60, 40, -1), "height": 12, "diameter": "cylinder_hole"},
                        {"origin": (15, 15, -1), "height": 12, "diameter": 7},
                        {"origin": (105, 15, -1), "height": 12, "diameter": 7},
                    ],
                },
                {
                    "type": "plate",
                    "name": "v_locator_base",
                    "description": "Inspection station locator base for cylindrical workpiece",
                    "params": {"length": 100, "width": 80, "thickness": 16, "sensor_hole": 8},
                    "size": ("length", "width", "thickness"),
                    "holes": [
                        {"origin": (15, 15, -1), "height": 18, "diameter": 7},
                        {"origin": (85, 15, -1), "height": 18, "diameter": 7},
                        {"origin": (50, 65, -1), "height": 18, "diameter": "sensor_hole"},
                    ],
                },
                {
                    "type": "plate",
                    "name": "transfer_cylinder_bracket",
                    "description": "Mount for 20 mm bore transfer cylinder",
                    "params": {"length": 140, "width": 90, "thickness": 10, "cylinder_hole": 22},
                    "size": ("length", "width", "thickness"),
                    "holes": [
                        {"origin": (70, 45, -1), "height": 12, "diameter": "cylinder_hole"},
                        {"origin": (20, 20, -1), "height": 12, "diameter": 7},
                        {"origin": (120, 20, -1), "height": 12, "diameter": 7},
                    ],
                },
            ],
            "layout": [
                {"kind": "block", "origin": (0, 0, 0), "size": (900, 500, 40)},
                {"kind": "block", "origin": (120, 210, 40), "size": (600, 70, 12)},
                {"kind": "cylinder", "origin": (80, 245, 52), "height": 180, "diameter": 320},
                {"kind": "block", "origin": (650, 190, 52), "size": (100, 110, 100)},
                {"kind": "block", "origin": (760, 180, 52), "size": (90, 130, 180)},
            ],
        },
        {
            "slug": "03_mkh650",
            "title": "MKH650 modular 20 kg manipulator",
            "layout_name": "mkh650_native_layout",
            "layout_params": {
                "rated_payload": 20,
                "upper_arm_length": 520,
                "forearm_length": 480,
                "tool_offset": 180,
                "maximum_radius": 1180,
            },
            "parts": [
                {
                    "type": "flange",
                    "name": "foundation_flange",
                    "description": "MKH650 foundation flange",
                    "params": {"diameter": 360, "thickness": 30, "center_hole": 120, "bolt_hole": 18},
                    "diameter": "diameter",
                    "thickness": "thickness",
                    "center_hole": "center_hole",
                    "holes": [
                        (130, 0, "bolt_hole"), (-130, 0, "bolt_hole"),
                        (0, 130, "bolt_hole"), (0, -130, "bolt_hole"),
                        (92, 92, "bolt_hole"), (-92, 92, "bolt_hole"),
                        (92, -92, "bolt_hole"), (-92, -92, "bolt_hole"),
                    ],
                },
                {
                    "type": "plate",
                    "name": "upper_arm_side_plate",
                    "description": "MKH650 520 mm upper arm structural plate",
                    "params": {"length": 520, "width": 110, "thickness": 20, "joint_hole": 65},
                    "size": ("length", "width", "thickness"),
                    "holes": [
                        {"origin": (45, 55, -1), "height": 22, "diameter": "joint_hole"},
                        {"origin": (475, 55, -1), "height": 22, "diameter": "joint_hole"},
                    ],
                },
                {
                    "type": "flange",
                    "name": "joint_output_flange",
                    "description": "MKH650 joint output flange",
                    "params": {"diameter": 220, "thickness": 28, "center_hole": 80, "bolt_hole": 14},
                    "diameter": "diameter",
                    "thickness": "thickness",
                    "center_hole": "center_hole",
                    "holes": [
                        (70, 0, "bolt_hole"), (-70, 0, "bolt_hole"),
                        (0, 70, "bolt_hole"), (0, -70, "bolt_hole"),
                    ],
                },
                {
                    "type": "plate",
                    "name": "heavy_gripper_finger",
                    "description": "MKH650 heavy-duty gripper finger baseline",
                    "params": {"length": 180, "width": 42, "thickness": 28, "mount_hole": 14},
                    "size": ("length", "width", "thickness"),
                    "holes": [
                        {"origin": (24, 21, -1), "height": 30, "diameter": "mount_hole"},
                        {"origin": (60, 21, -1), "height": 30, "diameter": "mount_hole"},
                    ],
                },
            ],
            "layout": [
                {"kind": "cylinder", "origin": (0, 0, 0), "height": 30, "diameter": 360},
                {"kind": "cylinder", "origin": (0, 0, 30), "height": 400, "diameter": 260},
                {"kind": "block", "origin": (0, -55, 390), "size": (520, 110, 100)},
                {"kind": "block", "origin": (500, -48, 410), "size": (480, 96, 80)},
                {"kind": "block", "origin": (960, -70, 390), "size": (180, 140, 180)},
            ],
        },
    ]


def main(args):
    root = os.path.abspath(args[0] if args else "nx_native_output")
    os.makedirs(root, exist_ok=True)
    report = {"status": "started", "root": root, "projects": {}, "errors": []}
    session = NXOpen.Session.GetSession()
    try:
        for project in project_data():
            folder = os.path.join(root, project["slug"])
            os.makedirs(folder, exist_ok=True)
            project_report = {"title": project["title"], "files": {}}
            for spec in project["parts"]:
                if spec["type"] == "flange":
                    result = flange(session, folder, spec)
                else:
                    result = plate_with_holes(session, folder, spec)
                project_report["files"][spec["name"]] = result
            project_report["files"][project["layout_name"]] = layout_part(
                session, folder, project
            )
            report["projects"][project["slug"]] = project_report
        report["status"] = "complete"
    except Exception:
        report["status"] = "failed"
        report["errors"].append(traceback.format_exc())
    finally:
        with open(os.path.join(root, "nx_generation_report.json"), "w") as stream:
            json.dump(report, stream, indent=2)


if __name__ == "__main__":
    main(sys.argv[1:])
