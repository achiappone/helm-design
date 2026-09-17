"""
Subassembly views -- the things a whole-unit render cannot show.

Each view here exists because a specific question had no picture:

  THERMAL   the stack is cover -> heatsink -> shroud -> mesh -> two fans, and
            only one of those is printed. Exploded along the axis so the order
            and the direction are unambiguous - in particular that the heatsink
            goes in BASE OUT from the inside, and that its fins end up outside.
  FIXING    how the shroud is held on. Four M3 run the full depth of corner
            bosses, enter at the LOUVRED face and stop in blind pilots in the
            cover. Nothing goes through the pressure boundary.
  WIRE      the only thing that crosses the boundary: the fans' leads, through
            one potted O6 pass in the cover, under the shroud.

REWRITTEN. The previous version drew a 6 mm alloy heat plate, a 120 mm fan and
a gluing jig - three parts that no longer exist - and died on H["HS_HOLE_C"],
a key housing.json stopped publishing when the plate went. It had been dead
long enough that the build page was showing its last successful output as if it
were current.

Everything is positioned from cad/out/housing.json and cad/out/shroud.json.
"""
import sys, json
sys.path.insert(0, "cad")
from build123d import *
from render import render_multi, png

H = json.load(open("cad/out/housing.json"))
S = json.load(open("cad/out/shroud.json"))
COVER = import_step("cad/out/helm_cover_revD.stp")
SHROUD = import_step("cad/out/heatsink_shroud_revD.stp")
sys.path.insert(0, "cad")
from parts_lib import finned

BLUE, DEEP = (0.16, 0.40, 0.74), (0.09, 0.24, 0.48)
ALLOY, STEEL = (0.66, 0.68, 0.72), (0.76, 0.77, 0.80)
BRASS, DARK, COPPER = (0.80, 0.68, 0.24), (0.18, 0.18, 0.20), (0.78, 0.42, 0.18)

AP_CX, AP_L, AP_W = H["AP_CX"], H["AP_L"], H["AP_W"]
HS_L, HS_W, HS_H = H["HS_L"], H["HS_W"], H["HS_H"]
HS_BASE = 3.0
COVER_T = H["COVER_T"]
GL_X, VENT_X, SMA_X = H["GL_X"], H["VENT_X"], H["SMA_X"]
BLK_Y0, BLK_Y1, BORE_Z = H["BLK_Y0"], H["BLK_Y1"], H["BORE_Z"]
BUMP_H = H["PI_BUMP_H"]
WIRE_X, WIRE_Y, WIRE_D = H["WIRE_X"], H["WIRE_Y"], H["WIRE_D"]
out = []

# Cover-local frame: z=0 is the OUTER face, z=COVER_T the inner, and cover y is
# the shell's y mirrored. Everything below is drawn in that frame, so "out the
# back" is -z.
def _ex(dz):
    return Pos(0, 0, dz)

# ── thermal stack, exploded ───────────────────────────────────────────────
# The heatsink goes in from the INSIDE: base into the seat in the inner face,
# fins down through the aperture to stand HS_PROUD outside. Drawn already
# trimmed to the aperture, which is how it has to be fitted - a bought
# extrusion carries fins to the edge of its base and they foul the seat.
hs_base = Pos(AP_CX, 0, COVER_T - HS_BASE) * Box(
    HS_L, HS_W, HS_BASE, align=(Align.CENTER, Align.CENTER, Align.MIN))
hs_fins = Pos(AP_CX, 0, COVER_T - HS_H) * finned(
    AP_L, AP_W, HS_H - HS_BASE, base=0.01, fin_t=1.4, gap=2.6, along_x=False)
HS = _ex(-70) * (hs_base + hs_fins)

MESH = _ex(-150) * Pos(0, 0, 0) * Box(S["OW"] - 1, S["OH"] - 1, 0.6,
                                      align=(Align.CENTER, Align.CENTER, Align.MIN))
FANS = [_ex(-190) * Pos(0, fy, 0) * Box(S["FAN_W"], S["FAN_W"], S["FAN_T"],
                                        align=(Align.CENTER, Align.CENTER, Align.MIN))
        for fy in S["FAN_CY"]]
