from pathlib import Path
import json
import time

import pythoncom
import win32com.client
from win32com.client import VARIANT


def point(x, y, z=0.0):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (float(x), float(y), float(z)))


def add_rect(ms, x, y, length, width):
    corners = [
        (x, y), (x + length, y), (x + length, y + width), (x, y + width)
    ]
    for index in range(4):
        a = corners[index]
        b = corners[(index + 1) % 4]
        ms.AddLine(point(*a), point(*b))


def add_center_marks(ms, x, y, size=5):
    ms.AddLine(point(x - size, y), point(x + size, y))
    ms.AddLine(point(x, y - size), point(x, y + size))


def draw_plate(ms, x, y, name, length, width, holes):
    add_rect(ms, x, y, length, width)
    for hx, hy, diameter in holes:
        cx = x + length / 2 + hx
        cy = y + width / 2 + hy
        ms.AddCircle(point(cx, cy), diameter / 2)
        add_center_marks(ms, cx, cy, min(5, diameter / 3))
    ms.AddText(name, point(x, y - 18), 8)
    ms.AddDimAligned(point(x, y), point(x + length, y), point(x + length / 2, y - 12))
    ms.AddDimAligned(point(x, y), point(x, y + width), point(x - 12, y + width / 2))


def draw_flange(ms, x, y, name, diameter, center_hole, holes):
    ms.AddCircle(point(x, y), diameter / 2)
    if center_hole:
        ms.AddCircle(point(x, y), center_hole / 2)
    for hx, hy, hole_diameter in holes:
        ms.AddCircle(point(x + hx, y + hy), hole_diameter / 2)
        add_center_marks(ms, x + hx, y + hy, 4)
    add_center_marks(ms, x, y, 12)
    ms.AddText(name, point(x - diameter / 2, y - diameter / 2 - 18), 8)
    ms.AddDimDiametric(
        ms.AddCircle(point(x, y), diameter / 2),
        point(x + diameter * 0.35, y + diameter * 0.35),
        15,
    )


PROJECTS = {
    "01_4axis_robot": {
        "title": "2 kg Four-axis Robot - Key Part Drawing",
        "notes": "Basis: 230 mm upper arm, 190 mm forearm, 70 mm tool offset, 2 kg payload",
        "parts": [
            ("plate", 0, 0, "Base mounting plate", 320, 320,
             [(-125,-125,14),(125,-125,14),(125,125,14),(-125,125,14)]),
            ("plate", 390, 230, "Upper arm side plate", 230, 70,
             [(-95,0,32),(95,0,32)]),
            ("plate", 390, 100, "Forearm side plate", 190, 60,
             [(-77,0,28),(77,0,28)]),
            ("plate", 390, 20, "Modular gripper finger", 70, 18,
             [(-23,0,6.6),(-7,0,6.6)]),
        ],
    },
    "02_feeding_inspection": {
        "title": "Automatic Feeding Inspection System - Key Part Drawing",
        "notes": "Basis: workpiece diameter 20 x 60 mm, 12 parts/min, 0.5 MPa",
        "parts": [
            ("plate", 0, 210, "Linear feeder track", 600, 70,
             [(-270,-23,9),(-270,23,9),(270,-23,9),(270,23,9)]),
            ("plate", 0, 70, "Separator cylinder mount", 120, 80,
             [(0,0,18),(-45,-25,7),(45,-25,7)]),
            ("plate", 190, 70, "V locator base", 100, 80,
             [(-35,-25,7),(35,-25,7),(0,25,8)]),
            ("plate", 360, 70, "Transfer cylinder bracket", 140, 90,
             [(0,0,22),(-50,-25,7),(50,-25,7)]),
        ],
    },
    "03_mkh650": {
        "title": "MKH650 20 kg Manipulator - Key Part Drawing",
        "notes": "Basis: upper arm 520 mm, forearm 480 mm, tool offset 180 mm, payload 20 kg",
        "parts": [
            ("flange", 190, 210, "Foundation flange", 360, 120,
             [(130,0,18),(-130,0,18),(0,130,18),(0,-130,18),(92,92,18),(-92,92,18),(92,-92,18),(-92,-92,18)]),
            ("plate", 420, 260, "Upper arm side plate", 520, 110,
             [(-215,0,65),(215,0,65)]),
            ("flange", 150, -80, "Joint output flange", 220, 80,
             [(70,0,14),(-70,0,14),(0,70,14),(0,-70,14)]),
            ("plate", 420, -40, "Heavy gripper finger", 180, 42,
             [(-66,0,14),(-30,0,14)]),
        ],
    },
}


def connect():
    pythoncom.CoInitialize()
    try:
        app = win32com.client.GetActiveObject("AutoCAD.Application")
    except Exception:
        app = win32com.client.Dispatch("AutoCAD.Application")
    app.Visible = True
    for _ in range(30):
        try:
            _ = app.Documents.Count
            return app
        except Exception:
            time.sleep(1)
    raise RuntimeError("AutoCAD COM interface did not become ready")


def main():
    root = Path(__file__).resolve().parent / "output"
    app = connect()
    report = {"status": "started", "files": [], "errors": []}
    for slug, project in PROJECTS.items():
        doc = None
        try:
            doc = app.Documents.Add()
            ms = doc.ModelSpace
            ms.AddText(project["title"], point(0, 430), 14)
            ms.AddText(project["notes"], point(0, 405), 8)
            for spec in project["parts"]:
                if spec[0] == "plate":
                    _, x, y, name, length, width, holes = spec
                    draw_plate(ms, x, y, name, length, width, holes)
                else:
                    _, x, y, name, diameter, center_hole, holes = spec
                    draw_flange(ms, x, y, name, diameter, center_hole, holes)
            doc.Regen(1)
            folder = root / slug
            folder.mkdir(parents=True, exist_ok=True)
            dwg = folder / (slug + "_key_parts.dwg")
            if dwg.exists():
                dwg.unlink()
            doc.SaveAs(str(dwg))
            report["files"].append({"project": slug, "dwg": str(dwg), "bytes": dwg.stat().st_size})
            doc.Close(False)
        except Exception as exc:
            report["errors"].append({"project": slug, "error": repr(exc)})
            if doc is not None:
                try:
                    doc.Close(False)
                except Exception:
                    pass
    report["status"] = "complete" if not report["errors"] else "partial"
    (root / "autocad_generation_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
