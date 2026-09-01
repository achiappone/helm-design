"""
Helm Display Housing  (rev C)  -- FRONT SHELL + REAR COVER
==========================================================
rev B put the four buttons and the encoder in a COLUMN beside the display.
That made the shell 389 wide, which does not fit the K2 Plus's 350 bed, so it
had to be printed in two halves and bonded across the front face.

rev C moves the controls into a ROW BELOW the display. The 38 mm control strip
stops being width and becomes height, where there was room to spare:

              rev B                        rev C
  OUT      389 x 165                    341 x 187
  bed      389 x 193  -> SPLIT          341 x 215  -> ONE PIECE

That is the whole point of the revision: the front shell prints as a single
object, face down, and split_shell.py is no longer needed.

Carried over from rev B:
  FRONT SHELL  bezel face + walls, one piece. NOTHING visible on the front.
  REAR COVER   flat plate. Its holes thread into the shell's rear brim.
  - front A-surface prints face-down, so it is smooth and bed-flat
  - gasket is on the back, out of sight and out of the weather
  - every precision feature (aperture, glue channel, controls) is on one part

DERIVED: active area 292.5 x 109.7 (12.3" at 1920x720 = 8:3)
ASSUMED: module outline 305 x 125 x 10  <-- still needs measuring
"""
from build123d import *
import math, json

ACT_W, ACT_H = 295.0, 112.0             # MEASURED, not derived
MOD_W, MOD_H, CLR = 310.0, 130.0, 1.0   # MEASURED (CLR was 1.5)
# ROW_H is set by what actually needs flat bezel, which is NOT the bores.
# Sizing the band to the O11.8 bore gave 38 mm for a 20.5 mm footprint and put
# the whole difference straight into overall height.
#
# MEASURED: the button's outer diameter is 17.5 (the parts sheet said 21 across
# the dome - that was wrong). So the GUITAR KNOB at O20.5 is now the largest
# thing on the face and it, not the buttons, sets the row.
#
# DIVIDER 4 is not a guess either: solving "bezel above the knob == bezel below
# it" gives D = 4.0 exactly, for any ROW_H. ROW_H then just buys bezel, 0.5 mm
# per side per mm. 22 gives 14.75 each way.
ROW_H = 18.0
DIVIDER = 1.5                       # = RIM - 6, the value that balances the
                                    # bezel above and below the control row
BTN_DOME, KNOB_OD, BTN_NUT_R = 17.5, 20.5, 8.0
CTRL_MAX = max(BTN_DOME, KNOB_OD)   # whatever is biggest governs the bezel
INT_W = MOD_W + 2*CLR
INT_H = (MOD_H + 2*CLR) + DIVIDER + ROW_H
# RIM 14 is the FLOOR, not a preference - see the brim budget below, which
# fails the build if RIM is ever set too small to hold all five features.
RIM = 7.5
OUT_W, OUT_H = INT_W + 2*RIM, INT_H + 2*RIM          # 341 x 205
# Viewer's right is model -X: the front face normal is -Z, so the camera looks
# along +Z and cross(forward, up) = (-1,0,0). The encoder therefore sits at
# NEGATIVE x to fall under the viewer's right hand.
DISP_CX = 0.0
DISP_CY =  INT_H/2 - (MOD_H + 2*CLR)/2               # +22.0, display sits high
ROW_CY  = -INT_H/2 + ROW_H/2                         # -69.5, control row below
DEPTH, FACE_T, WALL, COVER_T = 22.0, 2.5, 3.5, 6.0   # display measured 15 deep
R_OUT = 14.0

# -- control row -----------------------------------------------------------
# Four soft keys spread under the screen, encoder at the viewer's-right end.
# 70 mm pitch, not rev B's 24: across 313 mm there is no reason to crowd them,
# and each key now sits under the soft key it drives.
BTN_D, ENC_D, BTN_PITCH = 11.8, 9.7, 70.0    # BTN_D MEASURED, was 12.0 assumed
BTN_X = [120.0 - i*BTN_PITCH for i in range(4)]      # 120, 50, -20, -90
ENC_X = -134.5                                       # 44.5 clear of the last key
# Each button gets a RECESSED lead-in, now VERTICAL - it points up from the
# button to the screen edge instead of sideways. Recessed, not raised: the
# front A-surface prints face-down, so a proud feature stands the whole face
# off the bed and the part balances on four ribs. Cut in, the same graphic is
# just a gap in the first three layers.
# 0.6 = 3 x 0.2 layers, leaving 1.9 of the 2.5 mm face.
EMB_W, EMB_D = 1.6, 0.6
EMB_Y0, EMB_Y1 = -62.0, -49.0        # button bore top -64.1, aperture edge -47.0

# The aperture is set by the BOND BAND, not by the active area. The band used
# to be 7.0 wide and landed exactly on the module's edge, which pinned the
# bezel at 22.5. But the panel's weight is carried by the cover's bearing
# posts - the silicone only has to SEAL - so 5.0 is enough land, and the extra
# 2 mm per side goes into the aperture instead of the bezel. What shows there
# is the module's own black border, not housing.
BOND_BAND = 5.0                     # flat land for a single bead
APER_W, APER_H = MOD_W - 2*BOND_BAND, MOD_H - 2*BOND_BAND
assert APER_W > ACT_W and APER_H > ACT_H, (
    f"aperture {APER_W}x{APER_H} would mask active pixels ({ACT_W}x{ACT_H})")
APER_X, APER_Y = DISP_CX, DISP_CY

