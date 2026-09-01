"""Sectioned detail of the shell-to-cover seal, with the cord in place."""
import sys, base64, math
sys.path.insert(0, "cad")
from build123d import *
from render import render_multi, png

SHELL = import_step("cad/out/helm_shell_revB.stp")
COVER = import_step("cad/out/helm_cover_revB.stp")
DEPTH, GY, CORD = 24.0, 69.0, 3.0

# tight crop on the top rail so only the joint shows
CROP = Pos(0, 60, 14) * Box(150, 52, 40, align=(Align.CENTER,)*3)
half = Pos(-40, 0, 0) * Box(80, 300, 300, align=(Align.CENTER,)*3)
sh = (SHELL & CROP) - half
cv = ((Pos(0, 0, DEPTH + 6) * Rot(180, 0, 0) * COVER) & CROP) - half
cord = (Pos(0, GY, DEPTH - 2.31 + CORD/2 - 0.35) * Rot(0, 90, 0) * Cylinder(CORD/2, 150)) - half

W, H = 1100, 720
rgba, proj = render_multi(
    [(sh, (0.20, 0.48, 0.85)), (cv, (0.09, 0.24, 0.48)), (cord, (0.85, 0.30, 0.18))],
    az=72, el=14, W=W, H=H)
png("cad/out/seal_detail.png", rgba)

DIM = "#0f172a"; INK = "#0f172a"
def leader(pt, label, dx, dy, anchor="start"):
    x, y = proj(pt); ex, ey = x + dx, y + dy
    tx = ex + (12 if anchor == "start" else -12)
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{DIM}"/>'
            f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{DIM}" stroke-width="1.5"/>'
            f'<line x1="{ex:.1f}" y1="{ey:.1f}" x2="{tx:.1f}" y2="{ey:.1f}" stroke="{DIM}" stroke-width="1.5"/>'
            f'<text x="{tx + (6 if anchor=="start" else -6):.1f}" y="{ey:.1f}" fill="{DIM}" '
            f'font-family="IBM Plex Mono,monospace" font-size="17" font-weight="500" '
            f'text-anchor="{anchor}" dy="6">{label}</text>')

svg = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block">',
       f'<image href="data:image/png;base64,{base64.b64encode(open("cad/out/seal_detail.png","rb").read()).decode()}" '
       f'x="0" y="0" width="{W}" height="{H}"/>',
       leader((0, GY, DEPTH - 0.8), "3 mm CORD", -140, -110, "end"),
       leader((0, GY, DEPTH - 2.2), "GLAND 3.45 W x 2.31 D", -140, 110, "end"),
       leader((0, 76, DEPTH + 3), "REAR COVER", 150, -90),
       leader((0, 66, DEPTH - 4), "SHELL BRIM", 150, 120),
       '</svg>']
open("cad/out/seal_detail.svg", "w").write("".join(svg))
print(f"  seal_detail.svg  ({len(''.join(svg))//1024} KB)")
