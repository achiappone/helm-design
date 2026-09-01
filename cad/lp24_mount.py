"""
Helm Design - LP-24 Disconnect Mount  (rev C)  -- TWO PIECES
============================================================
rev B failed assembly review twice: the clamp fouled the opening, and even
enlarged, the strain-relief pad sat under a solid shelf with its screws
driving downward into a closed shroud. There was no assembly path.

rev C splits it:
  base plate  - flat. Wire and clamp the cable with nothing above you.
  shroud      - open-bottomed cover carrying the LP-24. Drops over, 8x M5.
Both bolt to the deck with the SAME 8 fasteners, so there is one set to undo.

Material : ASA (blue)   Orientation : both parts flat-face DOWN
Layers   : 0.2 mm       Perimeters  : 5     Infill : 30% gyroid
Supports : none
"""
from build123d import *

WALL, FLANGE_T, BASE_T = 4.5, 5.0, 6.0
PLAN_L, PLAN_W, CORNER_R = 132.0, 102.0, 10.0
BODY_W, BODY_H = 70.0, 58.0
X_FRONT, X_BACK_BOT, X_BACK_TOP = -30.0, 38.0, 25.0

LP24_BORE, LP24_PITCH = 24.4, 26.0
LP24_SCREW, LP24_BOSS_D, LP24_BOSS_H = 4.0, 8.5, 8.0
LP24_Z, TEARDROP_K = 29.0, 1.25          # LP24_Z measured from flange top

BOLT_D, BOLT_X, BOLT_Y = 5.5, 56.0, 43.0
BOLTS = [(-BOLT_X,-BOLT_Y),(0,-BOLT_Y),(BOLT_X,-BOLT_Y),
         (-BOLT_X, 0.0),                 (BOLT_X, 0.0),
         (-BOLT_X, BOLT_Y),(0, BOLT_Y),(BOLT_X, BOLT_Y)]

CORD_D = 3.0
GW, GD = CORD_D*1.15, CORD_D*0.77
GL, GH, GR = 98.0, 70.0, 10.0

CABLE_D = 14.0                            # SET FROM YOUR CABLE
OPEN_L, OPEN_W = 36.0, 28.0
LIP_H, LIP_T = 5.0, 2.5
SR_X, SR_HALF, SR_INSERT = -4.0, 22.0, 5.6    # screws straddle the opening
DRAIN_W, DRAIN_H = 14.0, 3.5

