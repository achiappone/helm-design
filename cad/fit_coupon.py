"""
Helm Design - Fit-Check Coupon  (rev A)
=======================================
Print this FIRST, in blue ASA, at your production settings.
It validates every panel interface and calibrates hole compensation
before you commit filament to the real enclosure.

Material : ASA (blue)     Orientation : flat, feature face UP
Layers   : 0.2 mm         Perimeters  : 5      Infill : 25% gyroid
Supports : none required
"""
from build123d import *

# ---------------------------------------------------------------- parameters
PLATE_L, PLATE_W = 190.0, 115.0
PANEL_T          = 4.0      # nominal panel thickness
THICK_PAD_T      = 7.0      # local thickening, to find button barrel limit

# CNLINKO LP-24  (confirmed drawing)
LP24_BORE        = 24.4
LP24_HOLE_D      = 3.0      # print 3.0, drill to 3.2
LP24_PITCH       = 26.0

# Twidec PBS-33B push button (confirmed drawing)
BTN_BORE         = 12.0

# Gore-style M12x1.5 pressure vent
VENT_CLEAR       = 12.3     # clearance hole; vent's own nut + O-ring seals
VENT_PAD_D       = 24.0     # flat sealing face for the washer

# LISTENJIALE NPT 3/4" cable gland, 12.5-18 mm cable  (item 16)
# !! NO DRAWING SUPPLIED - these are standard NPT 3/4 values. MEASURE YOURS.
NPT34_CLEAR      = 28.0     # panel bore for the male thread
NPT34_PAD_D      = 44.0     # flat face for the gland's O-ring + locknut

# Gasket gland - round cord face seal.  VERIFY CORD DIA FIRST.
CORD_D           = 3.0
GLAND_W          = CORD_D * 1.15   # 3.45
GLAND_D          = CORD_D * 0.77   # 2.31
GLAND_L, GLAND_H, GLAND_R = 100.0, 26.0, 8.0

# 316 SS heat-set inserts  (VERIFY against your insert datasheet)
INSERT_M3, INSERT_M4 = 4.0, 5.6
THREAD_M3, THREAD_M4 = 2.6, 3.5   # thread-forming pilots, 316 SS direct into ASA
BOSS_WALL, BOSS_H    = 2.0, 8.0

# Hole-compensation ladder: all nominally Ø8.00. Measure which prints true.
LADDER_NOM   = 8.0
LADDER_STEPS = [0.0, 0.1, 0.2, 0.3, 0.4]

TXT_H, TXT_D = 4.0, 0.6

def label(txt, x, y, size=TXT_H, rot=0):
    s = Pos(x, y) * Rot(0, 0, rot) * Text(txt, font_size=size)
    return extrude(s, amount=TXT_D)

# ---------------------------------------------------------------- base plate
p = Box(PLATE_L, PLATE_W, PANEL_T,
        align=(Align.CENTER, Align.CENTER, Align.MIN))
p = fillet(p.edges().filter_by(Axis.Z), 6.0)

# local thickened pad (button barrel depth test)
p += Pos(6, 32, 0) * Box(28, 28, THICK_PAD_T,
                          align=(Align.CENTER, Align.CENTER, Align.MIN))

# flat sealing pad for the vent washer
p += Pos(34, 32, 0) * Cylinder(VENT_PAD_D / 2, PANEL_T + 1.0,
                               align=(Align.CENTER, Align.CENTER, Align.MIN))

TOP = PANEL_T + THICK_PAD_T  # safe cut height

# ------------------------------------------- ZONE A: LP-24 connector cutout
p -= Pos(-62, 32) * Cylinder(LP24_BORE / 2, 3 * TOP)
for sx in (-1, 1):
    for sy in (-1, 1):
        p -= Pos(-62 + sx * LP24_PITCH / 2,
                 32 + sy * LP24_PITCH / 2) * Cylinder(LP24_HOLE_D / 2, 3 * TOP)

