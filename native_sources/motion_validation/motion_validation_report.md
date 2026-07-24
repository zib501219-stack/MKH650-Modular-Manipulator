# MKH650 motion-envelope and pose-load validation

## Inputs and assumptions

- Upper arm: 520 mm; forearm: 480 mm; tool offset: 180 mm
- Assumed J2 sample range: -60 to 120 degrees
- Assumed J3 sample range: -135 to 135 degrees
- Sample count: 4453
- Mass model: 38 kg upper arm, 24 kg forearm, 18 kg tool and 20 kg payload
- Static moment is multiplied by 2.218 so the horizontal reference pose aligns with the 1552 N.m design baseline.

## Results

- Maximum sampled radius: 1180.0 mm
- Maximum sampled factored J2 torque: 1552.0 N.m
- Maximum sampled utilization of the 1552 N.m baseline: 1.000
- Near-singularity samples use `abs(sin(J3)) < 0.0872`.

## Interpretation

The horizontal extended posture remains the governing J2 load region. Folded and straight elbow configurations are highlighted for motion-planning caution. The map supports portfolio-level posture and load reasoning, but it does not include J1 rotation, 3D wrist orientation, gearbox inertia, structural flexibility, collision solids or controller acceleration limits.
