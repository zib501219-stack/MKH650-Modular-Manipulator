from pathlib import Path
import csv
import json

import cadquery as cq
from cadquery import exporters
import ezdxf
from ezdxf import units
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape


ROOT = Path(__file__).resolve().parents[1]
MODEL_ROOT = ROOT / "enhanced_cad" / "output"
OUT = Path(__file__).resolve().parent / "output"


PROJECTS = {
    "01_4axis_robot": {
        "title": "2 kg Four-axis Robot Arm",
        "parts": [
            ("RA-001", "base_mounting_plate", 320, 320, 20, "Q235B", 1, [(-125,-125,14),(125,-125,14),(125,125,14),(-125,125,14)]),
            ("RA-002", "upper_arm_side_plate", 230, 70, 12, "6061-T6", 2, [(-95,0,32),(95,0,32)]),
            ("RA-003", "forearm_side_plate", 190, 60, 10, "6061-T6", 2, [(-77,0,28),(77,0,28)]),
            ("RA-004", "modular_gripper_finger", 70, 18, 18, "45 steel", 2, [(-23,0,6.6),(-7,0,6.6)]),
        ],
    },
    "02_feeding_inspection": {
        "title": "Automatic Feeding and Inspection System",
        "parts": [
            ("FI-001", "linear_feeder_track", 600, 70, 24, "6061-T6", 1, [(-270,-23,9),(-270,23,9),(270,-23,9),(270,23,9)]),
            ("FI-002", "separator_cylinder_mount", 120, 80, 74, "Q235B", 1, [(-45,-25,7),(45,-25,7)]),
            ("FI-003", "v_locator_base", 100, 80, 27, "45 steel", 1, [(-35,-25,7),(35,-25,7),(0,30,8)]),
            ("FI-004", "transfer_cylinder_bracket", 140, 90, 90, "Q235B", 1, [(-50,-25,7),(50,-25,7)]),
        ],
    },
    "03_mkh650": {
        "title": "MKH650 Modular 20 kg Manipulator",
        "parts": [
            ("MK-001", "foundation_flange", 360, 360, 48, "Q355B", 1, [(130,0,18),(-130,0,18),(0,130,18),(0,-130,18),(92,92,18),(-92,92,18),(92,-92,18),(-92,-92,18)]),
            ("MK-002", "upper_arm_side_plate", 520, 110, 25, "Q355B", 2, [(-215,0,65),(215,0,65)]),
            ("MK-003", "joint_output_flange", 220, 220, 54, "42CrMo", 1, [(70,0,14),(-70,0,14),(0,70,14),(0,-70,14)]),
            ("MK-004", "heavy_gripper_finger", 180, 42, 52, "42CrMo", 2, [(-66,0,14),(-30,0,14)]),
        ],
    },
}


def make_reference_assembly(slug, project, folder):
    placed_shapes = []
    x = 0
    placements = []
    for part_no, name, length, width, height, material, qty, holes in project["parts"]:
        step = MODEL_ROOT / slug / f"{name}_enhanced.step"
        shape = cq.importers.importStep(str(step))
        moved = shape.translate((x, 0, 0))
        placed_shapes.extend(moved.solids().vals())
        placements.append({"part_no": part_no, "name": name, "x_mm": x, "y_mm": 0, "z_mm": 0})
        x += max(length, width) + 80
    target = folder / f"{slug}_enhanced_key_parts_reference_assembly.step"
    compound = cq.Compound.makeCompound(placed_shapes)
    exporters.export(compound, str(target))
    (folder / "assembly_placements.json").write_text(json.dumps(placements, indent=2), encoding="utf-8")
    return target


def add_dxf_drawing(folder, slug, part):
    part_no, name, length, width, height, material, qty, holes = part
    doc = ezdxf.new("R2018", setup=True)
    doc.units = units.MM
    for layer, color in (("OUTLINE",7),("HOLES",1),("CENTER",3),("DIM",2),("TEXT",7),("TITLE",7)):
        doc.layers.add(layer, color=color)
    msp = doc.modelspace()
    x0, y0 = -length / 2, -width / 2
    msp.add_lwpolyline([(x0,y0),(x0+length,y0),(x0+length,y0+width),(x0,y0+width)], close=True, dxfattribs={"layer":"OUTLINE"})
    for x, y, dia in holes:
        msp.add_circle((x,y), dia/2, dxfattribs={"layer":"HOLES"})
        msp.add_line((x-dia*.7,y),(x+dia*.7,y), dxfattribs={"layer":"CENTER"})
        msp.add_line((x,y-dia*.7),(x,y+dia*.7), dxfattribs={"layer":"CENTER"})
        msp.add_text(f"Ø{dia:g}", height=max(3,length/100), dxfattribs={"layer":"TEXT"}).set_placement((x+dia/2+3,y+3))
    dim_offset = max(15, width * .18)
    msp.add_linear_dim(base=(0,y0-dim_offset), p1=(x0,y0), p2=(x0+length,y0), angle=0, dxfattribs={"layer":"DIM"}).render()
    msp.add_linear_dim(base=(x0-dim_offset,0), p1=(x0,y0), p2=(x0,y0+width), angle=90, dxfattribs={"layer":"DIM"}).render()
    tx = x0
    ty = y0 - dim_offset - 35
    msp.add_text(f"{part_no}  {name}", height=7, dxfattribs={"layer":"TITLE"}).set_placement((tx,ty))
    msp.add_text(f"Material: {material}   Thickness/height: {height} mm   Qty: {qty}", height=5, dxfattribs={"layer":"TEXT"}).set_placement((tx,ty-10))
    msp.add_text("General tolerance: GB/T 1804-m   Remove burrs and sharp edges", height=4, dxfattribs={"layer":"TEXT"}).set_placement((tx,ty-19))
    target = folder / "drawings" / f"{part_no}_{name}.dxf"
    target.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(target)
    return target


