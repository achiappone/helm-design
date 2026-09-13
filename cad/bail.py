"""
Dash Bail Mount  (rev A)  -- BASE PLATE + TWO ARMS
===================================================
Arms pivot on TRUNNIONS GROWN FROM THE REAR COVER (see helm_housing.py).
Replaces cad/tilt_bracket.py, which hinged the unit on ears BELOW its bottom
edge. That put the assembled CG 114.7 mm above the tilt axis and made the whole
unit a pendulum on it - 12.4 N*m at 6g, which no friction joint holds and which
is why that design needed a detent crown.

This is the Simrad GO-series arrangement: two arms rising either side of the
unit, pivoting at MID-HEIGHT, clamped by hand. The axis passes 1.4 mm from the
CG, so the moment falls to 0.15 N*m and friction wins comfortably - the
reduction is bought with geometry, not with hardware.

THREE PARTS, NOT A U. Not for bed size any more - at 334 wide a one-piece U
would fit a 350 bed - but for orientation: the base lies on the dash and the
arms stand up from it, and a single part cannot have both flat on the bed. Split
at the arm feet, the base prints flat and each arm prints blade-flat, so every
load-carrying section is in-plane and nothing is in cross-layer bending.
THE RISE IS SET BY THE TILT SWING. The base is BELOW the unit, so what tilt has
to clear is the dash under the unit's lowest corner - the shroud's, the bumps'
and the cover's, whichever swings lowest - and the axis sits that high plus a
margin. The arms are vertical: leaning them buys nothing here and puts a
bending moment into every foot bolt.
Material : ASA (blue)   Orientation : BASE FLAT / ARMS FLAT, both on the bed
Supports : none - the arm blade is in plane, the eye is a through boss
"""
from build123d import *
import json, math

H = json.load(open("cad/out/housing.json"))
# THE REAR OF THE UNIT IS NOT THE COVER. The fan shroud stands 40 mm proud of
# it, so the thing that has to clear the dash when this tilts is 68 mm back, not
# 28. The sweep below was solved against the cover face and came out with a
# standoff that would have driven the shroud into the dash at full tilt.
# heatsink_shroud.py publishes what it actually reaches; run it first.
SH = json.load(open("cad/out/shroud.json"))
OUT_W, OUT_H, DEPTH = H["OUT_W"], H["OUT_H"], H["DEPTH"]
TILT_Y = H["TILT_Y"]
# FRIC_R0/R1 are the VISOR's friction land, not this joint's - the trunnion
# land is TRUN_R. Only the shim thickness is shared, and the eye is sized from
# the trunnion it actually runs on.
FRIC_SHIM = H["FRIC_SHIM"]
TRUN_X, TRUN_LAND, TRUN_STAND = H["TRUN_X"], H["TRUN_LAND"], H["TRUN_STAND"]
BACK = DEPTH + H["GASKET_C"] + H["COVER_T"]
REAR = BACK + SH["REAR_PROUD"]      # the shroud's outer face - the real rear

# ---- where the arm's inner face has to sit -------------------------------
# THE PIVOT IS THE COVER'S TRUNNION, not a boss on the shell wall. This file
# was written against PIV2_PROUD - the shell side boss - and kept reading it
# after that boss was deleted, because housing.json kept exporting the number.
# The arm was therefore built for a pivot 32 mm in front of the real one and
# could not be assembled at all.
#
# The trunnion land is at x = TRUN_X + TRUN_LAND on the cover, the shim sits on
# it, and the arm's inner face lands on the shim. Its axis is TRUN_STAND behind
# the cover's rear face - BEHIND the unit, which is what keeps the bracket
# inside the bezel width.
AXIS_Z = BACK + TRUN_STAND
ARM_FACE = TRUN_X + TRUN_LAND + FRIC_SHIM
ARM_T = 7.0                         # 8 put the outer face 1 mm past the bezel
# The eye is a disc centred on the axis, so it reaches EYE_R IN FRONT of the
# axis as well as behind it. The axis is TRUN_STAND behind the cover's outer
# face, so an eye bigger than that eats into the cover: at r17 on a 15 mm stand
# it was 2 mm inside the cover plate at each side, ~7000 mm3 of arm inside the
# housing. Sized against the stand, and asserted below.
EYE_R = H["TRUN_R"] + 3.0           # rim round the r13 trunnion land
assert EYE_R < TRUN_STAND, (
    f"eye r{EYE_R:.0f} on a {TRUN_STAND:.0f} mm trunnion stand reaches "
    f"{EYE_R - TRUN_STAND:.1f} mm into the rear cover")
