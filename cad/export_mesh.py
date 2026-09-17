"""
STEP -> 3MF/STL for the slicer.

WHY NOT ROUND-TRIP THROUGH FUSION: these parts are built in build123d, so
Fusion would only re-tessellate a STEP it just imported - an extra conversion
with its own tolerance, and a chance to lose units or orientation on the way.
Meshing straight from the source keeps one tessellation step and lets us pick
the deflection deliberately.

WHY THE DEFLECTION MATTERS HERE: the detent crown has a 1.08 mm valley between
teeth and the button bores are O11.8. A coarse default rounds those off - the
teeth stop nesting and the bores print undersize. 0.01 mm linear / 5 deg
angular resolves them and still keeps the files small.

3MF over STL: it carries its unit explicitly, so there is no mm-vs-inch guess
at the slicer, and it survives multi-object files intact.
"""
from build123d import *
import json, os

LINEAR, ANGULAR = 0.01, 5.0          # mm, degrees
# Parts are modelled in DESIGN coordinates, which is not print orientation for
# all of them. Exporting them already laid down means the slicer drops each one
# the right way up - and in particular means the shell cannot end up face-UP,
# which would undo the whole reason its A-surface is flat.
#   shell  front face is already at z=0, so it lands A-surface down. Leave it.
#   cover  features stand off BOTH sides, so neither face can lie flat. The
#          bump tops are large and flat, so bumps-down is the best of the two -
#          and that is where it already sits.
#   visor  hood plate has its normal along +Y, i.e. standing on edge. Roll it
#          down so the hood is flat and the ears point up.
#   bracket same: the plate is vertical in the file.
PARTS = [("helm_shell_revD",   None,            "front A-surface down"),
         ("helm_cover_revD",   None,            "bumps down"),
         # The visor lies flat now: its hood hangs below the pivot axis by
         # R_EAR - VIS_T/2, so the underside is tangent to the ears. Hood normal
         # is +Y in the file, so roll it down.
         ("helm_visor_revD",   Rot(-90, 0, 0),  "hood underside down, ears up"),
         # Louvre tips and the 3 mm rim round them are the first layer - a
         # continuous perimeter loop plus the four boss ends. The ribs and fan
         # pads then land on the slat tops at 6 mm pitch, the walls go up, the
         # side awnings are 45 deg and the screw-head reliefs are pockets in the
         # top face. Nothing needs support. Open-end-down would be worse: the
         # two ribs become 162 mm bridges over the cavity.
         ("heatsink_shroud_revD", None,          "louvre tips + rim on the bed, walls up"),
         ("bail_base_revA",   Rot(0, 0, 0),    "plate flat on the bed"),
         # Rot(90), not Rot(-90). The foot pad thickens the blade INBOARD, so one face
         # of the part - blade and pad together - is flat and the other has a 7 mm
         # step. Laid the wrong way up it stood on the pad alone: 756 mm2 of a 131
         # mm part on the bed, with the blade floating 7 mm in the air.
         ("bail_arm_revA",    Rot(90, 0, 0),   "blade and pad flat, x2"),
         # Coupons. Flat already, bores vertical. The encoder one is the
         # 2.5 mm face the 8 mm bushing has to clamp - print it first.
         ("helm_encoder_coupon_revA", None,  "flat, bores up"),
         ("helm_fit_coupon_revA",     None,  "flat, feature face up")]

def lay_down(part, rot):
    """Apply the print orientation, then drop the part onto z=0."""
    if rot is not None:
        part = rot * part
    bb = part.bounding_box()
    return Pos(0, 0, -bb.min.Z) * Pos(-(bb.min.X+bb.max.X)/2, -(bb.min.Y+bb.max.Y)/2, 0) * part

def solid(path):
    s = import_step(path)
    return s.solids()[0] if len(s.solids()) == 1 else s

print(f"meshing at linear {LINEAR} mm / angular {ANGULAR} deg\n")
print(f"  {'part':22s}{'facets':>9}{'mesh cm3':>10}{'solid cm3':>11}{'error':>8}{'3mf':>10}"
      f"{'bed mm2':>9}  orientation")
for name, rot, how in PARTS:
    part = lay_down(solid(f"cad/out/{name}.stp"), rot)
    m = Mesher(unit=Unit.MM)
    m.add_shape(part, linear_deflection=LINEAR, angular_deflection=ANGULAR,
                part_number=name)
    m.write(f"cad/out/{name}.3mf")
    export_stl(part, f"cad/out/{name}.stl",
               tolerance=LINEAR, angular_tolerance=ANGULAR)
    # a mesh that has lost detail shows up as a volume error against the solid
    verts, tris = part.tessellate(LINEAR, ANGULAR)
    mv = 0.0
    for a, b, c in tris:
        p, q, r = verts[a], verts[b], verts[c]
        mv += (p.X*(q.Y*r.Z - r.Y*q.Z) - p.Y*(q.X*r.Z - r.X*q.Z)
               + p.Z*(q.X*r.Y - r.X*q.Y)) / 6.0
    mv = abs(mv)
    err = abs(mv - part.volume)/part.volume*100
    kb = os.path.getsize(f"cad/out/{name}.3mf")/1024
    _q = Pos(0,0,-part.bounding_box().min.Z)*part
    _sl = _q & (Pos(0,0,0.1)*Box(900,900,0.2))
    bed = 0.0 if _sl is None else _sl.volume/0.2
    assert err < 0.5, f"{name}: mesh is {err:.2f}% off the solid - deflection too coarse"
    b = part.bounding_box()
    print(f"  {name:22s}{len(tris):9d}{mv/1000:10.1f}{part.volume/1000:11.1f}"
          f"{err:7.3f}%{kb:7.0f} KB{bed:9.0f}  {how}")
print("\n3MF carries its own units and the part name - drop straight in, no scaling,\nand each part is already the right way up.")
