"""Dimensioned drawings of the two measured parts, redrawn from the photos.

These are MY READING of hand-measured sketches. Every number is labelled so it
can be checked against the real part; anything I could not read is marked.
"""
import json

DIM, INK, MUT = "#c2410c", "#1b2430", "#6b7a8c"
def hdr(w, h):
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
            f'style="width:100%;height:auto;display:block">'
            f'<rect x="0" y="0" width="{w}" height="{h}" fill="#f6f7f9"/>')
def rect(x, y, w, h, fill="#e3e8ef", sw=1.8):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{INK}" stroke-width="{sw}"/>'
def hole(x, y, r=4.5):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" stroke="{INK}" stroke-width="1.8"/>'
            f'<line x1="{x-r-3}" y1="{y}" x2="{x+r+3}" y2="{y}" stroke="{MUT}" stroke-width="0.8"/>'
            f'<line x1="{x}" y1="{y-r-3}" x2="{x}" y2="{y+r+3}" stroke="{MUT}" stroke-width="0.8"/>')
def dimh(x1, x2, y, label, fs=15):
    return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{DIM}" stroke-width="1.4"/>'
            f'<line x1="{x1}" y1="{y-5}" x2="{x1}" y2="{y+5}" stroke="{DIM}" stroke-width="1.4"/>'
            f'<line x1="{x2}" y1="{y-5}" x2="{x2}" y2="{y+5}" stroke="{DIM}" stroke-width="1.4"/>'
            f'<text x="{(x1+x2)/2}" y="{y-8}" fill="{DIM}" font-family="IBM Plex Mono,monospace" '
            f'font-size="{fs}" text-anchor="middle">{label}</text>')
def dimv(y1, y2, x, label, fs=15, side=1):
    mx, my = x, (y1+y2)/2
    return (f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{DIM}" stroke-width="1.4"/>'
            f'<line x1="{x-5}" y1="{y1}" x2="{x+5}" y2="{y1}" stroke="{DIM}" stroke-width="1.4"/>'
            f'<line x1="{x-5}" y1="{y2}" x2="{x+5}" y2="{y2}" stroke="{DIM}" stroke-width="1.4"/>'
            f'<text x="{mx}" y="{my}" transform="rotate(-90 {mx} {my})" fill="{DIM}" '
            f'font-family="IBM Plex Mono,monospace" font-size="{fs}" text-anchor="middle" dy="-7">{label}</text>')
def note(x, y, t, anchor="start", col=None, fs=14):
    return (f'<text x="{x}" y="{y}" fill="{col or MUT}" font-family="IBM Plex Mono,monospace" '
            f'font-size="{fs}" text-anchor="{anchor}">{t}</text>')

# ── driver board ─────────────────────────────────────────────────────────
S = 5.4; OX, OY = 130, 150
W, Hh = 113.25*S, 55.25*S
g = [hdr(880, 500), note(40, 42, "DRIVER BOARD  113.25 x 55.25 x 17", col=INK, fs=19),
     note(40, 66, "hole centres confirmed by measurement", fs=13),
     rect(OX, OY, W, Hh)]
# holes: insets read off the sketch
# confirmed hole centres, origin top-left. NOT a rectangle - the left and
# right columns sit at different heights.
HOLES = [("TL", 9.0, 3.75), ("TR", 113.25-4.0, 3.75),
         ("BL", 9.0, 55.25-7.25), ("BR", 113.25-4.0, 55.25-3.75)]
for _n, hx, hy in HOLES:
    g.append(hole(OX + hx*S, OY + hy*S, 4))
