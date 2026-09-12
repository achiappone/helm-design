"""
Heatsink Shroud  (rev E)  -- 120 mm AXIAL fan
==============================================
Covers the alloy heat plate and its external fins, carries the fan, and keeps
salt spray off the aluminium.

THE DOCSTRING USED TO DESCRIBE A DIFFERENT PART. Through revs B, C and D it
argued for a 5015 BLOWER - "it pressurises... that is a plenum, not general
stirring, and it is why a blower suits this better than an axial fan" - while
the code below built a 120 mm axial mount with a O114 bore and a 105 pitch.
It also described the fan fixings as SLOTS swallowing an ambiguous WINSINN
drawing; they are four round O3.6 pilots on Noctua's dimensioned 105 pattern.
None of that was true of the part it was attached to.

AIRFLOW, as actually built: the axial fan sits INSIDE the shroud and blows down
onto the fins across the full O114 bore. Air leaves through louvred slots at the
+x end and both flanks, each shielded by a 45 deg awning. The fan is not exposed
to direct spray or sun - the shroud is what protects it, not its own IP rating.

DEPTH IS DERIVED FROM THE FAN. OD is not a typed number any more, it is
WALL + FAN_T + HS_H + PLENUM, so swapping the fan re-derives the shroud instead
of leaving a hardcoded 52 that used to be right. That matters because the
obvious upgrade here is thickness: the NF-F12 is 25 mm (27 over the pads) and
dominates how far this whole assembly stands off the dash. A 15 mm slim 120 -
NF-A12x15, SilverStone FN123 - takes the shroud from 52 to 42.

ON IP RATINGS. The slim 120s do not carry one; the IP67 120s are all 25 or 38
thick. Since the shroud already shelters the fan from direct water, the rating
buys less here than the 10 mm costs. Salt-laden AIR reaches the windings either
way - IP67 does not stop that - so conformal-coating a slim fan is the better
trade than carrying 10 mm for a seal that is already redundant.

WIRE ROUTE: fan wires go to the Pi. The sealed penetration belongs in the
6 mm ALLOY PLATE - a grommet in metal beats a hole in ASA, and it sits under
the shroud where spray cannot reach it. The shroud only guides the wires.

Material : ASA (blue)   Orientation : OUTER FACE ON THE BED, walls up
Supports : none - slots vertical, awnings 45 deg
"""
from build123d import *

import json
H = json.load(open("cad/out/housing.json"))
PLATE = H["HS_PLATE"]
HS_H = H["HS_H"]                  # fin height, from the model - not retyped
WALL, R_OUT = 3.0, 6.0
PLENUM = 2.0                      # air gap between fan face and fin tops
# Pads must reach the walls to fuse, but their HOLES must land well inside the
# 114 plate. So the pad is a gusset from the wall inward, hole at 48.
MOUNT_D, HOLE_C = 3.4, 48.0

# THE FAN. Change FAN_T and the shroud re-derives around it.
#   NF-F12 iPPC-2000 IP67 PWM   120 x 120 x 25   (27 over the corner pads)
#   NF-A12x15 / SilverStone FN123   120 x 120 x 15, no IP rating
# 27, not 25: the sheet says 25 but the moulded corner pads stand proud, and it
# is the pads the shroud has to clear.
FAN_W, FAN_T, FAN_PITCH, FAN_BORE = 120.0, 27.0, 105.0, 114.0
OW = OH = FAN_W + 2*WALL + 8.0    # fan, walls, and room for the fixing pads
OD = WALL + FAN_T + HS_H + PLENUM
assert OW > PLATE, f"shroud {OW:.0f} does not cover the {PLATE:.0f} plate"
assert FAN_BORE <= FAN_W, "intake bore is wider than the fan"
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

# ── 316 SS mesh intake filter ────────────────────────────────────────────
# The shroud stops direct spray, but the fan still breathes salt-laden air and
# lays it down on the aluminium fins. A filter is the only thing that addresses
# that - an IP rating on the fan does not, because the air path IS the point.
#
# MESH, NOT FOAM, and the first pass here was foam. Three reasons it lost:
#   - Open-cell foam in salt air becomes a salt sponge. It holds moisture
#     against the print and the fins between rinses, which is worse than the
#     unfiltered air it was fitted to stop. Woven mesh sheds and dries.
#   - Foam is consumable: UV and salt rot it, so it is a part you re-buy.
#     316 mesh outlives the boat and rinses clean under a tap.
#   - DEPTH. A 5 mm foam disc needs a 5 mm rim standing proud of the outer
#     face, which pushed this shroud from 52 to 57 - the wrong direction on a
#     part whose thickness is the thing being argued about. Mesh is 0.6 thick
#     and needs 3.
# What foam would buy is finer aerosol capture. Not worth a salt poultice.
#
# Retention: a groove in the rim bore. Cut the disc ~3 mm over the rim ID, bow
# it slightly, and it springs into the groove - the standard way wire mesh is
# held, no hardware and no second printed part. The spoke cross behind it stops
# it being sucked through if it ever loads up. Drain notches through the base
# of the rim stop the tray holding standing water against the mesh.
FILT_T = 3.0                       # rim height off the outer face
FILT_MESH = 0.6                    # 316 woven mesh, ~20-40 mesh
FILT_ID = FAN_BORE + 8.0           # rim bore; cut the disc ~3 mm over this
FILT_RIM = 2.5
FILT_GRV = 0.9                     # groove depth, radially, for the mesh edge
FILT_DRAIN = 6.0
assert FILT_ID/2 + FILT_RIM < OW/2 - 1.0, (
    f"filter rim reaches {FILT_ID/2 + FILT_RIM:.1f}, past the {OW/2:.1f} shroud edge")
assert FILT_GRV < FILT_RIM - 1.0, "groove would leave the rim wall too thin to hold"
s += Pos(0, 0, -FILT_T) * Cylinder(
    FILT_ID/2 + FILT_RIM, FILT_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
s -= Pos(0, 0, -FILT_T - 1) * Cylinder(
    FILT_ID/2, FILT_T + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
# retaining groove, set back from the lip so the mesh sits below flush
s -= Pos(0, 0, -FILT_T + 0.8) * Cylinder(
    FILT_ID/2 + FILT_GRV, FILT_MESH + 0.4, align=(Align.CENTER, Align.CENTER, Align.MIN))
for i in range(4):
    s -= (Pos(0, 0, -FILT_T) * Rot(0, 0, 45 + 90*i)
          * Box(2*(FILT_ID/2 + FILT_RIM + 2), FILT_DRAIN, 1.6,
                align=(Align.CENTER, Align.CENTER, Align.MIN)))

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
print(f"       316 mesh filter: rim O{FILT_ID + 2*FILT_RIM:.0f} x {FILT_T:.0f} proud, "
      f"cut the disc O{FILT_ID + 3:.0f}, springs into a {FILT_GRV} groove; 4 drains")
print(f"       depth {OD:.0f} = {WALL:.0f} wall + {FAN_T:.0f} fan + "
      f"{HS_H:.0f} fins + {PLENUM:.0f} plenum; a 15 mm fan gives "
      f"{WALL + 15.0 + HS_H + PLENUM:.0f}")
print(f"       4 fixings at +/-{HOLE_C:.0f}, {PLATE/2-HOLE_C:.0f} mm inside the plate edge")