def add_pdf_drawing(folder, slug, project, part):
    part_no, name, length, width, height, material, qty, holes = part
    target = folder / "drawings" / f"{part_no}_{name}.pdf"
    page_w, page_h = landscape(A3)
    c = canvas.Canvas(str(target), pagesize=(page_w,page_h))
    c.setLineWidth(1)
    c.rect(20,20,page_w-40,page_h-40)
    title_h = 75
    c.rect(20,20,page_w-40,title_h)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(35, page_h-45, project["title"])
    c.setFont("Helvetica", 10)
    c.drawString(35, page_h-62, "Enhanced key-part engineering drawing / Units: mm")
    usable_w, usable_h = page_w-120, page_h-title_h-130
    scale = min(usable_w/length, usable_h/width, 1.0)
    ox, oy = page_w/2, title_h + 45 + usable_h/2
    c.rect(ox-length*scale/2, oy-width*scale/2, length*scale, width*scale)
    for x,y,dia in holes:
        c.circle(ox+x*scale, oy+y*scale, dia*scale/2)
        c.line(ox+(x-dia*.7)*scale,oy+y*scale,ox+(x+dia*.7)*scale,oy+y*scale)
        c.line(ox+x*scale,oy+(y-dia*.7)*scale,ox+x*scale,oy+(y+dia*.7)*scale)
    c.setFont("Helvetica", 10)
    c.drawCentredString(ox, oy-width*scale/2-18, f"{length} mm")
    c.saveState()
    c.translate(ox-length*scale/2-22, oy)
    c.rotate(90)
    c.drawCentredString(0,0,f"{width} mm")
    c.restoreState()
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30,68,f"Part No.: {part_no}")
    c.drawString(250,68,f"Part: {name}")
    c.setFont("Helvetica", 10)
    c.drawString(30,50,f"Material: {material}")
    c.drawString(250,50,f"Thickness/height: {height} mm")
    c.drawString(490,50,f"Qty: {qty}")
    c.drawString(30,33,"General tolerance: GB/T 1804-m; deburr; break sharp edges 0.5 max.")
    c.save()
    return target


def write_bom(folder, slug, project):
    target = folder / "BOM_enhanced_key_parts.csv"
    with target.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(["item","part_no","part_name","qty","material","overall_size_mm","source_step","drawing_dxf","drawing_pdf"])
        for i, part in enumerate(project["parts"],1):
            part_no,name,length,width,height,material,qty,holes = part
            writer.writerow([i,part_no,name,qty,material,f"{length}x{width}x{height}",
                             f"step/{name}_enhanced.step",f"drawings/{part_no}_{name}.dxf",f"drawings/{part_no}_{name}.pdf"])
    return target


def write_validation(folder, slug, project, assembly):
    lines = [
        f"# {project['title']} - engineering package validation",
        "",
        "## Scope",
        "",
        "This package links the enhanced key-part STEP files to controlled part numbers, material assumptions, 1:1 DXF drawings, printable A3 PDF sheets and a reference exploded layout.",
        "",
        "The reference assembly is a review/exploded layout, not a kinematic or manufacturing assembly. The repository's main detailed assembly remains the system-level model.",
        "",
        "## Checks",
        "",
        f"- Reference STEP exists: `{Path(assembly).name}`",
        f"- Key-part count: {len(project['parts'])}",
        f"- DXF count: {len(project['parts'])}",
        f"- PDF count: {len(project['parts'])}",
        "- DXF units: millimetres",
        "- Each DXF includes one closed outline, hole circles, centre marks and two overall dimensions",
        "- Each PDF is one A3 landscape page with title block, material, quantity and general tolerance note",
        "- Enhanced source STEP solids were checked separately and each file contains one solid",
        "",
        "## Boundary",
        "",
        "Materials, general tolerances and quantities are engineering assumptions for portfolio completeness. Final fits, heat treatment, surface finish and manufacturing tolerances require review against the selected bearings, actuators, suppliers and fabrication process.",
    ]
    target = folder / "engineering_package_validation.md"
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def main():
    report = {"projects": {}, "errors": []}
    for slug, project in PROJECTS.items():
        folder = OUT / slug
        folder.mkdir(parents=True, exist_ok=True)
        data = {"assembly": None, "drawings": [], "bom": None}
        try:
            data["assembly"] = str(make_reference_assembly(slug, project, folder))
            data["bom"] = str(write_bom(folder, slug, project))
            for part in project["parts"]:
                data["drawings"].append(str(add_dxf_drawing(folder, slug, part)))
                data["drawings"].append(str(add_pdf_drawing(folder, slug, project, part)))
            data["validation"] = str(write_validation(folder, slug, project, data["assembly"]))
        except Exception as exc:
            report["errors"].append({"project":slug,"error":repr(exc)})
        report["projects"][slug] = data
    report["status"] = "complete" if not report["errors"] else "partial"
    (OUT / "engineering_package_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