# ------------------------------------------------ ZONE B: push button bores
p -= Pos(-22, 32) * Cylinder(BTN_BORE / 2, 3 * TOP)   # through 4.0 mm
p -= Pos(6, 32) * Cylinder(BTN_BORE / 2, 3 * TOP)     # through 7.0 mm pad

# ------------------------------------------------------- ZONE C: vent bore
p -= Pos(34, 32) * Cylinder(VENT_CLEAR / 2, 3 * TOP)

# --------------------------------------------- ZONE C2: NPT 3/4 gland bore
p += Pos(70, 32, 0) * Cylinder(NPT34_PAD_D / 2, PANEL_T + 1.0,
                               align=(Align.CENTER, Align.CENTER, Align.MIN))
p -= Pos(70, 32) * Cylinder(NPT34_CLEAR / 2, 3 * TOP)

# --------------------------------------- ZONE D: hole compensation ladder
for i, step in enumerate(LADDER_STEPS):
    x = -70 + i * 35
    p -= Pos(x, 0) * Cylinder((LADDER_NOM + step) / 2, 3 * TOP)

# ------------------------------------------------- ZONE E: gasket gland run
outer = RectangleRounded(GLAND_L + GLAND_W, GLAND_H + GLAND_W, GLAND_R + GLAND_W / 2)
inner = RectangleRounded(GLAND_L - GLAND_W, GLAND_H - GLAND_W, GLAND_R - GLAND_W / 2)
ring  = Pos(-35, -33) * (outer - inner)
p -= extrude(Plane.XY.offset(PANEL_T) * ring, amount=-GLAND_D)

# ----------------------------------------- ZONE F: heat-set insert bosses
# left pair = heat-set inserts, right pair = screw threads straight into ASA.
# Drive a 316 SS screw into each right-hand boss and try to pull it out.
for x, bore, od in ((38, INSERT_M3, 8.0), (55, INSERT_M4, 9.6),
                    (72, THREAD_M3, 8.0), (89, THREAD_M4, 10.0)):
    p += Pos(x, -37, PANEL_T) * Cylinder(od / 2, BOSS_H,
                                         align=(Align.CENTER, Align.CENTER, Align.MIN))
    p -= Pos(x, -37, PANEL_T + BOSS_H - 6.0) * Cylinder(bore / 2, 6.5,
                                         align=(Align.CENTER, Align.CENTER, Align.MIN))

# ------------------------------------------------- first-layer chamfer relief
p = chamfer(p.faces().sort_by(Axis.Z)[0].edges(), 0.5)

# ---------------------------------------------------------------- labels
# Engraved, not raised: coincident-face fusion is unreliable and raised
# text on a 0.2 mm layer delaminates. 0.6 mm deep reads fine in blue ASA.
def engrave(solid, txt, x, y, size=3.0, z=PANEL_T, depth=0.6):
    return solid - Pos(x, y, z) * extrude(Text(txt, font_size=size), amount=-depth)

for t, x, y, sz in [
    ("LP-24",      -62, 51, 4.0),
    ("BTN 4mm",    -22, 51, 3.2),
    ("BTN 7mm",      6, 51, 3.2),
    ("VENT",        34, 51, 3.2),
    ("NPT 3/4",     70, 51, 3.2),
    ("8.0", -70, -9, 3.4), ("8.1", -35, -9, 3.4), ("8.2", 0, -9, 3.4),
    ("8.3",  35, -9, 3.4), ("8.4",  70, -9, 3.4),
    ("MEASURE ALL FIVE - PICK THE ONE THAT READS 8.00", 0, -14, 3.4),
    ("M3i", 38, -49, 3.0), ("M4i", 55, -49, 3.0),
    ("M3t", 72, -49, 3.0), ("M4t", 89, -49, 3.0),
    ("HELM FIT COUPON revA   ASA", -40, -53.5, 3.5),
]:
    p = engrave(p, t, x, y, sz)

# ---------------------------------------------------------------- export
out = "/Users/anthonychiappone/Helm_Design/cad/out/helm_fit_coupon_revA.stp"
export_step(p, out)
print(f"OK  volume = {p.volume/1000:.1f} cm^3   solids = {len(p.solids())}")
print(f"    {out}")
