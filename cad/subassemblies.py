"""
Subassembly views -- the three things the whole-unit renders cannot show.

A render of the finished unit answers "what does it look like". It does not
answer "where does that go" or "how do I hold it while the glue sets", and
those are the questions that actually come up with a part in your hand. Each
view here exists because a specific question had no picture:

  ANTENNA   it is a hole. In a whole-cover render a O15.75 bore reads as
            nothing at all, and the bought whip has no CAD, so the assembled
            views showed an empty plate. Two views: one close enough to see
            the sealing pad, one far enough back to see WHERE on the cover it
            is - the close-up alone was unreadable without the context.
  THERMAL   the stack is cover -> alloy plate -> heatsinks -> shroud -> fan,
            five parts deep, and only two of them are printed. Exploded along
            the axis, with the fan wire route drawn, because that route is the
            one part of it that is not obvious: the wires do NOT pierce the
            ASA, they go through a grommet in the 6 mm ALLOY PLATE, under the
            shroud where spray cannot reach.
  JIG       what the gluing fixture is for, which is impossible to convey in
            a render of the fixture on its own.

Everything is positioned from cad/out/housing.json. Bought parts with no CAD
are drawn as envelopes - correct size and place, no internal detail.
"""
import sys, json
sys.path.insert(0, "cad")
from build123d import *
from render import render_multi, png

H = json.load(open("cad/out/housing.json"))
COVER = import_step("cad/out/helm_cover_revC.stp")
SHROUD = import_step("cad/out/heatsink_shroud_revD.stp")
JIG = import_step("cad/out/heatsink_jig_revA.stp")

BLUE, DEEP = (0.16, 0.40, 0.74), (0.09, 0.24, 0.48)
ALLOY, STEEL = (0.66, 0.68, 0.72), (0.76, 0.77, 0.80)
BRASS, DARK, COPPER = (0.80, 0.68, 0.24), (0.18, 0.18, 0.20), (0.78, 0.42, 0.18)

AP_CX, HS_L, HS_W, HS_H = H["AP_CX"], H["HS_L"], H["HS_W"], H["HS_H"]
HS_CY, PLATE, HOLE_C = H["HS_CY"], H["HS_PLATE"], H["HS_HOLE_C"]
ANT_X, ANT_Y, SMA = H["ANT_X"], H["ANT_Y"], H["SMA_D"]
out = []

