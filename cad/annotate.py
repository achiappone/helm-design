"""Dimensioned section drawings. Orthographic projection -> exact SVG dimensions."""
import sys, json, base64, math
sys.path.insert(0, "cad")
from build123d import *
from render import render, png

SH = import_step("cad/out/lp24_shroud_revD.stp")
BIG = 400
export_step(SH - Pos(0, 0, 32 + BIG/2) * Box(BIG, BIG, BIG), "cad/out/_sec_plan.stp")
export_step(SH - Pos(0, -BIG/2, 0) * Box(BIG, BIG, BIG),      "cad/out/_sec_elev.stp")

DIM = "#e07b39"
def arrow(x, y, ux, uy, s=7):
    px, py = -uy, ux
    return (f'<polygon points="{x:.1f},{y:.1f} {x+ux*s+px*s*0.32:.1f},{y+uy*s+py*s*0.32:.1f} '
            f'{x+ux*s-px*s*0.32:.1f},{y+uy*s-py*s*0.32:.1f}" fill="{DIM}"/>')

def dim(a, b, label, off=34, flip=1, ext=8):
    dx, dy = b[0]-a[0], b[1]-a[1]
    L = math.hypot(dx, dy) or 1
    ux, uy = dx/L, dy/L
    nx, ny = -uy*flip, ux*flip
    a2 = (a[0]+nx*off, a[1]+ny*off); b2 = (b[0]+nx*off, b[1]+ny*off)
    mx, my = (a2[0]+b2[0])/2, (a2[1]+b2[1])/2
    s = (f'<line x1="{a[0]+nx*4:.1f}" y1="{a[1]+ny*4:.1f}" x2="{a2[0]+nx*ext:.1f}" y2="{a2[1]+ny*ext:.1f}" '
         f'stroke="{DIM}" stroke-width="1.2"/>'
         f'<line x1="{b[0]+nx*4:.1f}" y1="{b[1]+ny*4:.1f}" x2="{b2[0]+nx*ext:.1f}" y2="{b2[1]+ny*ext:.1f}" '
         f'stroke="{DIM}" stroke-width="1.2"/>'
         f'<line x1="{a2[0]:.1f}" y1="{a2[1]:.1f}" x2="{b2[0]:.1f}" y2="{b2[1]:.1f}" '
         f'stroke="{DIM}" stroke-width="1.4"/>')
    s += arrow(a2[0], a2[1], ux, uy) + arrow(b2[0], b2[1], -ux, -uy)
    rot = math.degrees(math.atan2(dy, dx))
    if rot > 90 or rot < -90: rot += 180
    s += (f'<text x="{mx:.1f}" y="{my:.1f}" transform="rotate({rot:.1f} {mx:.1f} {my:.1f})" '
          f'fill="{DIM}" font-family="IBM Plex Mono,monospace" font-size="19" font-weight="500" '
          f'text-anchor="middle" dy="-7">{label}</text>')
    return s

def leader(p, label, dx=90, dy=-70, anchor="start"):
    ex, ey = p[0]+dx, p[1]+dy
    tx = ex + (14 if anchor == "start" else -14)
    return (f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="3.4" fill="{DIM}"/>'
            f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{DIM}" stroke-width="1.4"/>'
            f'<line x1="{ex:.1f}" y1="{ey:.1f}" x2="{tx:.1f}" y2="{ey:.1f}" stroke="{DIM}" stroke-width="1.4"/>'
            f'<text x="{tx + (6 if anchor=="start" else -6):.1f}" y="{ey:.1f}" fill="{DIM}" '
            f'font-family="IBM Plex Mono,monospace" font-size="19" font-weight="500" '
            f'text-anchor="{anchor}" dy="6">{label}</text>')

