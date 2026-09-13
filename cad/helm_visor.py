"""
Helm Display Visor  (rev C)  -- HINGED, HAND-ADJUSTABLE
=======================================================
Tilts by hand on a pair of detent pivots at the top of the housing.

WHY DETENT TEETH, NOT PLAIN FRICTION
A friction pivot in ASA decays: the plastic creeps under sustained clamp
load, and a boat vibrates continuously. Six months on it flops. Radial teeth
give a POSITIVE position that vibration cannot walk out of, and the wave
washer keeps preload as the plastic relaxes. Same idea as an MFD bail mount.

  16 teeth -> 22.5 deg per click, range +15 to -25 deg
  M5 x 30 316 SS through a captive 316 NYLOC in the shell upstand. Set by hand:
  firm enough to stay put, loose enough to click over the detent bare-handed.
  Tef-Gel the threads - 316 galls on 316, and the pocket is a crevice.

The leading edge turns down 8 mm. That is not styling: on two pivots the hood
is a 310 mm cantilever, and the lip turns a floppy flat plate into a channel.

Material : ASA (blue)   Orientation : HOOD UNDERSIDE ON THE BED, ears up - it lies flat now
"""
from build123d import *
import math, json

H = json.load(open("cad/out/housing.json"))
OUT_W, OUT_H = H["OUT_W"], H["OUT_H"]

# EVERY mating dimension comes from the housing. rev B kept its own copies and
# they drifted: this part had teeth at r5.0-9.5 against the shell's r4.5-8.2,
# so the crowns could never have nested, and its pivot axis was at y94/z12
# against the shell's y87.75/z9. Nothing here is allowed to be a literal.
PIV_X = H["PIV_X"]                 # inboard faces of the housing upstands
PIV_Y, PIV_Z = H["PIV_Y"], H["PIV_Z"]
# FRICTION now, not a detent - see the note at the top of the FRICTION PIVOTS
# block in cad/helm_housing.py. The crown is gone from both joints because the
# tilt axis moved to the CG and the moment it has to hold fell 80x, and at that
# level friction is the better joint: hand-set, no steps to land between, and it
# slips instead of stripping a crown.
FRIC_R0, FRIC_R1 = H["FRIC_R0"], H["FRIC_R1"]
FRIC_SHIM = H["FRIC_SHIM"]
R_EAR = H["R_EAR"]                 # match the shell's ear so the joint is flush
# The NUT LIVES HERE now. It used to be pocketed in the shell's upstand, but
# that upstand came down from 9.0 to 6.0 once it stopped carrying a crown, and a
# 5.3 deep nyloc pocket in 6.0 leaves 0.7 mm. This is a free part above the top
# wall with nothing near it and no bed constraint, so the hardware moves here
# and the shell keeps the slim pad. 10.0 houses the pocket with 4.7 behind it.
EAR_T = 10.0
PIV_NUT_AF, PIV_NUT_DEEP = 8.2, 5.3     # M5 316 nyloc, 8.0 A/F x 5.0, + fit
PIV_NUT_CR = PIV_NUT_AF/2/math.cos(math.pi/6)
PIV_NUT_WALL = EAR_T - PIV_NUT_DEEP
assert PIV_NUT_WALL >= 4.0, (
    f"nyloc pocket leaves {PIV_NUT_WALL:.1f} mm behind the visor friction land")
BOLT_D = 5.4                       # M5 clearance; the nut is in THIS part
assert FRIC_R1 < R_EAR, "friction land would run off the edge of the ear"
# Neither side threads any more: the shell upstand carries a captive 316 nyloc
# and both holes are clearance. What still has to hold is that this one is not
# the tighter of the two, or the bolt binds here and the hand-set preload reads
# as tighter than what actually reaches the crown.
assert BOLT_D >= H["PIV_BOLT"], "visor bolt hole must not be tighter than the shell's"
# With no crown the faces sit almost flush - just the 316 shim plus a running
# clearance, instead of the 1.71 mm the interleaving teeth used to need.
MESH_GAP = FRIC_SHIM + 0.2


VIS_T, VIS_D, BEV = 4.0, 58.0, 6.0
WING_DROP = 34.0
TILT = 0.0                          # rendered attitude; the part is symmetric about this

X_MID = (PIV_X[0] + PIV_X[1]) / 2

# takes the flex under a 20 N push from 15 mm down to 6 mm on a 300 mm span.
SPAN  = PIV_X[1] - PIV_X[0]        # clear gap between the housing upstands
EAR_X = SPAN/2 - MESH_GAP          # ears sit MESH_GAP inboard, shim between
# The HOOD stops at the ear face too, not at the upstand face. The shell's own
# crowns project inboard past PIV_X, so a hood run out to the full SPAN has the
# shell's 16 teeth buried in it - a clash that does not vary with angle, because
# a flat plate has no angular features. That is what made the detent read dead.
HOOD_HALF = EAR_X
# THE HOOD HANGS BELOW THE AXIS, not on it. With the plate centred on the pivot
# the ears stood R_EAR - VIS_T/2 = 10 mm proud of BOTH hood faces and the part
# could not lie on a bed at all - 58 mm2 of contact, two ear rims, the hood in
# the air. Dropping the hood until its underside is tangent to the ear puts
# 17,000 mm2 on the bed and changes nothing the eye can see.
HOOD_DROP = R_EAR - VIS_T/2
# The rear overhang behind the axis is what swings DOWN toward the housing's top
# wall when the hood is lifted; 8 mm at the old height was fine, at the new
# height it touched the wall at 15 deg. 3 mm clears 25 deg; asserted below.
Z0, Z1 = 3.0, -(VIS_D - BEV)
OFF = VIS_T * 0.7071
prof = [(2.0, Z0), (2.0, Z1), (2.0 - BEV, Z1 - BEV),
        (2.0 - BEV - OFF, Z1 - BEV + OFF),
        (-2.0, Z1 + OFF + (2.0 - OFF - (-2.0))),
        (-2.0, Z0)]
