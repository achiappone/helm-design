"""
Split the front shell so it fits a 350 bed, both halves FACE DOWN.

Joint sits on the divider between the display zone and the control column, so
the seam lands on a line that is already there rather than across the face.

  A  display section   x > SPLIT_X
  B  control section   x < SPLIT_X

Bonded, not bolted. The 2.5 mm face is too thin for a lap and the gasket groove
runs straight through the joint, so this has to be a glued seam - a butt joint
would leak. B carries a 16 mm strap into A's rim and brim where there IS
thickness, giving a real glue land; 4 printed dowels align it.

The brim bolts then clamp both halves to the cover, so the joint carries very
little once assembled.
"""
from build123d import *
import json

SHELL = import_step("cad/out/helm_shell_revB.stp")
H = json.load(open("cad/out/housing.json"))
OW, OH, DEPTH = H["OUT_W"], H["OUT_H"], H["DEPTH"]

SPLIT_X = -137.0          # mid-divider
LAP, LAP_T = 16.0, 2.0    # strap into A's rim/brim
DOWEL_D, DOWEL_L = 4.0, 6.0
BIG = 600

def half(keep_positive):
    box = Pos(SPLIT_X + (BIG/2 if keep_positive else -BIG/2), 0, 0) * Box(BIG, BIG, BIG)
    return SHELL & box

A = half(True)
B = half(False)

# ── glue strap: only in the rim and brim, where there is material ─────────
# Across the face itself (z 0..2.5) it stays a butt joint - 2.5 mm cannot
# carry a lap - so the bond line does the work there.
RIM_Y = OH/2 - 3.0
strap = None
for sy in (-1, 1):
    s = Pos(SPLIT_X + LAP/2, sy*(RIM_Y - 5.0), DEPTH - 5.0) * Box(
        LAP, 10.0, 8.0, align=(Align.CENTER,)*3)
    strap = s if strap is None else strap + s
B += strap & Pos(SPLIT_X + BIG/2, 0, 0) * Box(BIG, BIG, BIG) & SHELL
A -= strap

# ── alignment dowels: 2 in the brim, 2 near the face ─────────────────────
DOWELS = [(OH/2 - 8.0, DEPTH - 4.0), (-(OH/2 - 8.0), DEPTH - 4.0),
          (OH/2 - 8.0, 6.0),         (-(OH/2 - 8.0), 6.0)]
for dy, dz in DOWELS:
    pin = Pos(SPLIT_X, dy, dz) * Rot(0, 90, 0) * Cylinder(
        DOWEL_D/2, DOWEL_L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    hole = Pos(SPLIT_X, dy, dz) * Rot(0, 90, 0) * Cylinder(
        DOWEL_D/2 + 0.25, DOWEL_L + 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    B += pin & SHELL
    A -= hole

for part, name in ((A, "helm_shell_A_display"), (B, "helm_shell_B_control")):
    export_step(part, f"cad/out/{name}.stp")
    b = part.bounding_box()
    print(f"{name:24s} {b.size.X:6.1f} x {b.size.Y:6.1f} x {b.size.Z:5.1f}   "
          f"{part.volume/1000*0.62*1.07:5.0f} g   solids={len(part.solids())}")
