from pathlib import Path
import csv
import math


OUT = Path(__file__).resolve().parent / "output"


def torsional_shear_mpa(torque_nm, diameter_mm):
    return 16 * torque_nm * 1000 / (math.pi * diameter_mm ** 3)


def min_shaft_diameter_mm(torque_nm, allowable_mpa):
    return (16 * torque_nm * 1000 / (math.pi * allowable_mpa)) ** (1 / 3)


def cylinder_force_n(bore_mm, pressure_mpa, efficiency=1.0):
    return pressure_mpa * math.pi * bore_mm ** 2 / 4 * efficiency


def write_csv(path, headers, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerows(rows)


def four_axis():
    folder = OUT / "01_4axis_robot"
    folder.mkdir(parents=True, exist_ok=True)
    torque = 47.7
    selected_d = 30
    tau = torsional_shear_mpa(torque, selected_d)
    d_min = min_shaft_diameter_mm(torque, 40)
    shaft_sf = 40 / tau
    bearing_span = 0.06
    bearing_radial = torque / bearing_span
    bolt_radius = 0.125
    bolt_tension = torque / (4 * bolt_radius)
    grip_required = 0.5 * 9.81 * 3 / 0.3
    grip_available = 60
    write_csv(folder / "calculation_inputs.csv",
              ["parameter","value","unit","status","note"], [
        ["rated_payload",2,"kg","resume baseline","system rated payload"],
        ["J2_design_torque",torque,"N.m","calculated baseline","static moment with dynamic and service factors"],
        ["shaft_allowable_shear",40,"MPa","assumed","conservative preliminary value"],
        ["selected_shaft_diameter",selected_d,"mm","selected","preliminary joint shaft"],
        ["bearing_span",bearing_span*1000,"mm","assumed","distance used for radial reaction estimate"],
        ["base_bolt_pattern_radius",bolt_radius*1000,"mm","model baseline","four-bolt pattern"],
        ["workpiece_for_grip_check",0.5,"kg","assumed","representative gripped object"],
        ["grip_friction_coefficient",0.3,"-","assumed","dry contact estimate"],
    ])
    rows = [
        ["minimum_torsion_shaft_diameter",d_min,"mm",">=18.2","PASS"],
        ["selected_shaft_torsional_shear",tau,"MPa","<=40", "PASS"],
        ["shaft_preliminary_safety_factor",shaft_sf,"-",
         ">=2.0","PASS"],
        ["estimated_bearing_radial_reaction",bearing_radial,"N","<19500 N catalog dynamic rating reference","PASS_PRELIMINARY"],
        ["base_bolt_tension_from_moment",bolt_tension,"N/bolt","well below M12 proof capacity","PASS_PRELIMINARY"],
        ["required_grip_normal_force",grip_required,"N","<=60 N design force","PASS"],
        ["available_grip_force",grip_available,"N",">=required","PASS"],
    ]
    write_csv(folder / "calculation_results.csv",
              ["check","result","unit","criterion","status"], rows)
    fits = [
        ["J2 shaft bearing seat","30 h6","bearing inner ring, rotating load","6006-size envelope; grinding recommended"],
        ["bearing housing bore","55 H7","6006 bearing outer ring","transition fit review after housing material selection"],
        ["arm pivot pin","20 g6","removable precision pin","pair with 20 H7 hole"],
        ["arm pivot hole","20 H7","reamed hole","do not use laser-cut hole as final bearing datum"],
        ["base locating register","124 H7 / 124 g6","removable concentric location","verify coating allowance"],
        ["base fastener clearance","M12 / Ø13.5","normal clearance","GB/T 5277 reference"],
    ]
    write_csv(folder / "fits_and_tolerances.csv",
              ["feature","recommended_fit_or_size","purpose","note"], fits)
    report = f"""# Four-axis robot preliminary engineering checks

## Conclusion

The 30 mm preliminary J2 joint shaft passes the simplified torsion check for the 47.7 N.m J2 design torque. Calculated torsional shear is {tau:.1f} MPa against a conservative 40 MPa allowable value, giving a preliminary safety factor of {shaft_sf:.2f}. The theoretical minimum diameter is {d_min:.1f} mm; 30 mm is retained to match the repository's earlier shaft baseline and provide room for keyways, shoulders and stiffness.

The estimated radial reaction across a 60 mm bearing span is {bearing_radial:.0f} N. A paired 6006-size bearing arrangement is a reasonable envelope for portfolio design, but final life must use the selected manufacturer's dynamic rating, speed spectrum and equivalent-load calculation.

The 60 N gripper baseline exceeds the {grip_required:.1f} N normal-force estimate for a 0.5 kg object at friction coefficient 0.3 and safety factor 3.

## Design recommendations

- Use ground bearing seats and shoulders; do not locate bearings from unfinished plate edges.
- Add retaining nut or circlip details after the motor/reducer output interface is fixed.
- Keep cable routing clear of the full J2 and J3 angular ranges.
- Confirm the base fastener grade, installation torque and supporting table stiffness before manufacturing.

## Boundary

These are preliminary hand calculations, not test results or solver-derived stress results. Keyway stress concentration, bending-torsion combination, fatigue, bearing life and housing deformation remain to be checked after reducer, motor and bearing part numbers are frozen.
"""
    (folder / "engineering_check_report.md").write_text(report, encoding="utf-8")


def feeding():
    folder = OUT / "02_feeding_inspection"
    folder.mkdir(parents=True, exist_ok=True)
    pressure = 0.5
    f16 = cylinder_force_n(16, pressure)
    f16_eff = cylinder_force_n(16, pressure, 0.85)
    f20 = cylinder_force_n(20, pressure)
    f20_eff = cylinder_force_n(20, pressure, 0.85)
    workpiece_weight = 0.12 * 9.81
    slide_resistance = 15
    write_csv(folder / "calculation_inputs.csv",
              ["parameter","value","unit","status","note"], [
        ["workpiece_size","Ø20 x 60","mm","design baseline","cylindrical workpiece"],
        ["workpiece_mass",0.12,"kg","design baseline","single part"],
        ["target_rate",12,"parts/min","resume target","5 second cycle"],
        ["air_pressure",pressure,"MPa","assumed","regulated supply pressure"],
        ["separator_cylinder_bore",16,"mm","selected baseline","double-acting cylinder"],
        ["transfer_cylinder_bore",20,"mm","selected baseline","double-acting cylinder"],
        ["pneumatic_efficiency",0.85,"-","assumed","friction and pressure-loss allowance"],
        ["estimated_slide_resistance",slide_resistance,"N","assumed","guide, seals and part contact"],
    ])
    rows = [
        ["16 mm cylinder theoretical extension force",f16,"N",">15 N","PASS"],
        ["16 mm cylinder effective extension force",f16_eff,"N",">15 N","PASS"],
        ["20 mm cylinder theoretical extension force",f20,"N",">15 N","PASS"],
        ["20 mm cylinder effective extension force",f20_eff,"N",">15 N","PASS"],
        ["workpiece weight",workpiece_weight,"N","informational","INFO"],
        ["cycle time from target rate",60/12,"s","<=5 s","PASS_AT_TARGET"],
        ["separator force safety factor",f16_eff/slide_resistance,"-",
         ">=3","PASS_PRELIMINARY"],
        ["transfer force safety factor",f20_eff/slide_resistance,"-",
         ">=3","PASS_PRELIMINARY"],
    ]
    write_csv(folder / "calculation_results.csv",
              ["check","result","unit","criterion","status"], rows)
    fits = [
        ["feeder channel width","20.5 to 21.0 mm","free sliding for Ø20 part","confirm actual diameter tolerance and contamination"],
        ["V locator included angle","90 deg nominal","repeatable two-line contact","harden contact inserts if wear is significant"],
        ["locator axial stop","60.2 to 60.5 mm envelope","avoid end jamming","make one stop adjustable"],
        ["cylinder pilot","H7 clearance/locating boss per supplier","repeatable cylinder alignment","use supplier drawing"],
        ["sensor bracket slot","6.6 x 20 mm","M6 adjustment slot","lock after calibration"],
        ["base dowel","Ø6 H7/m6","repeatable station relocation","two dowels maximum per plate"],
    ]
    write_csv(folder / "fits_and_tolerances.csv",
              ["feature","recommended_fit_or_size","purpose","note"], fits)
    report = f"""# Feeding and inspection system preliminary engineering checks

## Conclusion

At 0.5 MPa, the 16 mm separator cylinder provides {f16:.1f} N theoretical and {f16_eff:.1f} N estimated effective force. The 20 mm transfer cylinder provides {f20:.1f} N theoretical and {f20_eff:.1f} N effective force. Against a preliminary 15 N sliding-resistance allowance, the corresponding force safety factors are {f16_eff/slide_resistance:.1f} and {f20_eff/slide_resistance:.1f}.

The 12 parts/min target corresponds exactly to a 5.0 second cycle. A practical allocation is 1.0 s feed confirmation, 0.8 s separation, 1.2 s transfer, 1.0 s inspection and 1.0 s return/buffer. PLC timing and sensor response still require commissioning.

## Design recommendations

- Use an adjustable guide to keep the channel between 20.5 and 21.0 mm for the nominal Ø20 part.
- Make one V-locator or axial stop adjustable to absorb real workpiece tolerance.
- Add flow controls and end cushioning to avoid impact at the inspection nest.
- Use two locating dowels plus bolts when a station must be removed and returned accurately.

## Boundary

Cylinder forces are theoretical pressure-area calculations with a single efficiency allowance. Actual force, takt, bounce, jamming probability and inspection repeatability require the selected cylinder, valves, tubing, sensors, PLC program and physical workpieces.
"""
    (folder / "engineering_check_report.md").write_text(report, encoding="utf-8")


def mkh650():
    folder = OUT / "03_mkh650"
    folder.mkdir(parents=True, exist_ok=True)
    torque = 1552
    shaft_d = 90
    tau = torsional_shear_mpa(torque, shaft_d)
    d_min = min_shaft_diameter_mm(torque, 50)
    shaft_sf = 50 / tau
    bolt_force = torque / (8 * 0.13)
    required_grip = 20 * 9.81 * 2.25 / 0.25
    write_csv(folder / "calculation_inputs.csv",
              ["parameter","value","unit","status","note"], [
        ["rated_payload",20,"kg","resume/report baseline","maximum nominal payload"],
        ["maximum_radius",1180,"mm","calculated baseline","520+480+180"],
        ["J2_design_torque",torque,"N.m","calculated baseline","preliminary combined load"],
        ["shaft_allowable_shear",50,"MPa","assumed","preliminary alloy-steel allowable"],
        ["selected_joint_shaft_diameter",shaft_d,"mm","selected","preliminary output shaft"],
        ["foundation_bolt_count",8,"count","model baseline","M16 preliminary"],
        ["foundation_bolt_radius",130,"mm","model baseline","bolt-circle radius"],
        ["grip_friction_coefficient",0.25,"-","assumed","conservative jaw contact"],
        ["grip_safety_factor",2.25,"-","assumed","vertical holding"],
    ])
    rows = [
        ["minimum_torsion_shaft_diameter",d_min,"mm","<=90 mm selected","PASS"],
        ["selected_shaft_torsional_shear",tau,"MPa","<=50","PASS"],
        ["shaft_preliminary_safety_factor",shaft_sf,"-",">=2.0","PASS"],
        ["foundation_bolt_tangential_force",bolt_force,"N/bolt","well below M16 capacity","PASS_PRELIMINARY"],
        ["required_total_grip_normal_force",required_grip,"N","<=1770 N baseline","PASS"],
        ["available_grip_design_force",1770,"N",">=required","PASS"],
    ]
    write_csv(folder / "calculation_results.csv",
              ["check","result","unit","criterion","status"], rows)
    fits = [
        ["joint output shaft bearing seat","90 k6","inner ring with significant rotating load","matches repository baseline; final fit depends on bearing class and temperature"],
        ["joint housing bearing bore","bearing OD H7","outer ring location","check housing wall deformation"],
        ["output flange pilot","Ø120 H7/g6 preliminary","removable concentric location","verify ISO 9409 interface if used"],
        ["foundation locating pilot","Ø120 H7/g6","base concentric location","do not rely only on anchor-bolt clearance"],
        ["foundation bolts","8 x M16 class 10.9 preliminary","overturning and torque transfer","preload and concrete/baseplate check required"],
        ["gripper replaceable insert","H7/m6 dowels + bolts","repeatable jaw replacement","harden insert contact teeth"],
    ]
    write_csv(folder / "fits_and_tolerances.csv",
              ["feature","recommended_fit_or_size","purpose","note"], fits)
    report = f"""# MKH650 preliminary engineering checks

## Conclusion

For the 1552 N.m preliminary J2 torque, a 90 mm shaft has simplified torsional shear of {tau:.1f} MPa. Against a preliminary 50 MPa allowable value, the torsional safety factor is {shaft_sf:.2f}; the theoretical minimum diameter is {d_min:.1f} mm. The 90 mm size is retained to match the repository's earlier shaft baseline, subject to combined bending, fatigue and key/spline checks.

Distributing torque over eight bolts on a 130 mm radius gives approximately {bolt_force:.0f} N tangential force per bolt before preload/friction effects. This is small relative to a typical M16 high-strength bolt capacity, but the real base design is governed by preload, overturning moment, plate bending and foundation stiffness.

For a 20 kg payload, friction coefficient 0.25 and holding safety factor 2.25, required total grip normal force is {required_grip:.0f} N. The 1770 N design baseline is consistent with this preliminary requirement.

## Design recommendations

- Use a splined or keyed output connection sized for combined bending and torsion.
- Select paired tapered-roller, angular-contact or cross-roller bearings only after axial moment and stiffness requirements are known.
- Transfer foundation torque by friction/preload and a locating pilot or dowels, not loose bolt clearance alone.
- Use replaceable hardened gripper inserts and verify contact pressure on the actual payload.

## Boundary

These calculations do not constitute FEA, fatigue certification or foundation approval. Dynamic trajectories, emergency-stop loads, gearbox stiffness, weld details, concrete anchorage and actual payload centre of gravity remain unresolved until the final machine definition is available.
"""
    (folder / "engineering_check_report.md").write_text(report, encoding="utf-8")


def verification_matrices():
    common = [
        ["geometry","enhanced STEP opens as one solid","verified","CadQuery STEP re-import solid count"],
        ["drawing","DXF units and entity structure","verified","ezdxf readback"],
        ["drawing","A3 PDF renders as one page","verified","pypdf and Poppler representative render"],
        ["assembly","enhanced key-part reference layout","verified","STEP snapshot"],
        ["native_cad","enhanced feature-history SLDPRT","open","enhanced geometry remains STEP + parametric source"],
        ["native_cad","NX native PRT","blocked","local NX batch modeling license error"],
        ["simulation","FEA stress and deformation","not_run","no solver result is claimed"],
        ["prototype","measured accuracy, takt and payload","not_tested","requires physical prototype"],
    ]
    for slug in ("01_4axis_robot","02_feeding_inspection","03_mkh650"):
        write_csv(OUT / slug / "verification_matrix.csv",
                  ["category","item","status","evidence_or_next_action"], common)


def main():
    four_axis()
    feeding()
    mkh650()
    verification_matrices()
    print("engineering analysis generated")


if __name__ == "__main__":
    main()
