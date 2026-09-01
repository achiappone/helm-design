"""Three exploded views; one as a numbered CAD-style assembly drawing."""
import sys, json, base64
sys.path.insert(0, "cad")
from build123d import *

def _solid(path):
    """import_step may return a Compound; a Location on the wrapper is
    ignored by booleans, so hand back the Solid itself."""
    s = import_step(path)
    return s.solids()[0] if len(s.solids()) == 1 else s
from render import render_multi, png

H = json.load(open("cad/out/housing.json"))
DISP_CX = H["DISP_CX"]
SHELL = _solid("cad/out/helm_shell_revC.stp")
COVER = _solid("cad/out/helm_cover_revC.stp")
VISOR = _solid("cad/out/helm_visor_revC.stp")
BRACKET = _solid("cad/out/tilt_bracket_revC.stp")
SHROUD_F = _solid("cad/out/heatsink_shroud_revD.stp")
LP24_SH = _solid("cad/out/lp24_shroud_revD.stp")
LP24_CL = _solid("cad/out/lp24_clamp_revD.stp")
_fan_raw = import_step("NF-F12_iPPC_Public-CAD.stp")
_fok = []
for _s in _fan_raw.solids():
    try:
        _s.tessellate(0.25); _fok.append(_s)
    except Exception:
        pass
FAN = _fok[0]
for _s in _fok[1:]:
    FAN = FAN + _s

BLUE=(0.16,0.42,0.78); BLUE2=(0.13,0.34,0.64); GLASS=(0.10,0.12,0.16)
GREEN=(0.10,0.42,0.24); DGREEN=(0.07,0.30,0.18); ALLOY=(0.62,0.65,0.69)
BLACK=(0.13,0.13,0.15)

disp = Box(305, 125, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))

# sensor breakouts, from the Adafruit fab prints
mcp23017 = Box(43.18, 17.78, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
brk      = Box(25.40, 17.78, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
sdr      = Box(68, 27, 12, align=(Align.CENTER, Align.CENTER, Align.MIN))
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
pi   = (Box(85, 56, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
        + Pos(28, 0, 1.6) * Box(28, 50, 13.5, align=(Align.CENTER, Align.CENTER, Align.MIN)))
hat  = Box(65, 56.5, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
drok = Box(65, 58, 20, align=(Align.CENTER, Align.CENTER, Align.MIN))

# item number -> (shape, colour, balloon anchor)  numbers match the BOM
ITEMS = [
    (1, Pos(0, 0, -390) * VISOR,             BLUE,   (0, 30, -390)),
    (2, Pos(0, 0, -150) * SHELL,             BLUE,   (-160, 40, -130)),
    (3, Pos(DISP_CX, H["DISP_CY"], 110) * disp,         GLASS,  (DISP_CX-120, H["DISP_CY"], 115)),
    (5, Pos(-140, 45, 470) * drok,           ALLOY,  (-160, 45, 480)),
    (6, Pos(80, -25, 460) * pi,              GREEN,  (120, -25, 462)),
    (7, Pos(80, -25, 530) * hat,             DGREEN, (120, -25, 532)),
    (8, Pos(0, 0, 700) * COVER,              BLUE2,  (165, 0, 706)),
    (31, Pos(0, -260, 620) * BRACKET,        (0.10,0.26,0.52), (-190, -260, 616)),
    (33, Pos(118, 0, 830) * Box(114, 114, 6, align=(Align.CENTER,)*3), ALLOY, (200, 0, 826)),
    (34, Pos(118, 30, 890) * Box(100, 40, 20, align=(Align.CENTER,)*3), ALLOY, None),
    (34, Pos(118, -30, 890) * Box(100, 40, 20, align=(Align.CENTER,)*3), ALLOY, (200, -30, 886)),
    (35, Pos(118, 0, 1000) * Rot(90, 0, 0) * FAN, (0.42,0.30,0.26), (200, 0, 1010)),
    (17, Pos(-159.5, 45, -250) * Rot(0, 0, 0) * Cylinder(7.5, 21), BLACK, (-215, 45, -254)),
    (17, Pos(-159.5, 21, -250) * Cylinder(7.5, 21), BLACK, None),
    (17, Pos(-159.5, -3, -250) * Cylinder(7.5, 21), BLACK, None),
    (17, Pos(-159.5, -27, -250) * Cylinder(7.5, 21), BLACK, None),
    (16, Pos(-159.5, -55, -250) * Cylinder(10.25, 17.5), (0.72,0.60,0.25), (-215, -55, -254)),
    (32, Pos(118, 0, 1120) * SHROUD_F, BLUE2, (200, 0, 1150)),
    (9,  Pos(-150, -230, 1290) * LP24_SH, BLUE, (-215, -230, 1300)),
    (10, Pos(-150, -230, 1230) * LP24_CL, BLUE2, None),
    (12, Pos(-155, 42, 690) * mcp23017,      DGREEN, (-200, 42, 686)),
    (13, Pos(-155, 4, 690) * brk,            DGREEN, (-200, 4, 686)),
    (13, Pos(-72, -50, 690) * brk,           DGREEN, None),
    (13, Pos(-30, -50, 690) * brk,           DGREEN, None),
    (15, Pos(-150, 150, -140) * Rot(-90,0,0) * Box(18,18,8.6, align=(Align.CENTER,)*3), (0.20,0.55,0.35), (-190, 150, -140)),
    (28, Pos(-165, 150, -150) * Rot(-90,0,0) * sma_bulk,  ALLOY, (-200, 150, -150)),
    (36, Pos(-165, 205, -150) * Rot(-90,0,0) * whip,      BLACK, (-208, 300, -150)),
    (38, Pos(-165, 118, -150) * Rot(-90,0,0) * pigtail,  (0.78,0.55,0.42), (-208, 108, -150)),
]
parts = [(sh, col) for _n, sh, col, _a in ITEMS]
BALLOONS = [(n, a) for n, _sh, _c, a in ITEMS if a is not None]

for name, az, el in (("cad/out/exp_a.png", 205, -126),
                     ("cad/out/exp_b.png", 248, -118)):
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
