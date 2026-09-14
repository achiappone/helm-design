"""Three exploded views; one as a numbered CAD-style assembly drawing."""
import sys, json, base64, math
sys.path.insert(0, "cad")
from build123d import *
from parts_lib import (pi4, armor_lite, pican_m, drok as _drok, breakout, finned,
                       nyloc, cap_screw, push_button, driver_board, rtl_sdr,
                       sensor_breakout, lobe_knob)

def _solid(path):
    """import_step may return a Compound; a Location on the wrapper is
    ignored by booleans, so hand back the Solid itself."""
    s = import_step(path)
    return s.solids()[0] if len(s.solids()) == 1 else s
from render import render_multi, png

H = json.load(open("cad/out/housing.json"))
B = json.load(open("cad/out/bail.json"))
DISP_CX = H["DISP_CX"]
SHELL = _solid("cad/out/helm_shell_revC.stp")
COVER = _solid("cad/out/helm_cover_revC.stp")
VISOR = _solid("cad/out/helm_visor_revC.stp")
BAIL_B  = _solid("cad/out/bail_base_revA.stp")
BAIL_A  = _solid("cad/out/bail_arm_revA.stp")
SHROUD_F = _solid("cad/out/heatsink_shroud_revD.stp")
LP24_SH = _solid("cad/out/lp24_shroud_revD.stp")
LP24_CL = _solid("cad/out/lp24_clamp_revD.stp")
# Two 80 x 80 x 25 fans as envelopes - the NF-F12 STEP that used to be imported
# here was the single 120 mm fan the shroud no longer takes.
FAN = (Box(80, 80, 25, align=(Align.CENTER, Align.CENTER, Align.MIN))
       + Pos(0, 80, 0) * Box(80, 80, 25, align=(Align.CENTER, Align.CENTER, Align.MIN)))
FAN = Pos(0, -40, 0) * FAN

BLUE=(0.16,0.42,0.78); BLUE2=(0.13,0.34,0.64); GLASS=(0.10,0.12,0.16)
GREEN=(0.10,0.42,0.24); DGREEN=(0.07,0.30,0.18); ALLOY=(0.62,0.65,0.69)
BLACK=(0.13,0.13,0.15); STEEL=(0.78,0.79,0.82)
# One colour per BOARD, not one colour for "a PCB". Every board used to be GREEN
# or DGREEN - the Pi, the HAT, the MCP23017 and all three breakouts - so in a
# colour render they were six identical green rectangles and you had to count
# balloons to work out which was which. Distinct hues cost nothing and make the
# stack readable without the BOM.
PI_G   = (0.11, 0.46, 0.26)     # Raspberry Pi 4
HAT_R  = (0.58, 0.16, 0.18)     # PiCAN-M - CAN boards are red, and it reads
DROK_T = (0.12, 0.43, 0.47)     # DROK buck converter
MCP_P  = (0.40, 0.25, 0.55)     # MCP23017 expander
BRK_A  = (0.76, 0.47, 0.12)     # sensor breakouts
SDR_G  = (0.20, 0.55, 0.35)     # RTL-SDR

# Balloon captions. A bare number means cross-referencing the BOM to read the
# drawing; the name is the thing you actually wanted.
NAMES = {
    1: "Visor",            2: "Front shell",      3: "12.3in display",
    4: "LCD driver board",
    5: "DROK buck",        6: "Raspberry Pi 4",   7: "PiCAN-M HAT",
    8: "Rear cover",       9: "LP-24 shroud",    10: "Strain clamp",
    12: "MCP23017",       13: "Sensor breakout", 15: "RTL-SDR",
    14: "Audio ADC + DAC", 25: "LP-24 connector",
    26: "M16 cable gland", 27: "M12 Gore vent",
    16: "Encoder",        17: "Push button",     28: "SMA bulkhead",
    31: "Bail base",      32: "Fan shroud",     34: "Heatsink 150x74x10",
    35: "80 mm IP67 fan x2", 36: "Whip antenna",
    38: "RG316 pigtail",
}
# 33 IS GONE. It was the 114 alloy heat plate, and the BOM on the build page has
# no row for it any more - the heatsink's own base closes the aperture. ITEMS
# below still LAYS OUT that plate and a pair of 100x40 strip heatsinks at 34, so
# the drawing is one revision behind this dict; cad/build_review.py says so on
# the page rather than letting a reader chase balloon 33 through the BOM.

