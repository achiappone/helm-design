"""
Helm Design - LP-24 Angled Wedge Mount  (rev A)
===============================================
Holds a CNLINKO LP-24 24-pin flange receptacle at 45 deg as a serviceable
cable disconnect. Cable arrives from the helm enclosure's NPT 3/4 gland,
enters through the deck/bulkhead, is clamped internally, and terminates
on the connector.

This part is a WATER-SHEDDING SHROUD, not a pressure vessel. The watertight
barrier is the LP-24's own IP67 seal + the gland at the helm enclosure.
The drain slot is intentional - do not seal it.

Material : ASA (blue)   Orientation : BASE DOWN on the bed
Layers   : 0.2 mm       Perimeters  : 5     Infill : 30% gyroid
Supports : inside the LP-24 bore only (45 deg walls self-support)
"""
from build123d import *
import math

# ---------------------------------------------------------------- parameters
ANGLE      = 45.0        # connector face angle from horizontal
WALL       = 4.5
BASE_T     = 6.0
BASE_L, BASE_W = 128.0, 96.0
BODY_W     = 70.0        # wedge width (Y)
CORNER_R   = 10.0

# wedge side profile (XZ), z measured from top of base
RUN        = 50.0        # 45 deg -> run == rise
RISE       = RUN * math.tan(math.radians(ANGLE))
X_FRONT    = -35.0
X_TOP_BACK =  33.0
X_BACK     =  45.0

# CNLINKO LP-24  -- CONFIRMED from manufacturer drawing
LP24_BORE   = 24.4
LP24_PITCH  = 26.0       # <-- 26 mm SQUARE. Not a 61 mm bolt circle.
LP24_SCREW  = 4.0        # M3 316SS heat-set insert bore
LP24_BOSS_D = 8.0
LP24_BOSS_H = 8.0

# base mounting: 6 x M5 316SS  (6 not 4 - see notes on flange bowing)
BOLT_D     = 5.5
BOLT_X     = 53.0
BOLT_Y     = 37.0

# gasket gland - 3 mm cord (VERIFY CORD DIA)
CORD_D     = 3.0
GW, GD     = CORD_D * 1.15, CORD_D * 0.77
GL, GH, GR = 92.0, 58.0, 10.0

# cable / strain relief
import json as _j
CABLE_D = _j.load(open("cad/out/housing.json"))["CABLE_D"]   # set by the housing's M16 gland - do not retype
OPEN_L, OPEN_W = 46.0, 34.0
LIP_H      = 5.0
SR_PITCH   = 24.0        # strain relief screw spacing
SR_INSERT  = 5.6         # M4 316SS heat-set insert bore
DRAIN_W, DRAIN_H = 14.0, 3.5

