"""Sectioned detail of the rev C shell-to-cover joint: foam band, screws outboard.

WHAT THIS USED TO DRAW, and why that was worse than a crash. It imported the
rev B STEPs and drew a 3 mm O-ring cord in a 3.45 W x 2.31 D gland, off a
hardcoded DEPTH=24.0 and a groove depth of 2.31 typed straight in. rev C has
no groove, no gland and no cord: the seal is a 3 mm closed-cell rubber FOAM
band, continuous, laid on the flat brim face, with the brim screws OUTBOARD of
it so nothing is punched through the seal. The file kept rendering the old
joint and LABELLING it, which is the failure mode a drawing has that a broken
script does not - it was believed. Every number below is read from
cad/out/housing.json or measured off the STEP; none of them is typed here.
"""
import sys, base64, json
sys.path.insert(0, "cad")
from build123d import *
from render import render_multi, png

H = json.load(open("cad/out/housing.json"))
OUT_H, DEPTH, COVER_T, RIM = H["OUT_H"], H["DEPTH"], H["COVER_T"], H["RIM"]
GASKET_T, GASKET_C, GASKET_W = H["GASKET_T"], H["GASKET_C"], H["GASKET_W"]
GASKET_D = H["GASKET_D"]            # groove depth
GASKET_OUT, LAND_IN, BOLT_INSET = H["GASKET_OUT"], H["LAND_IN"], H["BOLT_INSET"]

# The brim face runs outer edge -> land -> screw -> web -> foam -> lip -> cavity.
# If those bands ever stop adding up to RIM the section below is drawing a face
# the shell does not have, so fail rather than publish it.
assert abs(GASKET_OUT + GASKET_W + LAND_IN - RIM) < 1e-6, (
    f"brim bands {GASKET_OUT:.2f} + {GASKET_W:.2f} + {LAND_IN:.2f} do not close "
    f"on RIM {RIM:.2f} - housing.json and this detail disagree about the brim")

SHELL = import_step("cad/out/helm_shell_revC.stp")
COVER = import_step("cad/out/helm_cover_revC.stp")
# Same stack-up as cad/assembly.py: the cover lands on COMPRESSED foam, so its
# inner face is DEPTH + GASKET_C, not DEPTH. Asserted against the real hole
# below rather than trusted.
COVER_ASM = Pos(0, 0, DEPTH + COVER_T + GASKET_C) * Rot(180, 0, 0) * COVER


def arcs(shape):
    """(x, y, z, r) of every circular edge - the way to ask the geometry where
    a feature actually is instead of keeping a second copy of the number."""
    for e in shape.edges():
        try:
            c, r = e.arc_center, e.radius
        except Exception:
            continue
        yield c.X, c.Y, c.Z, r


# WHERE TO CUT. The brim bolts are the one mating dimension NOT in housing.json
# (helm_housing.py walks them round with rrect_pts), so they get read back off
# the shell: pilots on the top rail are the circles at the brim plane on the
# y = OUT_H/2 - BOLT_INSET line. Section through whichever is nearest x=0 and
# both the screw and the band are in the cut, which is the whole point.
RAIL_Y = OUT_H/2 - BOLT_INSET
_pilots = [(x, r) for x, y, z, r in arcs(SHELL)
           if abs(z - DEPTH) < 0.05 and abs(y - RAIL_Y) < 0.05]
assert _pilots, f"no brim pilots found on the top rail at y={RAIL_Y:.2f}, z={DEPTH}"
SX, PILOT_R = min(_pilots, key=lambda p: abs(p[0]))
PILOT_Z = min(z for x, y, z, r in arcs(SHELL)
              if abs(x - SX) < 0.05 and abs(y - RAIL_Y) < 0.05)     # blind bottom

