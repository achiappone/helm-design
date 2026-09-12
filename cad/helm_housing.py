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
# DIVIDER is not a guess: solving "bezel above the knob == bezel below it"
# gives DIVIDER = RIM - 6 exactly, for any ROW_H. ROW_H then just buys bezel,
# 0.5 mm per side per mm. It is DERIVED below, not typed - it was typed as 1.5
# against RIM 7.5, and any change to RIM would have silently unbalanced the
# one surface on this part that anybody actually looks at.
ROW_H = 18.0
# RIM is the FLOOR from the brim budget below, which fails the build if it is
# ever too small to hold all five bands. 7.5 -> 11.0 when the screws moved
# OUTBOARD of the gasket: a continuous foam band cannot share the brim face
# with the fasteners the way a punched flat gasket did.
RIM = 11.0
DIVIDER = RIM - 6.0
BTN_DOME, KNOB_OD, BTN_NUT_R = 17.5, 20.5, 8.0
CTRL_MAX = max(BTN_DOME, KNOB_OD)   # whatever is biggest governs the bezel
INT_W = MOD_W + 2*CLR
INT_H = (MOD_H + 2*CLR) + DIVIDER + ROW_H
# The module has SQUARE corners and its top two sit CLR from the cavity in BOTH
# x and y, so a rounded cavity corner is a block of material exactly where the
# panel wants to be - at R8 it stood 3.1 mm into each one. Requiring the module
# corner to fall inside the rounded rect gives r <= CLR*(2+sqrt2) = 3.41, so
# the corner has to be very nearly square. INT_R is the radius the cavity is
# actually built with; the assert is what stops it drifting back up.
INT_R_MAX = CLR * (2 + math.sqrt(2))
INT_R = 2.0                         # squared, with just enough to not be a knife edge
assert INT_R <= INT_R_MAX, (
    f"cavity corner R{INT_R} against {CLR} mm clearance: the display's square "
    f"corners foul it. Max is R{INT_R_MAX:.2f}.")
OUT_W, OUT_H = INT_W + 2*RIM, INT_H + 2*RIM
# Viewer's right is model -X: the front face normal is -Z, so the camera looks
# along +Z and cross(forward, up) = (-1,0,0). The encoder therefore sits at
# NEGATIVE x to fall under the viewer's right hand.
DISP_CX = 0.0
DISP_CY =  INT_H/2 - (MOD_H + 2*CLR)/2               # +22.0, display sits high
ROW_CY  = -INT_H/2 + ROW_H/2                         # -69.5, control row below
DEPTH, FACE_T, WALL, COVER_T = 22.0, 2.5, 3.5, 6.0
MOD_D = 15.0                        # MEASURED panel depth, face to back
R_OUT = 14.0

# -- control row -----------------------------------------------------------
# Four soft keys spread under the screen, encoder at the viewer's-right end.
# 70 mm pitch, not rev B's 24: across 313 mm there is no reason to crowd them,
# and each key now sits under the soft key it drives.
BTN_D, ENC_D, BTN_PITCH = 11.8, 9.7, 70.0    # BTN_D MEASURED, was 12.0 assumed
BTN_X = [120.0 - i*BTN_PITCH for i in range(4)]      # 120, 50, -20, -90
ENC_X = -134.5                                       # 44.5 clear of the last key

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
# The brim carries a 3 mm CLOSED-CELL RUBBER FOAM gasket as a CONTINUOUS BAND,
# with the screws OUTBOARD of it. Nothing is punched through the seal.
#
# rev C ran the screws THROUGH a flat gasket, and that is exactly what let the
# brim be 7.5: the fasteners came inside the seal, so the band could span the
# whole face. It is the cheaper brim and the wrong one for foam. Soft foam
# tears from a punched hole, and the compression set around each one is
# whatever that screw's torque happened to be - so the squeeze goes uneven
# precisely where the band is already weakest. A continuous band has nothing
# to tear from and one uniform squeeze the whole way round.
#
# What that costs, radially outside-in across the brim face:
#     land 2.00 + M3 2.60 + web 1.20 + foam 4.00 + lip 0.80 = 10.60
# RIM is that floor rounded up, and the assert below holds it there.
#
# The trade it makes: the screws now sit in the wet zone OUTBOARD of the seal.
# The shell's own pilots are blind and never reach the cavity, so the leak path
# is the COVER's through-holes - those need bonded sealing washers.
#
# The brim face is a flat plane at z=DEPTH and the shell prints face-down, so
# that face is a solid top surface - the best finish FDM gives, and the right
# one to squeeze foam against.
GASKET_T = 3.0                      # SHEET AS BOUGHT - what you cut the band from
# ...and what it becomes once the brim screws are pulled up. The assembled gap
# is the COMPRESSED thickness, not the sheet: that is the number the cover sits
# at and the number DSP_POST_H is derived from further down.
#
# 50% is the working assumption for closed-cell neoprene/EPDM, which is usually
# specified somewhere in the 25-50% deflection band. It is a knob, not a fact -
# set it from the foam's own datasheet, or measure a squeezed offcut. Getting
# it wrong does not just move the cover: the panel bearing posts are derived
# from it, so the error comes out at the display.
GASKET_SQUASH = 0.50
GASKET_C = GASKET_T * GASKET_SQUASH
# The wall is straight, so the brim face is exactly RIM wide - no taper fudge.
BRIM_CAVITY = RIM
# Each band does a different job and none of them is padding:
#   OUT  hoop for a thread-forming M3 - too little and the screw splits out to
#        the free edge, which is the failure you find while assembling
#   WEB  shell between bolt hole and foam, so the boss cannot bulge into the
#        band and lift it locally
#   GSK  the foam, kept wider than it is thick so it cannot roll out of the
#        joint instead of compressing
#   IN   lip inboard of the foam, to the cavity edge
_MIN_OUT, _MIN_WEB, _MIN_GSK, _MIN_IN = 2.00, 1.20, 4.00, 0.80
RIM_FLOOR = _MIN_OUT + M3_PILOT + _MIN_WEB + _MIN_GSK + _MIN_IN
assert BRIM_CAVITY >= RIM_FLOOR, (
    f"brim too narrow at RIM={RIM}: face {BRIM_CAVITY:.2f} vs floor "
    f"{RIM_FLOOR:.2f}, short by {RIM_FLOOR - BRIM_CAVITY:.2f} mm.")