BOLT_D = 5.4                        # M5 316 clearance; thread is the cover's insert
assert ARM_FACE + ARM_T <= OUT_W/2 + 0.01, (
    f"arm outer face at {ARM_FACE + ARM_T:.1f} is past the bezel edge at {OUT_W/2:.1f}")

# ---- how high the axis has to sit, and how far the arms lean -------------
# THIS WAS SOLVING THE WRONG GEOMETRY. The base plate lies FLAT ON THE DASH
# BELOW the unit - the arms rise from it and the unit hangs between them, which
# is what a Simrad bail is - but the standoff was computed as if the dash were a
# vertical bulkhead BEHIND the unit, from "rear sweep". It then reported a
# horizontal offset as a height off the dash, and sized the arms' lean with a
# clearance calculation that belonged to the rise.
#
# The real constraint: tilt swings the unit's corners DOWN toward the dash. For
# a corner at (dy, dz) from the axis, rotating by theta puts it at
#     dy' = dy*cos(theta) - dz*sin(theta)
# and the axis must sit high enough that dy' never reaches the dash.
TILT_MAX = 20.0
BASE_T_MIN = 8.0
DASH_CLEAR = 10.0                   # air under the lowest corner at full tilt

def _drop(deg):
    """How far below the axis the lowest corner of the REAL envelope reaches at
    this tilt - the cover, the bay bumps and the fan shroud, not just the box."""
    worst = 0.0
    corners = [(OUT_H/2, 0.0), (-OUT_H/2, 0.0),            # front face
               (OUT_H/2, BACK), (-OUT_H/2, BACK),          # cover
               (OUT_H/2, BACK + H["PI_BUMP_H"]), (-OUT_H/2, BACK + H["PI_BUMP_H"]),
               (SH["OH"]/2, REAR), (-SH["OH"]/2, REAR)]    # shroud
    for cy, cz in corners:
        dy, dz = cy - TILT_Y, cz - AXIS_Z
        for t in (-deg, 0.0, deg):
            r = math.radians(t)
            worst = max(worst, -(dy*math.cos(r) - dz*math.sin(r)))
    return worst

RISE = _drop(TILT_MAX) + DASH_CLEAR
# and the eye has to clear the plate it is bolted to, whatever the swing says
RISE = max(RISE, EYE_R + BASE_T_MIN + 6.0)
assert RISE < 190.0, (
    f"the axis would sit {RISE:.0f} mm above the dash for {TILT_MAX:.0f} deg of "
    f"tilt - that is a tall bracket, cut the tilt range")

# THE LEAN IS ZERO. The arms are vertical. Leaning them puts the base plate
# behind the unit instead of under it, adds a bending moment at every foot bolt,
# and buys nothing: the clearance that matters is the height, solved above. The
# previous 59 mm of lean came out of the rear-sweep calculation that should not
# have existed.
STANDOFF = 0.0

# ---- base plate ----------------------------------------------------------
# 2*ARM_FACE - 2*ARM_T was 306 and put the foot bolts 14 mm inboard of each
# arm at every corner - the arms never touched the plate they are bolted to, and
# their four bolts were drilled through bare plastic beside them. The plate has
# to reach the ARM CENTRELINE, which is ARM_FACE + ARM_T/2.
BASE_L, BASE_W, BASE_T = 2*(ARM_FACE + ARM_T/2), 96.0, BASE_T_MIN
BASE_R = 10.0
DASH_D, DASH_SLOT = 5.5, 10.0       # 6 dash screws, slotted fore-and-aft
DASH_X = [-BASE_L/2 + 26.0, 0.0, BASE_L/2 - 26.0]
DASH_ROWS = 68.0                    # apart, so the rows take the peel moment
assert BASE_L <= 345.0, f"base plate {BASE_L:.0f} does not print on a 350 bed"

