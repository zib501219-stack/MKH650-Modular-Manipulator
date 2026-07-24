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

## Enhanced key parts

`enhanced_key_parts/` contains the second-pass engineering models:

- stepped foundation flange with counterbores, locating boss and radial reinforcing pads;
- upper-arm plate with reinforced joint rings and five lightening holes;
- stepped joint-output flange with seal register and counterbored bolt pattern;
- heavy gripper finger with counterbores, relief pocket and grip grooves;
- one reviewed isometric PNG for every enhanced part;
- editable CadQuery source used to regenerate the STEP files.

The original `.SLDPRT` files are retained as native sketch/extrusion examples. The enhanced STEP files are the more detailed geometry baseline.
