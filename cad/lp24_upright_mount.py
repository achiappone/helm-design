"""
Helm Design - LP-24 90 deg Upright Mount  (rev B)
=================================================
Holds a CNLINKO LP-24 24-pin flange receptacle with its face VERTICAL, so
water can never pool in the connector. Cable arrives from the helm
enclosure's NPT 3/4 gland, enters through the deck, is clamped internally,
and terminates on the connector.

WATER-SHEDDING SHROUD, not a pressure vessel. The watertight barrier is the
LP-24's own IP67 seal + the gland at the helm end. The drain slot is
intentional - do not seal it.

Material : ASA (blue)   Orientation : BASE DOWN on the bed
Layers   : 0.2 mm       Perimeters  : 5     Infill : 30% gyroid
Supports : NONE - connector bore is teardropped, back wall is 12 deg
"""
from build123d import *

# ---------------------------------------------------------------- parameters
WALL       = 4.5
BASE_T     = 6.0
BASE_L, BASE_W = 132.0, 102.0
BODY_W     = 62.0
CORNER_R   = 10.0

X_FRONT    = -30.0        # vertical connector face
X_BACK_BOT =  38.0
X_BACK_TOP =  25.0        # 12 deg back taper -> sheds water, no overhang
BODY_H     =  58.0        # above base
TOP_Z      = BASE_T + BODY_H

# CNLINKO LP-24  -- CONFIRMED from manufacturer drawing
LP24_BORE   = 24.4
LP24_PITCH  = 26.0        # 26 mm SQUARE pattern. NOT a 61 mm bolt circle.
LP24_SCREW  = 4.0         # M3 316SS heat-set insert bore
LP24_BOSS_D = 8.5
LP24_BOSS_H = 8.0
LP24_Z      = BASE_T + 29.0
TEARDROP_K  = 1.25        # bore peak height = k * radius (self-supporting)

BOLT_D     = 5.5          # 6 x M5 316SS
BOLT_X, BOLT_Y = 56.0, 43.0

CORD_D     = 3.0          # VERIFY
GW, GD     = CORD_D * 1.15, CORD_D * 0.77
GL, GH, GR = 98.0, 70.0, 10.0

CABLE_D    = 14.0         # SET TO YOUR ACTUAL CABLE OD (gland takes 12.5-18)
OPEN_L, OPEN_W = 40.0, 42.0   # service access, not just a cable hole
LIP_H      = 5.0
SR_PITCH   = 24.0
SR_INSERT  = 5.6          # M4 316SS heat-set insert bore
DRAIN_W, DRAIN_H = 14.0, 3.5

