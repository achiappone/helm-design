"""
Bought-part envelopes with enough shape to be RECOGNISED.

Every bought part in this project used to be a plain Box. That is honest about
what is known, but it makes a drawing unreadable: six green rectangles of
different sizes tell you nothing about which is the Pi, and a heatsink drawn as
a solid block hides the only feature it has. You end up counting balloons to
read your own assembly.

These are still ENVELOPES - correct outline, correct height, no internal detail
and no claim to be the vendor's CAD. What they add is the handful of features
that make a part identifiable at a glance: fins on a heatsink, the connector
stack on a Pi, a header on a HAT. Nothing here is a mating dimension; if you
need one of those, measure the real part and put it in cad/measured_parts.py.

Shared so that exploded.py, assembly.py and subassemblies.py draw the same
thing. They used to each have their own idea of a heatsink.
"""
from build123d import *
import math

MIN = (Align.CENTER, Align.CENTER, Align.MIN)
CEN = (Align.CENTER,) * 3


def finned(l, w, h, base=4.0, fin_t=1.6, gap=3.2, along_x=True):
    """Extruded heatsink: a base plate with fins standing off it.

    The fins ARE the part - a heatsink rendered as a solid block looks like a
    lump of metal and reads as packaging rather than cooling.
    """
    s = Box(l, w, base, align=MIN)
    span = w if along_x else l
    pitch = fin_t + gap
    n = max(2, int((span - fin_t) // pitch) + 1)
    used = (n - 1) * pitch + fin_t
    start = -used / 2 + fin_t / 2
    for i in range(n):
        off = start + i * pitch
        if along_x:
            s += Pos(0, off, base) * Box(l, fin_t, h - base, align=MIN)
        else:
            s += Pos(off, 0, base) * Box(fin_t, w, h - base, align=MIN)
    return s


def pcb(l, w, t=1.6, comps=()):
    """Bare board plus a few component blocks: (dx, dy, dl, dw, dh)."""
    s = Box(l, w, t, align=MIN)
    for dx, dy, dl, dw, dh in comps:
        s += Pos(dx, dy, t) * Box(dl, dw, dh, align=MIN)
    return s


def header(n_long, rows=2, pitch=2.54, h=8.5):
    """A pin header, drawn as its plastic body - the pins do not read at scale."""
    return Box(n_long * pitch, rows * pitch, h, align=MIN)


def pi4():
    """Raspberry Pi 4 B, 85 x 56. The connector stack at the +x end and the
    40-pin header along +y are what make it read as a Pi rather than a board."""
    s = pcb(85, 56, 1.6, comps=[
        (18, -12, 24, 24, 2.4),        # SoC + RAM, the bit under the heatsink
        (-30, -14, 12, 12, 1.2),       # USB-C PMIC area
    ])
    # USB x2 + Ethernet, the tall stack everyone recognises
    s += Pos(28, 14, 1.6) * Box(28, 17, 13.5, align=MIN)
    s += Pos(28, -8, 1.6) * Box(28, 17, 13.5, align=MIN)
    s += Pos(28, -30, 1.6) * Box(28, 16, 13.5, align=MIN)
    # 40-pin GPIO header along the long edge
    s += Pos(-13, 24.5, 1.6) * header(20)
    # micro-HDMI pair and USB-C on the -x edge
    for dy in (-8, 6):
        s += Pos(-40, dy, 1.6) * Box(8, 7, 3.2, align=MIN)
    s += Pos(-40, 20, 1.6) * Box(6, 9, 3.4, align=MIN)
    return s


def armor_lite(fan_d=35.0, h=17.0):
    """GeeekPi Armor Lite: a finned aluminium plate over the Pi with a 3510 PWM
    fan sunk into it. Drawn with its fins and its fan opening, because a plain
    block is indistinguishable from the Pi it sits on."""
    s = finned(84, 55, h - 6.0, base=3.5, fin_t=1.6, gap=3.4)
    s = Pos(0, 0, 0) * s
    # fan pocket and hub, roughly central
    s -= Pos(10, 0, 2.0) * Cylinder(fan_d / 2, h, align=MIN)
    s += Pos(10, 0, 2.0) * Cylinder(fan_d / 2, 2.0, align=MIN)
    s += Pos(10, 0, 4.0) * Cylinder(6.0, 6.0, align=MIN)
    for i in range(7):
        s += (Pos(10, 0, 4.0) * Rot(0, 0, i * 360 / 7)
              * Box(fan_d / 2 - 1, 2.2, 5.0, align=(Align.MIN, Align.CENTER, Align.MIN)))
    return s


def pican_m():
    """PiCAN-M HAT: board, GPIO socket underneath, and the screw terminal and
    can bus connector that make it recognisable."""
    s = pcb(65, 56.5, 1.6, comps=[
        (-18, -10, 18, 14, 3.0),       # transceiver / regulator cluster
    ])
    s += Pos(-3, 24.5, 1.6) * header(20, h=9.0)          # stacking socket
    s += Pos(22, 12, 1.6) * Box(16, 22, 12.0, align=MIN)  # screw terminal block
    return s


def drok():
    """DROK buck converter: board dominated by a toroid and two electrolytics."""
    s = pcb(65, 58, 1.6, comps=[(-12, 0, 20, 20, 3.0)])
    s += Pos(8, 6, 1.6) * Cylinder(11.0, 12.0, align=MIN)    # toroidal inductor
    for dx in (-20, -20):
        s += Pos(dx, -18, 1.6) * Cylinder(5.0, 13.0, align=MIN)
    s += Pos(22, -14, 1.6) * Box(14, 12, 9.0, align=MIN)     # terminal block
    return s


def breakout(l=25.4, w=17.8):
    """Adafruit-style breakout: small board with a header along one edge."""
    s = pcb(l, w, 1.2, comps=[(0, 0, 6, 6, 1.2)])
    s += Pos(0, w / 2 - 2.0, 1.2) * header(int(l / 2.54) - 1, rows=1, h=3.0)
    return s


def nyloc(af=8.0, h=5.0, bolt=5.0):
    """A 316 nyloc nut: hex body with the nylon insert collar proud of it.

    Drawn because "M5 nyloc" in a BOM is a line of text, and where the nut SITS
    is a geometric question - it needs a pocket, a face to bear on, and a hand
    to reach it. Three of these were specified on this unit before any of them
    had somewhere to go."""
    cr = af / 2 / math.cos(math.pi / 6)
    s = extrude(RegularPolygon(cr, 6), h)
    s += Pos(0, 0, h) * Cylinder(cr * 0.86, 1.6, align=MIN)   # nylon collar
    s -= Cylinder(bolt / 2, h + 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return s


def cap_screw(d=5.0, length=25.0, head_d=None, head_h=None):
    """A socket-head cap screw, drawn so a render shows which way it goes in."""
    head_d = head_d or d * 1.6
    head_h = head_h or d * 0.9
    return (Cylinder(head_d / 2, head_h, align=MIN)
            + Pos(0, 0, head_h) * Cylinder(d / 2, length, align=MIN))


def push_button(bore=11.8, dome=17.5, barrel=13.0):
    """Twidec PBS-33B: domed bezel in front of the panel, threaded barrel behind."""
    s = Cylinder(dome / 2, 5.7, align=MIN)
    s += Pos(0, 0, -barrel) * Cylinder(bore / 2 - 0.4, barrel, align=MIN)
    return s
