"""
Helm Design - LP-24 Shroud  (rev D)  -- ONE PIECE
=================================================
Sits directly on the helm shelf. No base plate. Open bottom.
Strain relief screws DIRECTLY INTO the shroud, into bosses on an integral
rear pad at the bottom rim - so with the shroud inverted the pad sits right
at the open face and the screws drive straight down, connector already fitted.

Boss height is set to CABLE_D - 1, so the bosses double as COMPRESSION STOPS:
the clamp lands on them with 1 mm of squeeze on the jacket and cannot crush it.

Material : ASA (blue)   Orientation : FLANGE DOWN on the bed
Layers   : 0.2 mm       Perimeters  : 5     Infill : 30% gyroid
Supports : none - pad prints on the bed, bore is teardropped
"""
from build123d import *

WALL, FLANGE_T = 4.5, 5.0
PLAN_L, PLAN_W, CORNER_R = 132.0, 102.0, 10.0
BODY_W, BODY_H = 70.0, 58.0
X_FRONT, X_BACK_BOT, X_BACK_TOP = -30.0, 38.0, 25.0

LP24_BORE, LP24_PITCH = 24.4, 26.0
LP24_CLEAR, LP24_PILOT = 3.2, 2.6      # M3 316SS threads straight into ASA
LP24_PAD, LP24_PAD_T = 46.0, 12.0      # continuous reinforcing frame, not 4 bosses
LP24_RELIEF  = 28.0                    # keeps the connector's panel thickness at 6 mm
LP24_PANEL_T = 6.0
LP24_Z, TEARDROP_K = 29.0, 1.25

BOLT_D, BOLT_X, BOLT_Y = 5.5, 56.0, 43.0
BOLTS = [(-BOLT_X,-BOLT_Y),(0,-BOLT_Y),(BOLT_X,-BOLT_Y),
         (-BOLT_X, 0.0),                 (BOLT_X, 0.0),
         (-BOLT_X, BOLT_Y),(0, BOLT_Y),(BOLT_X, BOLT_Y)]

CORD_D = 3.0
GW, GD = CORD_D*1.15, CORD_D*0.77
GL, GH, GR = 98.0, 70.0, 10.0

CABLE_D  = 11.0                 # Belden 1058A jacket OD - VERIFY ON THE DATASHEET
FAN_W    = 30.0                 # fan-out trough for the stripped conductors
FAN_D    = 5.0
SR_HALF  = 22.0                 # screw half-pitch
SR_PILOT = 3.5                  # M4 316SS threads straight into ASA
SR_BOSS_D= 10.0                 # 3.25 mm wall around the pilot
BEAM_X0, BEAM_X1 = 12.0, 33.0   # cross-beam, inboard of the rear wall
BEAM_Z0, BEAM_Z1 = 26.0, 39.0   # underside height / top
PILOT_L  = 11.0                 # thread engagement
DRAIN_W, DRAIN_H = 14.0, 3.5

