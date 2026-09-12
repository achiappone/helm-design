"""
Assembly renders: housing assembled, housing exploded, shroud with connector.

Components I have no CAD for are REPRESENTATIONS built to their datasheet
envelopes - correct size and position, not internal detail. They exist to show
fit and assembly order, not to be manufactured.
"""
import sys, json
sys.path.insert(0, "cad")
from build123d import *

def _solid(path):
    """import_step may return a Compound; a Location on the wrapper is
    ignored by booleans, so hand back the Solid itself."""
    s = import_step(path)
    return s.solids()[0] if len(s.solids()) == 1 else s
from render import render_multi, png

H = json.load(open("cad/out/housing.json"))
OUT_W, OUT_H = H["OUT_W"], H["OUT_H"]
DISP_CX = H["DISP_CX"]

SHELL  = _solid("cad/out/helm_shell_revC.stp")
COVER  = _solid("cad/out/helm_cover_revC.stp")
VISOR  = _solid("cad/out/helm_visor_revC.stp")
BRACKET = _solid("cad/out/tilt_bracket_revC.stp")
SHROUD_F = _solid("cad/out/heatsink_shroud_revD.stp")
_fan_raw = import_step("NF-F12_iPPC_Public-CAD.stp")
# ALL 11 solids now. This used to drop any solid whose tessellate() raised,
# which sounds conservative and was not: the one it dropped was solid 0, the
# 119 x 25 x 119 FRAME - 55 cm3, more than half the fan. Every assembly render
# showed the impeller and eight corner bumpers hanging in mid air, and nothing
# said so, because the filter swallowed the exception and printed a count that
# looked healthy at 10/11.
#
# The frame is not broken. It is 583 faces and exactly ONE of them fails to
# mesh, so render.safe_tessellate now keeps the other 582 instead of discarding
# the solid. See the note there.
# DO NOT boolean-union these. Fusing Noctua's 11 solids one by one collapses
# them: 96.0 cm3 of parts comes out as 5.6 cm3 in 6 solids, because OCC's fuse
# cannot cope with the overlapping, self-intersecting geometry a vendor ships
# for visualisation. The union destroyed the frame and the impeller and left the
# corner bumpers, which is exactly what the assembly renders have been showing.
# A Compound just holds them together with no boolean at all - same 96.0 cm3,
# same 1180 faces, and the renderer meshes each face on its own anyway.
FAN = Compound(_fan_raw.solids())
_fv = FAN.volume/1000
assert _fv > 90.0, (
    f"fan compound is {_fv:.1f} cm3, expected ~96 - something fused it again")
print(f"  fan: {len(_fan_raw.solids())} solids as a compound, {_fv:.1f} cm3")
SHROUD = _solid("cad/out/lp24_shroud_revD.stp")
CLAMP  = _solid("cad/out/lp24_clamp_revD.stp")

BLUE=(0.16,0.42,0.78); BLUE2=(0.13,0.34,0.64); CLAMPC=(0.42,0.68,0.95); GLASS=(0.10,0.12,0.16)
GREEN=(0.10,0.42,0.24); DGREEN=(0.07,0.30,0.18); ALLOY=(0.62,0.65,0.69)
STEEL=(0.55,0.58,0.62); BLACK=(0.12,0.12,0.14); COPPER=(0.72,0.45,0.20)

