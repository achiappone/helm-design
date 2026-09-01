"""
Helm Design - Sensor Tray  (rev A)
==================================
Carries the four I2C breakouts plus the RTL-SDR, and bolts to the aluminium
chassis plate behind the display.

Board dimensions are from the Adafruit fab prints in the project folder.
Tray OUTLINE is provisional - it gets re-cut once the housing is fixed.

Layout intent:
  - ICM20948 as far from the RTL-SDR and the power side as the tray allows.
    Its magnetometer is still compromised behind a backlight; see the notes.
  - MCP9808 over an open window so it senses enclosure AIR, not tray plastic.
  - ADXL345 on four screws, axis-aligned, no compliance.

Material : ASA (blue)   Orientation : flat, standoffs UP
Layers   : 0.2 mm       Perimeters  : 4     Infill : 25% gyroid
Supports : none
"""
from build123d import *

TRAY_L, TRAY_W, TRAY_T, CORNER_R = 196.0, 118.0, 4.0, 6.0
STAND_H, STAND_D = 4.0, 6.0
M25_PILOT, M25_DEPTH = 2.2, 5.0
MOUNT_D, MOUNT_X, MOUNT_Y = 4.5, 89.0, 52.0

BIG   = (38.10, 12.70)          # MCP23017
SMALL = (20.32, 12.70)          # MCP9808 / ADXL345 / ICM20948
BOARDS = [
    ("MCP23017", -55.0,  38.0, BIG,   (43.18, 17.78)),
    ("ADXL345",    5.0,  38.0, SMALL, (25.40, 17.78)),
    ("ICM20948",  45.0,  38.0, SMALL, (25.40, 17.78)),
    ("MCP9808",   35.0, -28.0, SMALL, (25.40, 17.78)),
]
SDR_X, SDR_Y, SDR_L, SDR_W = -45.0, -28.0, 70.0, 29.0
KERB_OFF, TIE_OFF = 15.0, 19.0

# Strap-down bays for generic modules whose hole patterns vary by seller.
# Board drops between the kerbs, sits on corner pips, held by one cable tie.
# Envelope is generous - anything up to the bay size fits, and so does the
# replacement you buy in two years.
BAYS = [("PCM1808",  -55.0,  8.0, 40.0, 32.0),
        ("PCM5102A",   0.0,  8.0, 32.0, 26.0),
        ("PCM5102A",  40.0,  8.0, 32.0, 26.0)]
PIP_D, PIP_H, KERB_T, KERB_H = 5.0, 1.5, 2.0, 5.0

t = Box(TRAY_L, TRAY_W, TRAY_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
t = fillet(t.edges().filter_by(Axis.Z), CORNER_R)

for mx in (-MOUNT_X, 0.0, MOUNT_X):
    for my in (-MOUNT_Y, MOUNT_Y):
        t -= Pos(mx, my) * Cylinder(MOUNT_D/2, 3*TRAY_T)

for name, bx, by, (hx, hy), _ in BOARDS:
    for sx in (-1, 1):
        for sy in (-1, 1):
            px, py = bx + sx*hx/2, by + sy*hy/2
            t += Pos(px, py, TRAY_T) * Cylinder(STAND_D/2, STAND_H,
                        align=(Align.CENTER, Align.CENTER, Align.MIN))
            t -= Pos(px, py, TRAY_T + STAND_H - M25_DEPTH) * Cylinder(
                        M25_PILOT/2, M25_DEPTH + 0.5,
                        align=(Align.CENTER, Align.CENTER, Align.MIN))
            t -= Pos(px, py, TRAY_T + STAND_H - 0.7) * Cone(
                        M25_PILOT/2 + 0.6, M25_PILOT/2, 0.8,
                        align=(Align.CENTER, Align.CENTER, Align.MIN))

# MCP9808 senses AIR, not plastic - open the tray under it
t -= Pos(35.0, -28.0) * Box(15.0, 8.0, 3*TRAY_T, align=(Align.CENTER,)*3)

# RTL-SDR cradle: low kerbs + tie slots, shell left exposed as its own heatsink
for sy in (-1, 1):
    t += Pos(SDR_X, SDR_Y + sy*KERB_OFF, TRAY_T) * Box(
        58.0, 3.0, 5.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
for tx in (SDR_X - 24, SDR_X + 24):
    for sy in (-1, 1):
        t -= Pos(tx, SDR_Y + sy*TIE_OFF) * Box(4.5, 2.5, 3*TRAY_T,
                                                       align=(Align.CENTER,)*3)

for _n, bx, by, bl, bw in BAYS:
    for sy in (-1, 1):                                   # kerb walls, long sides
        t += Pos(bx, by + sy*(bw/2 + KERB_T/2), TRAY_T) * Box(
            bl, KERB_T, KERB_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for sx in (-1, 1):                                   # corner support pips
        for sy in (-1, 1):
            t += Pos(bx + sx*(bl/2 - 4.0), by + sy*(bw/2 - 4.0), TRAY_T) * Cylinder(
                PIP_D/2, PIP_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for sx in (-1, 1):                                   # tie slots
        t -= Pos(bx + sx*(bl/2 - 6.0), by + (bw/2 + KERB_T + 3.5)) * Box(
            4.5, 2.5, 3*TRAY_T, align=(Align.CENTER,)*3)
        t -= Pos(bx + sx*(bl/2 - 6.0), by - (bw/2 + KERB_T + 3.5)) * Box(
            4.5, 2.5, 3*TRAY_T, align=(Align.CENTER,)*3)

def engrave(s, txt, x, y, size=3.2, rot=0):
    return s - Pos(x, y, TRAY_T) * Rot(0, 0, rot) * extrude(
        Text(txt, font_size=size), amount=-0.6)

for name, bx, by, _, (ol, ow) in BOARDS:
    t = engrave(t, name, bx, by + ow/2 + 4.5)
t = engrave(t, "RTL-SDR", SDR_X, SDR_Y, 4.0)
for _n, bx, by, bl, bw in BAYS:
    t = engrave(t, _n, bx, by - bw/2 - 8.5, 3.2)
t = engrave(t, "X>", 5.0, 38.0, 3.2)          # ADXL345 axis reference
t = engrave(t, "X>", 45.0, 38.0, 3.2)          # ICM20948 axis reference
t = engrave(t, "SENSOR TRAY revB", 40.0, -50.0, 3.6)

t = chamfer(t.faces().sort_by(Axis.Z)[0].edges(), 0.5)
export_step(t, "cad/out/sensor_tray_revA.stp")
bb = t.bounding_box()
print(f"TRAY   vol={t.volume/1000:6.1f} cm3 solids={len(t.solids())} "
      f"bbox={bb.size.X:.0f}x{bb.size.Y:.0f}x{bb.size.Z:.0f}")
