"""Dimensioned orthographic views of the ASSEMBLED housing.

rot(az,el) cannot orbit horizontally, so each view yaws the model and reuses
one solved front camera (az=180, el=-90: depth->+z, up->+y, right->-x).

EVERY number that reaches a label is formatted from housing.json. rev B typed
its labels as literals and they rotted in place: the front elevation still read
"384.0 x 160.0" long after the outline came down to 327 x 166.5, and the
control dims were 21.0 - rev B's button pitch DOWN a column that no longer
exists. A drawing that disagrees with the solid it is drawn over is worse than
no drawing, so nothing here is allowed to be a literal.
"""
import sys, json, math, base64
sys.path.insert(0, "cad")
from build123d import *
from render import render_multi, png

H = json.load(open("cad/out/housing.json"))
assert H.get("REV") == "D", f"housing.json is rev {H.get('REV')}, these views are rev D"
OW, OH, DEPTH, CT = H["OUT_W"], H["OUT_H"], H["DEPTH"], H["COVER_T"]
APW, APH = H["APER_W"], H["APER_H"]
DCX, DCY = H["DISP_CX"], H["DISP_CY"]
# rev C moved the controls out of a COLUMN beside the screen into a ROW under
# it, so there is no COL_CX / BTN_Y / ENC_Y any more - this file died on the
# first of those. BTN_X is four x positions, ENC_X the encoder's, ROW_CY the
# single y they all share.
BTN_X, ENC_X, ROW_CY = H["BTN_X"], H["ENC_X"], H["ROW_CY"]
BTN_D, ENC_D = H["BTN_D"], H["ENC_D"]
GL_X, VENT_X, SMA_X, SMA_D = H["GL_X"], H["VENT_X"], H["SMA_X"], H["SMA_D"]
BLK_Y0, BORE_Z = H["BLK_Y0"], H["BORE_Z"]
BUMP_H, GASKET_W, RIM = H["PI_BUMP_H"], H["GASKET_W"], H["RIM"]
PIV_X, PIV_Y, PIV_Z = H["PIV_X"], H["PIV_Y"], H["PIV_Z"]

# The row is dimensioned as a row, which is only honest if it IS one: one
# shared y and one shared pitch. Either would have caught the rev B carry-over.
assert len(BTN_X) == 4, f"the row dim assumes four keys, housing.json has {len(BTN_X)}"
BTN_PITCH = BTN_X[0] - BTN_X[1]
assert all(abs((BTN_X[i] - BTN_X[i+1]) - BTN_PITCH) < 1e-9 for i in range(3)), (
    f"buttons are not on one pitch ({BTN_X}) - a single pitch dim would lie")
assert ROW_CY + BTN_D/2 < H["APER_Y"] - APH/2, (
    "control row is not below the display aperture - this drawing is rev B again")

SHELL = import_step("cad/out/helm_shell_revD.stp")
COVER = import_step("cad/out/helm_cover_revD.stp")
VISOR = import_step("cad/out/helm_visor_revD.stp")
# Cover placement is assembly.py's, not this file's: Rot(180,0,0) then z up by
# DEPTH + COVER_T. The brim seal is closed-cell foam that the screws crush, so
# the cover rides on the COMPRESSED thickness - take that from housing.json the
# moment it publishes it rather than keeping a copy here, because a private
# copy is exactly how the two files would end up drawing different stacks.
GASKET_C = H.get("GASKET_C", 0.0)   # 0.0 until housing.json carries the band
COVER_Z = DEPTH + CT + GASKET_C
COVER_PLACED = Pos(0, 0, COVER_Z) * Rot(180, 0, 0) * COVER
# Check the placement against the solid rather than trusting the arithmetic.
# min.Z is NOT the seal - the display bearing posts stand 17 mm proud of the
# sealing face and reach down into the cavity, so the lowest point of the cover
# is inside the shell. The OUTERMOST point is the crown of the Pi bump-out, and
# that is also the number the side elevation calls the overall depth, so one
# check covers the placement and that label together.
# The crown is no longer the Pi bump. The tilt TRUNNIONS are grown from this
# plate now and stand TRUN_STAND + TRUN_R proud of its outer face, which is
# further out than the bump - so the outermost point, and the number the side
# elevation calls overall depth, is whichever of the two is taller.
_PROUD = max(BUMP_H, H["TRUN_STAND"] + H["TRUN_R"])
_cz = COVER_PLACED.bounding_box().max.Z
assert abs(_cz - (COVER_Z + _PROUD)) < 1e-6, (
    f"cover crowns at z={_cz:.3f}, expected {COVER_Z + _PROUD:.3f} - placement "
    f"disagrees with cad/assembly.py")