# ── representations ───────────────────────────────────────────────────────
disp  = Box(305, 125, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
pi    = Box(85, 56, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN)) \
      + Pi_ports if False else Box(85, 56, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
pi   += Pos(28, 0, 1.6) * Box(28, 50, 13.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
hat   = Box(65, 56.5, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
drok  = Box(65, 58, 20, align=(Align.CENTER, Align.CENTER, Align.MIN))
lp24  = Box(33, 33, 5, align=(Align.CENTER, Align.CENTER, Align.MIN)) \
      + Pos(0, 0, -19) * Cylinder(12.0, 19, align=(Align.CENTER, Align.CENTER, Align.MIN))
plug  = Cylinder(15.4, 60, align=(Align.CENTER, Align.CENTER, Align.MIN))

def tube(pts, r):
    return sweep(Circle(r), path=Spline(*pts))

# ══════════════════════════════════════════════ 1. HOUSING ASSEMBLED
PIVOT = (H["PIV_X"], H["PIV_Y"], H["PIV_Z"])
PX, PY, PZ = PIVOT
def tilt(deg):
    """Swing the visor about its real pivot axis."""
    return Pos(0, PY, PZ) * Rot(deg, 0, 0) * Pos(0, -PY, -PZ) * VISOR
# bracket: its pivot origin maps onto the housing bottom pivots
BRK = Pos(0, H["BP_Y"], H["BP_Z"]) * BRACKET
asm = [
    (BRK, (0.10, 0.26, 0.52)),
    (Pos(0, 0, 0) * SHELL, BLUE),
    (Pos(0, 0, H["DEPTH"] + H["COVER_T"] + H["GASKET_C"]) * Rot(180, 0, 0) * COVER, BLUE2),
    (tilt(0), BLUE),
]
# Camera solved rather than guessed: az=198, el=-112 gives depth.z>0 (front
# face nearest), up.y>0 (+Y up) and explode.z<0 (front of the stack on top).
png("cad/out/asm_housing.png", render_multi(asm, 198, -112, W=1200, H=850)[0])
print("  asm_housing (front)")
png("cad/out/asm_housing_rear.png", render_multi(asm, 34, 20, W=1200, H=850)[0])
print("  asm_housing_rear")
# rot(az,el) rotates about the model Z and X only - it cannot orbit
# horizontally. Yawing the assembly about Y is the same viewpoint change and
# is a proper rotation, so nothing is mirrored.
YAW = Rot(0, -40, 0)
for ang, name in ((15, "up"), (0, "flat"), (-30, "down")):
    a2 = [(YAW * BRK, (0.10, 0.26, 0.52)),
          (YAW * SHELL, BLUE),
          (YAW * Pos(0, 0, H["DEPTH"] + H["COVER_T"] + H["GASKET_C"]) * Rot(180, 0, 0) * COVER, BLUE2),
          (YAW * tilt(ang), (0.32, 0.62, 0.95))]
    png(f"cad/out/asm_tilt_{name}.png", render_multi(a2, 198, -100, W=900, H=760)[0])
print("  asm_tilt_up / flat / down")

# ══════════════════════════════════════════════ 2. HOUSING EXPLODED
E = 1.0
exp = [
    (Pos(0, 0, -170*E) * VISOR, BLUE),
    (Pos(0, 0, -60*E) * SHELL, BLUE),
    (Pos(DISP_CX, H["DISP_CY"], 40*E) * disp, GLASS),
    (Pos(60, -20, 150*E) * pi, GREEN),
    (Pos(60, -20, 172*E) * hat, DGREEN),
    (Pos(-140, 40, 150*E) * drok, ALLOY),
    (Pos(0, 0, 250*E) * COVER, BLUE2),
]
png("cad/out/asm_exploded.png", render_multi(exp, 205, -118, W=1200, H=1000)[0])
print("  asm_exploded")

# ══════════════════════════════════════════════ 3. SHROUD + LP-24 + CABLE
ZC = 5.0 + 29.0            # connector centreline
BEAM_UNDER, CLAMP_H = 26.0, 13.0
CLAMP_X = 22.5
CABLE_Z = BEAM_UNDER - CLAMP_H + 5.5    # jacket centre sitting in the saddle
BIG = 400

# The CNLINKO LP-24-C24PE STEP you supplied will NOT tessellate - 1734 faces,
# some with no triangulation, and an explicit BRepMesh pass does not fix it.
# It did confirm the plug envelope (73.4 x 40.3) against the drawing, so the
# plug below stays built from the CNLINKO dimensions instead.
import math as _m
plug = Pos(-35, 0, ZC) * Rot(0, -90, 0) * Cylinder(15.4, 60,
              align=(Align.CENTER, Align.CENTER, Align.MIN))
_fl = Pos(-32.5, 0, ZC) * Box(5.0, 33.0, 33.0)
_fl = fillet(_fl.edges().filter_by(Axis.X), 3.0)
for _sx in (-1, 1):
    for _sy in (-1, 1):
        _fl -= Pos(-32.5, _sx*13.0, ZC + _sy*13.0) * Rot(0, 90, 0) * Cylinder(1.6, 12)
_body = (Pos(-30, 0, ZC) * Rot(0, 90, 0) * Cylinder(12.2, 10.5,
             align=(Align.CENTER, Align.CENTER, Align.MIN))
         + Pos(-19.5, 0, ZC) * Rot(0, 90, 0) * Cylinder(14.9, 19.3,
             align=(Align.CENTER, Align.CENTER, Align.MIN)))
_pins = None
for _r, _n in ((4.2, 8), (7.6, 12), (0.0, 4)):
    for _i in range(_n):
        _a = 2*_m.pi*_i/_n
        _pin = Pos(-33.0, _r*_m.cos(_a), ZC + _r*_m.sin(_a)) * Rot(0, 90, 0) * Cylinder(0.7, 3.5,
                   align=(Align.CENTER, Align.CENTER, Align.MIN))
        _pins = _pin if _pins is None else _pins + _pin
lp24 = _fl + _body

# jacket: straight runs with a blended corner - a spline through this many
# points overshoots badly and reads as a knot
jacket = (Pos(28, 0, -14) * Cylinder(5.5, 32, align=(Align.CENTER, Align.CENTER, Align.MIN))
          + Pos(28, 0, CABLE_Z) * Sphere(5.5)
          + Pos(14, 0, CABLE_Z) * Rot(0, 90, 0) * Cylinder(5.5, 28,
                align=(Align.CENTER, Align.CENTER, Align.CENTER)))
# conductors leave the jacket and fan INTO the connector's rear cups at x=-11
cond = []
for dy, dz in ((-8, -6), (-4, 5), (0, 8), (4, 4), (8, -7), (-6, 2), (6, -2)):
    cond.append(sweep(Circle(0.8), path=Spline((0, 0, CABLE_Z),
                                               (-6, dy*0.55, CABLE_Z + (ZC-CABLE_Z)*0.55),
                                               (-11.5, dy, ZC + dz))))

shroud_cut = SHROUD - Pos(0, -BIG/2, 0) * Box(BIG, BIG, BIG)
clamp_cut = (Pos(CLAMP_X, 0, BEAM_UNDER - CLAMP_H) * CLAMP) - Pos(0, -BIG/2, 0) * Box(BIG, BIG, BIG)

png("cad/out/asm_shroud.png", render_multi([
    (shroud_cut, BLUE), (clamp_cut, CLAMPC), (lp24, STEEL), (_pins, (0.80,0.72,0.35)), (jacket, BLACK),
] + [(c, COPPER) for c in cond], 16, 24, W=1200, H=850)[0])
print("  asm_shroud (sectioned)")

png("cad/out/asm_shroud_mated.png", render_multi([
    (SHROUD, BLUE), (lp24, STEEL), (plug, BLACK),
], 36, 16, W=1200, H=850)[0])
print("  asm_shroud_mated")


# ══════════════════════════════════════════════ 4. FAN SHROUD + NF-F12
# Fan axis is Y in Noctua's file; the shroud's is Z. 27 mm thick including the
# anti-vibration pads, not the 25 mm on the spec sheet.
BIG2 = 500
fan_in_shroud = Pos(0, 0, 3.5) * Rot(90, 0, 0) * FAN
half2 = Pos(0, -BIG2/2, 0) * Box(BIG2, BIG2, BIG2)
png("cad/out/asm_shroud_fan.png", render_multi([
    (SHROUD_F, BLUE),
    (fan_in_shroud, (0.42, 0.30, 0.26)),
], 34, 26, W=1150, H=850)[0])
print("  asm_shroud_fan")

png("cad/out/asm_shroud_fan_cut.png", render_multi([
    (SHROUD_F - half2, BLUE),
    (fan_in_shroud, (0.42, 0.30, 0.26)),
], 18, 24, W=1150, H=850)[0])
print("  asm_shroud_fan_cut")
