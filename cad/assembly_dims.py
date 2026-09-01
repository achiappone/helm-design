"""Dimensioned orthographic views of the ASSEMBLED housing.

rot(az,el) cannot orbit horizontally, so each view yaws the model and reuses
one solved front camera (az=180, el=-90: depth->+z, up->+y, right->-x).
"""
import sys, json, math, base64
sys.path.insert(0, "cad")
from build123d import *
from render import render_multi, png

H = json.load(open("cad/out/housing.json"))
OW, OH, DEPTH, CT = H["OUT_W"], H["OUT_H"], H["DEPTH"], H["COVER_T"]
APW, APH = H["APER_W"], H["APER_H"]
DCX, CCX = H["DISP_CX"], H["COL_CX"]
BTN_Y, ENC_Y = H["BTN_Y"], H["ENC_Y"]
ANT_X, GPS_X, BUMP_H = H["ANT_X"], H["GPS_X"], H["PI_BUMP_H"]

SHELL = import_step("cad/out/helm_shell_revB.stp")
COVER = import_step("cad/out/helm_cover_revB.stp")
VISOR = import_step("cad/out/helm_visor_revB.stp")
# display fitted, otherwise the front elevation looks straight through the
# aperture at the cover behind and reads as clutter
DISP = Pos(DCX, 0, 2.5) * Box(305, 125, 17.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
ASM = [SHELL, Pos(0, 0, DEPTH + CT) * Rot(180, 0, 0) * COVER, VISOR, DISP]

AZ, EL = 180, -90
DIM = "#c2410c"

def arrow(x, y, ux, uy, s=8):
    px, py = -uy, ux
    return (f'<polygon points="{x:.1f},{y:.1f} {x+ux*s+px*s*.3:.1f},{y+uy*s+py*s*.3:.1f} '
            f'{x+ux*s-px*s*.3:.1f},{y+uy*s-py*s*.3:.1f}" fill="{DIM}"/>')

def dim(P, a, b, label, off=40, flip=1, ext=9, fs=18):
    ax, ay = P(a); bx, by = P(b)
    dx, dy = bx-ax, by-ay
    L = math.hypot(dx, dy) or 1
    ux, uy = dx/L, dy/L
    nx, ny = -uy*flip, ux*flip
    a2 = (ax+nx*off, ay+ny*off); b2 = (bx+nx*off, by+ny*off)
    mx, my = (a2[0]+b2[0])/2, (a2[1]+b2[1])/2
    s = (f'<line x1="{ax+nx*4:.1f}" y1="{ay+ny*4:.1f}" x2="{a2[0]+nx*ext:.1f}" y2="{a2[1]+ny*ext:.1f}" stroke="{DIM}" stroke-width="1.2"/>'
         f'<line x1="{bx+nx*4:.1f}" y1="{by+ny*4:.1f}" x2="{b2[0]+nx*ext:.1f}" y2="{b2[1]+ny*ext:.1f}" stroke="{DIM}" stroke-width="1.2"/>'
         f'<line x1="{a2[0]:.1f}" y1="{a2[1]:.1f}" x2="{b2[0]:.1f}" y2="{b2[1]:.1f}" stroke="{DIM}" stroke-width="1.5"/>')
    s += arrow(*a2, ux, uy) + arrow(*b2, -ux, -uy)
    r = math.degrees(math.atan2(dy, dx))
    if r > 90 or r < -90: r += 180
    s += (f'<text x="{mx:.1f}" y="{my:.1f}" transform="rotate({r:.1f} {mx:.1f} {my:.1f})" fill="{DIM}" '
          f'font-family="IBM Plex Mono,monospace" font-size="{fs}" font-weight="500" '
          f'text-anchor="middle" dy="-7">{label}</text>')
    return s

def note(P, pt, label, dx, dy, anchor="start", fs=17):
    x, y = P(pt); ex, ey = x+dx, y+dy
    tx = ex + (12 if anchor == "start" else -12)
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{DIM}"/>'
            f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{DIM}" stroke-width="1.4"/>'
            f'<line x1="{ex:.1f}" y1="{ey:.1f}" x2="{tx:.1f}" y2="{ey:.1f}" stroke="{DIM}" stroke-width="1.4"/>'
            f'<text x="{tx + (6 if anchor=="start" else -6):.1f}" y="{ey:.1f}" fill="{DIM}" '
            f'font-family="IBM Plex Mono,monospace" font-size="{fs}" font-weight="500" '
            f'text-anchor="{anchor}" dy="6">{label}</text>')

