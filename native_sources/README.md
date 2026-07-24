# Native CAD source files

This folder contains genuine SolidWorks 2023 part files created from the portfolio design baseline, plus neutral STEP copies for NX and other CAD systems.

Design basis: 20 kg payload, 520 mm upper arm, 480 mm forearm, 180 mm tool offset.

Files:

- `foundation_flange.SLDPRT`
- `upper_arm_side_plate.SLDPRT`
- `joint_output_flange.SLDPRT`
- `heavy_gripper_finger.SLDPRT`

The models contain editable sketches and extrusion features. Existing editable DXF drawings remain under `drawings/`.

NX note: the STEP files can be opened and saved as NX `.prt`. Native NX batch feature generation was not committed because the local NX feature-modeling license was unavailable during this build.