M3_PILOT, M3_CLEAR = 2.6, 3.4
M4_PILOT, M4_CLEAR, PILOT_L = 3.5, 4.5, 11.0
GW, GD = 3.0*1.15, 3.0*0.77          # 3 mm cord: 3.45 wide, 2.31 deep

# -- brim land budget ------------------------------------------------------
# The brim carries a FLAT GASKET with the screws passing THROUGH it, not an
# O-ring in a groove beside them. That is the whole reason it can be 8 mm.
#
# With a groove, the screw cannot pass through the seal, so the two sit side by
# side and the brim has to carry both:
#     land 2.0 + M4 3.5 + land 1.6 + groove 3.45 + land 2.0 = 12.55  -> RIM 13
# The O-ring itself was never the problem - alone it needs 7.45. The screws
# beside it cost the other 5.
#
# A flat gasket seals around each screw as well, so the fasteners come inside
# the seal instead of sitting in the wet zone outboard of it:
#     land + M4 + land = 7.90  -> RIM 8.5
#
# The brim face is a flat plane at z=DEPTH and the shell prints face-down, so
# that face is a solid top surface - the best finish FDM gives, and the right
# one to squeeze a soft gasket against.
#
# The tapered loft means the cavity edge at the BRIM FACE is not at RIM, it is
# ~0.95*RIM, because the taper has not quite finished.
_BRIM_FRAC  = (DEPTH - FACE_T)/(DEPTH + 1 - FACE_T)
BRIM_CAVITY = RIM - (RIM - WALL)*(1 - _BRIM_FRAC)
# The two lands do different jobs, so the spare is split unevenly. OUTER is
# hoop for a thread-forming M3 - too little and the screw splits out to the
# free edge, which is the failure you would find while assembling. INNER is the
# gasket's continuous sealing path inboard of the bolt holes. The outer one
# gets the larger share because it is the one that fails audibly.
_MIN_OUT, _MIN_IN = 2.00, 1.70
_slack = BRIM_CAVITY - M3_PILOT - _MIN_OUT - _MIN_IN
assert _slack >= 0, (f"brim too narrow at RIM={RIM}: budget {BRIM_CAVITY:.2f} vs "
                     f"need {M3_PILOT+_MIN_OUT+_MIN_IN:.2f}, short by {-_slack:.2f} mm.")
LAND_OUT, LAND_IN = _MIN_OUT + 0.65*_slack, _MIN_IN + 0.35*_slack
LAND_BG = 0.0                       # no groove to stand off from
BOLT_INSET = LAND_OUT + M3_PILOT/2
GASKET_W = BRIM_CAVITY              # gasket spans the whole brim face

VENT_D = 12.3                       # Gore vent, low on the cover
# Antenna: FM/SDR whip on a waterproof M16 SMA bulkhead. It lives on the REAR
# COVER, not the top wall. The top wall cannot take it, for a reason no amount
# of bump-out fixes: the INNER nut is trapped between the back of the bezel
# (z 2.50) and the floor of the gasket groove (z 19.69) = 17.19 mm, and a O20
# nut needs 20. Tilting the bore back shrinks what the nut spans in z
# (20*cos40 = 15.32, which fits) but then the PAD has to reach outboard past
# the wall, and on a tilted axis going out in y also goes back in z - the seat
# ends up at z 24.9, past the brim plane, straddling the shell/cover joint.
#
# The cover has none of this. It is a flat plate whose 6.0 mm thickness is
# already inside the bulkhead's 1..8 mm grip, both faces are parallel by
# construction, and O20 of clear flat face on each side costs nothing.
# FIT-CHECK BUILD: no bulkhead anywhere until the housing has been printed and
# offered up to a real display. Flip this to True once the call is made.
#
# WHERE IT CAN GO, and what actually limits it. The bulkhead must be on the TOP
# WALL for whip orientation. That wall's inside is the tapered loft - a ramp,
# 3.50 thick at z=2.5 and 12.30 by z=19.69 - so the inner nut has no flat seat.
#
# SPOTFACE IT. Cut the seat back to the ramp's shallow end, y = OUT_H/2 - 3.50.
# That leaves 3.50 of wall under the bore (grip is 1..8, fine), and puts the nut
# 6.50 clear of the display panel. Nut THICKNESS then stops mattering - there is
# 11.50 of room before the panel, so 3, 4 or 5 all clear.
#
# An earlier pass here concluded the PANEL was the limit and quoted <=O16 with a
# <=3 mm nut. That was wrong: it assumed the nut bearing on the raw ramp, where
# it contacts at the DEEPEST point of its footprint. With a spotface the panel
# is not in play at all.
#
# The real ceiling is the GASKET GROOVE:
#     window = groove floor (DEPTH-GD) 19.69  -  bezel back (FACE_T) 2.50 = 17.19
# A O20 spotface would reach z 22.5 and cut straight through the groove.
#   -> about O15 fits today, any nut thickness
#   -> O20 needs DEPTH 22 -> 27, or the O-ring groove moved to the cover
ANT_MOUNT = False
SMA_D, ANT_NUT = 15.75, 20.0        # MEASURED: bore, and the nut clearance dia
ANT_X, ANT_Y = -140.0, 62.0         # SHELL coords; converted for the cover
ANT_PAD_R, ANT_PAD_H = 14.0, 1.5    # raised sealing pad on the OUTER face
# The pad is there because a printed face leaks through its layer lines - the
# parameters doc calls for a raised flat pad at any bulkhead. 6.0 + 1.5 = 7.5
# of web at the bore, still inside the 1..8 grip.