VIEWS = [
 dict(src="_sec_plan", name="dim_plan", az=0, el=89, W=1180, H=880,
      title="PLAN SECTION - roof removed at z 32",
      dims=lambda P: (
        dim(P((22.5,22,26)), P((22.5,-22,26)), "44.0", off=190, flip=1) +
        dim(P((12,22,26)),   P((33,22,26)),    "21.0", off=150, flip=-1) +
        dim(P((-30,13,34)),  P((-30,-13,34)),  "26.0", off=-120, flip=1) +
        leader(P((22.5,22,26)),  "2x M4 PILOT Ø3.5 - OPENS DOWNWARD", dx=120, dy=-95) +
        leader(P((22.5,0,26)),   "CABLE CLAMPS UNDER THE BEAM", dx=-40, dy=150, anchor="end") +
        leader(P((-30,13,21)),   "4x M3 PILOT Ø2.6 x 11.5", dx=-110, dy=-120, anchor="end"))),
 dict(src="_sec_elev", name="dim_elev", az=0, el=0, W=1180, H=760,
      title="SECTION A-A - cut on the part centreline",
      dims=lambda P: (
        dim(P((22.5,22,0)),  P((22.5,22,26)), "26.0", off=150, flip=-1) +
        dim(P((22.5,22,26)), P((22.5,22,39)), "13.0", off=150, flip=-1) +
        dim(P((-46,0,0)),    P((-46,0,63)),   "63.0", off=-70, flip=1) +
        dim(P((-30,0,0)),    P((-30,0,34)),   "34.0", off=60, flip=1) +
        leader(P((22.5,22,26)), "M4 x 25 - DRIVEN UP FROM BELOW", dx=70, dy=-120) +
        leader(P((-30,0,34)),   "LP-24 CL - 12 mm FRAME BEHIND", dx=-120, dy=-140, anchor="end"))),
 dict(src="lp24_shroud_revD", name="dim_front", az=180, el=0, W=1180, H=760,
      title="FRONT ELEVATION",
      dims=lambda P: (
        dim(P((-30,-13,34)), P((-30,13,34)), "26.0", off=120, flip=1) +
        dim(P((-30,13,21)),  P((-30,13,47)), "26.0", off=95, flip=-1) +
        dim(P((-30,-51,0)),  P((-30,51,0)),  "132.0", off=95, flip=-1) +
        leader(P((-30,0,34)), "Ø24.4 TEARDROP - 6 mm PANEL", dx=110, dy=-155))),
 dict(src="lp24_shroud_revD", name="dim_bottom", az=0, el=-89, W=1180, H=880,
      title="UNDERSIDE - shelf face",
      dims=lambda P: (
        dim(P((-56,-43,0)), P((56,-43,0)), "112.0", off=105, flip=-1) +
        dim(P((56,-43,0)),  P((56,43,0)),  "86.0",  off=105, flip=-1) +
        dim(P((-66,51,0)),  P((66,51,0)),  "132.0", off=60, flip=-1) +
        leader(P((-49,0,0)), "GASKET GLAND 98 x 70", dx=-70, dy=-190, anchor="end") +
        leader(P((56,43,0)), "8x Ø5.5  M5", dx=90, dy=-95))),
]

out = []
for v in VIEWS:
    rgba, proj = render(f"cad/out/{v['src']}.stp", az=v["az"], el=v["el"], W=v["W"], H=v["H"])
    png(f"cad/out/{v['name']}.png", rgba)
    b64 = base64.b64encode(open(f"cad/out/{v['name']}.png", "rb").read()).decode()
    svg = (f'<svg viewBox="0 0 {v["W"]} {v["H"]}" xmlns="http://www.w3.org/2000/svg" '
           f'style="width:100%;height:auto;display:block">'
           f'<image href="data:image/png;base64,{b64}" x="0" y="0" width="{v["W"]}" height="{v["H"]}"/>'
           f'{v["dims"](proj)}</svg>')
    open(f"cad/out/{v['name']}.svg", "w").write(svg)
    out.append({"name": v["name"], "title": v["title"]})
    print(f"  {v['name']:11s} {len(svg)//1024:4d} KB  {v['title']}")
json.dump(out, open("cad/out/dims.json", "w"), indent=1)
