"""
Heatsink Shroud  (rev B)  -- with 5015 blower mount
===================================================
Covers the alloy heat plate and its external fins, carries the blower, and
keeps salt spray off the aluminium.

AIRFLOW: the 5015 is a BLOWER, not an axial fan - it pressurises. Mounted at
one end with its inlet on the sheltered underside, it drives air ALONG the
fin channels and out louvred slots at the far end. That is a plenum, not
general stirring, and it is why a blower suits this better than an axial fan.

FAN FIXING: the WINSINN drawing gives 2-O4.3 but its datum is ambiguous, so
the mounts are SLOTS. They swallow the real pattern whichever way it reads.

WIRE ROUTE: fan wires go to the Pi. The sealed penetration belongs in the
6 mm ALLOY PLATE - a grommet in metal beats a hole in ASA, and it sits under
the shroud where spray cannot reach it. The shroud only guides the wires.

Material : ASA (blue)   Orientation : OUTER FACE ON THE BED, walls up
Supports : none - slots vertical, awnings 45 deg
"""
from build123d import *

PLATE = 114.0
OW, OH, OD = 134.0, 134.0, 52.0   # 3 wall + 27 fan + 20 fins = 50, 2 mm plenum
WALL, R_OUT = 3.0, 6.0
# Pads must reach the walls to fuse, but their HOLES must land well inside the
# 114 plate. So the pad is a gusset from the wall inward, hole at 48.
MOUNT_D, HOLE_C = 3.4, 48.0

# Noctua NF-F12 iPPC-2000 IP67 PWM: 120 x 120 x 25, 105 mm hole pitch.
# IP67 matters - it is the only moving part and it lives in salt air.
FAN_W, FAN_T, FAN_PITCH, FAN_BORE = 120.0, 25.0, 105.0, 114.0
FAN_PILOT = 3.6                    # M4 thread-forming into ASA
WIRE_D = 7.0

s = extrude(Plane.XY * RectangleRounded(OW, OH, R_OUT), amount=OD)
s -= extrude(Plane.XY.offset(WALL) * RectangleRounded(OW - 2*WALL, OH - 2*WALL, R_OUT - WALL),
             amount=OD)

# ── 80 mm axial fan on the outer face, blowing onto the fins ──────────────
# The fan sits INSIDE the shroud so nothing ugly or corrodible is exposed.
# It draws through a ring of slots, each shielded by a 45 deg awning, and
# pushes down the fin channels to the louvres.
s -= Pos(0, 0, WALL/2) * Cylinder(FAN_BORE/2, 3*WALL,
                                  align=(Align.CENTER, Align.CENTER, Align.CENTER))
for sx in (-1, 1):
    for sy in (-1, 1):
        s += Pos(sx*FAN_PITCH/2, sy*FAN_PITCH/2, WALL) * Cylinder(
            8.0, 5.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        s -= Pos(sx*FAN_PITCH/2, sy*FAN_PITCH/2, WALL) * Cylinder(
            FAN_PILOT/2, 5.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
# The O76 bore IS the intake - a separate slot ring at r=46 fouls the boss
# ring at r=50.6 at any angle. Cross spokes keep fingers and debris out.
import math as _m
for i in range(4):
    s += Pos(0, 0, WALL/2) * Rot(0, 0, 45 + 90*i) * Box(
        FAN_BORE, 5.0, WALL, align=(Align.CENTER,)*3)
s += Pos(0, 0, WALL/2) * Cylinder(9.0, WALL, align=(Align.CENTER,)*3)

# ── exhaust louvres at the +x end and both flanks ─────────────────────────
for i in range(4):
    z = 10 + i*9
    s -= Pos(OW/2, 0, z) * Box(3*WALL, 76.0, 4.5, align=(Align.CENTER,)*3)
    s += Pos(OW/2 - 2.6, 0, z + 4.2) * Rot(0, 45, 0) * Box(
        9.0, 76.0, 3.0, align=(Align.CENTER,)*3)
for sx in (-1, 1):
    for i in range(3):
        z = 12 + i*10
        s -= Pos(sx*OW/2, 34.0, z) * Box(3*WALL, 40.0, 4.5, align=(Align.CENTER,)*3)
        s += Pos(sx*(OW/2 - 2.6), 34.0, z + 4.2) * Rot(0, 45, 0) * Box(
            9.0, 40.0, 3.0, align=(Align.CENTER,)*3)

# ── fan wire pass-through, into the housing via the plate grommet ─────────
s -= Pos(52.0, 52.0, WALL/2) * Cylinder(WIRE_D/2, 3*WALL,
                                                align=(Align.CENTER, Align.CENTER, Align.CENTER))

# ── mounting pads at the open edge -> tapped holes in the alloy plate ─────
PAD_C = OW/2 - 14.0
for sx in (-1, 1):
    for sy in (-1, 1):
        s += Pos(sx*PAD_C, sy*PAD_C, OD - 4.5) * Box(
            32.0, 32.0, 4.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
for sx in (-1, 1):
    for sy in (-1, 1):
        s -= Pos(sx*HOLE_C, sy*HOLE_C, OD - 6.0) * Cylinder(
            MOUNT_D/2, 9.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

export_step(s, "cad/out/heatsink_shroud_revD.stp")
bb = s.bounding_box()
print(f"SHROUD vol={s.volume/1000:6.1f} cm3 solids={len(s.solids())} "
      f"bbox={bb.size.X:.0f}x{bb.size.Y:.0f}x{bb.size.Z:.0f}")
print(f"       covers the {PLATE:.0f} sq plate with {(OW-PLATE)/2:.0f} mm margin")
print(f"       NF-F12 120 mm: O{FAN_BORE} bore, 4 x O{FAN_PILOT} at {FAN_PITCH} pitch")
print(f"       wire pass-through O{WIRE_D}")
print(f"       4 fixings at +/-{HOLE_C:.0f}, {PLATE/2-HOLE_C:.0f} mm inside the plate edge")
