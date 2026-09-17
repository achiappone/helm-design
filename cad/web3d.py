"""
Web meshes -- the assembly, packed small enough to live inside the page.

The build review has always been still renders. They are true, but you cannot
look BEHIND anything in a PNG, and every question this project has had lately
-- where does the coax go, where do the bracket nuts install, I can't see where
the internal wire routes -- was really a request to ROTATE THE PART. So the
same solids get tessellated once more, at a deflection chosen for a browser
rather than for a slicer, and the result is embedded in the page as base64
Float32: no second file to serve, no fetch, no CORS, and it cannot drift from
the STEP it came from.

WHY NOT SHIP THE SLICER MESH. Those are cut at 0.01 mm / 5 deg because the
detent crown has a 1.08 mm valley and the bores are O11.8 -- detail nobody can
see on a 700 px canvas, at many times the bytes. This runs coarse ON PURPOSE
and prints the saving so the choice stays honest.

EVERY PART CARRIES AN EXPLODE VECTOR, so the page can animate between the
assembled unit and the exploded stack instead of shipping two pictures. The
assembled transforms are the ones cad/assembly.py uses, not a second set - a
viewer that disagreed with the renders would be worse than no viewer.

Positions only. Normals are computed per face in the page, which is smaller
than shipping them and gives the same flat-shaded look as the stills.
"""
import sys, json, base64, struct, os
sys.path.insert(0, "cad")
from build123d import *
from parts_lib import pi4, pican_m, drok as _drok, rtl_sdr, finned

H = json.load(open("cad/out/housing.json"))
S = json.load(open("cad/out/shroud.json"))
B = json.load(open("cad/out/bail.json"))

# THE ANGULAR TOLERANCE IS THE ONE THAT MATTERS, which is not obvious and cost
# a round trip to find. At the default 0.1 rad the cover meshes to 55,810
# triangles and loosening the LINEAR tolerance from 0.25 to 2.0 changes that by
# nothing at all; at 0.5 rad the same solid is 12,216 for a result that is
# indistinguishable at 700 px. Curved-surface refinement, not chord height, is
# what fills this budget.
#
# (Watch out when measuring: OCC caches its triangulation on the shape, so a
# second tessellate() at a different tolerance hands back the FIRST mesh. Every
# number above came from a fresh import.)
WEB_TOL, WEB_ANG = 0.5, 0.5

BACK = H["DEPTH"] + H["GASKET_C"] + H["COVER_T"]
SDR_W, SDR_L, SDR_T = H["SDR_W"], H["SDR_L"], H["SDR_T"]
_floor = -H["PI_BUMP_H"] + H["WALL"]


def _solid(path):
    s = import_step(path)
    return s.solids()[0] if len(s.solids()) == 1 else s


SHELL = _solid("cad/out/helm_shell_revD.stp")
COVER = _solid("cad/out/helm_cover_revD.stp")
VISOR = _solid("cad/out/helm_visor_revD.stp")
SHROUD = _solid("cad/out/heatsink_shroud_revD.stp")
ARM = _solid("cad/out/bail_arm_revA.stp")
BASE = _solid("cad/out/bail_base_revA.stp")

# The display is an envelope, as it is everywhere else in this repo - it is a
# bought module and the only thing that matters is the volume it occupies.
DISP = Pos(H["APER_X"], H["APER_Y"], H["FACE_T"] + H["GLUE_T"]) * Box(
    H["MOD_W"], H["MOD_H"], H["MOD_D"], align=(Align.CENTER, Align.CENTER, Align.MIN))

# EXPLODE IS ALONG Z, the stack axis, and the numbers are ordered front to back
# so nothing overtakes its neighbour on the way out. Front of the unit is -z.
#   (key, title, shape, colour, explode dz)
PARTS = [
    ("visor",  "Sun visor",     VISOR,                              "#2f6fc4", -210),
    ("shell",  "Front shell",   SHELL,                              "#2a62b4",  -90),
    ("display", "12.3in display", DISP,                             "#14171c",    0),
    ("pi",     "Raspberry Pi 4", Pos(60, -20, BACK - 40) * pi4(),   "#1d7543",  110),
    ("hat",    "PiCAN-M",       Pos(60, -20, BACK - 28) * pican_m(), "#94282d", 140),
    ("drok",   "DROK buck",     Pos(-140, 40, BACK - 38) * _drok(), "#1f6e78",  110),
    ("sdr",    "RTL-SDR",       (Pos(H["SDR_X"], H["SDR_Y"], BACK - _floor - 3.5 - SDR_W)
                                 * Box(SDR_T, SDR_L, SDR_W,
                                       align=(Align.CENTER, Align.CENTER, Align.MIN))),
                                                                    "#33995c",  110),
    ("cover",  "Rear cover",    Pos(0, 0, BACK) * Rot(180, 0, 0) * COVER, "#21518f", 250),
    ("heatsink", "Heatsink",    (Pos(S["AP_CX"] if "AP_CX" in S else H["AP_CX"], 0, BACK - 3.0)
                                 * finned(H["HS_L"], H["HS_W"], H["HS_H"], base=3.0)),
                                                                    "#9ea4ac",  330),
    ("shroud", "Fan shroud",    (Pos(H["AP_CX"], 0, BACK + S["SHROUD_OD"])
                                 * Rot(180, 0, 0) * SHROUD),        "#21518f",  400),
]

out, raw_total = {}, 0
for key, title, shape, colour, dz in PARTS:
    verts, tris = shape.tessellate(WEB_TOL, WEB_ANG)
    verts = [(q.X, q.Y, q.Z) for q in verts]
    # Triangle soup. Indexed would be smaller in theory, but the index array
    # costs 4 bytes a corner and the vertex reuse on these solids is poor -
    # measured, the soup won.
    buf = bytearray()
    for a, b, c in tris:
        for i in (a, b, c):
            x, y, z = verts[i]
            buf += struct.pack("<fff", x, y, z)
    out[key] = {"title": title, "tris": len(tris), "colour": colour,
                "explode": [0, 0, dz],
                "b64": base64.b64encode(bytes(buf)).decode("ascii")}
    raw_total += len(buf)
    print(f"  {key:9s} {len(tris):6d} tris  {len(buf)/1024:7.1f} KB raw  "
          f"{len(out[key]['b64'])/1024:7.1f} KB b64")

# the whole assembly's bounds, so the page can frame it without guessing
_all = Compound([s for _, _, s, _, _ in PARTS])
bb = _all.bounding_box()
meta = {"centre": [(bb.min.X + bb.max.X)/2, (bb.min.Y + bb.max.Y)/2, (bb.min.Z + bb.max.Z)/2],
        "radius": max(bb.size.X, bb.size.Y, bb.size.Z) / 2,
        "rev": H["REV"], "tol": WEB_TOL, "ang": WEB_ANG}

b64_total = sum(len(v["b64"]) for v in out.values())
# The page has a hard 16 MB ceiling and the PNGs already spend most of it. If
# this grows, raise WEB_TOL rather than dropping a part - a viewer missing the
# cover is not a viewer.
assert b64_total < 3_500_000, (
    f"web meshes are {b64_total/1e6:.2f} MB of base64 - raise WEB_TOL")

json.dump({"meta": meta, "parts": out}, open("cad/out/web3d.json", "w"))
print(f"\n  {len(out)} parts, {b64_total/1024:.0f} KB of base64 "
      f"at {WEB_TOL} mm / {WEB_ANG} rad")
