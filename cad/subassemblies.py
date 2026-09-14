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
COVER = import_step("cad/out/helm_cover_revC.stp")
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
    for _x, _bore, _fl, _col in ((GL_X, 14.5, 22.0, STEEL),
                                 (SMA_X, 8.2, 12.7, BRASS),
                                 (VENT_X, 10.5, 19.0, STEEL)):
        body = (Pos(_x, _y0 + 6.0, BORE_Z) * Rot(90, 0, 0)
                * Cylinder(_fl/2, 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        tail = (Pos(_x, _y0 + 30.0, BORE_Z) * Rot(90, 0, 0)
                * Cylinder(_bore/2 - 1.0, 24.0, align=(Align.CENTER, Align.CENTER, Align.MIN)))
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
            "title": "THE Pi-SIDE BLOCK - M16 gland and M8 SMA",
            "note": f"M16x1.5 straight gland at x={GL_X:.0f} and an M8x0.75 IP67 SMA at "
                    f"x={SMA_X:.0f}, both tapped straight into the block and both wrenched "
                    f"from below with the cover on the bench, before anything else is "
                    f"fitted. Facing down means an automatic drip loop, no standing water "
                    f"on a seal and no sun on a nylon gland."})

json.dump(out, open("cad/out/subdims.json", "w"), indent=1)
for v in out:
    print(f"  {v['name']}.png  -  {v['title']}")