VIEWS = [
 ("dimasm_front", "FRONT ELEVATION", Rot(0, 0, 0), 1240, 760, lambda P: (
    dim(P, (-OW/2, -OH/2, 0), (OW/2, -OH/2, 0), "384.0", off=68, flip=-1) +
    dim(P, (OW/2, -OH/2, 0), (OW/2, OH/2, 0), "160.0", off=52, flip=-1) +
    dim(P, (DCX-APW/2, APH/2, 0), (DCX+APW/2, APH/2, 0), "293.5", off=52, flip=1) +
    dim(P, (DCX+APW/2, -APH/2, 0), (DCX+APW/2, APH/2, 0), "110.7", off=-46, flip=1, fs=16) +
    dim(P, (CCX, BTN_Y[0], 0), (CCX, BTN_Y[1], 0), "21.0", off=46, flip=1, fs=15) +
    note(P, (CCX, BTN_Y[0], 0), "4x &#216;12.0 BUTTON", 100, -95) +
    note(P, (CCX, ENC_Y, 0), "&#216;9.7 ENCODER", 100, 95) +
    note(P, (DCX, 0, 0), "ACTIVE AREA 292.5 x 109.7", -50, 118, "end"))),
 ("dimasm_side", "SIDE ELEVATION", Rot(0, 90, 0), 1240, 700, lambda P: (
    dim(P, (0, -OH/2, 0), (0, -OH/2, DEPTH + CT), "30.0", off=70, flip=-1) +
    dim(P, (0, -OH/2, 0), (0, -OH/2, DEPTH + CT + BUMP_H), "48.0", off=95, flip=-1) +
    dim(P, (0, OH/2, 0), (0, OH/2, DEPTH), "24.0", off=64, flip=1, fs=16) +
    note(P, (0, 87, -30), "VISOR, 58 mm HOOD", -60, -80, "end") +
    note(P, (0, 6, DEPTH + CT + BUMP_H), "Pi BUMP-OUT +18", 90, 60))),
 ("dimasm_rear", "REAR VIEW", Rot(0, 180, 0), 1240, 760, lambda P: (
    dim(P, (-50, -50, DEPTH+CT), (50, -50, DEPTH+CT), "100.0 VESA", off=70, flip=1) +
    dim(P, (76, -42, DEPTH+CT), (160, -42, DEPTH+CT), "84.0", off=48, flip=1, fs=16) +
    note(P, (-150, -48, DEPTH+CT), "NPT 3/4 GLAND", -80, 120, "end") +
    note(P, (-95, -50, DEPTH+CT), "M12 GORE VENT", 40, 150) +
    note(P, (118, 0, DEPTH+CT), "HEATSINK APERTURE", 110, -110))),
 ("dimasm_top", "TOP VIEW", Rot(-90, 0, 0), 1240, 700, lambda P: (
    dim(P, (-OW/2, OH/2, 0), (OW/2, OH/2, 0), "384.0", off=80, flip=1) +
    note(P, (ANT_X, OH/2, 10), "SMA BULKHEAD &#216;16.5", -50, -72, "end") +
    note(P, (GPS_X, OH/2, 12), "GPS, PATCH UP", 55, -72) +
    dim(P, (ANT_X, OH/2, 10), (GPS_X, OH/2, 12), "315.0 RF SEPARATION", off=-44, flip=1, fs=16))),
]

out = []
for name, title, yaw, W, Hh, dims in VIEWS:
    parts = [(yaw * p, (0.93, 0.93, 0.93)) for p in ASM[:3]] + [(yaw * ASM[3], (0.62, 0.64, 0.66))]
    rgba, proj = render_multi(parts, AZ, EL, W=W, H=Hh, style="line")
    png(f"cad/out/{name}.png", rgba)
    P = lambda pt: proj(tuple(yaw * Vertex(*pt)))
    svg = (f'<svg viewBox="0 0 {W} {Hh}" xmlns="http://www.w3.org/2000/svg" '
           f'style="width:100%;height:auto;display:block">'
           f'<image href="data:image/png;base64,'
           f'{base64.b64encode(open(f"cad/out/{name}.png","rb").read()).decode()}" '
           f'x="0" y="0" width="{W}" height="{Hh}"/>{dims(P)}</svg>')
    open(f"cad/out/{name}.svg", "w").write(svg)
    out.append({"name": name, "title": title})
    print(f"  {name:14s} {len(svg)//1024:4d} KB  {title}")
json.dump(out, open("cad/out/asmdims.json", "w"), indent=1)
