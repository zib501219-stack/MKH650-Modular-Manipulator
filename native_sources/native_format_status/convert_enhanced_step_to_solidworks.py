from pathlib import Path
import json
import pythoncom
import win32com.client
from win32com.client import VARIANT


ROOT = Path(__file__).resolve().parent / "output"


def connect():
    pythoncom.CoInitialize()
    try:
        app = win32com.client.GetActiveObject("SldWorks.Application")
    except Exception:
        app = win32com.client.Dispatch("SldWorks.Application")
    app.Visible = True
    return app


def main():
    app = connect()
    report = {"status": "started", "files": [], "errors": []}
    for step in ROOT.rglob("*_enhanced.step"):
        model = None
        try:
            errors = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
            warnings = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
            model = app.OpenDoc6(str(step), 1, 1, "", errors, warnings)
            if model is None:
                model = app.ActiveDoc
            if model is None:
                raise RuntimeError("SolidWorks could not import STEP")
            target = step.with_suffix(".SLDPRT")
            result = model.SaveAs3(str(target), 0, 1)
            if not target.exists():
                raise RuntimeError("SolidWorks native file was not created, result=%r" % result)
            title = model.GetTitle if isinstance(model.GetTitle, str) else model.GetTitle()
            app.CloseDoc(title)
            report["files"].append({
                "step": str(step), "sldprt": str(target), "bytes": target.stat().st_size
            })
        except Exception as exc:
            report["errors"].append({"step": str(step), "error": repr(exc)})
            if model is not None:
                try:
                    title = model.GetTitle if isinstance(model.GetTitle, str) else model.GetTitle()
                    app.CloseDoc(title)
                except Exception:
                    pass
    report["status"] = "complete" if not report["errors"] else "partial"
    (ROOT / "solidworks_conversion_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