# shroud, flown as it lands: its landing face against the cover
SH = _ex(-250) * Pos(0, 0, -S["SHROUD_OD"]) * SHROUD

rgba, _ = render_multi([(COVER, DEEP), (HS, ALLOY), (MESH, STEEL)]
                       + [(f, DARK) for f in FANS] + [(SH, BLUE)],
                       az=38, el=-22, W=1150, H=900)
png("cad/out/sub_thermal_exploded.png", rgba)
out.append({"name": "sub_thermal_exploded",
            "title": "THERMAL STACK - exploded, in fitting order",
            "note": f"Cover, heatsink, 316 mesh, two {S['FAN_W']:.0f} mm IP67 fans, shroud. "
                    f"The heatsink goes in FROM THE INSIDE - base into the {HS_BASE:.0f} mm "
                    f"seat, flush with the inner face, fins down through the "
                    f"{AP_L:.0f}x{AP_W:.0f} aperture to stand {H['HS_PROUD']:.0f} mm proud "
                    f"outside. The mesh is clamped by the fans' own screws, so one set of "
                    f"fasteners does both jobs and nothing stands proud of the face."})

# ── how the shroud is held on ─────────────────────────────────────────────
# A section through one corner boss, with the screw drawn, because "four M3
# through the bosses" does not convey that the screw enters at the weather face
# and stops blind.
BOSSES = H["HS_HOLES"]
screws = None
for bx, by in BOSSES:
    _z0 = -(S["SHROUD_OD"] + S["LOUV_H"]) - 2.0      # head sits at the louvred face
    sc = (Pos(bx, -by, _z0) * Cylinder(
              1.7, S["SCREW_L"], align=(Align.CENTER, Align.CENTER, Align.MIN))
          + Pos(bx, -by, _z0) * Cylinder(
              3.0, 2.5, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    screws = sc if screws is None else screws + sc
_sh_placed = Pos(0, 0, -S["SHROUD_OD"]) * SHROUD
CUT = Pos(0, -60, -25) * Box(300, 120, 130, align=(Align.CENTER,)*3)
rgba, _ = render_multi([(COVER & CUT, DEEP), (_sh_placed & CUT, BLUE),
                        (screws & CUT, STEEL)],
                       az=28, el=-18, W=1150, H=800)
png("cad/out/sub_shroud_fixing.png", rgba)
out.append({"name": "sub_shroud_fixing",
            "title": "SHROUD FIXING - sectioned through two bosses",
            "note": f"Four M3 x {S['SCREW_L']:.0f} 316. They enter at the LOUVRED face - the "
                    f"only face you can still reach once the shroud is on - run the full depth "
                    f"of a corner boss and stop in a blind pilot {H['SHROUD_PILOT_DEEP']} mm "
                    f"deep in the cover. Nothing passes through the plate: a fan shroud is not "
                    f"worth a hole in the pressure boundary. The pilots are also set inboard so "
                    f"that forming a thread does not swell the cord's sealing land."})

# ── the one thing that crosses the boundary ───────────────────────────────
wire = None
for a, b in (((WIRE_X, -WIRE_Y, -34), (WIRE_X, -WIRE_Y, 12)),):
    wire = Pos(a[0], a[1], a[2]) * Cylinder(2.0, b[2] - a[2],
                                            align=(Align.CENTER, Align.CENTER, Align.MIN))
pot = Pos(WIRE_X, -WIRE_Y, COVER_T - 0.3) * Box(9.0, 16.0, 3.3,
                                                align=(Align.CENTER, Align.CENTER, Align.MIN))
NEAR = Pos(WIRE_X, -WIRE_Y, -10) * Box(80, 80, 70, align=(Align.CENTER,)*3)
rgba, _ = render_multi([(COVER & NEAR, DEEP), (wire, COPPER), (pot & NEAR, (0.25, 0.25, 0.27))],
                       az=36, el=-26, W=1050, H=760)
png("cad/out/sub_wire_pass.png", rgba)
out.append({"name": "sub_wire_pass",
            "title": "FAN LEADS - the only penetration that is not a screw",
            "note": f"O{WIRE_D:.0f} at ({WIRE_X:.1f}, {WIRE_Y:.0f}), in the 10.7 mm strip between "
                    f"the heatsink seat and the shroud wall, so it sits UNDER the shroud where "
                    f"spray cannot reach it. The rectangular dam on the inner face is a cup for "
                    f"the potting compound - a flat face lets it run off before it cures. "
                    f"Countersunk on the weather side so the plug has a fillet to key into."})

# ── the three bulkhead fittings, in their blocks ──────────────────────────
# A whole-cover render shows three small holes on a face you cannot see, which
# is why all three were allowed to sit in mid air for three revisions. These two
# views exist to show WHICH face they are in and WHICH WAY they point.
BACK = H["DEPTH"] + H["GASKET_C"] + H["COVER_T"]
def _asm(shape):
    """Cover-local -> assembled: flown Rot(180,0,0) onto the back of the unit,
    so that DOWN in these pictures is down on the boat. The first cut of this
    view drew the cover in its own frame, where +y is the boat's DOWN, and every
    fitting appeared to point at the sky."""
    return Pos(0, 0, BACK) * Rot(180, 0, 0) * shape

def fit_parts(crop):
    plate = _asm(COVER & crop)
    out_ = [(plate, DEEP)]
    # The block's OUTER face is shell y = BLK_Y0 (-76), i.e. cover-local +76.
    # Rot(90,0,0) sends a cylinder's +z along -y, so each body is positioned
    # beyond the face and grows back toward it. The first cut of this put them
    # at the block's mid-plane growing inward, i.e. inside the bay.
    _y0 = -BLK_Y0
    # (x, bore, flange, colour, which block face it comes out of). The SMA is
    # in the TOP block and faces UP; the other two are in the bottom blocks and
    # face DOWN. Drawing all three on one face put the aerial under the boat.
    for _x, _bore, _fl, _col, _face in ((GL_X, 14.5, 22.0, STEEL, BLK_Y0),
                                        (VENT_X, 10.5, 19.0, STEEL, BLK_Y0),
                                        (SMA_X, 8.2, 12.7, BRASS, H["BLK_TY0"])):
        _out = -1.0 if _face < 0 else 1.0
        _y0 = -_face
        body = (Pos(_x, _y0 + _out*6.0, BORE_Z) * Rot(90*_out, 0, 0)
                * Cylinder(_fl/2, 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        _len = 24.0 if _face < 0 else 90.0        # the aerial is a whip, not a tail
        tail = (Pos(_x, _y0 + _out*(6.0 + _len), BORE_Z) * Rot(90*_out, 0, 0)
                * Cylinder(_bore/2 - 1.0, _len, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        # cropped like the plate, or the vent floats in space beside a detail
        # of the Pi-side block
        _b, _t = body & crop, tail & crop
        if _b is not None and _b.volume > 1:
            out_ += [(_asm(_b), _col), (_asm(_t), DARK)]
    return out_

WIDE = Pos(0, 0, -BUMP_H/2) * Box(400, 260, 160, align=(Align.CENTER,)*3)
rgba, _ = render_multi(fit_parts(WIDE), az=210, el=150, W=1150, H=780)
png("cad/out/sub_fittings_context.png", rgba)
out.append({"name": "sub_fittings_context",
            "title": "CABLE ENTRY, VENT AND COAX - where they are",
            "note": f"Seen from behind and below. All three are in blocks that fill the "
                    f"dead pockets beside the bay bumps, and all three bore HORIZONTALLY and "
                    f"exit DOWNWARD. Nothing is on the cover's flat face - the bays own it, "
                    f"and the three fittings used to be placed in that void with nothing "
                    f"under them."})

NEAR = Pos(GL_X + 10, -BLK_Y0 - 10, -BUMP_H/2) * Box(120, 130, 110, align=(Align.CENTER,)*3)
rgba, _ = render_multi(fit_parts(NEAR), az=200, el=145, W=1050, H=760)
png("cad/out/sub_fittings_detail.png", rgba)
out.append({"name": "sub_fittings_detail",
            "title": "THE Pi-SIDE BLOCK - M16 gland, facing down",
            "note": f"M16x1.5 straight gland at x={GL_X:.0f}, tapped into the block and "
                    f"wrenched from below with the cover on the bench, before anything else "
                    f"is fitted. Facing down means an automatic drip loop, no standing water "
                    f"on a seal and no sun on a nylon gland. The M8 SMA is NOT here any more "
                    f"- it moved to the TOP block of the driver bump at x={SMA_X:.0f}, where "
                    f"it bores upward and the whip can stand up."})

# ── the GPS chimney, sectioned, with the foil called out ─────────────────
if "GPS_X" in H:
    GX, GZ = H["GPS_X"], H["GPS_Z"]
    _gy = -(H["BLK_TY0"] + H["BLK_TY1"])/2
    # the module, where it ends up: patch upward, under the radome
    _mod = Pos(GX, -(H["BLK_TY0"] - H["GPS_WIN_T"] - H["GPS_T"]/2 - 0.5), GZ) * Box(
        H["GPS_L"], H["GPS_T"], H["GPS_W"], align=(Align.CENTER,)*3)
    # what you line with copper: the four walls and the shelf, never the window
    _foil = (Pos(GX, -(H["BLK_TY1"] - 1.0), GZ) * Box(
                 H["GPS_L"] + 3, 1.0, H["GPS_W"] + 3, align=(Align.CENTER,)*3))
    _CUT = Pos(GX, 0, GZ) * Box(200, 300, 150, align=(Align.CENTER,)*3)
    _half = Pos(GX - 60, 0, GZ) * Box(120, 300, 150, align=(Align.CENTER,)*3)
    rgba, _ = render_multi([(_asm((COVER & _CUT) - _half), DEEP),
                            (_asm(_mod), (0.20, 0.55, 0.35)),
                            (_asm(_foil), (0.80, 0.50, 0.22))],
                           az=150, el=-26, W=1100, H=780)
    png("cad/out/sub_gps.png", rgba)
    out.append({"name": "sub_gps",
                "title": "GPS - shielded chimney in the -x top block",
                "note": f"Sectioned. The module pushes UP from inside the Pi bay and sits on "
                        f"two shelves under a {H['GPS_WIN_T']} mm ASA radome - ASA is "
                        f"RF-transparent, so the window is the only thing between the patch "
                        f"and the sky. ORANGE is where the copper foil goes: the four walls "
                        f"and the shelf UNDER the module, which is both the EMI shield and "
                        f"the ground plane a patch needs and does not have inside a plastic "
                        f"box. Never foil the window. Bond to system ground at ONE point - "
                        f"ungrounded foil is a reflector and two bonds are a loop. It sits "
                        f"{abs(GX - H['SMA_X']):.0f} mm from the whip, which is the point: a "
                        f"400-470 MHz transmitter any closer desenses L1 on every key-down."})

# ── the coax route, SMA bulkhead to RTL-SDR ───────────────────────────────
# This view exists because the owner asked "how does the coax get to the SDR"
# and the honest answer was that it could not: all three bulkhead bores ended
# 3 mm short of the bay, and the dongle had an X and no Y. Both are fixed; this
# is the picture that shows it, and it is drawn from housing.json so it cannot
# drift from the model the way a hand-made diagram would.
import math
SDR_X, SDR_Y, SDR_L = H["SDR_X"], H["SDR_Y"], H["SDR_L"]
SDR_W, SDR_T = H["SDR_W"], H["SDR_T"]
BAY_Y_IN, WALL_ = H["BAY_Y_IN"], H["WALL"]
_floor = -H["PI_BUMP_H"] + WALL_
# Sectioned at the SMA end of the bay, which is the only place the route is
# visible: a whole-cover view puts the dongle behind 80 mm of bay wall.
# Cropped to the SMA end of the bay, and the PLATE IS TRANSLUCENT - the one
# idiom in render_multi for showing what is packed inside a box you cannot
# cut open. A solid plate hides the bulkhead behind the bay's end wall from
# every angle that also shows the dongle.
_cut = Pos(SDR_X - 14, -46.0, -H["PI_BUMP_H"]/2) * Box(80, 60, 92, align=(Align.CENTER,)*3)
_plate = COVER & _cut
# the dongle, standing on edge on its two strap bridges
_dong = Pos(SDR_X, -SDR_Y, _floor + H["TIE_H"] if "TIE_H" in H else _floor + 3.5) * Box(
    SDR_T, SDR_L, SDR_W, align=(Align.CENTER, Align.CENTER, Align.MIN))
# the bulkhead: barrel through the block, nut inside the bay
_barrel = (Pos(SMA_X, -(BAY_Y_IN + 7.0), BORE_Z) * Rot(-90, 0, 0)
           * Cylinder(H["SMA_D"]/2 - 0.6, 20.0, align=(Align.CENTER, Align.CENTER, Align.MIN)))
_nut = (Pos(SMA_X, -BAY_Y_IN, BORE_Z) * Rot(-90, 0, 0)
        * extrude(RegularPolygon(H["SMA_NUT_AF"]/2/math.cos(math.pi/6), 6), 3.0))
# the pigtail: bulkhead inner end -> the dongle's connector end
_a = Vector(SMA_X, -BAY_Y_IN, BORE_Z)
_b = Vector(SDR_X, -H["SDR_CONN_END"], _floor + 3.5 + SDR_W/2)
_d = _b - _a
_coax = (Plane(origin=tuple(_a), z_dir=tuple(_d.normalized()),
               x_dir=(0, 0, 1) if abs(_d.normalized().Z) < 0.9 else (1, 0, 0))
         * Cylinder(1.4, _d.length, align=(Align.CENTER, Align.CENTER, Align.MIN)))
_dcut = _dong & _cut
rgba, _ = render_multi([(_asm(_plate), (0.13, 0.31, 0.60, 0.42)),
                        (_asm(_dcut), (0.22, 0.60, 0.38)),
                        (_asm(_barrel), BRASS), (_asm(_nut), STEEL),
                        (_asm(_coax), COPPER)], az=36, el=28, W=1150, H=820)
png("cad/out/sub_coax_path.png", rgba)
out.append({"name": "sub_coax_path",
            "title": "COAX - SMA bulkhead to the RTL-SDR",
            "note": f"The hole does not pass a cable: it holds a BULKHEAD. The whip screws "
                    f"on outside, the barrel fills the &Oslash;{H['SMA_D']} bore through the "
                    f"top block, and its nut lands in open bay. GREEN is the "
                    f"{SDR_L:.0f}&nbsp;&times;&nbsp;{SDR_W:.0f}&nbsp;&times;&nbsp;{SDR_T:.0f} "
                    f"dongle STANDING ON EDGE on two strap bridges, centred in the "
                    f"{H['SDR_CHAN_OUT'] - H['SDR_CHAN_IN']:.2f} mm channel between the driver "
                    f"board and the bay wall - centred because the tie has to come up BOTH "
                    f"sides. ORANGE is the pigtail: <b>{H['SDR_PIGTAIL']:.0f} mm</b>, so a "
                    f"stock jumper covers it. Use a RIGHT-ANGLE SMA on the bulkhead end; "
                    f"RG316 bends to 10 mm radius and there is less than that in line."})

# ── the tilt-knob nyloc: where it is, and what it looks like seated ───────
# "I can't find them" - fair. Two pockets, both on the rear cover, and they are
# hard to spot for three reasons at once: they face SIDEWAYS toward the
# centreline, the trunnions are on the BED side when the cover prints
# bumps-down, and the mouth is an 8 mm hex in a 12 mm web.
#
# Two views, because "where is it" and "what does it look like" are different
# questions. The first was answered with a translucent plate and it was mush;
# a section and a highlighted locator are the honest answers.
from parts_lib import nyloc as _nyloc
TX, WT, ST = H["TRUN_X"], H["TRUN_WEB_T"], H["TRUN_STAND"]
TL, TB = H["TRUN_LAND"], H["TRUN_BORE"]
AF, ND = H["TRUN_NUT_AF"], H["TRUN_NUT_DEEP"]
_ty, _tz = -H["TILT_Y"], -ST
HOT = (0.90, 0.36, 0.10)

# THE ENTRY POINT. The first cut of this highlighted the trunnion in orange from
# behind - which shows the OUTBOARD face and its bolt bore, i.e. the one hole
# that is NOT where the nut goes. Useless, and the owner said so.
#
# The fix is not a camera angle, it is the crop: keep only what lies OUTBOARD of
# the mouth plane, so the web's inboard face - the face with the hex in it - is
# the nearest surface and nothing can stand in front of it.
_mouth_x = -(TX - WT)
_bay_x = H["SDR_CHAN_OUT"] if False else (abs(H["PI_BUMP_CX"]) + H["PI_BUMP_L"]/2 - H["WALL"])
_tight = Pos(-(_bay_x + (TX - WT + ND - _bay_x)/2 + 0.2), _ty, _tz) * Box(
    TX - WT + ND - _bay_x, 60, 64, align=(Align.CENTER,)*3)
rgba, _ = render_multi([(_asm(COVER & _tight), (0.16, 0.42, 0.78))],
                       az=252, el=18, W=1000, H=800)
png("cad/out/sub_trunnion_where.png", rgba)
out.append({"name": "sub_trunnion_where",
            "title": "TILT-KNOB NYLOC - the entry point",
            "note": f"<b>This is the hole the nut goes in.</b> An "
                    f"{AF:.0f}&nbsp;mm A/F hex, seen from inside the bay - which is where the nut goes "
                    f"in. It runs through the bay&rsquo;s end wall and on to its seat at "
                    f"|x|&nbsp;{TX-WT+ND:.0f}. It sits <b>vertex up</b>, and that is "
                    f"deliberate: the pocket is a horizontal blind hole in a part that prints "
                    f"bumps-down, and a vertex-up hex bridges itself. A flat-up hex would need "
                    f"support inside a hole 8 mm across. The round bore behind it is the "
                    f"&Oslash;{TB} the M5 comes through from the other side."})

# WHAT IT LOOKS LIKE SEATED. Section on the bore axis: az=0/el=0 is an elevation
# along +Y, and the renderer draws far-first, so the NEAR half is the one to cut
# away or the camera sees the outside of the remaining block.
_crop = Pos(-TX + 4, _ty, _tz) * Box(72, 80, 76, align=(Align.CENTER,)*3)
_half = Pos(-TX + 4, _ty - 40, _tz) * Box(220, 80, 220, align=(Align.CENTER,)*3)
_sec = (COVER & _crop) - _half
_nut = (Pos(-(TX - WT), _ty, _tz) * Rot(0, -90, 0) * _nyloc(AF, ND - 1.0, TB)) - _half
rgba, _ = render_multi([(_sec, (0.16, 0.42, 0.78)), (_nut, STEEL)],
                       az=0, el=0, W=1100, H=820)
png("cad/out/sub_trunnion_nut.png", rgba)
out.append({"name": "sub_trunnion_nut",
            "title": "TILT-KNOB NYLOC - sectioned, nut seated",
            "note": f"Cut on the bore axis. The hex pocket is <b>{AF:.0f} mm A/F &times; "
                    f"{ND:.0f} deep</b> seated at <b>|x|&nbsp;{TX-WT+ND:.0f}</b>, and the hex runs all "
                    f"the way back to the BAY so the nut can be fitted from inside the cover - "
                    f"through rev D it stopped at the lug and was sealed shut behind the bay "
                    f"wall. The M5 comes the other way, from OUTBOARD, through "
                    f"{TL:.0f} mm of land and {WT:.0f} of web, and pulls into the nyloc: steel "
                    f"against steel with the ASA only in compression, which is the one thing it "
                    f"is good at. <b>{WT - ND:.0f} mm of web stays behind the nut.</b>"})

json.dump(out, open("cad/out/subdims.json", "w"), indent=1)
for v in out:
    print(f"  {v['name']}.png  -  {v['title']}")