disp = Box(305, 125, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))

# sensor breakouts, from the Adafruit fab prints
mcp23017 = sensor_breakout(35.0, 25.4)   # expander, a bit bigger than a breakout
brk      = sensor_breakout(25.40, 17.78)
# RTL-SDR, 68 x 27 x 12. It STANDS ON EDGE in the driver bay: the bay's void is
# 75 x 118 and the driver board takes 55 of the width, which leaves a 19 mm
# strip down one side - too narrow to lay a dongle flat, wide enough to stand
# one in. The two tie anchors on that bay's floor are what strap it down, and
# the SMA bulkhead it feeds is directly above it in the top block.
sdr      = Rot(0, 90, 0) * Rot(0, 0, 90) * rtl_sdr()
# SMA bulkhead + whip. Antenna is 185 mm; shown truncated so the sheet fits.
# SMA female bulkhead, M16 waterproof box: hex body, O-ring, threaded shank
sma_bulk = (Cylinder(10.0, 9, align=(Align.CENTER, Align.CENTER, Align.MIN))
            + Pos(0, 0, 9) * Cylinder(8.0, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
            + Pos(0, 0, 11) * Cylinder(4.0, 8, align=(Align.CENTER, Align.CENTER, Align.MIN)))
# HYS whip, 185 mm: base collar, taper, thin element, tip section
whip = (Cylinder(6.5, 34, align=(Align.CENTER, Align.CENTER, Align.MIN))
        + Pos(0, 0, 34) * Cone(6.5, 2.0, 14, align=(Align.CENTER, Align.CENTER, Align.MIN))
        + Pos(0, 0, 48) * Cylinder(1.6, 95, align=(Align.CENTER, Align.CENTER, Align.MIN))
        + Pos(0, 0, 143) * Cone(2.0, 5.5, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
        + Pos(0, 0, 153) * Cylinder(5.5, 32, align=(Align.CENTER, Align.CENTER, Align.MIN)))
# RG316 pigtail, 150 mm, bulkhead to SMA male
pigtail = sweep(Circle(1.3), path=Spline((0, 0, 0), (-26, 14, -34), (-40, 6, -78),
                                         (-20, -18, -112), (10, -22, -140)))
# Recognisable envelopes, shared with assembly.py and subassemblies.py so the
# three views cannot drift. See cad/parts_lib.py for what these are and are not.
pi   = pi4()
armor = armor_lite()
hat  = pican_m()
drok = _drok()

# item number -> (shape, colour, balloon anchor)  numbers match the BOM
ITEMS = [
    (1, Pos(0, 0, -390) * VISOR,             BLUE,   (0, 30, -390)),
    (2, Pos(0, 0, -150) * SHELL,             BLUE,   (-160, 40, -130)),
    (3, Pos(DISP_CX, H["DISP_CY"], 110) * disp,         GLASS,  (DISP_CX-120, H["DISP_CY"], 115)),
    (4, Pos(140, 0, 470) * Rot(0, 0, 90) * driver_board(), (0.12,0.43,0.47),
        (200, 0, 474)),
    (5, Pos(-140, 45, 470) * drok,           DROK_T,  (-160, 45, 480)),
    (6, Pos(80, -25, 460) * pi,              PI_G,  (120, -25, 462)),
    (6, Pos(80, -25, 496) * armor,            ALLOY,  None),
    (7, Pos(80, -25, 560) * hat,             HAT_R, (120, -25, 532)),
    (8, Pos(0, 0, 700) * COVER,              BLUE2,  (165, 0, 706)),
    (31, Pos(0, -300, 760) * BAIL_B,         (0.10,0.26,0.52), (-190, -300, 756)),
    (31, Pos(-250, -120, 700) * BAIL_A,      (0.10,0.26,0.52), None),
    (31, Pos( 250, -120, 700) * Rot(0, 180, 0) * BAIL_A, (0.10,0.26,0.52), None),
    # ONE 150 x 74 x 10 heatsink, base-out, where a 114 alloy plate and two
    # 100 x 40 x 20 strips used to be ballooned - parts that left the design
    # two revisions before this view stopped drawing them.
    (34, Pos(0, 0, 880) * Rot(180, 0, 0) * finned(H["HS_L"], H["HS_W"], H["HS_H"], base=3.0,
                                                  fin_t=1.4, gap=2.6, along_x=False), ALLOY, (80, 0, 856)),
    (35, Pos(0, 0, 1120) * FAN, (0.42,0.30,0.26), (120, 0, 1020)),
    # THE CONTROLS, at their real positions. They were drawn as a COLUMN at
    # x=-159.5 - the rev B layout, deleted when the controls moved into a ROW
    # under the display. The drawing kept showing four buttons stacked up the
    # left-hand bezel, which is not where a single one of them is. Read from
    # housing.json now, so the sheet cannot disagree with the part again.
    (17, Pos(H["BTN_X"][0], H["ROW_CY"], -250) * push_button(H["BTN_D"], 17.5), BLACK, (H["BTN_X"][0]+60, H["ROW_CY"]-30, -254)),
    (17, Pos(H["BTN_X"][1], H["ROW_CY"], -250) * push_button(H["BTN_D"], 17.5), BLACK, None),
    (17, Pos(H["BTN_X"][2], H["ROW_CY"], -250) * push_button(H["BTN_D"], 17.5), BLACK, None),
    (17, Pos(H["BTN_X"][3], H["ROW_CY"], -250) * push_button(H["BTN_D"], 17.5), BLACK, None),
    (16, Pos(H["ENC_X"], H["ROW_CY"], -250) * Cylinder(10.25, 17.5), (0.72,0.60,0.25), (H["ENC_X"]-60, H["ROW_CY"]-30, -254)),
    # the shroud was off at x=118 while the heatsink and fans it covers sat on
    # x=0. Three parts of one stack, drawn on two different axes.
    (32, Pos(0, 0, 1400) * SHROUD_F, BLUE2, (150, 0, 1430)),
    (9,  Pos(-150, -230, 1620) * LP24_SH, BLUE, (-215, -230, 1300)),
    (10, Pos(-150, -230, 1560) * LP24_CL, BLUE2, (-215, -230, 1236)),
    # ITEM 15 WAS DELETED BY ACCIDENT when the old antenna block came out of
    # this list, and it had been wrong before that anyway - drawn as an
    # 18 x 18 x 8.6 box, which is the GPS module's envelope, at the rev B
    # antenna position on the shell's top wall. It is a 68 x 27 x 12 dongle and
    # it lives in the driver bay, under the bulkhead it feeds.
    # clear of the cover in x and dropped below it, or the dongle disappears
    # behind the plate in the projection and the balloon points at nothing
    (15, Pos(H["DRV_CX"] + 110, 0, 620) * sdr, SDR_G, (H["DRV_CX"] + 165, 0, 616)),
    # ---- the five the cross-check found with no shape on the sheet -------
    # A BOM row nobody can point at is a part the builder has to find by
    # reading prose. Each of these is where it is actually fitted.
    (26, Pos(H["GL_X"], -132, 700) * Rot(90, 0, 0)
         * Cylinder(11.0, 30, align=(Align.CENTER, Align.CENTER, Align.MIN)), ALLOY,
         (H["GL_X"] - 70, -150, 700)),
    (27, Pos(H["VENT_X"], -132, 700) * Rot(90, 0, 0)
         * Cylinder(9.5, 20, align=(Align.CENTER, Align.CENTER, Align.MIN)), ALLOY,
         (H["VENT_X"] + 70, -150, 700)),
    (36, Pos(H["SMA_X"], 215, 700) * Rot(-90, 0, 0) * whip, BLACK,
         (H["SMA_X"] + 80, 300, 700)),
    (25, Pos(-150, -230, 1700) * Rot(0, 0, 0)
         * Cylinder(16.5, 30, align=(Align.CENTER, Align.CENTER, Align.MIN)), ALLOY,
         (-230, -230, 1370)),
    (14, Pos(-250, 120, 690) * breakout(30.0, 20.0), (0.35,0.30,0.55),
         (-320, 120, 686)),
    (12, Pos(-155, 42, 690) * mcp23017,      MCP_P, (-200, 42, 686)),
    (13, Pos(-155, 4, 690) * brk,            BRK_A, (-200, 4, 686)),
    (13, Pos(-72, -50, 690) * brk,           BRK_A, None),
    (13, Pos(-30, -50, 690) * brk,           BRK_A, None),
    # THE AERIAL GOES ON TOP OF THE +x BUMP. It was laid out here at x=-165 on
    # the shell's top wall, which is the rev B position - the bulkhead has been
    # on the rear cover for two revisions and is now in the TOP block of the
    # driver bump, boring UP. Exploded along +y, the way it is fitted.
    (28, Pos(H["SMA_X"], 150, 700) * Rot(-90, 0, 0) * sma_bulk, ALLOY,
         (H["SMA_X"] + 70, 150, 700)),
    (38, Pos(H["SMA_X"] - 10, 96, 700) * Rot(-90, 0, 0) * pigtail, (0.78,0.55,0.42),
         (H["SMA_X"] + 70, 96, 700)),
    # THE PIVOT HARDWARE. Four M5 316 nylocs and two bolts that the sheet never
    # drew, so the one question the drawing exists to answer - where does the
    # nut go - had no answer on it.
    # Placed OUTBOARD OF THE JOINT THEY BELONG TO, not in a hardware pile:
    # the visor pair beside the shell's pivot ears, the bail pair beside the
    # cover's trunnions. Where the nut goes is the question this sheet exists
    # to answer.
    (19, Pos(-200, H["PIV_Y"], -150) * Rot(0, -90, 0) * nyloc(8.0, 4.0), STEEL,
         (-250, H["PIV_Y"], -146)),
    (19, Pos(-232, H["PIV_Y"], -150) * Rot(0, -90, 0) * cap_screw(5.0, 25.0), STEEL, None),
    (20, Pos(-200, H["TILT_Y"], 700) * Rot(0, -90, 0)
         * nyloc(H["TRUN_NUT_AF"], H["TRUN_NUT_DEEP"] - 1.0, H["TRUN_BORE"]), STEEL,
         (-250, H["TILT_Y"], 704)),
    (20, Pos(-236, H["TILT_Y"], 700) * Rot(0, -90, 0)
         * lobe_knob(stud=B["KNOB_STUD"], boss_d=B["KNOB_BOSS_D"]), (0.20,0.20,0.22), None),
]
# ══════════════════════════════════════════════ AND IT HAS TO BE VISIBLE
# Being in ITEMS is not the same as being READABLE. Item 15 was in the list,
# ballooned, and rendering - on top of the Pi stack, where you could not pick it
# out. The fans were on x=0 while the shroud that covers them was on x=118.
# Both passed every check there was, because every check asked "is it drawn".
#
# So the layout SOLVES ITSELF. The structural stack stays where it is, because
# its positions mean something - that is the order the thing comes apart in.
# Every other item is then placed one at a time, and if its projected box is
# buried under what is already down, it gets pushed outward until it is not.
# Hand-tuning 28 positions against a projection is a job nobody can do twice.
STACK = {1, 2, 3, 8, 31, 32, 34, 35, 9}      # the assembly axis itself
MAX_COVER = 0.45                              # of its own area, before it moves


def _bbox2d(shape, proj):
    b = shape.bounding_box()
    pts = [proj((x, y, z)) for x in (b.min.X, b.max.X)
           for y in (b.min.Y, b.max.Y) for z in (b.min.Z, b.max.Z)]
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    return min(xs), min(ys), max(xs), max(ys)


def _overlap(a, b):
    w = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    h = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    return w * h


def _covered(box, placed):
    area = max(1.0, (box[2] - box[0]) * (box[3] - box[1]))
    return sum(_overlap(box, o) for o in placed) / area


def solve_layout(items, proj):
    """Return items with the loose hardware nudged clear of everything else."""
    out, placed = [], []
    for n, sh, col, anc in items:                     # the stack first, unmoved
        if n in STACK:
            placed.append(_bbox2d(sh, proj))
            out.append((n, sh, col, anc))
    moved = 0
    for n, sh, col, anc in items:
        if n in STACK:
            continue
        best = None
        for r in (0, 45, 90, 140, 200, 270, 350, 440, 540, 650, 780):
            for ang in range(0, 360, 15) if r else (0,):
                dx = r * math.cos(math.radians(ang))
                dy = r * math.sin(math.radians(ang))
                cand = Pos(dx, dy, 0) * sh
                cov = _covered(_bbox2d(cand, proj), placed)
                if best is None or cov < best[0]:
                    best = (cov, dx, dy, cand)
                if cov <= MAX_COVER:
                    break
            if best[0] <= MAX_COVER:
                break
        cov, dx, dy, cand = best
        if abs(dx) > 1 or abs(dy) > 1:
            moved += 1
        placed.append(_bbox2d(cand, proj))
        out.append((n, cand, col,
                    None if anc is None else (anc[0] + dx, anc[1] + dy, anc[2])))
    return out, moved


_probe = render_multi([(sh, c) for _n, sh, c, _a in ITEMS], 208, -124,
                      W=1200, H=1900, style="line")[1]
ITEMS, _moved = solve_layout(ITEMS, _probe)


# ---- and then COUNT THE PIXELS, because bboxes lie ----------------------
# A bounding box around a thin plate seen edge-on is enormous and almost
# entirely empty, so a box-overlap test calls every small part near the cover
# "buried" and cannot tell the difference between hidden and merely nearby.
#
# This renders the sheet ONCE with every item in a colour of its own and counts
# what survives. A part with no pixels is a part that is not on the drawing,
# whatever the list says - which is the only definition that matters.
def _decode(path):
    import zlib, struct
    d = open(path, "rb").read(); i = 8; idat = b""
    while i < len(d):
        ln = struct.unpack(">I", d[i:i+4])[0]; typ = d[i+4:i+8]
        if typ == b"IHDR":
            w, h, _bd, ct = struct.unpack(">IIBB", d[i+8:i+18])
        elif typ == b"IDAT":
            idat += d[i+8:i+8+ln]
        i += 12 + ln
    raw = zlib.decompress(idat); ch = {0: 1, 2: 3, 4: 2, 6: 4}[ct]
    stride = w*ch; prev = bytearray(stride); out = []; pos = 0
    for _y in range(h):
        f = raw[pos]; pos += 1
        line = bytearray(raw[pos:pos+stride]); pos += stride
        for x in range(stride):
            a = line[x-ch] if x >= ch else 0
            b = prev[x]; c = prev[x-ch] if x >= ch else 0
            if f == 1: line[x] = (line[x]+a) & 255
            elif f == 2: line[x] = (line[x]+b) & 255
            elif f == 3: line[x] = (line[x]+(a+b)//2) & 255
            elif f == 4:
                pp = a+b-c; pa, pb, pc = abs(pp-a), abs(pp-b), abs(pp-c)
                line[x] = (line[x] + (a if (pa <= pb and pa <= pc)
                                      else (b if pb <= pc else c))) & 255
        out.append(bytes(line)); prev = line
    return w, h, ch, out


_KEY = []
for _i, (_n, _sh, _c, _a) in enumerate(ITEMS):
    _KEY.append(((_i % 12) / 12.0 + 0.02, 0.35 + (_i // 12) * 0.25, 0.9))
def _hsv(h, s_, v):
    import colorsys
    return colorsys.hsv_to_rgb(h, s_, v)
_tag = [( _sh, _hsv(*_KEY[_i])) for _i, (_n, _sh, _c, _a) in enumerate(ITEMS)]
png("cad/out/_vis.png", render_multi(_tag, 208, -124, W=1200, H=1900)[0])
_w, _h, _ch, _rows = _decode("cad/out/_vis.png")
_seen = {}
for _y in range(0, _h, 2):
    _r = _rows[_y]
    for _x in range(0, _w, 2):
        _px = (_r[_x*_ch], _r[_x*_ch+1], _r[_x*_ch+2])
        if max(_px) - min(_px) < 12:
            continue                                  # grey: background
        _best, _bd = None, 1e9
        for _i, _k in enumerate(_KEY):
            _t = _hsv(*_k); _dd = sum((_t[_j]*255 - _px[_j])**2 for _j in range(3))
            if _dd < _bd:
                _best, _bd = _i, _dd
        _seen[_best] = _seen.get(_best, 0) + 1
_invisible = [ITEMS[_i][0] for _i in range(len(ITEMS)) if _seen.get(_i, 0) < 3]
if _invisible:
    raise AssertionError(
        "these BOM items are in the drawing but put NO PIXELS on it - they are "
        "hidden behind something (sampled every 2nd pixel, so an 8 mm nut is "
        "only a handful of samples - 0 means gone, not small): " + ", ".join(str(n) for n in sorted(set(_invisible), key=int)))
print(f"  visibility: all {len(ITEMS)} items put ink on the sheet "
      f"(smallest {min(_seen.values())} px)")

parts = [(sh, col) for _n, sh, col, _a in ITEMS]
BALLOONS = [(n, a) for n, _sh, _c, a in ITEMS if a is not None]

parts = [(sh, col) for _n, sh, col, _a in ITEMS]
BALLOONS = [(n, a) for n, _sh, _c, a in ITEMS if a is not None]

# exp_c is the SAME stack seen from BEHIND. The two front views show the
# display side of every part, which is the wrong side for the half of this BOM
# that lives on the cover - the bumps, the blocks, the three fittings, the
# shroud's louvres and all four bail parts only read from the back.
# FOUR angles. One view of an exploded stack always hides something behind
# something else - the layout solver works on ONE projection, and a part it
# cleared on that sheet can still sit behind a neighbour from elsewhere.
for name, az, el in (("cad/out/exp_a.png", 205, -126),      # front three-quarter
                     ("cad/out/exp_b.png", 248, -118),      # from the right
                     ("cad/out/exp_c.png", 165, -132),      # from the left
                     ("cad/out/exp_rear.png", 25, -126)):   # from behind
    png(name, render_multi(parts, az, el, W=1200, H=1900)[0])
    print(f"  {name}")

# ── numbered CAD-style sheet ──────────────────────────────────────────────
W, Hh = 1200, 1900
rgba, proj = render_multi(parts, 208, -124, W=W, H=Hh, style="line")
png("cad/out/exp_cad.png", rgba)
INK = "#1b2430"
svg = [f'<svg viewBox="0 0 {W} {Hh}" xmlns="http://www.w3.org/2000/svg" '
       f'style="width:100%;height:auto;display:block">',
       f'<image href="data:image/png;base64,'
       f'{base64.b64encode(open("cad/out/exp_cad.png","rb").read()).decode()}" '
       f'x="0" y="0" width="{W}" height="{Hh}"/>']

# dash-dot assembly axis running through the stack
a0, a1 = proj((0, 0, -470)), proj((0, 0, 1500))
svg.append(f'<line x1="{a0[0]:.1f}" y1="{a0[1]:.1f}" x2="{a1[0]:.1f}" y2="{a1[1]:.1f}" '
           f'stroke="{INK}" stroke-width="1" stroke-dasharray="14 5 3 5" opacity="0.55"/>')

for n, anchor in BALLOONS:
    ax, ay = proj(anchor)
    side = -1 if ax < W/2 else 1
    bx, by = ax + side*88, ay - 26
    svg.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" '
               f'stroke="{INK}" stroke-width="1.4"/>')
    svg.append(f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="3" fill="{INK}"/>')
    svg.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="16" fill="#fff" '
               f'stroke="{INK}" stroke-width="1.6"/>')
    svg.append(f'<text x="{bx:.1f}" y="{by:.1f}" text-anchor="middle" dy="6.5" '
               f'fill="{INK}" font-family="IBM Plex Mono,monospace" font-size="17" '
               f'font-weight="600">{n}</text>')
svg.append('</svg>')
open("cad/out/exp_cad.svg", "w").write("".join(svg))
print(f"  cad/out/exp_cad.svg  ({len(''.join(svg))//1024} KB, {len(BALLOONS)} balloons)")


# ══════════════════════════════════════════════ EVERY BOM ITEM GETS A BALLOON
# THE RULE: if it is in the bill of materials, it is in this drawing. A BOM row
# with no balloon is a part the builder has to find by reading prose, and a
# balloon with no row is a part they cannot buy.
#
# This has been wrong repeatedly and quietly - item 15 was deleted from ITEMS by
# accident and nothing noticed for two revisions, because the drawing still
# rendered and the BOM still listed it. Neither file can see the other, so the
# check has to reach across: the BOM's numbers are parsed out of
# cad/build_review.py, which is the file that owns them.
import re as _re
_bom_src = open("cad/build_review.py").read()
_BOM = {m for m in _re.findall(r'<tr><td class="m">(\d{1,2})[a-z]?</td>', _bom_src)}
_DRAWN = {str(n) for n, _sh, _c, _a in ITEMS}
_BALLOONED = {str(n) for n, _a in BALLOONS}

# Hardware that is fitted rather than exploded - a bonded washer or a smear of
# sealant has no shape worth a balloon. Named, so the exemption is a decision
# and not an oversight.
_NO_SHAPE = {"11", "21", "22", "23", "24", "29", "30", "39", "40", "41",
             "42", "43", "44", "45", "46", "18"}

_missing_shape = sorted(_BOM - _DRAWN - _NO_SHAPE, key=int)
_missing_balloon = sorted(_BOM - _BALLOONED - _NO_SHAPE, key=int)
_orphan = sorted(_DRAWN - _BOM, key=int)
if _missing_shape or _missing_balloon or _orphan:
    _msg = []
    if _missing_shape:
        _msg.append(f"in the BOM but NOT DRAWN: {', '.join(_missing_shape)}")
    if _missing_balloon:
        _msg.append(f"drawn but NOT BALLOONED: {', '.join(_missing_balloon)}")
    if _orphan:
        _msg.append(f"drawn but NOT IN THE BOM: {', '.join(_orphan)}")
    raise AssertionError("the exploded view and the BOM disagree:\n  - "
                         + "\n  - ".join(_msg))
print(f"  BOM cross-check: {len(_BOM)} rows, {len(_DRAWN)} drawn, "
      f"{len(_BALLOONED)} ballooned, {len(_NO_SHAPE)} fitted-not-exploded")