# -- visor pivots ----------------------------------------------------------
# Symmetric at +/-148, so the hood covers the full 296 screen. This was only
# possible once the antenna moved to the cover - while it was on the top wall
# the -x pivot had to pull in to 125 to free 22.5 mm for the knockout, which
# cost 23 mm of unshaded screen on the viewer's right.
# Detent crown. The 45 deg roll turns a TOOTH_H*1.5 square into a diamond
# TOOTH_H*1.5*sqrt2 wide TANGENTIALLY, and that has to fit inside the pitch arc
# at the INNER radius or adjacent teeth merge and the crown becomes a plain
# ring. rev A/B had 20 teeth at r4.5-8.2: a 2.55 tooth in a 1.41 pitch, so 97%
# of the crown was solid and there was no detent at any angle - the joint was a
# friction pivot, which is exactly what the visor's own notes say must not
# happen. The asserts below now make that impossible to reintroduce.
N_TEETH, TOOTH_H, R_T0, R_T1 = 16, 0.97, 8.0, 13.0
TOOTH_W  = TOOTH_H * 1.5 * math.sqrt(2)          # tangential width after the roll
# How far the crown stands proud of the face it is built on. The box is centred
# TOOTH_H*0.5 off the face, and the 45 deg roll gives it an x half-extent of
# TOOTH_H*1.5*sqrt2/2 - so 1.5607*TOOTH_H, NOT the 1.25 you get if you forget
# the roll. The mating parts set their mesh gap from this.
TOOTH_PROUD = TOOTH_H * (0.5 + 1.5*math.sqrt(2)/2)
_pitch0  = 2*math.pi*R_T0/N_TEETH                # pitch arc at the inner radius
VALLEY   = _pitch0 - TOOTH_W
assert VALLEY >= 0.8, (f"teeth merge into a ring: {TOOTH_W:.2f} wide in a "
                       f"{_pitch0:.2f} pitch at r={R_T0} leaves {VALLEY:.2f}")

PIV_X = [-148.0, 148.0]
UPS_T, R_EAR = 9.0, R_T1 + 1.5
# The axis has to stand at least the EAR RADIUS clear of the wall, or the
# bottom of every ear - the housing's and the visor's alike - is buried in the
# top wall. rev B had it at +4.5 against a 9.5 ear and got away with it only
# because the visor carried its own axis height (94) and never agreed with the
# shell. Now both read this number, so it has to be right.
PIV_Y, PIV_Z = OUT_H/2 + R_EAR + 1.5, 9.0
assert PIV_Y - OUT_H/2 > R_EAR, "pivot ears would sink into the top wall"
PIV_BOLT = 4.3                      # M5 thread-forming pilot

# VESA deleted - the unit hinges off a bracket on its BOTTOM edge, the same
# detent principle as the visor: it tilts back when standing, forward when sat.
BP_X = [-120.0, 120.0]
BP_T, BP_R = 9.0, R_T1 + 1.5
# Same rule, plus 1.5 because the bracket's ear is deliberately a touch proud
# of the shell's so the joint does not show a step.
BP_Y, BP_Z = -(OUT_H/2 + BP_R + 3.0), 9.0
assert abs(BP_Y) - OUT_H/2 > BP_R + 1.5, "bracket ears would sink into the bottom wall"
BP_BOLT = 4.3

# -- cover-frame conversion ------------------------------------------------
# assembly.py places the cover as Rot(180,0,0) then z += DEPTH+COVER_T, so the
# cover MIRRORS IN Y: cover +y is shell -y. rev B specified the GPS cradle at
# cover y +63.5..72.5 with a comment saying it sits under the TOP wall - it
# actually landed on the BOTTOM one. Everything below is written in SHELL
# coordinates and converted here, so that cannot happen again.
def cy(shell_y):
    return -shell_y

M25_PILOT, STANDOFF_H, STANDOFF_D = 2.2, 1.5, 6.0   # 1.5 + 1.6 board = 3.1
# Cover packaging, all in SHELL coordinates. The bumps protrude OUTWARD, so
# they only have to clear each other, the bolt ring and the heat aperture.
PI_BUMP_L, PI_BUMP_W, PI_BUMP_H = 108.0, 78.0, 18.0
PI_BUMP_CX, PI_BUMP_CY = -75.0, 0.0
DRV_CX, DRV_CY = 20.0, 0.0
DRV_BUMP_L, DRV_BUMP_W, DRV_BUMP_H = 65.0, 125.0, 18.0
AP, AP_CX, AP_PITCH = 84.0, 103.0, 49.0     # plate 114 sq, tapped M3
GL_X, GL_Y = -120.0, -56.0                  # cable gland, low and outboard
GL_BOSS_R, GL_PROUD, GL_TAP_D = 16.0, 10.0, 18.5
VENT_X, VENT_Y = -55.0, -64.0
# All of these lie in the 4.5 mm behind the display panel (1.5 standoff +
# 1.6 board = 3.1), and all must stay INBOARD of the cover's sealing face.
SENSORS = [                      # (name, shell x, shell y, pitch x, pitch y)
    # The encoder and all four buttons land on this one chip, so it belongs
    # at the control end, not across the box.
    ("MCP23017", -100.0, -35.0, 38.10, 12.70),
    ("MCP9808",    60.0, -35.0, 20.32, 12.70),
    ("ADXL345",    95.0, -35.0, 20.32, 12.70),
    ("ICM20948",  -60.0,  55.0, 20.32, 12.70),
]
# Anchor x's are picked to clear what shares those bands: the bottom row must
# miss the gland boss at x -150 and the Gore vent at -60, the top row must miss
# the GPS cradle at x 128..152.
TIE_TOP = [ -40.0,   0.0,  60.0, 100.0]
TIE_BOT = [-110.0, -45.0,  85.0, 145.0]
TIE_Y, TIE_L, TIE_W, TIE_H, TIE_SLOT = 70.0, 13.0, 7.0, 3.5, 2.2
# GPS sits under the TOP WALL with its ceramic patch facing UP through the ASA,
# which is RF-transparent. It goes in the OPPOSITE top corner from the antenna:
# a transmit whip beside a GPS receiver would desense it badly.
GPS_X, GPS_W, GPS_T = 140.0, 19.0, 8.6
GPS_Y0, GPS_Y1, GPS_Z = 61.0, 70.0, 12.0
DSP_POST_D, DSP_POST_H = 8.0, 4.5