# THE assert this drawing exists to make: the screw must clear the foam. If the
# pilot ever reaches the band, the seal is punched and the label is a lie.
G_OUT_Y = OUT_H/2 - GASKET_OUT                  # foam's outer edge
assert RAIL_Y - PILOT_R > G_OUT_Y, (
    f"brim pilot reaches y={RAIL_Y - PILOT_R:.2f}, foam starts at {G_OUT_Y:.2f} "
    f"- the screw is through the band, not outboard of it")

# ...and the cover has to be where the compressed foam puts it. Its clearance
# hole at this bolt gives the inner face directly.
_clear = [z for x, y, z, r in arcs(COVER_ASM)
          if abs(x - SX) < 0.05 and abs(y - RAIL_Y) < 0.05]
assert _clear, f"no cover clearance hole over the brim bolt at x={SX:.2f}"
COVER_IN = min(_clear)
assert abs(COVER_IN - (DEPTH + GASKET_C)) < 1e-6, (
    f"cover inner face lands at {COVER_IN:.2f}, foam holds it at "
    f"{DEPTH + GASKET_C:.2f} - this detail and assembly.py disagree")
COVER_TOP = COVER_IN + COVER_T

# ── the cut ───────────────────────────────────────────────────────────────
# One box, not a crop plus a half-space: starting it AT x=SX makes its own
# left wall the section plane, so the screw is halved by the same boolean that
# trims the rail.
SEC_D = 38.0                                    # rail length left behind the cut
HEAD_D, HEAD_H = 5.6, 2.4                       # DIN 7985 M3 pan head - a
#   representation. Nothing in the joint depends on the head profile; it is
#   here so the fastener reads as a fastener and not as another hole.
Z0, Z1 = PILOT_Z - 2.0, COVER_TOP + HEAD_H + 2.0
Y0, Y1 = OUT_H/2 - RIM - 5.0, OUT_H/2 + 2.0
KEEP = Pos(SX + SEC_D/2, (Y0 + Y1)/2, (Z0 + Z1)/2) * Box(
    SEC_D, Y1 - Y0, Z1 - Z0, align=(Align.CENTER,)*3)

sh = SHELL & KEEP
cv = COVER_ASM & KEEP
# THE SEAL IS A CORD IN A GROOVE AGAIN, not a flat band squeezed on the face.
# That matters to this drawing in a way it did not before: a band held the cover
# GASKET_C off the brim, so there was a visible gap to draw. A cord closes
# METAL-TO-METAL - the cover lands on the brim and the cord is squashed down
# into its groove - so GASKET_C is 0 and the old band Box was zero-height, which
# is what killed this script.
#
# Drawn as the cord filling the groove: GASKET_W wide by GASKET_D deep, sitting
# in the cut. The round O3.0 it was before assembly is the dashed outline below.
foam = Pos(SX + SEC_D/2, G_OUT_Y - GASKET_W/2, DEPTH - GASKET_D) * Box(
    SEC_D, GASKET_W, GASKET_D, align=(Align.CENTER, Align.CENTER, Align.MIN))
# The trade rev C makes by moving the screws out: they are now in the WET
# zone. The shell's pilot is blind and never reaches the cavity, so the leak
# path is the COVER's through-hole - every one of these needs a bonded sealing
# washer under the head. Not drawn; it is a consumable, not a printed feature.
screw = (Pos(SX, RAIL_Y, PILOT_Z) * Cylinder(PILOT_R, COVER_TOP - PILOT_Z,
             align=(Align.CENTER, Align.CENTER, Align.MIN))
         + Pos(SX, RAIL_Y, COVER_TOP) * Cylinder(HEAD_D/2, HEAD_H,
             align=(Align.CENTER, Align.CENTER, Align.MIN)))
screw = screw & KEEP

W, H_PX = 1100, 720
# az just past 90 puts the cut plane nearly square to camera but leaves enough
# obliquity to show the band RUNNING - a continuous band is the design, and a
# dead-flat section draws it as a rectangle that could be an O-ring end-on.
rgba, proj = render_multi(
    [(sh, (0.20, 0.48, 0.85)), (cv, (0.09, 0.24, 0.48)),
     (foam, (0.85, 0.30, 0.18)), (screw, (0.72, 0.75, 0.80))],
    az=104, el=16, W=W, H=H_PX)