b = extrude(Plane.XY * RectangleRounded(BASE_L, BASE_W, BASE_R), amount=BASE_T)
for sx in DASH_X:
    for sy in (-DASH_ROWS/2, DASH_ROWS/2):
        b -= Pos(sx, sy, -1) * Box(DASH_D, DASH_SLOT, BASE_T + 2,
                                   align=(Align.CENTER, Align.CENTER, Align.MIN))
        for e in (-1, 1):
            b -= Pos(sx, sy + e*DASH_SLOT/2, -1) * Cylinder(
                DASH_D/2, BASE_T + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
# arm feet bolt down at the ends, two each
# The arm foot straddles the base's short edge, so its two bolts run fore-and-
# aft along y. Same pair spacing the arm uses - both read FOOT_BOLT_X.
FOOT_BOLT_X = 17.0
FOOT_X = BASE_L/2 - ARM_T/2
for sx in (-1, 1):
    for sy in (-1, 1):
        b -= Pos(sx*FOOT_X, sy*FOOT_BOLT_X, -1) * Cylinder(
            BOLT_D/2, BASE_T + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
assert len(b.solids()) == 1, f"base is {len(b.solids())} solids, not 1"
export_step(b, "cad/out/bail_base_revA.stp")

# ---- arm -----------------------------------------------------------------
# Drawn flat in its own XZ plane: foot at the origin, eye at (STANDOFF, rise).
# It prints lying on this face, so every load-carrying section is in-plane and
# nothing is in cross-layer bending.
FOOT_L = 54.0
# THE BLADE CANNOT BE A SIMPLE TAPER. The arms run INSIDE the bezel width, which
# the owner asked for, so at x 160..167 they share the unit's own footprint -
# and the rear cover is 334 wide, i.e. it reaches x 167 too. A blade that widens
# steadily from eye to foot is therefore inside the cover for the whole lower
# half of the unit: 583 mm3 a side, at z 22..28, exactly where the plate is.
#
# So the blade stays NARROW - behind the cover, never in front of it - for as
# long as it is beside the unit, and only flares into its foot once it is below
# the unit's bottom edge.
HW_MID = AXIS_Z - BACK - 2.0        # keeps the blade 2 mm clear of the cover
Z_CLEAR = RISE - TILT_Y - OUT_H/2   # local height of the unit's bottom edge
assert Z_CLEAR > 12.0, (
    f"the unit's bottom edge is only {Z_CLEAR:.0f} mm up the arm - there is no "
    f"room below it to flare a foot")
assert HW_MID > EYE_R*0.55 + 2.0, (
    f"the trunnion stands {AXIS_Z - BACK:.0f} mm off the cover, which leaves a "
    f"{HW_MID:.0f} mm blade - too thin to carry the unit")
# The blade runs UP TO THE EYE'S CENTRE, not to its rim. Stopping at the rim
# leaves the two tangent, which is a zero-width contact: OCC fuses it into two
# solids that merely touch, and the arm is then a blade and a loose ring.
a = extrude(Plane.XZ * Polygon((-FOOT_L/2, 0), (FOOT_L/2, 0),
                               (HW_MID, Z_CLEAR),
                               (STANDOFF + EYE_R*0.55, RISE),
                               (STANDOFF - EYE_R*0.55, RISE),
                               (-HW_MID, Z_CLEAR),
                               align=None), amount=ARM_T)
a += Pos(STANDOFF, 0, RISE) * Rot(90, 0, 0) * Cylinder(
        EYE_R, ARM_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
# the pivot bore - the thread is a 316 insert in the SHELL, this is clearance
a -= Pos(STANDOFF, 0, RISE) * Rot(90, 0, 0) * Cylinder(
        BOLT_D/2, 3*ARM_T, align=(Align.CENTER, Align.CENTER, Align.CENTER))
# two bolts down through the foot into the base plate. They sit fore-and-aft of
# each other so the pair resists the arm rotating about its own foot, which is
# the load that actually arrives here - the unit's weight is a moment on the
# arm, not a shear.
# extrude(Plane.XZ, amount) runs in -Y, so the arm occupies y -ARM_T..0 and its
# centreline is at -ARM_T/2. The cut was at +ARM_T/2 - the whole thickness away -
# so the arm came out with NO FOOT HOLES and four bores in the air beside it.
# solids==1 passed, the bbox passed, and the part cannot be bolted down.
for sx in (-1, 1):
    a -= Pos(sx*FOOT_BOLT_X, -ARM_T/2, -1) * Cylinder(
        BOLT_D/2, BASE_T + 12, align=(Align.CENTER, Align.CENTER, Align.MIN))
_holes = len([f for f in a.faces() if f.geom_type == GeomType.CYLINDER])
assert _holes >= 3, f"arm has {_holes} cylindrical faces - the bores missed it again"
assert len(a.solids()) == 1, f"arm is {len(a.solids())} solids, not 1"
_ab = a.bounding_box()
assert abs(_ab.size.Y - ARM_T) < 1e-6, (
    f"arm is {_ab.size.Y:.1f} thick, not {ARM_T} - the eye and the blade are in "
    f"different Y bands and it has come out a Z-section")
export_step(a, "cad/out/bail_arm_revA.stp")

# ---- where the arms actually go, published so nothing re-derives it -------
# assembly.py used to build this transform itself, and it built it WITHOUT a
# mirror: the -x arm came out pointing inboard, 3114 mm3 inside the trunnion it
# is supposed to clamp. The recipe lives here now, next to the part, and the
# clash check below uses the same numbers the renders will.
def arm_plane(sx):
    """Plane that lands one arm with its INNER face on the trunnion shim at
    x = sx*ARM_FACE. The part's thickness always runs toward +x from the
    plane's origin, so the -x arm's origin is one thickness further out - it is
    not a mirror, and mirroring it about YZ (the obvious fix) throws it onto
    the other side of the unit. Without this the -x arm ran INBOARD from -160
    toward the middle and sat 3450 mm3 inside the housing."""
    ox = ARM_FACE if sx > 0 else -(ARM_FACE + ARM_T)
    return Plane(origin=(ox, TILT_Y - RISE, AXIS_Z + STANDOFF),
                 x_dir=(0, 0, -1), z_dir=(0, 1, 0))

def arm_at(sx):
    return arm_plane(sx) * a

# ---- can the arms be fitted to the unit at all? --------------------------
# The one check neither part had: intersect the placed arm with the housing.
_SHELL = import_step("cad/out/helm_shell_revC.stp")
_COVER = import_step("cad/out/helm_cover_revC.stp")
_UNIT = Compound([_SHELL, Pos(0, 0, BACK) * Rot(180, 0, 0) * _COVER])
for _sx in (-1, 1):
    _hit = arm_at(_sx) & _UNIT
    _v = 0.0 if _hit is None else _hit.volume
    # The trunnion LAND is what the arm clamps, so a touch there is correct;
    # anything with volume is the arm inside the housing.
    assert _v < 50.0, (
        f"the {'+' if _sx > 0 else '-'}x bail arm is {_v:.0f} mm3 inside the "
        f"housing - it cannot be assembled")
print(f"       arms clear the housing on both sides")

json.dump({"ARM_FACE": ARM_FACE, "ARM_T": ARM_T, "STANDOFF": STANDOFF,
           "RISE": RISE, "EYE_R": EYE_R, "AXIS_Z": AXIS_Z,
           "BASE_L": BASE_L, "BASE_W": BASE_W, "BASE_T": BASE_T,
           "N_DASH": 2*len(DASH_X), "DASH_D": DASH_D, "DASH_SLOT": DASH_SLOT,
           "DASH_ROWS": DASH_ROWS, "N_FOOT_BOLTS": 4, "BOLT_D": BOLT_D,
           "TILT_MAX": TILT_MAX, "FOOT_BOLT_X": FOOT_BOLT_X,
           "FACE_STANDOFF": AXIS_Z + STANDOFF,
           # the build page states this part's size, mass and why the standoff
           # is what it is; all three come from here, never typed into the page
           "DROP": _drop(TILT_MAX), "DASH_CLEAR": DASH_CLEAR, "REAR": REAR,
           "BASE_CM3": b.volume/1000.0, "ARM_CM3": a.volume/1000.0,
           "ARM_ORIGIN": {"pos": [ARM_FACE, TILT_Y - RISE, AXIS_Z + STANDOFF],
                          "neg": [-(ARM_FACE + ARM_T), TILT_Y - RISE, AXIS_Z + STANDOFF],
                          "x_dir": [0, 0, -1], "z_dir": [0, 1, 0]}},
          open("cad/out/bail.json", "w"), indent=1)
bb, ab = b.bounding_box(), a.bounding_box()
print(f"BAIL   base {bb.size.X:.0f}x{bb.size.Y:.0f}x{bb.size.Z:.0f}  "
      f"arm {ab.size.X:.0f}x{ab.size.Y:.0f}x{ab.size.Z:.0f}  (x2)")
print(f"       arm inner face x=+/-{ARM_FACE:.0f}, assembled width "
      f"{2*(ARM_FACE + ARM_T):.0f} - inside the {OUT_W:.0f} bezel, as asked")
print(f"       eye r{EYE_R:.0f} on the r{H['TRUN_R']:.0f} trunnion land, {FRIC_SHIM} mm 316 "
      f"serrated pair, M5 316 nyloc into the trunnion's insert")
print(f"       axis {RISE:.0f} mm above the dash, arms vertical; the unit's bottom "
      f"edge clears the dash by {RISE - TILT_Y - OUT_H/2:.0f} at rest and "
      f"{DASH_CLEAR:.0f} at {TILT_MAX:.0f} deg")
print(f"       whole thing stands {RISE + OUT_H/2 - TILT_Y:.0f} tall and "
      f"{SH['OH'] if SH['OH'] > OUT_H else OUT_H:.0f} wide on the dash")
# What the tilt range actually costs, so the trade is visible rather than argued.
print("       tilt   axis height   total height")
for _t in (10, 15, 20, 25):
    _r = max(_drop(_t) + DASH_CLEAR, EYE_R + BASE_T_MIN + 6.0)
    print(f"       {_t:3.0f}    {_r:8.0f}     {_r + OUT_H/2 - TILT_Y:8.0f}")
print(f"       6 dash slots O{DASH_D} x {DASH_SLOT}, rows {DASH_ROWS:.0f} apart")
