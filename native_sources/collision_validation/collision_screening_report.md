# Detailed STEP solid-overlap screening

## Result

- Source: `mkh650_manipulator.step`
- Imported solid count: 248
- Broad-phase bounding-box candidate pairs: 550
- Exact common-volume pairs above 0.5 mm3: 465
- Exact intersection operation failures: 0
- Runtime: 2.266 s

## Interpretation

This is a static geometry-overlap screen over every imported solid in the detailed STEP. Bounding boxes are used only for broad-phase filtering; listed overlap pairs were then checked with exact CAD common-volume operations.

An overlap is not automatically a design error. The portfolio STEP uses simplified primitives, and intended press fits, fasteners, embedded motors, welded interfaces and visual envelopes can overlap by construction. STEP import in this workflow does not preserve a reliable part-name mapping for every solid, so `solid_a` and `solid_b` are stable indices only within this exported file.

Use `solid_bounding_boxes.csv` and `overlap_pairs.csv` to investigate the largest pairs. Final interference approval requires a native assembly with component identity, suppression rules, intended-contact definitions and joint-position sweeps.
