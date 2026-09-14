"""
Print Check -- will each part sit on the bed, and will it stay there?

The repo already asserts that parts FIT the bed. Fitting is not the question a
334 x 177 ASA plate asks. The questions are how much of it touches the bed on
the first layer, how much of what is above that is unsupported, and whether the
first layer is a thin picture frame that will peel at the corners.

Measured, in each part's OWN export orientation (cad/export_mesh.py owns those,
and this file reads them, so the two cannot drift):

  BED CONTACT   the area of the part within one layer of the lowest plane. A
                cover balanced on two trunnion tips reads 429 mm2; the same
                cover with its bumps coplanar reads 23,000.
  OVERHANG      downward-facing area steeper than the printable angle, i.e. the
                area that needs support. Reported per part, with the worst
                single face.
  FOOTPRINT     the bounding rectangle on the bed, against the machine.
  SLENDERNESS   height over the smaller footprint dimension. A tall part on a
                narrow base is the one that comes off in a draught.

Nothing here fails a build on its own - support is a legitimate answer and so is
a brim. It fails when a part has SO LITTLE contact that it cannot be held down
at all, because that is not a slicer setting, it is a design fault.
"""
import sys, json, math
sys.path.insert(0, "cad")
from build123d import *

BED_X, BED_Y = 350.0, 350.0
LAYER = 0.24                        # first layer, ASA on a textured sheet
OVERHANG_OK = 45.0                  # degrees from horizontal, printable unaided
MIN_CONTACT = 1500.0                # mm2 below which nothing will hold it down

# The orientations are export_mesh.py's, parsed from it rather than retyped -
# a second copy of a print orientation is a second thing to get wrong.
_src = open("cad/export_mesh.py").read()
PARTS = []
for _m in __import__("re").finditer(
        r'\("(\w+)",\s*(None|Rot\([^)]*\)),\s*"([^"]*)"\)', _src):
    PARTS.append((_m.group(1), _m.group(2), _m.group(3)))

rows, warn = [], []


def lay_down(part, rot):
    if rot is not None:
        part = rot * part
    bb = part.bounding_box()
    return Pos(-(bb.min.X + bb.max.X)/2, -(bb.min.Y + bb.max.Y)/2, -bb.min.Z) * part


def bed_contact(part):
    """Area of the part within one layer of the bed, measured as a slab volume
    divided by its thickness - robust where face-picking is not."""
    bb = part.bounding_box()
    slab = Pos(0, 0, LAYER/2) * Box(bb.size.X + 2, bb.size.Y + 2, LAYER,
                                    align=(Align.CENTER,)*3)
    hit = part & slab
    return 0.0 if hit is None else hit.volume / LAYER


def overhang(part, bed_z=0.0):
    """Downward-facing area shallower than OVERHANG_OK, and the worst face.

    Faces sitting ON the bed are downward-facing and perfectly horizontal, so a
    naive sweep reports the whole first layer as unsupported - the first cut of
    this called a 334 mm cover's own bed face a 25,000 mm2 overhang."""
    total, worst, worst_a = 0.0, 0.0, 0.0
    for f in part.faces():
        try:
            n = f.normal_at(f.center())
            a = f.area
        except Exception:
            continue
        if n.Z >= -1e-6 or a < 1.0:
            continue
        if f.center().Z < bed_z + LAYER*2:        # it IS the bed face
            continue
        # inclination of the face from horizontal: 90 = vertical wall, 0 = roof
        ang = 90.0 - math.degrees(math.asin(min(1.0, abs(n.Z))))
        # strictly BELOW the limit: a face AT 45 deg is printable by definition,
        # and floating point was failing the shroud's 29 louvre slats - which are
        # 45 deg on purpose - for a rounding error.
        if ang < OVERHANG_OK - 0.5:       # too close to horizontal, unsupported
            total += a
            if a > worst:
                worst, worst_a = a, ang
    return total, worst, worst_a


print(f"PRINT CHECK  -- bed {BED_X:.0f} x {BED_Y:.0f}, first layer {LAYER}, "
      f"unaided to {OVERHANG_OK:.0f} deg")
for name, rot_src, how in PARTS:
    try:
        _raw = import_step(f"cad/out/{name}.stp")
    except Exception:
        continue
    # import_step hands back a Compound, and a Location on that WRAPPER is
    # ignored by booleans - so a rotated part probes as if it were never
    # rotated, and every orientation reads the same. assembly.py documents the
    # same trap. Unwrap to the Solid before anything touches it.
    part = _raw.solids()[0] if len(_raw.solids()) == 1 else _raw
    rot = None if rot_src == "None" else eval(rot_src)
    part = lay_down(part, rot)
    bb = part.bounding_box()
    area = bed_contact(part)
    over, worst, worst_ang = overhang(part, bb.min.Z)
    slender = bb.size.Z / min(bb.size.X, bb.size.Y)
    flag = "  "
    if bb.size.X > BED_X or bb.size.Y > BED_Y:
        flag = "!!"; warn.append(f"{name} does not fit the bed")
    elif area < MIN_CONTACT:
        flag = "!!"; warn.append(
            f"{name} has only {area:.0f} mm2 on the bed - nothing will hold it")
    elif area < 0.10 * bb.size.X * bb.size.Y:
        flag = " ?"
    rows.append((flag, name, bb, area, over, worst, worst_ang, slender, how))

w = max(len(r[1]) for r in rows)
print(f"   {'part':{w}s}  {'footprint':>13s} {'tall':>6s} {'bed mm2':>9s} "
      f"{'%':>5s} {'support mm2':>12s}  orientation")
for flag, name, bb, area, over, worst, worst_ang, slender, how in rows:
    pct = 100.0 * area / (bb.size.X * bb.size.Y)
    print(f"{flag} {name:{w}s}  {bb.size.X:5.0f} x {bb.size.Y:5.0f} {bb.size.Z:6.0f} "
          f"{area:9.0f} {pct:4.0f}% {over:12.0f}  {how}")
    if over > 200.0:
        print(f"   {'':{w}s}  worst single face {worst:.0f} mm2 at "
              f"{worst_ang:.0f} deg from horizontal")
    if slender > 2.0:
        print(f"   {'':{w}s}  slender: {slender:.1f} tall per unit of base")

print()
print(f"  first layer under {MIN_CONTACT:.0f} mm2 is a design fault, not a slicer "
      f"setting; everything else is a brim and supports")
if warn:
    raise AssertionError("cannot be printed:\n  - " + "\n  - ".join(warn))