# Spare goes to the foam. Of the five bands it is the only one that gets
# BETTER with more rather than merely adequate.
LAND_OUT, LAND_WEB, LAND_IN = _MIN_OUT, _MIN_WEB, _MIN_IN
BOLT_INSET = LAND_OUT + M3_PILOT/2
GASKET_OUT = LAND_OUT + M3_PILOT + LAND_WEB     # foam's OUTER edge from the edge
GASKET_W = BRIM_CAVITY - GASKET_OUT - LAND_IN
assert GASKET_W >= GASKET_T, (
    f"foam band {GASKET_W:.2f} wide against {GASKET_T} thick - it will roll "
    f"out of the joint under clamp instead of compressing")

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
# The ceiling used to be the GASKET GROOVE: a O20 spotface reached z 22.5 and cut
# straight through it, so the note here read "O20 needs DEPTH 22 -> 27, or the
# O-ring groove moved to the cover" and the mount was switched off to wait.
#
# THAT CONSTRAINT IS GONE. There is no groove - the seal is a flat foam band on
# the brim face, and the antenna moved to the rear COVER besides, where the bore
# goes straight through 6.0 mm of flat plate. Nothing is in its way any more.
#
# The block below had gone stale while it sat switched off: it still read G_INSET
# and GW, which the groove took with it when it went, so turning the flag on
# raised a NameError rather than building a mount. That is the failure mode of a
# feature behind a flag nobody sets - it rots quietly and the BOM keeps promising
# it. The whip is item 36 and the pigtail item 38; both were listed on the build
# page while the cover had no hole to take them.
ANT_MOUNT = True
SMA_D, ANT_NUT = 15.75, 20.0        # MEASURED: bore, and the nut clearance dia
# SHELL coords, converted for the cover. y was 62.0, which put the O15.75 bore
# 6.25 mm from the display bearing post at (-140, 68.25) - the bore ate 5.6 of
# that post's 8.0 diameter and the M3 screw hole through it, leaving one of the
# THREE posts that carry the panel as a crescent. The cover still passed its
# solids==1 check because the far side of the post stayed attached, so nothing
# complained. 52.0 clears it by 2.9 mm.
#
# It was free to move: the old constraint was to sit in the opposite top corner
# from the GPS patch so a transmit whip would not desense the receiver, and the
# GPS is now an external puck. Staying outboard at x=-140 is worth more than the
# 10 mm of height, so the move is in y.
ANT_X, ANT_Y = -140.0, 52.0
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
# CLEARANCE, with the thread in a 316 SS NYLOC on the outboard face - the same
# move the bottom pivot made, and for a sharper reason here. This joint is meant
# to be SET BY HAND: firm enough that the visor stays where you put it, loose
# enough to click over the detent under bare-hand pressure. That is a preload
# you dial in by feel, so the nut IS the adjustment - and a thread formed in ASA
# gives up a little grip every time you work it, so the setting drifts.
#
# NYLOC here, where the bottom pivot took a plain hex. Different jobs: down there
# the Bellevilles are the locking element and a nyloc's nylon would only relax
# under their sustained load. Up here there is no sustained spring load to fight,
# just a hand-set torque that vibration must not walk out - which is exactly what
# a nylon insert is for. All 316 through the joint; brass against 316 is a
# galvanic couple in salt water. Tef-Gel the threads - 316 galls on 316.
PIV_BOLT = 5.4
PIV_NUT_AF, PIV_NUT_DEEP = 8.2, 5.3     # M5 316 nyloc, 8.0 A/F x 5.0, + fit
PIV_NUT_CR = PIV_NUT_AF/2/math.cos(math.pi/6)
PIV_NUT_WALL = UPS_T - PIV_NUT_DEEP
assert PIV_NUT_WALL >= 3.0, (
    f"nyloc pocket leaves only {PIV_NUT_WALL:.1f} mm behind the visor detent "
    f"crown - the teeth would be standing on a floor, not on the upstand")

