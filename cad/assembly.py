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
BAIL_B  = _solid("cad/out/bail_base_revA.stp")
BAIL_A  = _solid("cad/out/bail_arm_revA.stp")
SHROUD_F = _solid("cad/out/heatsink_shroud_revD.stp")
# TWO 80 x 80 x 25 fans, drawn as envelopes at the positions the shroud was
# built for. The NF-F12 STEP import that used to live here was the single 120 mm
# fan; the shroud was rebuilt for two 80s and this file kept drawing the old one
# inside it, so every assembly render showed a fan the shroud no longer fits.
# Read the positions from the shroud script's own numbers rather than retyping.
import re as _re
_sh_src = open("cad/heatsink_shroud.py").read()
FAN_W  = float(_re.search(r"^FAN_W, FAN_T, FAN_PITCH, FAN_BORE = ([\d.]+)", _sh_src, _re.M).group(1))
FAN_T  = float(_re.search(r"^FAN_W, FAN_T, FAN_PITCH, FAN_BORE = [\d.]+, ([\d.]+)", _sh_src, _re.M).group(1))
FAN_N  = int(_re.search(r"^FAN_N = (\d+)", _sh_src, _re.M).group(1))
FAN_CY = [(-FAN_N/2 + 0.5 + i) * FAN_W for i in range(FAN_N)]
_SH_WALL = 3.0
def _fans():
    """Both fans, in the SHROUD's local frame: on the inside of its outer wall."""
    out = None
    for _fy in FAN_CY:
        f = Pos(0, _fy, _SH_WALL) * Box(FAN_W, FAN_W, FAN_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
        out = f if out is None else out + f
    return out
FAN = _fans()
print(f"  fan: {FAN_N}x {FAN_W:.0f}x{FAN_W:.0f}x{FAN_T:.0f} at y {FAN_CY}")
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
# THE BAIL pivots on the COVER'S TRUNNIONS, which sit behind the unit at
# z = BACK + TRUN_STAND and x = +/-(TRUN_X + TRUN_LAND). This placement used to
# aim at TILT_Z on the SHELL wall - a pivot deleted earlier the same day - and
# read PIV2_PROUD for the arm face, so the arms sat 32 mm in front of the real
# trunnions and could not have been bolted to anything. Every number here is
# now the cover's, read from housing.json, plus the bail's own geometry read
# from cad/out/bail.json which bail.py writes.
_BJ = json.load(open("cad/out/bail.json"))
_SJ = json.load(open("cad/out/shroud.json"))
_BACK = H["DEPTH"] + H["GASKET_C"] + H["COVER_T"]
_AXIS_Z = _BACK + H["TRUN_STAND"]
_ARM_FACE, _ARM_T, _RISE = _BJ["ARM_FACE"], _BJ["ARM_T"], _BJ["RISE"]
_ORG = _BJ["ARM_ORIGIN"]
def _arm(sx):
    # The recipe is bail.py's, read from bail.json, NOT re-derived here. This
    # file used to build the transform itself with origin x = sx*ARM_FACE, and
    # the part's thickness always runs toward +x from that origin - so the -x
    # arm came out pointing INBOARD and sat inside the trunnion it clamps.
    org = _ORG["pos"] if sx > 0 else _ORG["neg"]
    return Plane(origin=tuple(org), x_dir=tuple(_ORG["x_dir"]),
                 z_dir=tuple(_ORG["z_dir"])) * BAIL_A
# The base plate lies FLAT ON THE DASH, below the unit - the arms stand on it.
# It used to be placed with its thickness along z, i.e. on edge like a fence,
# with the arms' feet touching nothing.
_DASH_Y = H["TILT_Y"] - _RISE
BRK = (Plane(origin=(0, _DASH_Y - _BJ["BASE_T"], _AXIS_Z),
             x_dir=(1, 0, 0), z_dir=(0, 1, 0)) * BAIL_B
       + _arm(-1) + _arm(1))
# THE WHOLE BOM, not just the printed shell. These two renders are what the build
# page calls "Assembled", and until now they drew shell, cover, visor and bail
# and stopped - no shroud, no fans, no heatsink, no boards. A reader could not
# tell from them that the fan had changed, which is exactly what happened.
from parts_lib import (finned, pi4, armor_lite, pcb, nyloc, cap_screw,
                       driver_board, rtl_sdr, sensor_breakout, push_button,
                       lobe_knob, breather_vent, cable_gland)
_BACK = H["DEPTH"] + H["COVER_T"] + H["GASKET_C"]
# The LANDING FACE is shroud-local z = OD, not the part's bounding box: the
# louvres stand LOUV_H proud on the other side, so using the bbox floated the
# whole shroud 6 mm off the cover in every assembled render.
_OD = _SJ["SHROUD_OD"]
_SHROUD_ASM = Pos(H["AP_CX"], 0, _BACK + _OD) * Rot(180, 0, 0) * SHROUD_F
# fans sit on the mesh, on the bosses: shroud-local FILT_Z + FILT_MESH upward
_FAN_Z0 = _SJ["FILT_Z"] + _SJ["FILT_MESH"]
_FANS_ASM = Pos(H["AP_CX"], 0, _BACK + _OD - _FAN_Z0 - FAN_T) * Compound([
    Pos(0, fy, 0) * Box(FAN_W, FAN_W, FAN_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for fy in FAN_CY])
# heatsink: base flush in the cover's INNER-face seat (assembled z 22..25), fins
# through the 58x134 aperture standing proud out the back. Drawn already trimmed
# to the aperture, which is how it has to be fitted.
_HS_Z0 = H["DEPTH"] + H["GASKET_C"]                       # cover inner face
_HS = (Pos(H["AP_CX"], 0, _HS_Z0) * Box(H["HS_L"], H["HS_W"], 3.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
       + Pos(H["AP_CX"], 0, _HS_Z0 + 3.0) * finned(H["AP_L"], H["AP_W"], H["HS_H"] - 3.0 + 0.01,
                                                   base=0.01, fin_t=1.4, gap=2.6, along_x=False))
# boards in their bays: the bays are hollow from the cover's inner face out to the
# bump skin, so the boards sit on the bump floor with components facing INTO the
# box. Pi is on its side (portrait); driver is portrait natively.
_BAY_FLOOR = _BACK + H["PI_BUMP_H"] - 3.0                 # inside face of the bump skin
_PI  = Pos(H["PI_BUMP_CX"], 0, _BAY_FLOOR - 1.6) * Rot(180, 0, 0) * Rot(0, 0, 90) * pi4()
_ARM = Pos(H["PI_BUMP_CX"], 0, _BAY_FLOOR - 1.6 - 2.4) * Rot(180, 0, 0) * Rot(0, 0, 90) * armor_lite()
# the RTL-SDR, on edge in the driver bay under the bulkhead it feeds
_SDR = (Pos(H["SDR_X"], 0, _BAY_FLOOR - H["SDR_W"]/2) * Rot(0, 90, 0) * Rot(0, 0, 90)
        * rtl_sdr())
# the real board, from the owner's dimensioned photos, turned so its 113 runs
# along the bay's long axis the way it is actually fitted
_DRV = (Pos(H["DRV_BOARD_CX"], 0, _BAY_FLOOR - 1.6) * Rot(180, 0, 0) * Rot(0, 0, 90)
        * driver_board())
# The three bulkhead fittings, drawn as bodies hanging BELOW their blocks. The
# whip that used to be drawn here has come off the housing (see helm_housing.py
# at SMA_X) - what the housing has is a coax entry.
_FIT_Z = _BACK - H["BORE_Z"]
# THE REAL FITTINGS, and they STAND PROUD. They were a disc and a long thin
# tail, which is neither end of either part and made both look flush with the
# block. The gland's hex hangs below the unit and the vent's nose stands off
# its face; how far each one reaches is a number a builder needs.
_FITS = None
for _fx, _fpart in ((H["GL_X"], cable_gland(thread_d=H["GL_TAP"] + 3.3,
                                            thread_l=H["GL_BOSS_PROUD"] + 8.0)),
                    (H["VENT_X"], breather_vent())):
    _f = (Pos(_fx, H["BLK_Y0"] - (H["GL_BOSS_PROUD"] if _fx < 0 else 0.0), _FIT_Z)
          * Rot(90, 0, 0) * _fpart)
    _FITS = _f if _FITS is None else _FITS + _f
# ---- THE PIVOT HARDWARE, where it actually sits --------------------------
# Four M5 316 nylocs on this unit and not one of them was drawn, so "where does
# the nut go" was never a question anyone could answer by looking. Two are
# captive in hex pockets in the TRUNNION WEBS, reached from the middle of the
# back; two are in the VISOR EARS' outboard faces.
_STEEL = (0.78, 0.79, 0.82)
_NUTS, _BOLTS = None, None
for _sx in (-1, 1):
    _nz = _sx*(H["TRUN_X"] - H["TRUN_WEB_T"])
    _n = (Pos(_nz, H["TILT_Y"], _AXIS_Z) * Rot(0, 90*_sx, 0)
          * nyloc(H["TRUN_NUT_AF"], H["TRUN_NUT_DEEP"] - 1.0, H["TRUN_BORE"]))
    # the KNOB, seated EYE_CB down in the arm's eye, with the stud length the
    # joint actually accepts - see the window bail.py computes
    _b = (Pos(_sx*(_BJ["ARM_FACE"] + _BJ["ARM_T"] - _BJ["EYE_CB"]), H["TILT_Y"], _AXIS_Z)
          * Rot(0, 90*_sx, 0) * lobe_knob(stud=_BJ["KNOB_STUD"],
                                          boss_d=_BJ["KNOB_BOSS_D"]))
    _NUTS = _n if _NUTS is None else _NUTS + _n
    _BOLTS = _b if _BOLTS is None else _BOLTS + _b
    _vx = _sx*(H["PIV_X"][1] - 1.2)
    _NUTS = _NUTS + (Pos(_vx, H["PIV_Y"], H["PIV_Z"]) * Rot(0, 90*_sx, 0)
                     * nyloc(8.0, 4.0, 5.0))

# ---- THE ANTENNA, ON TOP OF THE DRIVER BUMP -----------------------------
# It was drawn on a rail mount beside the unit with a coax run, which is where
# it lived while the only SMA was on the cover's flat face pointing backwards.
# The bulkhead moved into the TOP block of the +x bump and bores UP, so the whip
# screws straight onto it and stands at the sky - no remote mount, no coax run,
# nothing to lead round the outside of the boat.
_SMA_Z = _BACK - H["BORE_Z"]
_SMA_Y = H["BLK_TY0"]
_ANT = Pos(H["SMA_X"], _SMA_Y, _SMA_Z) * Rot(-90, 0, 0) * (
    Cylinder(9.0, 16, align=(Align.CENTER, Align.CENTER, Align.MIN))            # base collar
    + Pos(0, 0, 16) * Cylinder(6.5, 30, align=(Align.CENTER, Align.CENTER, Align.MIN))
    + Pos(0, 0, 46) * Cone(6.5, 2.0, 14, align=(Align.CENTER, Align.CENTER, Align.MIN))
    + Pos(0, 0, 60) * Cylinder(1.6, 95, align=(Align.CENTER, Align.CENTER, Align.MIN))
    + Pos(0, 0, 155) * Cone(2.0, 5.5, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    + Pos(0, 0, 165) * Cylinder(5.5, 20, align=(Align.CENTER, Align.CENTER, Align.MIN)))
# the bulkhead body itself, sitting in the block with its nut inside
_SMA = (Pos(H["SMA_X"], _SMA_Y, _SMA_Z) * Rot(-90, 0, 0)
        * Cylinder(6.35, 5.0, align=(Align.CENTER, Align.CENTER, Align.MIN)))

# ---- THE CONTROLS, in the assembled views for the first time -------------
# Four buttons and the encoder are the only things on this unit a person
# touches, and no assembled render has ever drawn them - they existed in the
# exploded sheet and nowhere else.
_BTN = None
for _bx in H["BTN_X"]:
    _b = Pos(_bx, H["ROW_CY"], 0) * Rot(180, 0, 0) * push_button(H["BTN_D"], 17.5)
    _BTN = _b if _BTN is None else _BTN + _b
_ENC = (Pos(H["ENC_X"], H["ROW_CY"], -17.5) * Cylinder(10.25, 17.5,
        align=(Align.CENTER, Align.CENTER, Align.MIN)))
# and the four sensor breakouts on their standoffs, inner face
_SENS = None
for _sn in H["SENSORS"]:
    _s = (Pos(_sn["x"], _sn["y"], H["DEPTH"] + H["GASKET_C"] - H["STANDOFF_H"] - 1.2)
          * Rot(180, 0, 0) * sensor_breakout(_sn["pitch_x"] + 12.0, _sn["pitch_y"] + 10.0))
    _SENS = _s if _SENS is None else _SENS + _s

ALLOY, PI_G, DARK = (0.66, 0.68, 0.72), (0.11, 0.46, 0.26), (0.20, 0.20, 0.22)
# The display itself. Without it the front view looks straight through the
# aperture at the cover's inner face, and every reader took the bays for the
# front of the unit.
_DISP = Pos(H["APER_X"], H["APER_Y"], H["FACE_T"] + H["GLUE_T"]) * Box(
    H["MOD_W"], H["MOD_H"], H["MOD_D"], align=(Align.CENTER, Align.CENTER, Align.MIN))
asm = [
    (BRK, (0.10, 0.26, 0.52)),
    (Pos(0, 0, 0) * SHELL, BLUE),
    (_DISP, (0.08, 0.09, 0.11)),
    (Pos(0, 0, _BACK) * Rot(180, 0, 0) * COVER, BLUE2),
    (tilt(0), BLUE),
    (_SHROUD_ASM, (0.10, 0.26, 0.52)),
    (_FANS_ASM, DARK),
    (_HS, ALLOY),
    (_PI, PI_G), (_ARM, ALLOY), (_DRV, (0.12, 0.43, 0.47)), (_SDR, (0.20, 0.55, 0.35)),
    (_FITS, (0.55, 0.56, 0.58)),
    (_NUTS, _STEEL), (_BOLTS, _STEEL),
    (_ANT, DARK), (_SMA, (0.80, 0.68, 0.24)),
    (_BTN, (0.13, 0.13, 0.15)), (_ENC, (0.72, 0.60, 0.25)),
    (_SENS, (0.76, 0.47, 0.12)),
]
# Camera solved rather than guessed: az=198, el=-112 gives depth.z>0 (front
# face nearest), up.y>0 (+Y up) and explode.z<0 (front of the stack on top).
# FOUR angles on the finished unit. One three-quarter view hides half of what
# is on this thing: the controls only read from the front, the bumps, blocks,
# fittings and bail only from behind, and the shroud's depth only from the side.
for _nm, _az, _el in (("asm_housing", 198, -112),        # front three-quarter
                      ("asm_housing_left", 232, -120),   # front, other shoulder
                      ("asm_housing_side", 270, -100),   # side elevation
                      ("asm_housing_top", 198, -150)):   # down onto the top
    png(f"cad/out/{_nm}.png", render_multi(asm, _az, _el, W=1200, H=850)[0])
print("  asm_housing / _left / _side / _top")
# from behind and a little below, so the bail base reads as what it is - a
# plate on the dash under the unit - and the shroud drain is in view
png("cad/out/asm_housing_rear.png", render_multi(asm, 150, -20, W=1200, H=850)[0])
print("  asm_housing_rear")
# rot(az,el) rotates about the model Z and X only - it cannot orbit
# horizontally. Yawing the assembly about Y is the same viewpoint change and
# is a proper rotation, so nothing is mirrored.
# ---- THE VISOR FOLDS ----------------------------------------------------
# It is a hood at 0 and a screen cover at -90, and the only way to show that is
# to draw both. Rotated about the pivot axis, which is where it actually turns.
def visor_at(deg):
    return (Pos(0, H["PIV_Y"], H["PIV_Z"]) * Rot(deg, 0, 0)
            * Pos(0, -H["PIV_Y"], -H["PIV_Z"]) * VISOR)

_FOLD = [(Pos(0, 0, 0) * SHELL, BLUE),
         (Pos(0, 0, _BACK) * Rot(180, 0, 0) * COVER, BLUE2),
         (_DISP, (0.08, 0.09, 0.11))]
for _d, _nm in ((0, "deployed"), (-45, "half"), (-90, "stowed")):
    png(f"cad/out/asm_visor_{_nm}.png",
        render_multi(_FOLD + [(visor_at(_d), BLUE)], 210, -135, W=980, H=760)[0])
print("  asm_visor_deployed / half / stowed")

# ---- GHOSTED: the housing translucent, everything inside solid -----------
# A section answers "what is at this plane". The question a builder actually
# asks is "what is in there, and does it all fit" - and for that the box has to
# go see-through rather than get cut open. Printed parts drop to 22% alpha;
# every bought part stays solid, so what you see is exactly the packing.
GHOST = 0.22
_ghost = [(Pos(0, 0, 0) * SHELL, BLUE + (GHOST,)),
          (Pos(0, 0, _BACK) * Rot(180, 0, 0) * COVER, BLUE2 + (GHOST,)),
          (_SHROUD_ASM, (0.10, 0.26, 0.52, GHOST)),
          (visor_at(0), BLUE + (GHOST,)),
          (_DISP, (0.08, 0.09, 0.11, 0.55)),
          (_HS, ALLOY), (_FANS_ASM, DARK),
          (_PI, PI_G), (_ARM, ALLOY), (_DRV, (0.12, 0.43, 0.47)),
          (_SDR, (0.20, 0.55, 0.35)), (_SENS, (0.76, 0.47, 0.12)),
          (_BTN, (0.13, 0.13, 0.15)), (_ENC, (0.72, 0.60, 0.25)),
          (_FITS, (0.55, 0.56, 0.58)), (_NUTS, _STEEL), (_BOLTS, _STEEL),
          (_ANT, DARK), (_SMA, (0.80, 0.68, 0.24))]
if "GPS_X" in H:
    _GPS = Pos(H["GPS_X"], H["BLK_TY0"] - H["GPS_WIN_T"] - H["GPS_T"]/2 - 0.5,
               _BACK - H["GPS_Z"]) * Box(H["GPS_L"], H["GPS_T"], H["GPS_W"],
                                         align=(Align.CENTER,)*3)
    _ghost.append((_GPS, (0.20, 0.55, 0.35)))
# rendered at 1900 wide, not 1200: these are the views a builder zooms into to
# find out where a board goes, and they run full page width rather than in the
# two-up grid the rest of the page uses.
for _nm, _az, _el in (("ghost_front", 198, -112), ("ghost_rear", 150, -20),
                      ("ghost_side", 270, -100), ("ghost_top", 198, -150)):
    png(f"cad/out/asm_{_nm}.png", render_multi(_ghost, _az, _el, W=1900, H=1150)[0])
print("  asm_ghost_front / _rear / _side / _top  (housing translucent)")

YAW = Rot(0, -40, 0)
# 0 / +10 / +20, not 15 / 0 / -30. Tilt is FACE UP ONLY now - the arms run
# inside the bezel width, so face-down swings the unit into them - and a sheet
# showing a -30 deg attitude is showing a position the mount cannot reach.
for ang, name in ((0, "flat"), (10, "up"), (20, "max")):
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


# ══════════════════════════════════════════════ 4. FAN SHROUD + 2x 80 mm
BIG2 = 500
fan_in_shroud = FAN                       # already in the shroud's frame
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
