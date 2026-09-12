"""
Heatsink Gluing Jig  (rev A)  -- CONSUMABLE, not part of the unit
==================================================================
Two Easycargo 100 x 40 x 20 heatsinks bond to the alloy plate's outer face
with thermal adhesive. The plate is a flat, featureless piece of 6 mm
aluminium, so there is nothing on it to line the fins up against - you are
eyeballing two 100 mm blocks square to each other while the epoxy skins, and
whatever you end up with is what the shroud has to fit over.

This is a flat plate with two pockets in it. Drop it on the alloy plate,
located by the same four fixings the shroud uses, drop the heatsinks into the
pockets, and they are square and centred while the adhesive cures. Lift it off
afterwards.

WHY NOT RIBS IN THE SHROUD. The shroud covers the fins, so it looks like the
obvious place to put locating features. It is the wrong place twice over: ribs
inside it would sit in the fin channels the fan is trying to push air down,
and using the shroud as a curing fixture invites squeeze-out to bond the
shroud to the heatsinks - turning a serviceable cover into a permanent one.
A jig is cheap, does one job, and is thrown away if it gets glued to anything.

The pockets are THROUGH, so adhesive squeeze-out has somewhere to go rather
than pooling against a floor and lifting the part it is meant to be seating.

Material : anything - PLA is fine, it is a fixture, not a boat part
Orientation: flat on the bed         Supports : none
"""
from build123d import *
import json

H = json.load(open("cad/out/housing.json"))
PLATE = H["HS_PLATE"]
HS_L, HS_W, HS_CY, FIT = H["HS_L"], H["HS_W"], H["HS_CY"], H["HS_FIT"]
HOLE_C = H["HS_HOLE_C"]

T = 6.0                 # thick enough not to bow when you press a block into it
BOLT_D = 3.6            # clearance over the M3 that tap the plate
LEAD_IN = 1.2           # chamfer so a 100 mm block drops in instead of jamming

# Pocket is the heatsink plus FIT per side. FIT comes from housing.json because
# the shroud and the exploded view size themselves off the same numbers - a jig
# built to its own idea of where the heatsinks go would be worse than no jig.
POCK_L, POCK_W = HS_L + 2*FIT, HS_W + 2*FIT
assert HS_CY + POCK_W/2 + 4.0 < PLATE/2, (
    f"pocket wall reaches {HS_CY + POCK_W/2:.1f}, leaving under 4 mm to the "
    f"{PLATE} plate edge - the jig would be a pair of flexing fingers")
assert HOLE_C - BOLT_D/2 > HS_CY + POCK_W/2, (
    f"locating hole at {HOLE_C} lands inside the pocket at "
    f"{HS_CY + POCK_W/2:.1f} - it has to bear on solid jig, not on fresh air")

j = extrude(Plane.XY * RectangleRounded(PLATE, PLATE, 6.0), amount=T)

for sy in (-1, 1):
    pocket = Pos(0, sy*HS_CY, -1) * Box(
        POCK_L, POCK_W, T + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    j -= pocket
    # lead-in on the TOP face only: the bottom face has to stay flat on the
    # plate, and a chamfer there would let the heatsink slide under the jig.
    j -= Pos(0, sy*HS_CY, T - LEAD_IN) * Box(
        POCK_L + 2*LEAD_IN, POCK_W + 2*LEAD_IN, LEAD_IN + 1,
        align=(Align.CENTER, Align.CENTER, Align.MIN))

for sx in (-1, 1):
    for sy in (-1, 1):
        j -= Pos(sx*HOLE_C, sy*HOLE_C, -1) * Cylinder(
            BOLT_D/2, T + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))

# Something to grip, because a flat plate sitting in cured adhesive with 0.4 mm
# of clearance is genuinely hard to get off. The first attempt cut finger notches
# INTO the plate edges and split the jig into three pieces: the pockets reach
# within 6.6 mm of the edge, so a notch big enough for a finger goes straight
# through the strip that holds the ends on. Ears cost nothing and remove nothing.
EAR_L, EAR_W = 18.0, 26.0
for sx in (-1, 1):
    j += Pos(sx*(PLATE/2 + EAR_L/2 - 2.0), 0, 0) * Box(
        EAR_L + 4.0, EAR_W, T, align=(Align.CENTER, Align.CENTER, Align.MIN))

assert len(j.solids()) == 1, f"jig is {len(j.solids())} solids, not 1"
export_step(j, "cad/out/heatsink_jig_revA.stp")
bb = j.bounding_box()
print(f"JIG    vol={j.volume/1000:6.1f} cm3 solids={len(j.solids())} "
      f"bbox={bb.size.X:.0f}x{bb.size.Y:.0f}x{bb.size.Z:.0f}")
print(f"       2 pockets {POCK_L:.1f} x {POCK_W:.1f} at y +/-{HS_CY:.0f} "
      f"({FIT} clearance per side), {LEAD_IN} lead-in")
print(f"       locates on the 4 shroud fixings at +/-{HOLE_C:.0f}; pull-off ears at x +/-{PLATE/2 + EAR_L - 2:.0f}")
print(f"       plenum between the heatsinks: {2*HS_CY - HS_W:.0f} mm")