# VESA deleted - the unit hinges off a bracket on its BOTTOM edge, the same
# detent principle as the visor: it tilts back when standing, forward when sat.
BP_X = [-120.0, 120.0]
BP_T, BP_R = 9.0, R_T1 + 1.5
# Same rule, plus 1.5 because the bracket's ear is deliberately a touch proud
# of the shell's so the joint does not show a step.
BP_Y, BP_Z = -(OUT_H/2 + BP_R + 3.0), 9.0
assert abs(BP_Y) - OUT_H/2 > BP_R + 1.5, "bracket ears would sink into the bottom wall"

# CLEARANCE, not a pilot. rev C up to here threaded the M5 straight into the
# ASA ear. Two things kill that: the tilt is meant to be re-set by hand, and a
# formed thread in ASA gives up grip every time it is worked; and the detent's
# 45 deg flanks throw an axial SEPARATING force equal to the tangential one -
# 240 N per ear at 6g - which is what the clamp has to hold shut. A wave washer
# on a creeping plastic thread does not hold 240 N, so the crown climbs its own
# ramps and ratchets a click, losing preload it never gets back.
# The thread moves into a captive 316 nut pocketed in the OUTBOARD face, with
# 316 Bellevilles under the head. All-316 through the clamp: a brass insert
# against a 316 bolt is a ~0.25 V couple in salt water and the brass - the
# small part - dezincifies. Tef-Gel the threads: 316 on 316 galls, and a nut
# buried in a plastic pocket is a textbook crevice.
BP_BOLT = 5.4                        # M5 clearance both sides now
NUT_AF, NUT_DEEP = 8.2, 4.3          # M5 plain hex 8.0 A/F x 4.0, + fit
NUT_CR = NUT_AF/2/math.cos(math.pi/6)               # across corners / 2
# Plain hex, NOT a nyloc: a nyloc is 5.0 thick and would leave 3.7 mm under the
# tooth crown, and its nylon relaxes under sustained Belleville load anyway.
# The Bellevilles are the locking element - do not pay for it twice in material
# this ear does not have.
BP_NUT_WALL = BP_T - NUT_DEEP        # material left behind the crown
assert BP_NUT_WALL >= 3.0, (
    f"nut pocket leaves only {BP_NUT_WALL:.1f} mm behind the detent crown - "
    f"the teeth would be standing on a floor, not on the ear")
assert NUT_CR + 2.0 < BP_R, (
    f"nut pocket (across corners {2*NUT_CR:.1f}) breaks out of the r{BP_R} ear")

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
TC_PAD = 0.5                                # gap pad each end, takes up tolerance
TC_L = TC_W = AP - 2.0                      # 1 mm clearance into the aperture
# Thickness is DERIVED from the assembled z-stack: the panel's back sits at
# FACE_T + MOD_D, the alloy plate's inner face at DEPTH + GASKET_C + COVER_T
# (the plate bolts to the cover's OUTER face, so the aperture is a window onto
# it). Everything in that chain has moved at least once today - the foam alone
# shifted the cover 1.5 - so this is derived, never typed.
TC_GAP = (DEPTH + GASKET_C + COVER_T) - (FACE_T + MOD_D)
TC_T = TC_GAP - 2*TC_PAD
HS_PLATE = 114.0                            # the alloy plate the fins bolt to
# -- thermal conduction block ---------------------------------------------
# THE DISPLAY'S BACK IS METAL, and it is the largest heat source and the largest
# conductor in the box - roughly 400 cm2 of it. Until now it faced dead air
# across the heat aperture to the alloy plate, so every watt the panel made had
# to cross that gap by convection in a SEALED enclosure before it could reach
# the plate, the fins and the fan. That air gap, not the fan, was the bottleneck,
# and it is why the box needed internal circulation at all.
#
# An aluminium block bridges it: panel back -> gap pad -> block -> gap pad ->
# alloy plate -> external fins. Metal the whole way. Even plain silicone gap
# filler over this area is about 0.6 K/W - 6 K at 10 W - and a metal block is far
# better, silent, and has nothing in it to fail in salt air.
#
# Thickness is DERIVED from the assembled stack, not typed. It has to span from
# the panel's back to the plate's inner face exactly; the plate sits on the
# cover's OUTER face, so the aperture is a window onto it.
# Easycargo 100 x 40 x 20, two of them side by side on the plate's OUTER face,
# fins running along +x so the fan's air exits through the louvres at that end.
# They live here rather than in the shroud because THREE parts need to agree on
# where they are - the shroud that covers them, the exploded view that draws
# them, and the jig that positions them while the thermal adhesive cures. When
# only the exploded view knew, it was the only thing that could be right.
# HS_H STAYS 20. Halving the fin height was costed and rejected: it saves 10 mm
# of shroud depth and costs roughly half the convective area (three 100x25x10 is
# ~47% of the current fin surface, one 100x60x10 is ~37%), and thermal is the
# open risk on this build. There is no drop-in 100x40x10 anyway. The same 10 mm
# is available for free by fitting a slim fan - see FAN_T in heatsink_shroud.py,
# where the depth is derived - so the fins are the wrong place to cut.
HS_L, HS_W, HS_H = 100.0, 40.0, 20.0
HS_FIT = 0.4                                # per side, in the gluing jig
HS_HOLE_C = 48.0                            # shroud/jig fixings, tapped in the plate
# HS_CY is DERIVED from those fixings, not chosen. exploded.py drew the pair at
# y +/-30, which puts their outer edges at 50 - straight over the shroud's own
# mounting screws at +/-48. Nothing caught it because the heatsinks existed only
# as envelope boxes in the exploded view, and an envelope in a drawing clashes
# with nothing. The screws have to land on bare plate, so the heatsinks come
# inboard until they do.
HS_CLR_FIX = 3.3                            # washer + a little air, around an M3
HS_CY = HS_HOLE_C - HS_CLR_FIX - HS_W/2
HS_PLENUM = 2*HS_CY - HS_W
assert HS_PLENUM >= 6.0, (
    f"only {HS_PLENUM:.1f} mm between the heatsinks - they are being squeezed "
    f"together by the fixing pattern, and the fan needs somewhere to breathe")