def rrect_pts(hw, hh, r, target):
    sx, sy, arc = 2*(hw-r), 2*(hh-r), math.pi*r/2
    per = 2*sx + 2*sy + 4*arc
    n = max(4, round(per/target)); step = per/n
    pts = []
    for i in range(n):
        s = i*step
        for seg, ln in (("b", sx), ("br", arc), ("r", sy), ("tr", arc),
                        ("t", sx), ("tl", arc), ("l", sy), ("bl", arc)):
            if s <= ln:
                if seg == "b":  pts.append((-(hw-r)+s, -hh)); break
                if seg == "r":  pts.append((hw, -(hh-r)+s)); break
                if seg == "t":  pts.append(((hw-r)-s, hh)); break
                if seg == "l":  pts.append((-hw, (hh-r)-s)); break
                a = s/arc*(math.pi/2)
                ax, ay, a0 = {"br": (hw-r, -(hh-r), -math.pi/2), "tr": (hw-r, hh-r, 0.0),
                              "tl": (-(hw-r), hh-r, math.pi/2),
                              "bl": (-(hw-r), -(hh-r), math.pi)}[seg]
                pts.append((ax + r*math.cos(a0+a), ay + r*math.sin(a0+a))); break
            s -= ln
    return pts

# 12 fasteners, not 24. The Gore vent equalises pressure, so the gasket only
# resists water - the usual driver for a high bolt count is absent.
BOLTS = rrect_pts(OUT_W/2 - BOLT_INSET, OUT_H/2 - BOLT_INSET,
                  R_OUT - BOLT_INSET, 60.0)

# -- control footprint checks ----------------------------------------------
# Against the DOMES and the KNOB, not the bores - see ROW_H above.
_ap_bot = APER_Y - APER_H/2
for _x in BTN_X:
    assert ROW_CY + BTN_DOME/2 <= _ap_bot, (
        f"button dome at x={_x} overlaps the display aperture by "
        f"{ROW_CY + BTN_DOME/2 - _ap_bot:.2f} mm")
    assert ROW_CY - BTN_DOME/2 >= -OUT_H/2, "button dome runs off the bottom edge"
    # the nut sits 2.5..11.5 behind the face; it must miss the display module
    assert ROW_CY + BTN_NUT_R <= APER_Y - MOD_H/2 - 1.0, (
        f"button nut at x={_x} fouls the display module by "
        f"{ROW_CY + BTN_NUT_R - (APER_Y - MOD_H/2):.2f} mm")
assert ROW_CY + KNOB_OD/2 <= _ap_bot, "encoder knob overlaps the display aperture"
_feet = [(x, BTN_DOME) for x in BTN_X] + [(ENC_X, KNOB_OD)]
for _i in range(len(_feet)):
    for _j in range(_i+1, len(_feet)):
        _a, _b = _feet[_i], _feet[_j]
        _gap = abs(_a[0]-_b[0]) - (_a[1]+_b[1])/2
        assert _gap > 0, f"controls at x={_a[0]} and {_b[0]} overlap by {-_gap:.1f} mm"

def clash(a, b):                  # OCC returns an EMPTY shape here, not None
    r = a & b
    return 0.0 if r is None else r.volume


# ============================================================ FRONT SHELL
f = extrude(Plane.XY * RectangleRounded(OUT_W, OUT_H, R_OUT), amount=DEPTH)
# tapered interior: WALL at the face growing to the full rim at the rear brim.
# The taper prints without a ledge to bridge.
f -= loft([
    Plane.XY.offset(FACE_T) * RectangleRounded(OUT_W - 2*WALL, OUT_H - 2*WALL, R_OUT - WALL),
    Plane.XY.offset(DEPTH + 1) * RectangleRounded(INT_W, INT_H, 8.0)])

# display aperture. The bond is ONE BEAD of silicone on the display's blind
# border, so the land behind this face is left FLAT - nothing built up on it.
# rev B had a dam ring, a 5 mm channel, an outer rim and six standoff pips: a
# labyrinth for a bead that does not need one, and it cost bezel. That band was
# 7.0 wide and landed exactly on the module's edge, which pinned the side bezel
# at 22.5. At BOND_BAND 5.0 the 2 mm per side comes back as aperture, and what
# shows there is the module's own black border, not housing.
f -= extrude(Plane.XY * Pos(APER_X, APER_Y) * RectangleRounded(APER_W, APER_H, 4.0),
             amount=3*FACE_T)