# recompute the inner corner exactly: where the offset bevel line meets y=-2
by, bz = 2.0 - OFF, Z1 + OFF
t = ((-2.0) - by) / (-0.7071)
prof[4] = (-2.0, bz + t * (-0.7071))
prof = [(py - HOOD_DROP, pz) for py, pz in prof]
# the rear edge's lowest corner, swung by the visor's lift, must clear the top wall
_wall = H["OUT_H"]/2 - PIV_Y                 # top wall, in this part's frame (negative)
for _lift in (0.0, 15.0, 25.0):
    _r = math.radians(_lift)
    _cy, _cz = -HOOD_DROP - VIS_T/2, Z0
    _y = _cy*math.cos(_r) - _cz*math.sin(_r)
    assert _y > _wall + 1.0, (
        f"hood's rear edge swings to {_y:.1f} at {_lift:.0f} deg lift, wall is at "
        f"{_wall:.1f} - shorten Z0 or raise PIV_Y")
v = extrude(Plane.YZ * Polygon(*prof, align=None), amount=HOOD_HALF, both=True)

for wx in (-EAR_X + EAR_T/2, EAR_X - EAR_T/2):
    v += Pos(wx, 0, 0) * Rot(0, 90, 0) * Cylinder(R_EAR, EAR_T,
            align=(Align.CENTER, Align.CENTER, Align.CENTER))
for wx, outward in ((-EAR_X + EAR_T/2, -1), (EAR_X - EAR_T/2, +1)):
    v -= Pos(wx, 0, 0) * Rot(0, 90, 0) * Cylinder(BOLT_D/2, 60)
    # Nyloc pocket in the OUTBOARD face; the INBOARD face is the friction land
    # that runs on the 316 shim. Same sign trick the housing uses: rotating by
    # 90*outward sends the prism the same way as the face it is cut from, so one
    # expression does both ears with no sign table to get wrong. Cut the other
    # way it extrudes into open air and removes nothing, leaving a part that
    # looks right and has no pocket - so the removal is measured.
    _v0 = v.volume
    # NOTE the sign is the OPPOSITE of the housing's. There the upstands sit
    # outboard of the visor, so "into the part" is inboard; here the visor's
    # ears sit inboard of the upstands, so into the part is outboard. Same
    # expression with the rotation negated - and the volume check below is what
    # caught it, because cutting the wrong way removed exactly 0 mm3.
    v -= (Pos(wx + outward*EAR_T/2, 0, 0) * Rot(0, -90*outward, 0)
          * extrude(RegularPolygon(PIV_NUT_CR, 6), PIV_NUT_DEEP))
    _want = (math.sqrt(3)/2*PIV_NUT_AF**2 - math.pi*(BOLT_D/2)**2) * PIV_NUT_DEEP
    assert abs((_v0 - v.volume) - _want) < 0.05*_want, (
        f"visor nyloc pocket removed {_v0 - v.volume:.0f} mm3, expected "
        f"{_want:.0f} - it is cutting outboard into air, not into the ear")

v = Rot(TILT, 0, 0) * v
v = Pos(X_MID, PIV_Y, PIV_Z) * v
export_step(v, "cad/out/helm_visor_revC.stp")
bb = v.bounding_box()
print(f"VISOR  vol={v.volume/1000:6.1f} cm3 solids={len(v.solids())} "
      f"bbox={bb.size.X:.0f}x{bb.size.Y:.0f}x{bb.size.Z:.0f}")
print(f"       hood {2*HOOD_HALF:.0f} wide, ear faces at x=+/-{EAR_X:.1f} "
      f"({MESH_GAP:.2f} clear of the upstands at {PIV_X[1]:.0f} for the crowns)")
print(f"       friction land r{FRIC_R0}-{FRIC_R1} on a {FRIC_SHIM} 316 shim, "
      f"316 nyloc pocketed in this ear, {PIV_NUT_WALL:.1f} mm behind the land")
json.dump({"PIV_X":PIV_X,"PIV_Y":PIV_Y,"PIV_Z":PIV_Z,"R_EAR":R_EAR,"EAR_T":EAR_T,
           "FRIC_R0":FRIC_R0,"FRIC_R1":FRIC_R1,"FRIC_SHIM":FRIC_SHIM,"EAR_T":EAR_T,"PIV_NUT_WALL":PIV_NUT_WALL,
           "BOLT_D":BOLT_D,"SPAN":SPAN,
           # published so the build page states this part's size and mass from
           # the solid rather than from a remembered number
           "VOL_CM3":v.volume/1000.0,"HOOD_W":2*HOOD_HALF,
           "BBOX":[bb.size.X,bb.size.Y,bb.size.Z]},
          open("cad/out/pivot.json","w"), indent=1)