assert HS_CY + HS_W/2 < HS_PLATE/2 and HS_L/2 < HS_PLATE/2, (
    f"heatsinks overhang the {HS_PLATE} plate")
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
# miss the gland boss at x -150 and the Gore vent at -60. The top row used to
# have to dodge the GPS cradle at x 128..152 as well; that is gone, and the
# anchors are left where they are rather than re-spaced for nothing.
TIE_TOP = [ -40.0,   0.0,  60.0, 100.0]
TIE_BOT = [-110.0, -45.0,  85.0, 145.0]
TIE_Y, TIE_L, TIE_W, TIE_H, TIE_SLOT = 70.0, 13.0, 7.0, 3.5, 2.2
# GPS IS EXTERNAL - a puck on the hardtop, its lead in through the gland.
#
# The internal cradle is deleted. It held the patch facing up under the top
# wall, which meant standing 17 mm proud of the cover's inner face, and there
# are 4.5 mm behind the display panel. It had driven 1047 mm3 straight through
# the panel since before rev C; nothing caught it because the clash checks all
# compared cover features to OTHER COVER FEATURES and to the seal, never to the
# display. The assembly check at the bottom of this file is what found it, and
# is why that check compares against the panel envelope rather than a list.
#
# Laying the patch flat in the 4.5 mm was the only way to keep it inside, and a
# patch lying flat against a near-vertical dash sees no sky. So it goes out.
DSP_POST_D = 8.0
# DERIVED, and it has to be. The post has to span exactly the gap between the
# cover's inner face and the back of the panel:
#     cover inner  = DEPTH + GASKET_C      (the foam holds it off the brim)
#     panel back   = FACE_T + MOD_D
# It was typed as 4.5, which was right only while the cover sat flat on the
# brim - DEPTH - FACE_T - MOD_D. Adding the 3 mm foam lifted the cover 1.5 and
# left the posts 1.5 short of the panel they are supposed to bear on, which is
# invisible in a render and obvious on a bench. Now it moves with the stack.
DSP_POST_H = DEPTH + GASKET_C - FACE_T - MOD_D
assert DSP_POST_H > 0, (
    f"cover inner face is {-DSP_POST_H:.2f} mm INSIDE the panel - the panel, "
    f"the foam and the case depth do not fit together")
# Screws INTO the panel's own M3 standoffs, not just posts bearing on them.
# They approach from behind, which is through the cover, so each one is a new
# penetration in the weather face - counterbored for a bonded sealing washer,
# the same call the brim screws now make. M3 x 14: 3.5 of cover under the
# counterbore + 4.5 of post + 5 into the standoff.
DSP_SCREW, DSP_CB_D, DSP_CB_DEEP = 3.4, 7.0, 2.5   # M3 clearance, washer seat
# -- display locating recess ----------------------------------------------
# The panel is glued to a flat land with a wet bead under it and, until now,
# nothing at all holding it in place: the cavity pinched it to +/-1 on three
# sides and the fourth was open 24 mm into the control row, so it could slide
# down as the silicone skinned. That matters more than it sounds, because the
# cover's posts have to land on the standoffs afterwards - the glued position
# IS the tolerance the screws inherit.
#
# The recess is a SEAT, not a pocket: a rail across the bottom the panel rests
# on, and pads down the sides. The top is deliberately left OPEN so the panel
# goes in the way anyone actually fits a glass part - bottom edge onto the
# rail, swing the top in. Tight on all four and you would have to slide it
# straight down through a bead of wet silicone.
MOD_FIT = 0.35                      # per side, once the pads have it
MOD_REC_H = 2.0                     # rail and pad height off the bond land
MOD_PAD_PROUD = CLR - MOD_FIT       # how far a pad stands off the cavity wall
MOD_RAIL_L, MOD_RAIL_X = 80.0, 70.0 # two segments, centre left open for flex
MOD_PAD_L, MOD_PAD_DY = 20.0, 40.0
assert MOD_PAD_PROUD > 0.4, (
    f"locating pads would stand only {MOD_PAD_PROUD:.2f} off the wall - "
    f"under two perimeters, so they print as nothing")