# -- control row: four buttons + encoder, with vertical lead-ins -----------
for x in BTN_X:
    f -= Pos(x, ROW_CY) * Cylinder(BTN_D/2, 3*FACE_T)
    # z=0 is the OUTER face and material runs +z, so cutting INTO the face is
    # a MIN-aligned solid at z=0.
    f -= Pos(x, (EMB_Y0 + EMB_Y1)/2, 0) * Box(
        EMB_W, EMB_Y1 - EMB_Y0, EMB_D, align=(Align.CENTER, Align.CENTER, Align.MIN))
    f -= Pos(x, EMB_Y1, 0) * Cylinder(
        EMB_W, EMB_D, align=(Align.CENTER, Align.CENTER, Align.MIN))
f -= Pos(ENC_X, ROW_CY) * Cylinder(ENC_D/2, 3*FACE_T)

# rear brim: blind M4 pilots. The cover's screws come UP into these.
for bx, by in BOLTS:
    f -= Pos(bx, by, DEPTH - PILOT_L) * Cylinder(
        M3_PILOT/2, PILOT_L + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
# No gasket groove: the seal is a flat gasket squeezed on this face.
GROOVE = None

# visor pivot upstands. Undersides chamfered 45 deg so they print as part of
# the top wall rather than as an unsupported cantilever.
def teeth(face_x, outward):
    out = None
    for i in range(N_TEETH):
        t = (Rot(360.0*i/N_TEETH, 0, 0)
             * Pos(face_x + outward*TOOTH_H*0.5, R_T0, 0)
             * Rot(0, 45, 0)
             * Box(TOOTH_H*1.5, R_T1 - R_T0, TOOTH_H*1.5,
                   align=(Align.CENTER, Align.MIN, Align.CENTER)))
        out = t if out is None else out + t
    return out

_crown = teeth(0.0, 1)
assert len(_crown.solids()) == N_TEETH, (
    f"crown made {len(_crown.solids())} solid(s), not {N_TEETH} - the teeth "
    f"have merged into a ring and there is no detent")

for px, outward in ((PIV_X[0] - UPS_T/2, +1), (PIV_X[1] + UPS_T/2, -1)):
    ups = Pos(px, 0, 0) * Rot(0, 90, 0) * Cylinder(R_EAR, UPS_T,
              align=(Align.CENTER, Align.CENTER, Align.CENTER))
    ups = Pos(0, PIV_Y, PIV_Z) * ups
    ups += Pos(px, (PIV_Y + OUT_H/2)/2 - 6, PIV_Z) * Box(
        UPS_T, PIV_Y - OUT_H/2 + 12, 2*R_EAR,
        align=(Align.CENTER, Align.CENTER, Align.CENTER))
    f += ups
    f += Pos(0, PIV_Y, PIV_Z) * teeth(px + outward*UPS_T/2, outward)
    f -= Pos(px, PIV_Y, PIV_Z) * Rot(0, 90, 0) * Cylinder(PIV_BOLT/2, 26)

# (antenna is on the rear cover - see the note at SMA_D)

# -- bottom pivot upstands, for the tilt bracket ---------------------------
for px, outward in ((BP_X[0] - BP_T/2, +1), (BP_X[1] + BP_T/2, -1)):
    ups = Pos(0, BP_Y, BP_Z) * Pos(px, 0, 0) * Rot(0, 90, 0) * Cylinder(
              BP_R, BP_T, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    # mirror of the top blend: spans from the axis up to OUT_H/2 - 12, inside
    # the wall. rev B wrote the height as OUT_H/2 + BP_Y + 12, which is the
    # NEGATIVE of the span - it stayed positive only while the offset was small.
    ups += Pos(px, (BP_Y - OUT_H/2)/2 + 6, BP_Z) * Box(
              BP_T, abs(BP_Y) - OUT_H/2 + 12, 2*BP_R, align=(Align.CENTER,)*3)
    f += ups
    f += Pos(0, BP_Y, BP_Z) * teeth(px + outward*BP_T/2, outward)
    f -= Pos(px, BP_Y, BP_Z) * Rot(0, 90, 0) * Cylinder(BP_BOLT/2, 26)

# -- front-face plane guard ------------------------------------------------
# z=0 IS THE BED. The pivot ears are r9.5 cylinders on a z=9 axis, so they
# cross the front plane by 0.5, and their blend blocks come with them: six pads
# the whole A-surface would balance on, floating 0.5 clear of the glass.
# Guaranteed ASA warp.
#
# Shaving the radius is the wrong lever - it eats the ear's rim over the R_T1
# 8.2 detent teeth, and it fixes one feature while the next reintroduces the
# bug (the antenna bore and the GPS cradle both did this before). So the plane
# is enforced once, globally, on the finished shell. What is left where the
# ears met it is a ~6 mm chord FLUSH with the face - first-layer area, not a bump.
f -= Pos(0, 0, -50.0) * Box(4*OUT_W, 4*OUT_H, 100.0, align=(Align.CENTER,)*3)
_zmin = f.bounding_box().min.Z
assert abs(_zmin) < 1e-6, f"front face is not flat: material at z={_zmin:.3f}"
assert len(f.solids()) == 1, f"shell is {len(f.solids())} solids, not 1"

# -- rear mating-plane guard ----------------------------------------------
# z=DEPTH is where the cover lands. The pivot ears are r14.5 on a z=9 axis, so
# they reach z=23.5 - and their BLEND BLOCKS run inboard to OUT_H/2 - 12, well
# inside the cover's footprint. That put 619 mm3 of shell in the cover's space.
# The ears themselves sit at |y| > OUT_H/2, outboard of the cover, and are left
# alone; only what intrudes on the footprint is trimmed. Same idea as the front
# face guard: enforce the plane once, globally, instead of per feature.
_lid = extrude(Plane.XY.offset(DEPTH) * RectangleRounded(OUT_W, OUT_H, R_OUT), amount=200)
f -= _lid
assert clash(f, _lid) < 1e-6, "shell still stands proud of the cover mating plane"

# -- the whole point of rev C: one object, on one bed ----------------------
BED = 350.0
_bb = f.bounding_box()
assert _bb.size.X <= BED and _bb.size.Y <= BED, (
    f"shell is {_bb.size.X:.0f} x {_bb.size.Y:.0f}, will not fit a {BED:.0f} bed")

export_step(f, "cad/out/helm_shell_revC.stp")
print(f"SHELL  vol={f.volume/1000:6.0f} cm3 solids={len(f.solids())} "
      f"bbox={_bb.size.X:.0f}x{_bb.size.Y:.0f}x{_bb.size.Z:.0f}   brim bolts={len(BOLTS)}")
print(f"       ONE PIECE on a {BED:.0f} bed: {(BED-_bb.size.X)/2:.1f} mm/side spare in x, "
      f"{(BED-_bb.size.Y)/2:.1f} in y")
print(f"       controls: bore O{BTN_D}/dome O{BTN_DOME}, knob O{KNOB_OD} at y={ROW_CY:.1f}; "
      f"bezel round the O{CTRL_MAX} knob {_ap_bot-(ROW_CY+CTRL_MAX/2):.2f} above / "
      f"{(ROW_CY-CTRL_MAX/2)+OUT_H/2:.2f} below")
print(f"       brim @ RIM {RIM}: FLAT gasket {GASKET_W:.2f} wide, screws through it; "
      f"lands {LAND_OUT:.2f} / {LAND_IN:.2f}, bolt inset {BOLT_INSET:.2f}")
print(f"       bezel {(OUT_W-APER_W)/2:.1f} side / {OUT_H/2-(APER_Y+APER_H/2):.1f} top")

# ============================================================ REAR COVER
c = extrude(Plane.XY * RectangleRounded(OUT_W, OUT_H, R_OUT), amount=COVER_T)
for bx, by in BOLTS:
    c -= Pos(bx, cy(by)) * Cylinder(M3_CLEAR/2, 3*COVER_T)
c -= Pos(VENT_X, cy(VENT_Y)) * Cylinder(VENT_D/2, 3*COVER_T)
# Cable entry: a PERPENDICULAR tapped boss taking a 90 deg elbow gland. The
# elbow turns the cable parallel to the cover, so nothing projects straight
# back and the case depth is untouched away from this corner.
c += Pos(GL_X, cy(GL_Y), -GL_PROUD) * Cylinder(
        GL_BOSS_R, GL_PROUD + COVER_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
c -= Pos(GL_X, cy(GL_Y), -GL_PROUD - 1) * Cylinder(
        GL_TAP_D/2, GL_PROUD + COVER_T + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))

# -- Pi and driver bumps, both OUTWARD (-z on this part) -------------------
for _cx, _cyy, _l, _w, _h in ((PI_BUMP_CX, PI_BUMP_CY, PI_BUMP_L, PI_BUMP_W, PI_BUMP_H),
                              (DRV_CX, DRV_CY, DRV_BUMP_L, DRV_BUMP_W, DRV_BUMP_H)):
    c += Pos(_cx, cy(_cyy), -_h) * Box(_l, _w, _h,
                                       align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= Pos(_cx, cy(_cyy), -_h + WALL) * Box(
        _l - 2*WALL, _w - 2*WALL, _h, align=(Align.CENTER, Align.CENTER, Align.MIN))

# board lies with its 113.25 along Y; holes from the confirmed centres
DRV_HOLES = [(-55.25/2 + 3.75,  113.25/2 - 9.0),
             (-55.25/2 + 3.75, -113.25/2 + 4.0),
             ( 55.25/2 - 7.25,  113.25/2 - 9.0),
             ( 55.25/2 - 3.75, -113.25/2 + 4.0)]
for _hx, _hy in DRV_HOLES:
    _p = Pos(DRV_CX + _hx, cy(DRV_CY + _hy), -DRV_BUMP_H + WALL)
    c += _p * Cylinder(6.0/2 + 1.6, 5.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= _p * Cylinder(M25_PILOT/2 + 0.3, 5.5, align=(Align.CENTER, Align.CENTER, Align.MIN))

# -- tie-wrap anchors, inner face ------------------------------------------
for _xs, _sgn in ((TIE_TOP, 1), (TIE_BOT, -1)):
    for _tx in _xs:
        c += Pos(_tx, cy(_sgn*TIE_Y), COVER_T - 0.3) * Box(
            TIE_L, TIE_W, TIE_H + 0.3, align=(Align.CENTER, Align.CENTER, Align.MIN))
        c -= Pos(_tx, cy(_sgn*TIE_Y), COVER_T + TIE_H - TIE_SLOT/2 - 0.4) * Box(
            TIE_L + 2, TIE_SLOT, TIE_SLOT, align=(Align.CENTER,)*3)

# -- sensor standoffs, cover inner face ------------------------------------
for _n, sx_, sy_, py, px in SENSORS:
    for ix in (-1, 1):
        for iy in (-1, 1):
            hx, hy = sx_ + ix*py/2, sy_ + iy*px/2
            c += Pos(hx, cy(hy), COVER_T - 0.3) * Cylinder(
                STANDOFF_D/2, STANDOFF_H + 0.3, align=(Align.CENTER, Align.CENTER, Align.MIN))
            c -= Pos(hx, cy(hy), COVER_T + STANDOFF_H - 5.0) * Cylinder(
                M25_PILOT/2, 5.2, align=(Align.CENTER, Align.CENTER, Align.MIN))

# -- display bearing posts -------------------------------------------------
# The panel has M3 standoffs on its back. Using them takes slam load off the
# silicone bond entirely - the adhesive then only has to seal, not carry the
# display. The CENTRE standoff is skipped: the driver bay owns that spot.
_L, _R = APER_X - MOD_W/2, APER_X + MOD_W/2
_T, _B = APER_Y + MOD_H/2, APER_Y - MOD_H/2
DSP_POSTS = [(_L + 15.0, _T - 8.25), (_R - 12.0, _T - 8.25),
             (_L + 30.5, _B + 13.0), (_R - 26.5, _B + 13.0)]
# Centring the display raised it 22 mm, which pulls the LOWER standoffs into
# the heat-plate aperture's band. A post there would print as a loose island,
# so it is dropped - the same call rev B made for the centre standoff, which
# the driver bay owns. Dropped posts are named so this is never silent.
_DROPPED = [(x, y) for x, y in DSP_POSTS
            if abs(x - AP_CX) < AP/2 + DSP_POST_D/2 and abs(y) < AP/2 + DSP_POST_D/2]
DSP_POSTS = [p for p in DSP_POSTS if p not in _DROPPED]
if _DROPPED:
    print("       display posts dropped (inside the heat aperture): "
          + ", ".join(f"({x:.1f},{y:.1f})" for x, y in _DROPPED)
          + f"  -> {len(DSP_POSTS)} posts carry the panel")
for _px, _py in DSP_POSTS:
    c += Pos(_px, cy(_py), COVER_T - 0.3) * Cylinder(
        DSP_POST_D/2, DSP_POST_H + 0.3, align=(Align.CENTER, Align.CENTER, Align.MIN))

# -- GPS cradle, patch facing the sky --------------------------------------
GPS_Z0, GPS_Z1 = 4.0, 23.0
GPS_PZ0, GPS_PZ1 = 5.5, 21.5
_gy = cy((GPS_Y0 + GPS_Y1)/2)
c += Pos(GPS_X, _gy, (GPS_Z0 + GPS_Z1)/2) * Box(
        GPS_W + 5.0, GPS_Y1 - GPS_Y0, GPS_Z1 - GPS_Z0, align=(Align.CENTER,)*3)
c -= Pos(GPS_X, _gy + GPS_T/2 - 0.05, (GPS_PZ0 + GPS_PZ1)/2) * Box(
        GPS_W, GPS_T, GPS_PZ1 - GPS_PZ0, align=(Align.CENTER,)*3)
c -= Pos(GPS_X, _gy - 3.0, (GPS_PZ0 + GPS_PZ1)/2) * Box(
        GPS_W - 7.0, GPS_Y1 - GPS_Y0, GPS_PZ1 - GPS_PZ0, align=(Align.CENTER,)*3)

# -- antenna bulkhead, rear cover ------------------------------------------
if ANT_MOUNT:
    # No tilt and no boss thickness: the plate's own 6.0 mm is already inside the
    # bulkhead's 1..8 grip, so the bore goes straight through and BOTH nut faces
    # are flat and parallel for free. The only added feature is a raised sealing
    # pad on the OUTER face, because a printed face leaks through its layer lines.
    _ax, _ay = ANT_X, cy(ANT_Y)
    c += Pos(_ax, _ay, -ANT_PAD_H) * Cylinder(
            ANT_PAD_R, ANT_PAD_H + COVER_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    ANT_BORE = Pos(_ax, _ay, -ANT_PAD_H - 1) * Cylinder(
            SMA_D/2, ANT_PAD_H + COVER_T + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= ANT_BORE

    # O20 of clear flat face is needed on BOTH sides. Check it against everything
    # that shares the plate, in shell coordinates.
    _nut_r = ANT_NUT/2
    _seal_in = OUT_H/2 - G_INSET - GW/2          # innermost edge of the gasket path
    assert ANT_Y + ANT_PAD_R < _seal_in, (
        f"antenna pad reaches y={ANT_Y+ANT_PAD_R:.1f}, into the gasket path at "
        f"{_seal_in:.1f} - the cover's sealing face must stay unbroken")
    for _bx, _by in BOLTS:
        _d = ((_bx-ANT_X)**2 + (_by-ANT_Y)**2)**0.5
        assert _d > ANT_PAD_R + M3_CLEAR/2, f"antenna pad hits the brim bolt at ({_bx:.0f},{_by:.0f})"
    for _tx in TIE_TOP:
        _d = ((_tx-ANT_X)**2 + (TIE_Y-ANT_Y)**2)**0.5
        assert _d > _nut_r + TIE_L/2, f"antenna nut hits the tie-wrap anchor at x={_tx:.0f}"
    assert abs(ANT_X - GPS_X) > _nut_r + GPS_W/2, "antenna nut hits the GPS cradle"
    # the inner nut sits in the gap behind the display panel
    _gap = DEPTH - (FACE_T + 15.0)
    assert _gap >= 4.0, f"only {_gap:.1f} mm behind the panel for the inner nut"

# -- heatsink aperture -----------------------------------------------------
# No internal boss: the shell interior is 21.5 and the display takes 17.5, so
# anything protruding inward here fouls the panel. The 6 mm ALLOY PLATE is
# tapped instead - aluminium threads far better than ASA.
c -= Pos(AP_CX, 0) * Box(AP, AP, 3*COVER_T, align=(Align.CENTER,)*3)
for hx, hy in [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]:
    px, py = AP_CX + hx*AP_PITCH, hy*AP_PITCH
    c -= Pos(px, py) * Cylinder(M3_CLEAR/2, 3*COVER_T)
    c -= Pos(px, py, COVER_T - 1.9) * Cone(
        M3_CLEAR/2, M3_CLEAR/2 + 1.9, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

# -- the cover's sealing face must be unbroken -----------------------------
# The gasket path moved inboard when OUT_H came down, and it stranded the
# sensors and the tie-wrap anchors straddling it. Checked now, not assumed.
SEAL_Y = OUT_H/2 - BRIM_CAVITY
SEAL_X = OUT_W/2 - BRIM_CAVITY
def _seal_ok(x, y, hx, hy=None, what=""):
    hy = hx if hy is None else hy
    assert abs(x) + hx < SEAL_X and abs(y) + hy < SEAL_Y, (
        f"{what} at ({x:.0f},{y:.0f}) +/-({hx:.1f},{hy:.1f}) crosses the cover's "
        f"sealing face (limits |x|<{SEAL_X:.1f}, |y|<{SEAL_Y:.1f})")
for _n, _sx, _sy, _py, _px in SENSORS:
    _seal_ok(_sx, _sy, _py/2 + STANDOFF_D/2, _px/2 + STANDOFF_D/2, f"sensor {_n}")
for _xs, _sgn in ((TIE_TOP, 1), (TIE_BOT, -1)):
    for _tx in _xs:
        _seal_ok(_tx, _sgn*TIE_Y, TIE_L/2 + 1, TIE_W/2 + 1, "tie-wrap anchor")
for _px_, _py_ in DSP_POSTS:
    _seal_ok(_px_, _py_, DSP_POST_D/2, None, "display post")
if ANT_MOUNT:
    _seal_ok(ANT_X, ANT_Y, ANT_PAD_R, None, "antenna pad")
_seal_ok(GL_X, GL_Y, GL_BOSS_R, None, "cable gland boss")
_seal_ok(VENT_X, VENT_Y, VENT_D/2, None, "Gore vent")
_seal_ok(GPS_X, (GPS_Y0+GPS_Y1)/2, (GPS_W+5)/2, (GPS_Y1-GPS_Y0)/2, "GPS cradle")
_seal_ok(AP_CX, 0.0, AP_PITCH + M3_CLEAR/2, None, "heat-plate bolt ring")
_cb0 = c.bounding_box()
assert _cb0.size.X <= OUT_W + 1e-6 and _cb0.size.Y <= OUT_H + 1e-6, (
    f"cover is {_cb0.size.X:.1f} x {_cb0.size.Y:.1f}, overhangs the {OUT_W:.0f} x "
    f"{OUT_H:.0f} outline")

if len(c.solids()) != 1:
    _iso = sorted(c.solids(), key=lambda t: t.volume)[:-1]
    raise AssertionError("cover has floating features: " + "; ".join(
        "vol %.0f at x %.0f..%.0f y %.0f..%.0f z %.0f..%.0f" % (
            t.volume, t.bounding_box().min.X, t.bounding_box().max.X,
            t.bounding_box().min.Y, t.bounding_box().max.Y,
            t.bounding_box().min.Z, t.bounding_box().max.Z) for t in _iso))
export_step(c, "cad/out/helm_cover_revC.stp")
_cb = c.bounding_box()
print(f"COVER  vol={c.volume/1000:6.0f} cm3 solids={len(c.solids())} "
      f"bbox={_cb.size.X:.0f}x{_cb.size.Y:.0f}x{_cb.size.Z:.0f}")

json.dump({"REV":"C","OUT_W":OUT_W,"OUT_H":OUT_H,"DEPTH":DEPTH,"COVER_T":COVER_T,
           "RIM":RIM,"BOLT_INSET":BOLT_INSET,"GASKET_W":GASKET_W,
           "LAND_OUT":LAND_OUT,"LAND_BG":LAND_BG,"LAND_IN":LAND_IN,
           "APER_W":APER_W,"APER_H":APER_H,"APER_X":APER_X,"APER_Y":APER_Y,
           "BTN_X":BTN_X,"ENC_X":ENC_X,"ROW_CY":ROW_CY,"BTN_D":BTN_D,"ENC_D":ENC_D,
           "ANT_X":ANT_X,"ANT_Y":ANT_Y,"SMA_D":SMA_D,"GPS_X":GPS_X,"PI_BUMP_H":PI_BUMP_H,
           "PIV_X":PIV_X,"PIV_Y":PIV_Y,"PIV_Z":PIV_Z,"BP_X":BP_X,"BP_Y":BP_Y,"BP_Z":BP_Z,
           # mating dimensions - the visor and the bracket read these rather
           # than keeping their own copies, which is how rev B ended up with
           # visor teeth at r5.0-9.5 against shell teeth at r4.5-8.2.
           "N_TEETH":N_TEETH,"TOOTH_H":TOOTH_H,"R_T0":R_T0,"R_T1":R_T1,
           "TOOTH_PROUD":TOOTH_PROUD,"TOOTH_W":TOOTH_W,"VALLEY":VALLEY,
           "R_EAR":R_EAR,"UPS_T":UPS_T,"PIV_BOLT":PIV_BOLT,
           "BP_T":BP_T,"BP_R":BP_R,"BP_BOLT":BP_BOLT,
           "DISP_CX":DISP_CX,"DISP_CY":DISP_CY},
          open("cad/out/housing.json","w"), indent=1)