# The shell is exactly OUT_W again. It briefly was not: the tilt pivot spent a
# revision as a boss on each SIDE WALL, which was mechanically the best place -
# 1.4 mm from the CG - but hung hardware off the front shell and stood proud of
# the bezel line. The pivot moved to trunnions on the REAR COVER, so the shell
# went back to its body width. This assert tracked it both ways.
OW_BBOX = OW
assert abs(SHELL.bounding_box().size.X - OW_BBOX) < 1e-6, (
    f"shell is {SHELL.bounding_box().size.X:.1f} wide, housing.json says {OW:.1f}")

# Display fitted, otherwise the front elevation looks straight through the
# aperture at the cover behind and reads as clutter. Envelope only, and the
# same 305 x 125 representation assembly.py uses - but at DISP_CY, because the
# panel sits HIGH in rev C to leave the control row its band at the bottom.
DISP = Pos(DCX, DCY, 2.5) * Box(305, 125, 17.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
ASM = [SHELL, COVER_PLACED, VISOR, DISP]

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

# Rear-face callout anchors, all READ from housing.json now. The three fittings
# sit in the blocks beside the bay bumps and bore horizontally, so their leader
# lands on the block's underside at shell y = BLK_Y0 and z = cover face +
# half the bump depth. HEAT_XY is the aperture centre (AP_CX, 0).
FIT_Z   = COVER_Z - BORE_Z          # BORE_Z is cover-local (negative = proud)
GL_XY   = (GL_X,   BLK_Y0)
VENT_XY = (VENT_X, BLK_Y0)
SMA_XY  = (SMA_X,  BLK_Y0)
HEAT_XY = (H["AP_CX"], 0.0)

# The four yaws mirror each other, so a flip that puts a dim OUTSIDE the part in
# the front view puts it INSIDE in the rear view. Every off/flip below was set
# against the projected pixel positions, not guessed.
VIEWS = [
 ("dimasm_front", "FRONT ELEVATION", Rot(0, 0, 0), 1240, 820, lambda P: (
    dim(P, (-OW/2, -OH/2, 0), (OW/2, -OH/2, 0), f"{OW:.1f}", off=96, flip=-1) +
    dim(P, (OW/2, -OH/2, 0), (OW/2, OH/2, 0), f"{OH:.1f}", off=56, flip=-1) +
    dim(P, (DCX-APW/2, H["APER_Y"]+APH/2, 0), (DCX+APW/2, H["APER_Y"]+APH/2, 0),
        f"{APW:.1f}", off=44, flip=1) +
    dim(P, (DCX+APW/2, H["APER_Y"]-APH/2, 0), (DCX+APW/2, H["APER_Y"]+APH/2, 0),
        f"{APH:.1f}", off=-44, flip=1, fs=16) +
    # The row, dimensioned AS a row - which is the whole point of rev C. A
    # builder drilling this face needs the pitch, the span it makes, where the
    # encoder hangs off the end of it, and how high the line sits off the
    # bottom edge. rev B's "21.0" was a pitch DOWN a column that is gone.
    dim(P, (BTN_X[0], ROW_CY, 0), (BTN_X[1], ROW_CY, 0), f"{BTN_PITCH:.1f}", off=40, flip=1, fs=15) +
    dim(P, (BTN_X[-1], ROW_CY, 0), (ENC_X, ROW_CY, 0), f"{BTN_X[-1]-ENC_X:.1f}", off=40, flip=1, fs=15) +
    dim(P, (BTN_X[0], ROW_CY, 0), (BTN_X[-1], ROW_CY, 0),
        f"{BTN_X[0]-BTN_X[-1]:.1f} = 3 x {BTN_PITCH:.1f}", off=86, flip=1, fs=16) +
    dim(P, (ENC_X, -OH/2, 0), (ENC_X, ROW_CY, 0), f"{ROW_CY+OH/2:.1f}", off=48, flip=1, fs=15) +
    note(P, (BTN_X[2], ROW_CY, 0), f"4x &#216;{BTN_D} BUTTON", -90, 120, "end") +
    note(P, (ENC_X, ROW_CY, 0), f"&#216;{ENC_D} ENCODER", -50, 130, "end") +
    note(P, (DCX, DCY, 0), "PANEL SEATED ON THE BOND LAND", -40, 104, "end"))),
 ("dimasm_side", "SIDE ELEVATION", Rot(0, 90, 0), 1240, 700, lambda P: (
    # The part is a thin slice in this projection - 250 px of a 1240 canvas -
    # so the depth stack nests along the bottom edge and the notes live in the
    # dead space either side rather than on top of the section.
    dim(P, (0, -OH/2, 0), (0, -OH/2, DEPTH), f"{DEPTH:.1f}", off=24, flip=-1, fs=16) +
    dim(P, (0, -OH/2, 0), (0, -OH/2, DEPTH + CT + GASKET_C),
        f"{DEPTH+CT+GASKET_C:.1f}", off=64, flip=-1, fs=16) +
    dim(P, (0, -OH/2, 0), (0, -OH/2, DEPTH + CT + GASKET_C + BUMP_H),
        f"{DEPTH+CT+GASKET_C+BUMP_H:.1f}", off=104, flip=-1) +
    note(P, (0, PIV_Y, PIV_Z), f"VISOR PIVOT - FRICTION, HAND SET", -200, -20, "end") +
    note(P, (0, 6, DEPTH + CT + GASKET_C + BUMP_H), f"Pi BUMP-OUT +{BUMP_H:.0f}", -160, -60, "end") +
    note(P, (0, -OH/2, DEPTH), f"BRIM {RIM:.1f} - FOAM BAND {GASKET_W:.2f}", 200, 30))),
 ("dimasm_rear", "REAR VIEW", Rot(0, 180, 0), 1240, 820, lambda P: (
    # rev B dimensioned a 100 mm VESA pattern here. VESA is deleted in rev C -
    # the unit hinges off a bracket on its bottom edge - so what this face is
    # for now is the seal and the service openings. The 7.3 mm gasket band is
    # 23 px at this scale and will not carry a dimension line, so it is a note.
    dim(P, (-OW/2, -OH/2, COVER_Z), (OW/2, -OH/2, COVER_Z), f"{OW:.1f}", off=96, flip=1) +
    note(P, (OW/2 - GASKET_W/2, 0, DEPTH), f"FOAM GASKET BAND {GASKET_W:.2f} WIDE", -90, -150, "end") +
    note(P, (*HEAT_XY, COVER_Z), "HEAT-PLATE APERTURE", -260, -150, "end") +
    note(P, (*SMA_XY, FIT_Z), f"SMA COAX ENTRY M8, FACES DOWN", 70, -130) +
    note(P, (*GL_XY, FIT_Z), "CABLE GLAND M16x1.5, FACES DOWN", 60, 150) +
    note(P, (*VENT_XY, FIT_Z), "GORE VENT M12, FACES DOWN", 200, 90))),
 ("dimasm_top", "TOP VIEW", Rot(-90, 0, 0), 1240, 700, lambda P: (
    dim(P, (-OW/2, 0, 0), (OW/2, 0, 0), f"{OW:.1f}", off=200, flip=-1) +
    dim(P, (PIV_X[0], PIV_Y, PIV_Z), (PIV_X[1], PIV_Y, PIV_Z),
        f"{PIV_X[1]-PIV_X[0]:.1f} PIVOT SPAN", off=150, flip=1, fs=16) +
    note(P, (0, 0, DEPTH + CT + GASKET_C + BUMP_H),
         f"{DEPTH+CT+GASKET_C+BUMP_H:.1f} OVER THE Pi BUMP", -330, -80, "end"))),
]

out = []
for name, title, yaw, W, Hh, dims in VIEWS:
    parts = [(yaw * p, (0.93, 0.93, 0.93)) for p in ASM[:3]] + [(yaw * ASM[3], (0.62, 0.64, 0.66))]
    rgba, proj = render_multi(parts, AZ, EL, W=W, H=Hh, style="line")
    png(f"cad/out/{name}.png", rgba)
    # tuple(yaw * Vertex(...)) hands back the UN-YAWED point: the rotation goes
    # on the wrapper's Location and tuple() reads the raw geometry under it -
    # the same trap assembly.py's _solid() documents for booleans. Every note in
    # the side, rear and top views was therefore being placed with the FRONT
    # camera, and rev B hid it by nudging the leaders until they looked right.
    # .center() evaluates the located vertex, so the yaw actually lands.
    P = lambda pt: proj(tuple((yaw * Vertex(*pt)).center()))
    svg = (f'<svg viewBox="0 0 {W} {Hh}" xmlns="http://www.w3.org/2000/svg" '
           f'style="width:100%;height:auto;display:block">'
           f'<image href="data:image/png;base64,'
           f'{base64.b64encode(open(f"cad/out/{name}.png","rb").read()).decode()}" '
           f'x="0" y="0" width="{W}" height="{Hh}"/>{dims(P)}</svg>')
    open(f"cad/out/{name}.svg", "w").write(svg)
    out.append({"name": name, "title": title})
    print(f"  {name:14s} {len(svg)//1024:4d} KB  {title}")
json.dump(out, open("cad/out/asmdims.json", "w"), indent=1)