assert MOD_REC_H < MOD_D, (
    f"locating rail {MOD_REC_H} stands proud of a {MOD_D} deep panel - it "
    f"would hold the cover off instead of the panel")


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
# DIVIDER = RIM - 6 is what balances the bezel above and below the control row.
# It was a typed constant against one value of RIM; now it is derived, and this
# is the assert that says the derivation is still the right one.
_bz_up = _ap_bot - (ROW_CY + CTRL_MAX/2)
_bz_dn = (ROW_CY - CTRL_MAX/2) + OUT_H/2
assert abs(_bz_up - _bz_dn) < 1e-9, (
    f"bezel round the control row is unbalanced: {_bz_up:.2f} above vs "
    f"{_bz_dn:.2f} below - DIVIDER = RIM - 6 no longer solves it")
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
# STRAIGHT interior: the wall is RIM thick from the back of the bezel all the
# way to the brim. rev C lofted it from WALL at the face out to RIM at the
# brim, which bought interior width but tapered the bezel in section and left
# the brim face ~0.2 narrower than RIM - a fudge the land budget then had to
# carry. Vertical walls have no overhang to print, so the taper bought nothing
# the printer needed; dropping it makes the brim face exactly RIM.
f -= extrude(Plane.XY.offset(FACE_T) * RectangleRounded(INT_W, INT_H, INT_R),
             amount=DEPTH + 1 - FACE_T)

# display aperture. The bond is ONE BEAD of silicone on the display's blind
# border, so the land behind this face is left FLAT - nothing built up on it.
# rev B had a dam ring, a 5 mm channel, an outer rim and six standoff pips: a
# labyrinth for a bead that does not need one, and it cost bezel. That band was
# 7.0 wide and landed exactly on the module's edge, which pinned the side bezel
# at 22.5. At BOND_BAND 5.0 the 2 mm per side comes back as aperture, and what
# shows there is the module's own black border, not housing.
f -= extrude(Plane.XY * Pos(APER_X, APER_Y) * RectangleRounded(APER_W, APER_H, 4.0),
             amount=3*FACE_T)