g += [dimh(OX, OX+W, OY+Hh+58, "113.25"),
      dimv(OY, OY+Hh, OX-56, "55.25"),
      dimh(OX, OX+9*S, OY-26, "9.0", 13),
      dimh(OX+(113.25-4)*S, OX+W, OY-26, "4.0", 13),
      dimv(OY, OY+3.75*S, OX+9*S+26, "3.75", 12),
      dimv(OY+(55.25-7.25)*S, OY+Hh, OX+9*S+26, "7.25", 12),
      dimv(OY+(55.25-3.75)*S, OY+Hh, OX+(113.25-4)*S-26, "3.75", 12),
      note(OX+W-8, OY-38, "HDMI edge &#8594;", "end", INK, 14),
      note(OX, OY+Hh+96, "4 x &#216;3.5 - M3 clearance", col=INK, fs=14),
      note(OX, OY+Hh+118, "TL (9.00, 3.75)   TR (109.25, 3.75)", fs=13),
      note(OX, OY+Hh+137, "BL (9.00, 48.00)  BR (109.25, 51.50)   origin top-left", fs=13),
      note(OX, OY+Hh+160, "note the columns differ: left pair 44.25 apart, right pair 47.75", col=DIM, fs=13),
      "</svg>"]
open("cad/out/meas_driver.svg", "w").write("".join(g))

# ── display back ─────────────────────────────────────────────────────────
# 5 standoffs. All Ø8 base, M3 thread, 5 deep. Every dimension is to an EDGE,
# so the outline itself is still unknown - drawn to an assumed 305 x 125.
S2 = 2.05; OX2, OY2 = 100, 165
MW, MH = 305.0, 125.0
W2, H2 = MW*S2, MH*S2
RE, BE = OX2 + W2, OY2 + H2
d = [hdr(900, 540), note(40, 42, "DISPLAY REAR - 5 standoffs, &#216;8 base, M3 x 5 deep", col=INK, fs=19),
     note(40, 66, "every figure is measured to an edge, as given", fs=13),
     rect(OX2, OY2, W2, H2, "#e3e8ef")]
HOLES = [("TL", OX2 + 15*S2,    OY2 + 8.25*S2),
         ("TR", RE  - 12*S2,    OY2 + 8.25*S2),
         ("BL", OX2 + 30.5*S2,  BE  - 13*S2),
         ("BR", RE  - 26.5*S2,  BE  - 13*S2),
         ("C",  RE  - 133*S2,   BE  - 31*S2)]
for _n, hx, hy in HOLES:
    d.append(hole(hx, hy, 6))
d += [dimh(OX2, OX2+15*S2, OY2-28, "15.0", 13),
      dimh(RE-12*S2, RE, OY2-28, "12.0", 13),
      dimv(OY2, OY2+8.25*S2, OX2+15*S2-30, "8.25", 12),
      dimh(OX2, OX2+30.5*S2, BE+34, "30.5", 13),
      dimh(RE-26.5*S2, RE, BE+34, "26.5", 13),
      dimh(RE-133*S2, RE, BE+70, "133.0", 13),
      dimv(BE-13*S2, BE, OX2+30.5*S2-30, "13.0", 12),
      dimv(BE-31*S2, BE, RE-133*S2-30, "31.0", 12),
      dimh(OX2, RE, OY2-64, "305 ASSUMED"),
      dimv(OY2, BE, OX2-56, "125 ASSUMED"),
      note(OX2, BE+108, "&#9888; NO top-centre standoff - 5 total, not 6.", col=INK, fs=14),
      note(OX2, BE+130, "&#9888; module outline is still unmeasured. Every hole above is fixed to an", col=DIM, fs=13),
      note(OX2, BE+149, "   edge, so the pattern is exact the moment the outline is known.", col=DIM, fs=13),
      "</svg>"]
open("cad/out/meas_display.svg", "w").write("".join(d))
json.dump([{"name": "meas_driver", "title": "DRIVER BOARD 113.25 x 55.25 x 17"},
           {"name": "meas_display", "title": "DISPLAY REAR - 5 standoffs"}],
          open("cad/out/measdims.json", "w"), indent=1)
print("  display sheet: 5 holes, all edge dims")
