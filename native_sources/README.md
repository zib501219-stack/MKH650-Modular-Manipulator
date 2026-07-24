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

## Engineering package

`engineering_package/` adds controlled part numbers `MK-001` to `MK-004`, BOM, four DXF drawings, four A3 PDF sheets, an exploded reference assembly STEP, placement data, a reviewed assembly snapshot and a validation note.

The reference assembly is an exploded key-part review layout. Use the repository's main detailed manipulator assembly for system-level arrangement and load-path context.

## Engineering analysis

`engineering_analysis/` adds traceable preliminary checks for the 1552 N.m J2 torque, 90 mm output shaft, foundation-bolt load distribution and 1770 N gripper force. It also records shaft, bearing, pilot and dowel fit recommendations plus a verification matrix separating calculations from unrun FEA and prototype tests.

## Motion and pose-load validation

`motion_validation/` contains 4,453 sampled J2/J3 poses, a workspace/load map, singularity flags and pose-by-pose J2 torque utilization. The assumed joint ranges are recorded in the report; the horizontal extended posture reaches the 1552 N.m baseline.

## Solid overlap screening

`collision_validation/` contains the per-solid bounding boxes and exact common-volume results from the detailed manipulator STEP. The scan found many intersecting pairs, so the detailed STEP is **not released as a collision-free manufacturing assembly**. Expected fitted interfaces and construction-geometry overlaps must be separated and resolved in a named, constrained native assembly.

## Structural analysis

`structural_analysis/` contains a reproducible 26-element Euler-Bernoulli beam FE check for the equivalent twin-plate upper arm under the 1552 N.m J2 design moment. The global bending check passes the preliminary stress and deflection limits. Local 3D checks remain required around the joint rings, lightening holes, bearing seats, bolts and contacts.

## Native-format status

`native_format_status/` records exactly which SolidWorks, STEP and DXF sources were verified, the NX `-10005` license failure, the enhanced-STEP import limitation and the steps needed to complete a named constrained assembly and 3D solver study on a licensed workstation.
