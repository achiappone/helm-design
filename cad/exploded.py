"""Three exploded views; one as a numbered CAD-style assembly drawing."""
import sys, json, base64
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
    (34, Pos(0, 0, 860) * Rot(180, 0, 0) * finned(H["HS_L"], H["HS_W"], H["HS_H"], base=3.0,
                                                  fin_t=1.4, gap=2.6, along_x=False), ALLOY, (80, 0, 856)),
    (35, Pos(0, 0, 1000) * FAN, (0.42,0.30,0.26), (100, 0, 1010)),
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
    (32, Pos(118, 0, 1120) * SHROUD_F, BLUE2, (200, 0, 1150)),
    (9,  Pos(-150, -230, 1290) * LP24_SH, BLUE, (-215, -230, 1300)),
    (10, Pos(-150, -230, 1230) * LP24_CL, BLUE2, None),
    # ITEM 15 WAS DELETED BY ACCIDENT when the old antenna block came out of
    # this list, and it had been wrong before that anyway - drawn as an
    # 18 x 18 x 8.6 box, which is the GPS module's envelope, at the rev B
    # antenna position on the shell's top wall. It is a 68 x 27 x 12 dongle and
    # it lives in the driver bay, under the bulkhead it feeds.
    # clear of the cover in x and dropped below it, or the dongle disappears
    # behind the plate in the projection and the balloon points at nothing
    (15, Pos(H["DRV_CX"] + 110, 0, 620) * sdr, SDR_G, (H["DRV_CX"] + 165, 0, 616)),
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
parts = [(sh, col) for _n, sh, col, _a in ITEMS]
BALLOONS = [(n, a) for n, _sh, _c, a in ITEMS if a is not None]

# exp_c is the SAME stack seen from BEHIND. The two front views show the
# display side of every part, which is the wrong side for the half of this BOM
# that lives on the cover - the bumps, the blocks, the three fittings, the
# shroud's louvres and all four bail parts only read from the back.
for name, az, el in (("cad/out/exp_a.png", 205, -126),
                     ("cad/out/exp_b.png", 248, -118),
                     ("cad/out/exp_rear.png", 25, -126)):
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
a0, a1 = proj((0, 0, -470)), proj((0, 0, 1330))
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
