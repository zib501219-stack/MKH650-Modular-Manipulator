"""Reusable Build123d primitives for the four resume engineering projects."""

from math import atan2, cos, degrees, hypot, radians, sin
from build123d import Align, Box, Color, Compound, Cylinder, Location

ORANGE = "#E87500"
DARK = "#25282B"
MID = "#6C737B"
LIGHT = "#C9CED3"
STEEL = "#8A929A"
BLUE = "#1779BA"
YELLOW = "#F2C230"
RED = "#D8342A"
GREEN = "#31A354"


def tag(shape, name, color=None):
    shape.label = name
    if color:
        shape.color = Color(color)
    return shape


def bx(x, y, z, p=(0, 0, 0), name="box", color=LIGHT, center=True):
    align = (Align.CENTER, Align.CENTER, Align.CENTER) if center else (Align.MIN, Align.MIN, Align.MIN)
    return tag(Box(x, y, z, align=align).located(Location(p)), name, color)


def cz(r, h, p=(0, 0, 0), name="cylinder_z", color=STEEL):
    return tag(Cylinder(r, h, align=(Align.CENTER, Align.CENTER, Align.CENTER)).located(Location(p)), name, color)


def cx(r, h, p=(0, 0, 0), name="cylinder_x", color=STEEL):
    return tag(Cylinder(r, h, align=(Align.CENTER, Align.CENTER, Align.CENTER)).located(Location(p, (0, 90, 0))), name, color)


def cy(r, h, p=(0, 0, 0), name="cylinder_y", color=STEEL):
    return tag(Cylinder(r, h, align=(Align.CENTER, Align.CENTER, Align.CENTER)).located(Location(p, (90, 0, 0))), name, color)


def bolt_z(p, length=18, diameter=6, name="bolt"):
    x, y, z = p
    shaft = cz(diameter / 2, length, (x, y, z), name + "_shaft", DARK)
    head = cz(diameter * 0.85, diameter * 0.65, (x, y, z + length / 2 + diameter * 0.325), name + "_head", DARK)
    return tag(Compound(children=[shaft, head]), name, DARK)


def bolt_y(p, length=18, diameter=6, name="bolt"):
    x, y, z = p
    shaft = cy(diameter / 2, length, (x, y, z), name + "_shaft", DARK)
    head = cy(diameter * 0.85, diameter * 0.65, (x, y + length / 2 + diameter * 0.325, z), name + "_head", DARK)
    return tag(Compound(children=[shaft, head]), name, DARK)


def bolt_circle_z(parts, center, radius, count, z, prefix, diameter=6):
    cx0, cy0 = center
    for i in range(count):
        a = radians(i * 360 / count)
        parts.append(bolt_z((cx0 + radius * cos(a), cy0 + radius * sin(a), z), diameter=diameter, name=f"{prefix}_{i+1:02d}"))


def bolt_circle_y(parts, center_xz, radius, count, y, prefix, diameter=6):
    x0, z0 = center_xz
    for i in range(count):
        a = radians(i * 360 / count)
        parts.append(bolt_y((x0 + radius * cos(a), y, z0 + radius * sin(a)), diameter=diameter, name=f"{prefix}_{i+1:02d}"))


def beam_xz(start, end, width, height, name, color=ORANGE):
    x0, y0, z0 = start
    x1, y1, z1 = end
    length = hypot(x1 - x0, z1 - z0)
    angle = degrees(atan2(z1 - z0, x1 - x0))
    beam = Box(length, width, height, align=(Align.MIN, Align.CENTER, Align.CENTER))
    return tag(beam.located(Location((x0, y0, z0), (0, -angle, 0))), name, color)


def cable_chain(parts, start, end, links, prefix, link_size=(18, 30, 10)):
    x0, y0, z0 = start
    x1, y1, z1 = end
    for i in range(links):
        t = i / max(1, links - 1)
        parts.append(bx(*link_size, (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t), f"{prefix}_{i+1:02d}", DARK))


def frame_rect(parts, x0, x1, y0, y1, z, section, prefix, color=MID):
    parts.extend([
        bx(x1-x0, section, section, ((x0+x1)/2, y0, z), prefix+"_front", color),
        bx(x1-x0, section, section, ((x0+x1)/2, y1, z), prefix+"_rear", color),
        bx(section, y1-y0, section, (x0, (y0+y1)/2, z), prefix+"_left", color),
        bx(section, y1-y0, section, (x1, (y0+y1)/2, z), prefix+"_right", color),
    ])


def assembly(parts, label):
    result = Compound(children=parts)
    result.label = label
    return result