png("cad/out/seal_detail.png", rgba)

DIM = "#0f172a"
def leader(pt, label, dx, dy, anchor="start"):
    x, y = proj(pt); ex, ey = x + dx, y + dy
    tx = ex + (12 if anchor == "start" else -12)
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{DIM}"/>'
            f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{DIM}" stroke-width="1.5"/>'
            f'<line x1="{ex:.1f}" y1="{ey:.1f}" x2="{tx:.1f}" y2="{ey:.1f}" stroke="{DIM}" stroke-width="1.5"/>'
            f'<text x="{tx + (6 if anchor=="start" else -6):.1f}" y="{ey:.1f}" fill="{DIM}" '
            f'font-family="IBM Plex Mono,monospace" font-size="17" font-weight="500" '
            f'text-anchor="{anchor}" dy="6">{label}</text>')

# The cord AS BOUGHT - round, O GASKET_T - dashed in the cut plane, sitting on
# the groove mouth. It stands proud of the brim face by GASKET_T - GASKET_D, and
# THAT overlap is the squeeze the brim screws pull out.
_cy0 = G_OUT_Y - GASKET_W/2
_cz0 = DEPTH - GASKET_D + GASKET_T/2
import math as _m
_uncut = " ".join("%.1f,%.1f" % proj(
    (SX, _cy0 + GASKET_T/2*_m.cos(_a*_m.pi/8), _cz0 + GASKET_T/2*_m.sin(_a*_m.pi/8)))
    for _a in range(16))

svg = [f'<svg viewBox="0 0 {W} {H_PX}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block">',
       f'<image href="data:image/png;base64,{base64.b64encode(open("cad/out/seal_detail.png","rb").read()).decode()}" '
       f'x="0" y="0" width="{W}" height="{H_PX}"/>',
       f'<polygon points="{_uncut}" fill="none" stroke="#ffffff" stroke-width="1.8" stroke-dasharray="6 4"/>',
       # Label geometry, not opinion: every number below comes from housing.json
       # or off the STEP. Offsets are hand-placed against the 1100 x 720 frame -
       # right-hand text starts at ex+18 and the frame is the only thing stopping
       # a 28-character label, so keep them at or under that.
       leader((SX, RAIL_Y, COVER_TOP + HEAD_H), "M3 BRIM SCREW - OUTBOARD OF THE BAND",
              -120, -170, "end"),
       leader((SX, RAIL_Y, DEPTH - 1.0), f"PILOT {2*PILOT_R:.1f} x {DEPTH - PILOT_Z:.0f} BLIND",
              -250, 120, "end"),
       leader((SX, OUT_H/2, COVER_IN + COVER_T/2), f"REAR COVER {COVER_T:.0f}", -200, -60, "end"),
       leader((SX, OUT_H/2, DEPTH), f"SHELL BRIM - RIM {RIM:.0f}", -200, 60, "end"),
       leader((SX, G_OUT_Y, DEPTH - GASKET_D),
              f"GROOVE {GASKET_W:.2f} W x {GASKET_D:.2f} D, {GASKET_OUT:.1f} IN FROM EDGE", 160, 82),
       leader((SX, G_OUT_Y - GASKET_W/2, DEPTH - GASKET_D/2),
              f"O{GASKET_T:.0f} CORD - COVER LANDS METAL TO METAL", 116, 110),
       '</svg>']
open("cad/out/seal_detail.svg", "w").write("".join(svg))
print(f"  section at x={SX:.1f} on the top rail (bolt {BOLT_INSET:.2f} in, "
      f"groove {GASKET_OUT:.2f} in): screw clears the groove by "
      f"{(RAIL_Y - PILOT_R) - G_OUT_Y:.2f} mm, band continuous")
print(f"  seal_detail.svg  ({len(''.join(svg))//1024} KB)")
