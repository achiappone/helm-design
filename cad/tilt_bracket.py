"""
Dash Tilt Bracket  (rev C)
==========================
Flat plate that screws to the dashboard and carries the housing on the two
bottom detent pivots. Tilt back to read standing, forward when seated.

The plate is FLAT and the hinge sits above it, so the same bracket works on a
flat dash or a raked one - the detents absorb the difference. Slotted dash
holes give +/-4 mm of fore-and-aft adjustment on assembly.

Detent teeth are identical to the housing's, so they nest: 20 teeth = 18 deg
per click. Range is set by how far the housing can swing before its rear
corner meets the dash, which depends on your dash - see the note in the page.

Material : ASA (blue)   Orientation : PLATE FLAT ON THE BED, ears up
Layers   : 0.2 mm       Perimeters  : 5     Infill : 35% gyroid
Supports : none - ears are vertical, web is a 45 deg gusset
"""
from build123d import *
import json, math

H = json.load(open("cad/out/housing.json"))
BP_X, BP_T = H["BP_X"], H["BP_T"]

# Mating dimensions come from the housing, not from copies kept here.
# The shell's bottom upstands are centred at BP_X -/+ BP_T/2, so their INBOARD
# faces - the ones carrying the teeth - land exactly on BP_X. This part's teeth
# sit MESH_GAP inboard of that so the two crowns interleave rather than butt.
MESH_GAP = H["TOOTH_PROUD"] + 0.2   # crown height + running clearance
EAR_FACE = abs(BP_X[0]) - MESH_GAP
N_TEETH, TOOTH_H = H["N_TEETH"], H["TOOTH_H"]
R_T0, R_T1 = H["R_T0"], H["R_T1"]
EAR_R = H["BP_R"] + 1.5          # a touch proud of the shell's ear
EAR_T = 6.0                      # this part's own thickness, not a mating dim
BOLT_D = 5.4                     # M5 clearance - and so is the shell's now
assert R_T1 < EAR_R, "teeth would run off the edge of the ear"
# Neither ear threads any more: the shell carries a captive 316 nut and both
# holes are clearance. What still has to hold is that this one is not the
# tighter of the two, or the bolt binds here and the clamp reads as preload it
# is not actually delivering to the crown.
assert BOLT_D >= H["BP_BOLT"], "bracket bolt hole must not be tighter than the shell's"

PLATE_L, PLATE_W, PLATE_T = 276.0, 84.0, 5.5
PIVOT_ABOVE = 15.0               # pivot axis above the plate top
DASH_D, DASH_SLOT = 5.5, 8.0     # 4 dash screws, slotted fore-and-aft
# Mounted flat to the VERTICAL front face of the dash with the housing
# cantilevered off the top, the screw rows carry a peel moment. Spreading them
# 65 mm instead of 26 cuts the per-screw load 2.5x and stops the plate flexing
# between them. Costs nothing - the plate is already 84 long.
DASH_X, DASH_Z = 112.0, 80.0
DASH_Z2 = 15.0

def teeth(face_x, outward):
    out = None
    for i in range(N_TEETH):
        t = (Rot(360.0*i/N_TEETH, 0, 0)
             * Pos(face_x + outward*TOOTH_H*0.5, R_T0, 0)
             * Rot(0, 45, 0)
             * Box(TOOTH_H*1.5, R_T1 - R_T0, TOOTH_H*1.5,
                   align=(Align.CENTER, Align.MIN, Align.CENTER)))
        out = t if out is None else out + t
    return out

# ---- plate: pivot axis at the origin, plate below it -------------------
# Plate runs REARWARD from the pivot only - it lives under the housing where
# it is hidden. Extending it forward as well would put a lip in front of the
# display for no benefit.
b = Pos(0, -PIVOT_ABOVE - PLATE_T/2, PLATE_W/2 + 4.0) * Box(
        PLATE_L, PLATE_T, PLATE_W, align=(Align.CENTER,)*3)
b = fillet(b.edges().filter_by(Axis.Y), 8.0)

# ---- ears + gussets ----------------------------------------------------
for sx in (-1, 1):
    xc = sx * (EAR_FACE - EAR_T/2)
    ear = Pos(xc, 0, 0) * Rot(0, 90, 0) * Cylinder(EAR_R, EAR_T,
              align=(Align.CENTER, Align.CENTER, Align.CENTER))
    # web down to the plate, plus a 45 deg gusset so nothing is unsupported
    ear += Pos(xc, -PIVOT_ABOVE/2, 0) * Box(EAR_T, PIVOT_ABOVE, 2*EAR_R,
              align=(Align.CENTER,)*3)
    ear += Pos(xc, -PIVOT_ABOVE + 1, EAR_R) * Rot(0, 0, 0) * Box(
              EAR_T, 2.0, 2*EAR_R, align=(Align.CENTER,)*3)
    b += ear
    b += teeth(sx * EAR_FACE, sx)
    b -= Pos(xc, 0, 0) * Rot(0, 90, 0) * Cylinder(BOLT_D/2, 40)

# ---- dash fixings: slotted for fore-and-aft adjustment ------------------
for sx in (-1, 1):
    for zc in (DASH_Z2, DASH_Z):
        sz = 1
        b -= (Pos(sx*DASH_X, -PIVOT_ABOVE - PLATE_T/2, zc)
              * Box(DASH_D, 3*PLATE_T, DASH_SLOT, align=(Align.CENTER,)*3))
        # The end rounds go THROUGH the plate, so their axis is Y. Left on the
        # default Z axis they lie in the plane of the plate, and since their
        # radius is DASH_D/2 = PLATE_T/2 exactly, the cylinder ends up tangent
        # to both plate faces - a knife edge that is a valid solid but cannot
        # be meshed. That is what made this part fail 3MF export.
        for e in (-1, 1):
            b -= (Pos(sx*DASH_X, -PIVOT_ABOVE - PLATE_T/2, zc + e*DASH_SLOT/2)
                  * Rot(90, 0, 0) * Cylinder(DASH_D/2, 3*PLATE_T))

try:
    b = chamfer(b.faces().sort_by(Axis.Y)[0].edges(), 0.5)
except Exception:
    print("  ~ first-layer chamfer skipped (slotted face)")
export_step(b, "cad/out/tilt_bracket_revC.stp")
bb = b.bounding_box()
print(f"BRACKET vol={b.volume/1000:6.1f} cm3 solids={len(b.solids())} "
      f"bbox={bb.size.X:.0f}x{bb.size.Y:.0f}x{bb.size.Z:.0f}")
print(f"        ears at x +/-{EAR_FACE - EAR_T/2:.1f}, pivot {PIVOT_ABOVE:.0f} above the plate")
print(f"        4 dash slots O{DASH_D} x {DASH_SLOT} at x +/-{DASH_X:.0f}, z {DASH_Z2:.0f} and {DASH_Z:.0f}")
print(f"        {N_TEETH} teeth = {360/N_TEETH:.0f} deg per click")
print(f"        screw rows {DASH_Z - DASH_Z2:.0f} mm apart")