# ── antenna: context, then detail ────────────────────────────────────────
# cover-local y is the shell's y mirrored, so the antenna lands at -ANT_Y
AY = -ANT_Y
def ant_parts(crop):
    plate = COVER & crop
    whip  = Pos(ANT_X, AY, -40) * Cylinder(3.0, 34, align=(Align.CENTER, Align.CENTER, Align.MIN))
    onut  = Pos(ANT_X, AY, -6.0) * Cylinder(10.0, 3.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    bulk  = Pos(ANT_X, AY, -2.0) * Cylinder(SMA/2 - 0.15, 14, align=(Align.CENTER, Align.CENTER, Align.MIN))
    inut  = Pos(ANT_X, AY, 6.2) * Cylinder(10.0, 3.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return [(plate, DEEP), (bulk, BRASS), (whip, DARK), (onut, STEEL), (inut, STEEL)]

WIDE = Pos(0, 0, -6) * Box(400, 220, 90, align=(Align.CENTER,)*3)
rgba, _ = render_multi(ant_parts(WIDE), az=34, el=-30, W=1100, H=720)
png("cad/out/sub_antenna_context.png", rgba)
out.append({"name": "sub_antenna_context",
            "title": "ANTENNA - where it sits on the cover",
            "note": f"O{SMA} bulkhead bore at shell ({ANT_X:.0f}, {ANT_Y:.0f}), "
                    f"top corner of the rear cover, opposite the cable gland."})

NEAR = Pos(ANT_X, AY, -6) * Box(95, 85, 60, align=(Align.CENTER,)*3)
rgba, _ = render_multi(ant_parts(NEAR), az=40, el=-26, W=1000, H=700)
png("cad/out/sub_antenna_detail.png", rgba)
out.append({"name": "sub_antenna_detail",
            "title": "ANTENNA - bulkhead stack",
            "note": "Outside in: whip, outer nut, sealing washer, M16 bulkhead, inner nut. "
                    "The raised pad gives the nut a flat face instead of layer lines."})

# ── thermal stack, exploded, with the wire route ─────────────────────────
# Cover-local: the plate lands on the OUTER face, which is -z.
THERM = Pos(AP_CX, 0, -8) * Box(210, 210, 80, align=(Align.CENTER,)*3)
cov = COVER & THERM
plate = Pos(AP_CX, 0, -34) * Box(PLATE, PLATE, 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
sinks = [Pos(AP_CX, sy*HS_CY, -62) * Box(HS_L, HS_W, HS_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
         for sy in (-1, 1)]
shroud = Pos(AP_CX, 0, -150) * Rot(180, 0, 0) * SHROUD
fan = Pos(AP_CX, 0, -196) * Box(120, 120, H_FAN := 27.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
# the wire route: fan -> shroud pass-through -> grommet in the ALLOY PLATE ->
# inside the housing. Drawn as a polyline of segments so it reads as a path.
wire = None
for a, b in (((AP_CX + 52, 52, -196), (AP_CX + 52, 52, -150)),
             ((AP_CX + 52, 52, -150), (AP_CX + 52, 52, -34)),
             ((AP_CX + 52, 52, -34), (AP_CX + 52, 52, 12))):
    seg = Pos(a[0], a[1], min(a[2], b[2])) * Cylinder(
        2.2, abs(b[2] - a[2]), align=(Align.CENTER, Align.CENTER, Align.MIN))
    wire = seg if wire is None else wire + seg
grommet = Pos(AP_CX + 52, 52, -34) * Cylinder(5.0, 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

rgba, _ = render_multi([(cov, DEEP), (plate, ALLOY)] + [(s, ALLOY) for s in sinks]
                       + [(shroud, BLUE), (fan, DARK), (wire, COPPER), (grommet, (0.25, 0.25, 0.27))],
                       az=38, el=-22, W=1100, H=860)
png("cad/out/sub_thermal_exploded.png", rgba)
out.append({"name": "sub_thermal_exploded",
            "title": "THERMAL STACK - exploded",
            "note": "Cover, 6 mm alloy plate, two heatsinks, shroud, fan. The copper line is "
                    "the fan wire: it leaves the shroud through the O7 pass-through, then goes "
                    "through a GROMMET IN THE ALLOY PLATE - metal, not ASA - and into the "
                    "housing. No printed part is pierced, and the penetration sits under the "
                    "shroud where spray cannot reach it."})

# ── the jig, doing its job ───────────────────────────────────────────────
jplate = Pos(0, 0, 0) * Box(PLATE, PLATE, 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
jig_a = Pos(0, 0, 6.0) * JIG
jsinks = [Pos(0, sy*HS_CY, 30) * Box(HS_L, HS_W, HS_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
          for sy in (-1, 1)]
rgba, _ = render_multi([(jplate, ALLOY), (jig_a, (0.85, 0.45, 0.15))]
                       + [(s, STEEL) for s in jsinks],
                       az=36, el=-26, W=1050, H=740)
png("cad/out/sub_heatsink_jig.png", rgba)
out.append({"name": "sub_heatsink_jig",
            "title": "HEATSINK GLUING JIG - in use",
            "note": f"Orange is the jig. It drops onto the alloy plate located by the same four "
                    f"fixings the shroud uses, and its two pockets hold the heatsinks square at "
                    f"y +/-{HS_CY:.1f} while the thermal adhesive cures. Pockets are through, so "
                    f"squeeze-out escapes instead of lifting the part. Lift it off after."})

json.dump(out, open("cad/out/subdims.json", "w"), indent=1)
for v in out:
    print(f"  {v['name']}.png  -  {v['title']}")