# -- display locating seat, on the bond land ------------------------------
# Everything here grows +z off the land at FACE_T, i.e. AWAY from the bed. The
# front face is still untouched: nothing added here reaches z=0.
_ml, _mr = APER_X - MOD_W/2, APER_X + MOD_W/2
_mb, _mt = APER_Y - MOD_H/2, APER_Y + MOD_H/2
# bottom rail, two segments - the panel sits on this and it sets Y
for _rx in (-MOD_RAIL_X, MOD_RAIL_X):
    f += Pos(APER_X + _rx, _mb - MOD_FIT - 1.6/2, FACE_T) * Box(
        MOD_RAIL_L, 1.6, MOD_REC_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
# side pads, two per side - these take X from the cavity's +/-CLR down to FIT
for _sx in (-1, 1):
    for _dy in (-MOD_PAD_DY, MOD_PAD_DY):
        f += Pos(APER_X + _sx*(MOD_W/2 + MOD_FIT + MOD_PAD_PROUD/2),
                 APER_Y + _dy, FACE_T) * Box(
            MOD_PAD_PROUD, MOD_PAD_L, MOD_REC_H,
            align=(Align.CENTER, Align.CENTER, Align.MIN))

# -- control row: four buttons + encoder ----------------------------------
# No lead-in graphics. rev C cut a 1.6 x 13 slot 0.6 deep from each button up
# toward the screen edge; they are gone, and the bezel is plain. Nothing else
# on this face moved - the bores are where they were.
for x in BTN_X:
    f -= Pos(x, ROW_CY) * Cylinder(BTN_D/2, 3*FACE_T)
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
    # Nyloc pocket in the OUTBOARD face - the crown owns the inboard one. Same
    # sign trick as the bottom pivot: the teeth face is px + outward*UPS_T/2, so
    # the far face is px - that, and the pocket runs back along +outward.
    _v0 = f.volume
    f -= (Pos(px - outward*UPS_T/2, PIV_Y, PIV_Z) * Rot(0, 90*outward, 0)
          * extrude(RegularPolygon(PIV_NUT_CR, 6), PIV_NUT_DEEP))
    _want = (math.sqrt(3)/2*PIV_NUT_AF**2 - math.pi*(PIV_BOLT/2)**2) * PIV_NUT_DEEP
    assert abs((_v0 - f.volume) - _want) < 0.05*_want, (
        f"visor nyloc pocket removed {_v0 - f.volume:.0f} mm3, expected {_want:.0f} "
        f"- it is cutting outboard into air, not into the upstand")

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
    # Captive nut, sunk in the OUTBOARD face - the crown owns the inboard one.
    # The teeth face is px + outward*BP_T/2, so the far face is px - that, and
    # the pocket runs from it back INTO the ear, i.e. along +outward. Rotating
    # by 90*outward sends the prism's +z the same way, so one expression does
    # both ears without a sign table to get wrong.
    # Cut the wrong way it would extrude into open air OUTBOARD of the ear,
    # remove nothing, and leave a shell that looks perfect and has no pocket.
    # So measure: the hex less the bolt bore already through it, over NUT_DEEP.
    _v0 = f.volume
    f -= (Pos(px - outward*BP_T/2, BP_Y, BP_Z) * Rot(0, 90*outward, 0)
          * extrude(RegularPolygon(NUT_CR, 6), NUT_DEEP))
    _want = (math.sqrt(3)/2*NUT_AF**2 - math.pi*(BP_BOLT/2)**2) * NUT_DEEP
    assert abs((_v0 - f.volume) - _want) < 0.05*_want, (
        f"nut pocket removed {_v0 - f.volume:.0f} mm3, expected {_want:.0f} - "
        f"it is cutting outboard into air, not into the ear")

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

# -- the display has to physically go in -----------------------------------
# Not inferred from INT_R and CLR - the module is put where it lives and the
# shell is asked whether anything is in the way. This is the check that caught
# the rounded corners standing in the panel's top two corners; it catches the
# next feature that grows into the bay too, whatever that turns out to be.
_mod = Pos(APER_X, APER_Y, FACE_T) * Box(
    MOD_W, MOD_H, DEPTH - FACE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
_fouled = clash(f, _mod)
assert _fouled < 1e-6, (
    f"{_fouled:.0f} mm3 of shell stands inside the {MOD_W}x{MOD_H} display "
    f"envelope at ({APER_X:.0f},{APER_Y:.1f}) - the panel will not seat")

# ...and that the seat actually SEATS it. A rail that clears the panel at
# nominal has done nothing; what makes it an index is that the panel cannot
# move. Push it past the fit in each direction and the shell must push back.
# Without this, a rail modelled 1 mm too far out reads as a pass above and
# ships as a panel free to slide while the silicone skins.
_SLOP = MOD_FIT + 0.15
for _dx, _dy, _dir in ((_SLOP, 0, "right"), (-_SLOP, 0, "left"),
                       (0, -_SLOP, "down")):
    _off = Pos(APER_X + _dx, APER_Y + _dy, FACE_T) * Box(
        MOD_W, MOD_H, DEPTH - FACE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    assert clash(f, _off) > 1e-6, (
        f"panel slides {_SLOP:.2f} mm {_dir} and touches nothing - the "
        f"locating seat is not locating it")
# UP is deliberately unconstrained: the top is left open so the panel goes in
# bottom-edge-first and swings home. Asserting it here would be asserting the
# opposite of the assembly method.

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
print(f"       brim @ RIM {RIM}: {GASKET_T:.0f} mm FOAM band {GASKET_W:.2f} wide "
      f"(compressed {GASKET_C:.1f}), screws OUTBOARD of it")
print(f"       bands out {LAND_OUT:.2f} / M3 {M3_PILOT} / web {LAND_WEB:.2f} / "
      f"foam {GASKET_W:.2f} / lip {LAND_IN:.2f}; bolt inset {BOLT_INSET:.2f}, "
      f"foam outer edge {GASKET_OUT:.2f}")
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
    # through the boss AND the cover, so an M3 can reach the panel's standoff
    c -= Pos(_px, cy(_py)) * Cylinder(
        DSP_SCREW/2, COVER_T + DSP_POST_H + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # counterbore on the WEATHER face for the head and its bonded washer
    c -= Pos(_px, cy(_py)) * Cylinder(
        DSP_CB_D/2, DSP_CB_DEEP, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # lead-in at the boss tip: the screw is started blind, 4.5 mm from the
    # standoff it has to find, with the panel already glued down.
    c -= Pos(_px, cy(_py), COVER_T + DSP_POST_H - 1.0) * Cone(
        DSP_SCREW/2, DSP_SCREW/2 + 1.0, 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))


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
    # Innermost edge of the FOAM BAND: the band's outer edge is GASKET_OUT in from
    # the shell's edge and it is GASKET_W wide, so the sealing face ends here. The
    # pad has to stay inboard of it or it lifts the foam locally and the joint
    # leaks at exactly the fitting you added to keep water out.
    _seal_in = OUT_H/2 - GASKET_OUT - GASKET_W
    assert ANT_Y + ANT_PAD_R < _seal_in, (
        f"antenna pad reaches y={ANT_Y+ANT_PAD_R:.1f}, into the gasket path at "
        f"{_seal_in:.1f} - the cover's sealing face must stay unbroken")
    for _bx, _by in BOLTS:
        _d = ((_bx-ANT_X)**2 + (_by-ANT_Y)**2)**0.5
        assert _d > ANT_PAD_R + M3_CLEAR/2, f"antenna pad hits the brim bolt at ({_bx:.0f},{_by:.0f})"
    for _tx in TIE_TOP:
        _d = ((_tx-ANT_X)**2 + (TIE_Y-ANT_Y)**2)**0.5
        assert _d > _nut_r + TIE_L/2, f"antenna nut hits the tie-wrap anchor at x={_tx:.0f}"
    # The display bearing posts. This check did not exist, because the posts were
    # added to the cover AFTER the antenna block was written and switched off - so
    # the two features never met until the flag went back on. The bore is cut after
    # the posts are built, so a clash here does not error: it quietly mills a post
    # away and leaves the remainder attached to the plate, which passes solids==1.
    for _px, _py in DSP_POSTS:
        _d = ((_px-ANT_X)**2 + (_py-ANT_Y)**2)**0.5
        assert _d > SMA_D/2 + DSP_POST_D/2 + 1.5, (
            f"antenna bore is {_d:.1f} mm from the display post at ({_px:.0f},{_py:.0f}) "
            f"- needs {SMA_D/2 + DSP_POST_D/2 + 1.5:.1f}. It would cut the post away and "
            f"take the panel screw with it, and the cover would still look like one solid.")
    # the inner nut sits in the gap behind the display panel
    _gap = DEPTH - (FACE_T + MOD_D)
    assert _gap >= 4.0, f"only {_gap:.1f} mm behind the panel for the inner nut"

# -- heatsink aperture -----------------------------------------------------
# No internal boss: the shell interior is DEPTH-FACE_T and the panel takes
# MOD_D of it, so
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
           "LAND_OUT":LAND_OUT,"LAND_WEB":LAND_WEB,"LAND_IN":LAND_IN,
           "GASKET_T":GASKET_T,"GASKET_C":GASKET_C,"GASKET_SQUASH":GASKET_SQUASH,
           "N_BRIM_BOLTS":len(BOLTS),"BRIM_BOLT":M3_PILOT,
           "AP":AP,"AP_CX":AP_CX,"AP_PITCH":AP_PITCH,"HS_PLATE":HS_PLATE,
           "HS_L":HS_L,"HS_W":HS_W,"HS_H":HS_H,"HS_CY":HS_CY,
           "HS_FIT":HS_FIT,"HS_HOLE_C":HS_HOLE_C,"HS_PLENUM":HS_PLENUM,
           "TC_L":TC_L,"TC_W":TC_W,"TC_T":TC_T,"TC_GAP":TC_GAP,"TC_PAD":TC_PAD,"GASKET_OUT":GASKET_OUT,
           "APER_W":APER_W,"APER_H":APER_H,"APER_X":APER_X,"APER_Y":APER_Y,
           "BTN_X":BTN_X,"ENC_X":ENC_X,"ROW_CY":ROW_CY,"BTN_D":BTN_D,"ENC_D":ENC_D,
           "ANT_X":ANT_X,"ANT_Y":ANT_Y,"SMA_D":SMA_D,"PI_BUMP_H":PI_BUMP_H,
           "PIV_X":PIV_X,"PIV_Y":PIV_Y,"PIV_Z":PIV_Z,"BP_X":BP_X,"BP_Y":BP_Y,"BP_Z":BP_Z,
           # mating dimensions - the visor and the bracket read these rather
           # than keeping their own copies, which is how rev B ended up with
           # visor teeth at r5.0-9.5 against shell teeth at r4.5-8.2.
           "N_TEETH":N_TEETH,"TOOTH_H":TOOTH_H,"R_T0":R_T0,"R_T1":R_T1,
           "TOOTH_PROUD":TOOTH_PROUD,"TOOTH_W":TOOTH_W,"VALLEY":VALLEY,
           "R_EAR":R_EAR,"UPS_T":UPS_T,"PIV_BOLT":PIV_BOLT,
           "PIV_NUT_AF":PIV_NUT_AF,"PIV_NUT_DEEP":PIV_NUT_DEEP,
           "PIV_NUT_WALL":PIV_NUT_WALL,
           "BP_T":BP_T,"BP_R":BP_R,"BP_BOLT":BP_BOLT,
           "NUT_AF":NUT_AF,"NUT_DEEP":NUT_DEEP,"BP_NUT_WALL":BP_NUT_WALL,
           "DISP_CX":DISP_CX,"DISP_CY":DISP_CY},
          open("cad/out/housing.json","w"), indent=1)


# ==================================================== ASSEMBLY REALITY CHECK
# Not "do the solids look right" - can a person put this together, in order,
# with the parts touching what they are supposed to touch. Every number below
# is the assembled stack, measured from the front face at z=0.
_z_land   = FACE_T                        # panel sits on this
_z_panel  = FACE_T + MOD_D                # ...and its back is here
_z_brim   = DEPTH                         # foam sits on this
_z_cover  = DEPTH + GASKET_C              # cover inner face, foam compressed
_z_tip    = _z_cover - DSP_POST_H         # where a bearing post reaches to

# 1. the posts have to actually land on the panel - not short, not through it
assert abs(_z_tip - _z_panel) < 1e-9, (
    f"bearing posts reach z={_z_tip:.2f} but the panel's back is z={_z_panel:.2f}"
    f" - {'a ' + format(_z_tip - _z_panel, '.2f') + ' mm gap' if _z_tip > _z_panel else 'they press INTO it by ' + format(_z_panel - _z_tip, '.2f')}")

# 2. the cover, in its assembled place, must not foul the panel anywhere else
_cov_asm = Pos(0, 0, DEPTH + COVER_T + GASKET_C) * Rot(180, 0, 0) * c
_panel_solid = Pos(APER_X, APER_Y, FACE_T) * Box(
    MOD_W, MOD_H, MOD_D, align=(Align.CENTER, Align.CENTER, Align.MIN))
_hit_solid = _cov_asm & _panel_solid
_hit = 0.0 if _hit_solid is None else _hit_solid.volume
# The three bearing posts are SUPPOSED to touch it; a face-to-face touch is
# zero volume, so anything above that is real interference. Name the lumps -
# "1047 mm3 somewhere" is not something anyone can act on.
if _hit > 1e-6:
    _where = []
    for _s in _hit_solid.solids():
        _b = _s.bounding_box()
        _where.append(f"\n    {_s.volume:7.0f} mm3 at x {_b.min.X:.0f}..{_b.max.X:.0f}"
                      f"  y {_b.min.Y:.0f}..{_b.max.Y:.0f}  z {_b.min.Z:.1f}..{_b.max.Z:.1f}")
    raise AssertionError(
        f"{_hit:.0f} mm3 of the COVER is inside the panel once assembled. There "
        f"is only {DEPTH - _z_panel:.1f} mm behind the display and something on "
        f"the inner face is taller than that:" + "".join(_where))

# 3. THE CONDUCTION BLOCK has to span the gap exactly. It is a bought/cut metal
#    part so it is not modelled as geometry, but its thickness is a number this
#    file owns - it is set by the same stack as everything else, and if DEPTH,
#    the foam, the panel depth or the cover thickness move, this moves with them.
_z_plate_in = DEPTH + GASKET_C + COVER_T      # alloy plate's inner face
assert abs(TC_GAP - (_z_plate_in - _z_panel)) < 1e-9, "conduction block gap drifted"
assert TC_T > 3.0, (
    f"only {TC_GAP:.1f} mm between the panel's back and the plate - a "
    f"{TC_T:.1f} mm block is not worth making; bond the plate straight to the panel")
assert TC_L < AP - 1.0 and TC_W < AP - 1.0, (
    f"conduction block {TC_L}x{TC_W} does not clear the {AP} aperture it sits in")
for _px, _py in DSP_POSTS:
    assert (abs(_px - AP_CX) > TC_L/2 + DSP_POST_D/2
            or abs(_py) > TC_W/2 + DSP_POST_D/2), (
        f"conduction block overlaps the display post at ({_px:.0f},{_py:.0f})")

# 4. the panel screws have to be long enough to reach, and not bottom out
_grip = (COVER_T - DSP_CB_DEEP) + DSP_POST_H     # material the screw passes
DSP_SCREW_L = _grip + 5.0                        # + standoff engagement
assert DSP_SCREW_L <= 16.0, f"panel screw wants {DSP_SCREW_L:.1f} mm - odd length"

print(f"ASSY   front face 0 | land {_z_land} | panel back {_z_panel} | "
      f"brim {_z_brim} | foam {GASKET_C} | cover {_z_cover}")
print(f"       seat: rail at y={APER_Y - MOD_H/2 - MOD_FIT:.2f}, side pads "
      f"{MOD_PAD_PROUD:.2f} proud -> panel located +/-{MOD_FIT} in x, on the rail in y")
print(f"       order: bond panel into the seat (top open, swing it in) -> cure "
      f"-> foam on brim -> cover -> {len(DSP_POSTS)}x M{3} x {DSP_SCREW_L:.0f} "
      f"into the panel standoffs -> {len(BOLTS)}x M3 brim screws")
print(f"       sealed penetrations on the weather face: {len(BOLTS)} brim + "
      f"{len(DSP_POSTS)} panel = {len(BOLTS) + len(DSP_POSTS)}, all need bonded washers")
print(f"THERM  panel back {_z_panel} -> alloy plate inner {_z_plate_in}: {TC_GAP:.1f} mm gap")
print(f"       conduction block {TC_L:.0f} x {TC_W:.0f} x {TC_T:.1f} AL + "
      f"{TC_PAD} gap pad each end - metal path from the display's back to the fins")