# ---------------------------------------------------------------- base plate
base = Box(BASE_L, BASE_W, BASE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
base = fillet(base.edges().filter_by(Axis.Z), CORNER_R)

# ---------------------------------------------------------------- wedge body
prof = [(X_FRONT, BASE_T),
        (X_FRONT + RUN, BASE_T + RISE),
        (X_TOP_BACK, BASE_T + RISE),
        (X_BACK, BASE_T)]
sk = Plane.XZ * Polygon(*prof, align=None)
body = extrude(sk, amount=BODY_W / 2, both=True)
body = fillet(body.edges().filter_by(Axis.Y).group_by(Axis.Z)[-1], 6.0)

# hollow it, leaving the bottom open
bottom = body.faces().sort_by(Axis.Z)[0]
body = offset(body, amount=-WALL, openings=bottom, kind=Kind.INTERSECTION)

# There is deliberately NO vertical-corner fillet after this union. The line
# that used to sit here,
#     fillet(p.edges().filter_by(Axis.Z).group_by(SortBy.LENGTH)[-1], 4.0)
# threw at EVERY radius, not just at 4.0, so do not go hunting for a smaller
# number - the real limit is 0 and max_fillet cannot converge on it either.
# It came over from lp24_upright_mount.py, whose body genuinely does have four
# tall vertical corners to round because its connector face stands upright. A
# wedge has none: every face here is the 45 deg incline, the top flat, the back
# slope or an XZ side wall. So filter_by(Axis.Z) on the fused part finds only 8
# edges, every one of them BASE_T long, and every one of them a tangent seam
# where the base plate's CORNER_R round meets a flat side. A plane and a
# cylinder already G1 across an edge have no corner left to take a radius,
# which is what OCC means by "There are no suitable edges for chamfer or
# fillet". Those corners are already rounded - CORNER_R did it up at the base
# plate. A root fillet where the walls land on the base top face IS buildable
# (max_fillet allows ~13 mm there) but that is a different feature, and the
# middle M5 pair at (0, +-BOLT_Y) already grazes the wall foot, so it is not
# something to slip in silently.
assert not body.edges().filter_by(Axis.Z), (
    "wedge body grew a vertical face - round its corners before the shell op, "
    "the way lp24_upright_mount.py does, not after the union")
p = base + body

# ------------------------------------------------- LP-24 on the angled face
a = math.radians(ANGLE)
fc = ((X_FRONT + RUN / 2), 0.0, BASE_T + RISE / 2)          # face centre
n  = (-math.sin(a), 0.0, math.cos(a))                        # outward normal
fp = Plane(origin=fc, z_dir=n, x_dir=(0, 1, 0))

p -= fp * Pos(0, 0, 1) * Cylinder(LP24_BORE / 2, WALL + 6,
                                  align=(Align.CENTER, Align.CENTER, Align.MAX))
for sx in (-1, 1):
    for sy in (-1, 1):
        o = (sx * LP24_PITCH / 2, sy * LP24_PITCH / 2)
        # inner boss to host the heat-set insert (front wall alone is too thin)
        p += fp * Pos(o[0], o[1], -WALL) * Cylinder(
            LP24_BOSS_D / 2, LP24_BOSS_H,
            align=(Align.CENTER, Align.CENTER, Align.MAX))
        p -= fp * Pos(o[0], o[1], 1) * Cylinder(
            LP24_SCREW / 2, WALL + LP24_BOSS_H + 2,
            align=(Align.CENTER, Align.CENTER, Align.MAX))

# ---------------------------------------------------- base mounting holes
for bx in (-BOLT_X, 0.0, BOLT_X):
    for by in (-BOLT_Y, BOLT_Y):
        p -= Pos(bx, by) * Cylinder(BOLT_D / 2, 3 * BASE_T)

# ---------------------------------------------------------- gasket gland
outer = RectangleRounded(GL + GW, GH + GW, GR + GW / 2)
inner = RectangleRounded(GL - GW, GH - GW, GR - GW / 2)
p -= extrude(Plane.XY * (outer - inner), amount=GD)

# ------------------------------------------- cable opening + anti-wick lip
p -= Pos(5, 0) * Box(OPEN_L, OPEN_W, 3 * BASE_T,
                     align=(Align.CENTER, Align.CENTER, Align.CENTER))
lip = Pos(5, 0, BASE_T) * Box(OPEN_L + 2 * 3.0, OPEN_W + 2 * 3.0, LIP_H,
                              align=(Align.CENTER, Align.CENTER, Align.MIN))
lip -= Pos(5, 0, BASE_T) * Box(OPEN_L, OPEN_W, 3 * LIP_H,
                               align=(Align.CENTER, Align.CENTER, Align.MIN))
p += lip

# ------------------------------------------------ internal strain relief pad
pad = Pos(26, 0, BASE_T) * Box(40, 18, 4.0,
                               align=(Align.CENTER, Align.CENTER, Align.MIN))
p += pad
for sy in (-1, 1):
    p += Pos(26, sy * SR_PITCH / 2, BASE_T) * Cylinder(
        SR_INSERT / 2 + 2.0, 12.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    p -= Pos(26, sy * SR_PITCH / 2, BASE_T + 12.0 - 7.0) * Cylinder(
        SR_INSERT / 2, 7.5, align=(Align.CENTER, Align.CENTER, Align.MIN))

# ------------------------------------------------------------- drain slot
p -= Pos(X_FRONT + 2, 0, BASE_T) * Box(20.0, DRAIN_W, DRAIN_H,
                                       align=(Align.CENTER, Align.CENTER, Align.MIN))

# --------------------------------------------------- first-layer chamfer
p = chamfer(p.faces().sort_by(Axis.Z)[0].edges(), 0.5)

# Repo-root-relative, like every other script here. This used to be an
# absolute /Users/... path, which meant a run from anywhere but the main
# checkout - a worktree, say - silently wrote its STEP into the main repo.
out = "cad/out/lp24_wedge_mount_revA.stp"
export_step(p, out)
print(f"WEDGE  volume={p.volume/1000:.1f} cm^3  solids={len(p.solids())}")
bb = p.bounding_box()
print(f"       bbox = {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm")
print(f"       {out}")

# ==================================================== strain relief clamp
clamp = Box(40, 18, 12, align=(Align.CENTER, Align.CENTER, Align.MIN))
clamp = fillet(clamp.edges().filter_by(Axis.Z), 3.0)
clamp -= Pos(0, 0, 0) * Rot(0, 90, 0) * Cylinder(CABLE_D / 2 + 0.4, 60)
for sy in (-1, 1):
    clamp -= Pos(0, sy * SR_PITCH / 2) * Cylinder(4.5 / 2, 40)
    clamp -= Pos(0, sy * SR_PITCH / 2, 12 - 2.6) * Cone(
        8.4 / 2, 4.5 / 2, 2.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
out2 = "cad/out/lp24_wedge_clamp_revA.stp"
export_step(clamp, out2)
print(f"CLAMP  volume={clamp.volume/1000:.1f} cm^3  solids={len(clamp.solids())}")
print(f"       {out2}")
