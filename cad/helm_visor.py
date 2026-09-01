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
  M5 316 SS + wave washer + nyloc. Firm hand pressure to click, holds otherwise.

The leading edge turns down 8 mm. That is not styling: on two pivots the hood
is a 310 mm cantilever, and the lip turns a floppy flat plate into a channel.

Material : ASA (blue)   Orientation : HOOD FLAT ON THE BED, ears up
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
N_TEETH, TOOTH_H = H["N_TEETH"], H["TOOTH_H"]
R_T0, R_T1 = H["R_T0"], H["R_T1"]  # tooth crown inner / outer radius
R_EAR = H["R_EAR"]                 # match the shell's ear so the joint is flush
EAR_T = 6.0                        # this part's own thickness, not a mating dim
BOLT_D = 5.4                       # M5 clearance; the shell takes the 4.3 pilot
assert R_T1 < R_EAR, "teeth would run off the edge of the ear"
assert BOLT_D > H["PIV_BOLT"], "visor bolt hole must clear, not thread"
# A crown stands TOOTH_H*1.25 proud of the face it is built on, so the two ear
# faces must sit that far APART or the teeth simply bury themselves in the
# opposing solid instead of interleaving. rev B had them coincident: the
# crowns could never mesh at any angle, which is also why nobody noticed the
# tooth radii did not match. The bracket got this right; this part did not.
MESH_GAP = H["TOOTH_PROUD"] + 0.2   # crown height + running clearance


VIS_T, VIS_D, BEV = 4.0, 58.0, 6.0
WING_DROP = 34.0
TILT = 0.0                          # rendered attitude; the part is symmetric about this

X_MID = (PIV_X[0] + PIV_X[1]) / 2

def teeth(face_x, outward):
    """Radial crown on a face normal to X. Each tooth is a bar running
    radially, rolled 45 deg so its exposed edge is a ridge; the gaps between
    are the matching V grooves, so two identical crowns nest."""
    out = None
    for i in range(N_TEETH):
        t = (Rot(360.0*i/N_TEETH, 0, 0)
             * Pos(face_x + outward*TOOTH_H*0.5, R_T0, 0)
             * Rot(0, 45, 0)
             * Box(TOOTH_H*1.5, R_T1 - R_T0, TOOTH_H*1.5,
                   align=(Align.CENTER, Align.MIN, Align.CENTER)))
        out = t if out is None else out + t
    return out

# ── visor body ────────────────────────────────────────────────────────────
# No side wings: a flat hood with a 45 deg turned-down bevel at the leading
# edge. The bevel is not decoration - it lifts I from 373 to 953 mm4, which
# takes the flex under a 20 N push from 15 mm down to 6 mm on a 300 mm span.
SPAN  = PIV_X[1] - PIV_X[0]        # clear gap between the housing upstands
EAR_X = SPAN/2 - MESH_GAP          # ears and crowns sit MESH_GAP inboard
# The HOOD stops at the ear face too, not at the upstand face. The shell's own
# crowns project inboard past PIV_X, so a hood run out to the full SPAN has the
# shell's 16 teeth buried in it - a clash that does not vary with angle, because
# a flat plate has no angular features. That is what made the detent read dead.
HOOD_HALF = EAR_X
Z0, Z1 = 8.0, -(VIS_D - BEV)
OFF = VIS_T * 0.7071
prof = [(2.0, Z0), (2.0, Z1), (2.0 - BEV, Z1 - BEV),
        (2.0 - BEV - OFF, Z1 - BEV + OFF),
        (-2.0, Z1 + OFF + (2.0 - OFF - (-2.0))),
        (-2.0, Z0)]
# recompute the inner corner exactly: where the offset bevel line meets y=-2
by, bz = 2.0 - OFF, Z1 + OFF
t = ((-2.0) - by) / (-0.7071)
prof[4] = (-2.0, bz + t * (-0.7071))
v = extrude(Plane.YZ * Polygon(*prof, align=None), amount=HOOD_HALF, both=True)

for wx in (-EAR_X + EAR_T/2, EAR_X - EAR_T/2):
    v += Pos(wx, 0, 0) * Rot(0, 90, 0) * Cylinder(R_EAR, EAR_T,
            align=(Align.CENTER, Align.CENTER, Align.CENTER))
v += teeth(-EAR_X, -1)
v += teeth( EAR_X, +1)
for wx in (-EAR_X + EAR_T/2, EAR_X - EAR_T/2):
    v -= Pos(wx, 0, 0) * Rot(0, 90, 0) * Cylinder(BOLT_D/2, 60)

v = Rot(TILT, 0, 0) * v
v = Pos(X_MID, PIV_Y, PIV_Z) * v
export_step(v, "cad/out/helm_visor_revC.stp")
bb = v.bounding_box()
print(f"VISOR  vol={v.volume/1000:6.1f} cm3 solids={len(v.solids())} "
      f"bbox={bb.size.X:.0f}x{bb.size.Y:.0f}x{bb.size.Z:.0f}")
print(f"       hood {2*HOOD_HALF:.0f} wide, ear faces at x=+/-{EAR_X:.1f} "
      f"({MESH_GAP:.2f} clear of the upstands at {PIV_X[1]:.0f} for the crowns)")
print(f"       {N_TEETH} teeth = {360/N_TEETH:.1f} deg per click")
json.dump({"PIV_X":PIV_X,"PIV_Y":PIV_Y,"PIV_Z":PIV_Z,"R_EAR":R_EAR,"EAR_T":EAR_T,
           "N_TEETH":N_TEETH,"TOOTH_H":TOOTH_H,"R_T0":R_T0,"R_T1":R_T1,
           "BOLT_D":BOLT_D,"SPAN":SPAN}, open("cad/out/pivot.json","w"), indent=1)