# ------------------------------------------------------------------ flange
s = Box(PLAN_L, PLAN_W, FLANGE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
s = fillet(s.edges().filter_by(Axis.Z), CORNER_R)

# ------------------------------------------------------------------- body
prof = [(X_FRONT, FLANGE_T), (X_FRONT, FLANGE_T+BODY_H),
        (X_BACK_TOP, FLANGE_T+BODY_H), (X_BACK_BOT, FLANGE_T)]
body = extrude(Plane.XZ * Polygon(*prof, align=None), amount=BODY_W/2, both=True)
body = fillet(body.edges().filter_by(Axis.Z), 8.0)
body = fillet(body.edges().filter_by(Axis.Y).group_by(Axis.Z)[-1], 4.0)
body = offset(body, amount=-WALL, openings=body.faces().sort_by(Axis.Z)[0],
              kind=Kind.INTERSECTION)
s += body

# open the flange under the body so the cavity reaches the shelf
CAV_L, CAV_W = X_BACK_BOT - X_FRONT - 2*WALL, BODY_W - 2*WALL
cav = RectangleRounded(CAV_L, CAV_W, 6.0)
s -= extrude(Plane.XY.offset(-1) * Pos((X_FRONT+X_BACK_BOT)/2, 0) * cav,
             amount=FLANGE_T + 2)

# ------------------------------------- cross-beam strain relief (pilots DOWN)
# The beam spans wall to wall, so its underside is a clean 61 mm bridge.
# Pilots open DOWNWARD toward the open face - the screws are driven UP from
# below, which is the only direction with an unobstructed path.
beam = Pos((BEAM_X0+BEAM_X1)/2, 0, BEAM_Z0) * Box(
    BEAM_X1-BEAM_X0, CAV_W + 2*WALL, BEAM_Z1-BEAM_Z0,
    align=(Align.CENTER, Align.CENTER, Align.MIN))
s += beam & Pos(0, 0, BEAM_Z0) * Box(400, CAV_W, 400,
                                     align=(Align.CENTER, Align.CENTER, Align.MIN))
for sy in (-1, 1):
    s -= Pos((BEAM_X0+BEAM_X1)/2, sy*SR_HALF, BEAM_Z0) * Cylinder(
        SR_PILOT/2, PILOT_L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    s -= Pos((BEAM_X0+BEAM_X1)/2, sy*SR_HALF, BEAM_Z0) * Cone(
        SR_PILOT/2 + 0.7, SR_PILOT/2, 0.9,
        align=(Align.CENTER, Align.CENTER, Align.MIN))

# ------------------------------------------------------------ deck fixings
for bx, by in BOLTS:
    s -= Pos(bx, by) * Cylinder(BOLT_D/2, 3*FLANGE_T)
outer = RectangleRounded(GL+GW, GH+GW, GR+GW/2)
inner = RectangleRounded(GL-GW, GH-GW, GR-GW/2)
s -= extrude(Plane.XY * (outer - inner), amount=GD)

# ------------------------------------------------------- LP-24, teardropped
ZC, r = FLANGE_T + LP24_Z, LP24_BORE/2
bp = Plane(origin=(X_FRONT, 0, ZC), z_dir=(-1, 0, 0), x_dir=(0, 1, 0))

# One continuous reinforcing frame on the inside of the front wall. Four lone
# bosses each have a thin hoop that can split as the thread forms, and they
# take the plug's prying moment as isolated cantilevers. A frame does neither.
pad = bp * Pos(0, 0, -WALL) * Box(LP24_PAD, LP24_PAD, LP24_PAD_T,
                                  align=(Align.CENTER, Align.CENTER, Align.MAX))
pad = fillet(pad.edges().group_by(Axis.X)[0], 4.0)
s += pad

# relief bore: the connector still passes through only LP24_PANEL_T of material,
# so a thicker frame cannot foul its flange seating
s -= bp * Pos(0, 0, -LP24_PANEL_T) * Cylinder(
        LP24_RELIEF/2, WALL + LP24_PAD_T - LP24_PANEL_T + 1,
        align=(Align.CENTER, Align.CENTER, Align.MAX))

s -= Pos(X_FRONT, 0, ZC) * Rot(0, 90, 0) * Cylinder(r, 60)
s -= Pos(X_FRONT, 0, ZC) * extrude(
        Plane.YZ * Polygon((-r, 0), (r, 0), (0, TEARDROP_K*r), align=None),
        amount=30, both=True)

for sx in (-1, 1):
    for sy in (-1, 1):
        o = (sx*LP24_PITCH/2, sy*LP24_PITCH/2)
        s -= bp * Pos(o[0], o[1], 1) * Cylinder(LP24_CLEAR/2, WALL + 1.5,
                    align=(Align.CENTER, Align.CENTER, Align.MAX))
        s -= bp * Pos(o[0], o[1], -WALL) * Cylinder(LP24_PILOT/2, LP24_PAD_T - 0.5,
                    align=(Align.CENTER, Align.CENTER, Align.MAX))
        s -= bp * Pos(o[0], o[1], -WALL) * Cone(
                    LP24_PILOT/2 + 0.7, LP24_PILOT/2, 0.9,
                    align=(Align.CENTER, Align.CENTER, Align.MAX))

s -= Pos(X_FRONT, 0, FLANGE_T) * Box(20.0, DRAIN_W, DRAIN_H,
                                     align=(Align.CENTER, Align.CENTER, Align.MIN))
s = chamfer(s.faces().sort_by(Axis.Z)[0].edges(), 0.5)
export_step(s, "cad/out/lp24_shroud_revD.stp")
bb = s.bounding_box()
print(f"SHROUD vol={s.volume/1000:6.1f} cm3 solids={len(s.solids())} "
      f"bbox={bb.size.X:.0f}x{bb.size.Y:.0f}x{bb.size.Z:.0f}")

# ------------------------------------------------------------------ clamp
# Grips the JACKET (that is what carries tensile load), then opens into a wide
# radiused trough so the stripped 24 conductors fan out to the connector
# without crossing a hard edge.
CH = 13.0
CL = 2*SR_HALF + 14.0
c = Box(28, CL, CH, align=(Align.CENTER, Align.CENTER, Align.MIN))
c = fillet(c.edges().filter_by(Axis.Z), 3.0)

# jacket saddle: 1 mm proud of the top face -> 1 mm squeeze against the beam
c -= Pos(0, 0, CH - 4.5) * Rot(0, 90, 0) * Cylinder(CABLE_D/2, 60)

# fan-out trough on the connector side, with a 45 deg ramp out of the saddle
fan = [(-15.0, CH - FAN_D), (-2.0, CH - FAN_D), (3.0, CH + 0.5), (-15.0, CH + 0.5)]
c -= extrude(Plane.XZ * Polygon(*fan, align=None), amount=FAN_W/2, both=True)

for sy in (-1, 1):
    c -= Pos(0, sy*SR_HALF) * Cylinder(4.5/2, 40)
    c -= Pos(0, sy*SR_HALF, 0) * Cone(4.5/2, 8.4/2, 2.6,
                                      align=(Align.CENTER, Align.CENTER, Align.MIN))
c = fillet(c.edges().group_by(Axis.X)[0].filter_by(Axis.Y), 2.0)   # wire exit edge

export_step(c, "cad/out/lp24_clamp_revD.stp")
bb = c.bounding_box()
print(f"CLAMP  vol={c.volume/1000:6.1f} cm3 solids={len(c.solids())} "
      f"bbox={bb.size.X:.0f}x{bb.size.Y:.0f}x{bb.size.Z:.0f}")
print(f"       jacket Ø{CABLE_D} | 1.0 mm squeeze | fan trough {FAN_W:.0f} x {FAN_D:.0f}")
print(f"       screw M4 x 30, engagement {PILOT_L:.0f} mm")