# ---------------------------------------------------------------- base plate
base = Box(BASE_L, BASE_W, BASE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
base = fillet(base.edges().filter_by(Axis.Z), CORNER_R)

# ---------------------------------------------------------------- body
prof = [(X_FRONT, BASE_T), (X_FRONT, TOP_Z), (X_BACK_TOP, TOP_Z), (X_BACK_BOT, BASE_T)]
body = extrude(Plane.XZ * Polygon(*prof, align=None), amount=BODY_W / 2, both=True)
body = fillet(body.edges().filter_by(Axis.Z), 8.0)
body = fillet(body.edges().filter_by(Axis.Y).group_by(Axis.Z)[-1], 4.0)

bottom = body.faces().sort_by(Axis.Z)[0]
body = offset(body, amount=-WALL, openings=bottom, kind=Kind.INTERSECTION)

p = base + body

# ------------------------------------------- LP-24 bore, teardropped for FDM
r = LP24_BORE / 2
bore_pl = Plane(origin=(X_FRONT, 0, LP24_Z), z_dir=(-1, 0, 0), x_dir=(0, 1, 0))

# Teardrop bore, built in GLOBAL coords (bore axis == global X) so the apex
# direction is unambiguous. Plane.YZ maps sketch-X -> global Y, sketch-Y -> global Z.
bore_cut = Pos(X_FRONT, 0, LP24_Z) * Rot(0, 90, 0) * Cylinder(r, 40)
peak = extrude(Plane.YZ * Polygon((-r, 0), (r, 0), (0, TEARDROP_K * r), align=None),
               amount=20, both=True)
p -= bore_cut + Pos(X_FRONT, 0, LP24_Z) * peak

# heat-set insert bosses on the inside of the front wall
for sx in (-1, 1):
    for sy in (-1, 1):
        o = (sx * LP24_PITCH / 2, sy * LP24_PITCH / 2)
        p += bore_pl * Pos(o[0], o[1], -WALL) * Cylinder(
            LP24_BOSS_D / 2, LP24_BOSS_H, align=(Align.CENTER, Align.CENTER, Align.MAX))
        p -= bore_pl * Pos(o[0], o[1], 1) * Cylinder(
            LP24_SCREW / 2, WALL + LP24_BOSS_H + 2,
            align=(Align.CENTER, Align.CENTER, Align.MAX))

# ---------------------------------------------------- base mounting holes
for bx, by in [(-BOLT_X,-BOLT_Y),(0,-BOLT_Y),(BOLT_X,-BOLT_Y),
               (-BOLT_X, 0.0),                 (BOLT_X, 0.0),
               (-BOLT_X, BOLT_Y),(0, BOLT_Y),(BOLT_X, BOLT_Y)]:
    p -= Pos(bx, by) * Cylinder(BOLT_D / 2, 3 * BASE_T)

# ---------------------------------------------------------- gasket gland
outer = RectangleRounded(GL + GW, GH + GW, GR + GW / 2)
inner = RectangleRounded(GL - GW, GH - GW, GR - GW / 2)
p -= extrude(Plane.XY * (outer - inner), amount=GD)

# ------------------------------------------- cable opening + anti-wick lip
p -= Pos(-4, 0) * Box(OPEN_L, OPEN_W, 3 * BASE_T,
                     align=(Align.CENTER, Align.CENTER, Align.CENTER))
lip = Pos(-4, 0, BASE_T) * Box(OPEN_L + 5, OPEN_W + 5, LIP_H,
                              align=(Align.CENTER, Align.CENTER, Align.MIN))
lip -= Pos(-4, 0, BASE_T) * Box(OPEN_L, OPEN_W, 3 * LIP_H,
                               align=(Align.CENTER, Align.CENTER, Align.MIN))
p += lip

# ------------------------------------------------ internal strain relief
p += Pos(24, 0, BASE_T) * Box(18, 36, 4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
for sy in (-1, 1):
    p += Pos(24, sy * SR_PITCH / 2, BASE_T) * Cylinder(
        SR_INSERT / 2 + 2.0, 13.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    p -= Pos(24, sy * SR_PITCH / 2, BASE_T + 13.0 - 7.5) * Cylinder(
        SR_INSERT / 2, 8.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

# ------------------------------------------------------------- drain slot
p -= Pos(X_FRONT, 0, BASE_T) * Box(20.0, DRAIN_W, DRAIN_H,
                                   align=(Align.CENTER, Align.CENTER, Align.MIN))

p = chamfer(p.faces().sort_by(Axis.Z)[0].edges(), 0.5)

out = "/Users/anthonychiappone/Helm_Design/cad/out/lp24_upright_mount_revB.stp"
export_step(p, out)
bb = p.bounding_box()
print(f"MOUNT  vol={p.volume/1000:6.1f} cm^3  solids={len(p.solids())}  "
      f"bbox={bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f}")

# ==================================================== strain relief clamp
clamp = Box(18, 36, 13, align=(Align.CENTER, Align.CENTER, Align.MIN))
clamp = fillet(clamp.edges().filter_by(Axis.Z), 3.0)
clamp -= Rot(0, 90, 0) * Cylinder(CABLE_D / 2 + 0.4, 60)
for sy in (-1, 1):
    clamp -= Pos(0, sy * SR_PITCH / 2) * Cylinder(4.5 / 2, 40)
    clamp -= Pos(0, sy * SR_PITCH / 2, 13 - 2.6) * Cone(
        8.4 / 2, 4.5 / 2, 2.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
out2 = "/Users/anthonychiappone/Helm_Design/cad/out/lp24_upright_clamp_revB.stp"
export_step(clamp, out2)
bb2 = clamp.bounding_box()
print(f"CLAMP  vol={clamp.volume/1000:6.1f} cm^3  solids={len(clamp.solids())}  "
      f"bbox={bb2.size.X:.1f} x {bb2.size.Y:.1f} x {bb2.size.Z:.1f}")
