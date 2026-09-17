"""
Web meshes -- the assembled unit, packed small enough to live inside the page.

The build review has always been still renders. They are true, but you cannot
look BEHIND anything in a PNG, and every question this project has had lately
-- where does the coax go, where do the bracket nuts install, I can't see where
the internal wire routes -- was really a request to ROTATE THE PART.

THIS FILE DOES NOT MODEL ANYTHING. cad/assembly.py already owns the assembled
unit, every part in its true place; it calls dump() at the end with the same
shape objects it renders. An earlier cut of this file rebuilt ten parts from
housing.json and was immediately wrong in the way this repo keeps being wrong:
it quietly omitted the antenna, the bail, the fans, the fittings and the
controls, because nothing compared it to the bill of materials.

So dump() CROSS-CHECKS THE BOM, the same way cad/exploded.py does for the
printed drawing: the numbers are parsed out of cad/build_review.py, which is
the file that owns them, and anything neither drawn nor explicitly exempt fails
the build. A viewer that silently drops a part is worse than no viewer.
"""
import json, base64, struct, re

# THE ANGULAR TOLERANCE IS THE ONE THAT MATTERS, which is not obvious and cost
# a round trip to find. At the default 0.1 rad the cover meshes to 55,810
# triangles, and loosening the LINEAR tolerance from 0.25 to 2.0 changes that
# by nothing at all; at 0.5 rad the same solid is 12,216 for a result that is
# indistinguishable at 700 px. Curved-surface refinement, not chord height, is
# what fills this budget.
#
# (Watch out when measuring: OCC caches its triangulation on a shape, so a
# second tessellate() at a different tolerance hands back the FIRST mesh.)
WEB_TOL, WEB_ANG = 0.5, 0.5

# Fitted rather than exploded: a bonded washer, a smear of sealant, a length of
# cord. Same list cad/exploded.py keeps, and for the same reason - the
# exemption is a decision, written down, not an oversight. 11 is the fit
# coupon, which is not part of the unit at all.
NO_SHAPE = {"11", "18", "21", "22", "23", "24", "29", "30", "39",
            "40", "41", "42", "43", "44", "45", "46"}

# NOT ON THE UNIT. The LP-24 disconnect bracket bolts to the DASH and the unit's
# cable plugs into it; cad/assembly.py draws it in its own local frame because
# nothing fixes where on the dash it goes - that is the installer's call. Giving
# it a position in this viewer's explode would be modelling a decision nobody has
# made, which this repo has been bitten by before. It has its own views on the
# page instead, and this exemption is why it is not in the stack.
SEPARATE_ASSEMBLY = {"9", "10", "25"}

# The page has a hard 16 MB ceiling and the PNGs already spend most of it.
BUDGET = 3_500_000


def _hex(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v * 255))) for v in c[:3])


def dump(entries, meta_extra=None, path="cad/out/web3d.json"):
    """entries = [(key, title, shape, colour, bom_items, explode_dz), ...]

    colour is a (r,g,b) float triple, as everywhere else in this repo.
    bom_items is a set of BOM numbers as strings - what this shape stands for.
    explode_dz is millimetres along +z, the stack axis, at full explode.
    """
    src = open("cad/build_review.py").read()
    bom = {m for m in re.findall(r'<tr><td class="m">(\d{1,2})[a-z]?</td>', src)}
    covered = set().union(*[e[4] for e in entries]) if entries else set()
    missing = sorted(bom - covered - NO_SHAPE - SEPARATE_ASSEMBLY, key=int)
    orphan = sorted(covered - bom, key=int)
    if missing or orphan:
        msg = []
        if missing:
            msg.append("in the BOM but NOT IN THE 3D VIEW: " + ", ".join(missing)
                       + " - add a shape, or name it in NO_SHAPE / SEPARATE_ASSEMBLY "
                         "with a reason")
        if orphan:
            msg.append("in the 3D view but NOT IN THE BOM: " + ", ".join(orphan))
        raise AssertionError("the 3D viewer and the BOM disagree:\n  - "
                             + "\n  - ".join(msg))

    out, lo, hi = {}, None, None
    for key, title, shape, colour, items, dz in entries:
        verts, tris = shape.tessellate(WEB_TOL, WEB_ANG)
        buf = bytearray()
        for a, b, c in tris:
            for i in (a, b, c):
                q = verts[i]
                buf += struct.pack("<fff", q.X, q.Y, q.Z)
        out[key] = {"title": title, "tris": len(tris), "colour": _hex(colour),
                    "items": sorted(items, key=int), "explode": [0, 0, dz],
                    "b64": base64.b64encode(bytes(buf)).decode("ascii")}
        bb = shape.bounding_box()
        lo = bb.min if lo is None else type(lo)(min(lo.X, bb.min.X), min(lo.Y, bb.min.Y),
                                                min(lo.Z, bb.min.Z))
        hi = bb.max if hi is None else type(hi)(max(hi.X, bb.max.X), max(hi.Y, bb.max.Y),
                                                max(hi.Z, bb.max.Z))
        print(f"  {key:11s} {len(tris):6d} tris  {len(buf)/1024:7.1f} KB  "
              f"items {','.join(sorted(items, key=int))}")

    meta = {"centre": [(lo.X + hi.X)/2, (lo.Y + hi.Y)/2, (lo.Z + hi.Z)/2],
            "radius": max(hi.X - lo.X, hi.Y - lo.Y, hi.Z - lo.Z) / 2,
            "tol": WEB_TOL, "ang": WEB_ANG}
    meta.update(meta_extra or {})

    total = sum(len(v["b64"]) for v in out.values())
    assert total < BUDGET, (
        f"web meshes are {total/1e6:.2f} MB of base64 against a {BUDGET/1e6:.1f} MB "
        f"budget - raise WEB_ANG rather than dropping a part")
    json.dump({"meta": meta, "parts": out}, open(path, "w"))
    print(f"\n  3D view: {len(out)} parts, {total/1024:.0f} KB of base64 at "
          f"{WEB_TOL} mm / {WEB_ANG} rad")
    print(f"  BOM cross-check: {len(bom)} rows, {len(covered)} in the view, "
          f"{len(NO_SHAPE)} fitted-not-shown, {len(SEPARATE_ASSEMBLY)} on the dash")
    return out