def plan(t):
    s = Box(PLAN_L, PLAN_W, t, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return fillet(s.edges().filter_by(Axis.Z), CORNER_R)

# ══════════════════════════════════════════════════ PART 1 - BASE PLATE
b = plan(BASE_T)
for bx, by in BOLTS:
    b -= Pos(bx, by) * Cylinder(BOLT_D/2, 3*BASE_T)

outer = RectangleRounded(GL+GW, GH+GW, GR+GW/2)
inner = RectangleRounded(GL-GW, GH-GW, GR-GW/2)
b -= extrude(Plane.XY * (outer - inner), amount=GD)          # deck gasket gland

# cable opening + anti-wick lip
b -= Pos(SR_X, 0) * Box(OPEN_L, OPEN_W, 3*BASE_T, align=(Align.CENTER,)*3)
lip = Pos(SR_X, 0, BASE_T) * Box(OPEN_L+2*LIP_T, OPEN_W+2*LIP_T, LIP_H,
                                 align=(Align.CENTER, Align.CENTER, Align.MIN))
lip -= Pos(SR_X, 0, BASE_T) * Box(OPEN_L, OPEN_W, 3*LIP_H,
                                  align=(Align.CENTER, Align.CENTER, Align.MIN))
b += lip

# strain-relief bosses straddle the opening -> clamp screws down from ABOVE,
# with the shroud off and nothing overhead.
for sy in (-1, 1):
    y = sy * SR_HALF
    b += Pos(SR_X, y, BASE_T) * Cylinder(SR_INSERT/2+2.2, 13.0,
                                         align=(Align.CENTER, Align.CENTER, Align.MIN))
    b -= Pos(SR_X, y, BASE_T+13.0-8.0) * Cylinder(SR_INSERT/2, 8.5,
                                         align=(Align.CENTER, Align.CENTER, Align.MIN))
SR_SPAN = 2*SR_HALF

# drain channel: carries shroud runoff out to the front edge
b -= Pos(-PLAN_L/2 + 12, 0, BASE_T-1.6) * Box(30, DRAIN_W, 2.0,
                                              align=(Align.CENTER, Align.CENTER, Align.MIN))
b = chamfer(b.faces().sort_by(Axis.Z)[0].edges(), 0.5)
export_step(b, "cad/out/lp24_base_plate_revC.stp")
bb = b.bounding_box()
print(f"BASE   vol={b.volume/1000:6.1f} cm3 solids={len(b.solids())} "
      f"bbox={bb.size.X:.0f}x{bb.size.Y:.0f}x{bb.size.Z:.0f}")

# ══════════════════════════════════════════════════ PART 2 - SHROUD
FT = FLANGE_T
s = plan(FT)
prof = [(X_FRONT, FT), (X_FRONT, FT+BODY_H), (X_BACK_TOP, FT+BODY_H), (X_BACK_BOT, FT)]
body = extrude(Plane.XZ * Polygon(*prof, align=None), amount=BODY_W/2, both=True)
body = fillet(body.edges().filter_by(Axis.Z), 8.0)
body = fillet(body.edges().filter_by(Axis.Y).group_by(Axis.Z)[-1], 4.0)
body = offset(body, amount=-WALL, openings=body.faces().sort_by(Axis.Z)[0],
              kind=Kind.INTERSECTION)
s += body

# open the flange under the body so the cavity reaches the base plate
cav = RectangleRounded(X_BACK_BOT-X_FRONT-2*WALL, BODY_W-2*WALL, 6.0)
s -= extrude(Plane.XY.offset(-1) * Pos((X_FRONT+X_BACK_BOT)/2, 0) * cav, amount=FT+2)

for bx, by in BOLTS:
    s -= Pos(bx, by) * Cylinder(BOLT_D/2, 3*FT)

ZC = FT + LP24_Z
r = LP24_BORE/2
s -= Pos(X_FRONT, 0, ZC) * Rot(0, 90, 0) * Cylinder(r, 40)
s -= Pos(X_FRONT, 0, ZC) * extrude(
        Plane.YZ * Polygon((-r, 0), (r, 0), (0, TEARDROP_K*r), align=None),
        amount=20, both=True)
bp = Plane(origin=(X_FRONT, 0, ZC), z_dir=(-1, 0, 0), x_dir=(0, 1, 0))
for sx in (-1, 1):
    for sy in (-1, 1):
        o = (sx*LP24_PITCH/2, sy*LP24_PITCH/2)
        s += bp * Pos(o[0], o[1], -WALL) * Cylinder(LP24_BOSS_D/2, LP24_BOSS_H,
                    align=(Align.CENTER, Align.CENTER, Align.MAX))
        s -= bp * Pos(o[0], o[1], 1) * Cylinder(LP24_SCREW/2, WALL+LP24_BOSS_H+2,
                    align=(Align.CENTER, Align.CENTER, Align.MAX))

s -= Pos(X_FRONT, 0, FT) * Box(20.0, DRAIN_W, DRAIN_H,
                               align=(Align.CENTER, Align.CENTER, Align.MIN))
s = chamfer(s.faces().sort_by(Axis.Z)[0].edges(), 0.5)
export_step(s, "cad/out/lp24_shroud_revC.stp")
bb = s.bounding_box()
print(f"SHROUD vol={s.volume/1000:6.1f} cm3 solids={len(s.solids())} "
      f"bbox={bb.size.X:.0f}x{bb.size.Y:.0f}x{bb.size.Z:.0f}")

# ══════════════════════════════════════════════════ PART 3 - CLAMP
CL = SR_SPAN + 12.0
c = Box(22, CL, 13, align=(Align.CENTER, Align.CENTER, Align.MIN))
c = fillet(c.edges().filter_by(Axis.Z), 3.0)
c -= Rot(0, 90, 0) * Cylinder(CABLE_D/2 + 0.4, 60)
for sy in (-1, 1):
    c -= Pos(0, sy*SR_SPAN/2) * Cylinder(4.5/2, 40)
    c -= Pos(0, sy*SR_SPAN/2, 13-2.6) * Cone(8.4/2, 4.5/2, 2.6,
                                             align=(Align.CENTER, Align.CENTER, Align.MIN))
export_step(c, "cad/out/lp24_clamp_revC.stp")
bb = c.bounding_box()
print(f"CLAMP  vol={c.volume/1000:6.1f} cm3 solids={len(c.solids())} "
      f"bbox={bb.size.X:.0f}x{bb.size.Y:.0f}x{bb.size.Z:.0f}")
print(f"       screw span {SR_SPAN:.0f} mm, straddling the {OPEN_W:.0f} mm opening")
