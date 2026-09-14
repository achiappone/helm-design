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
# 3 mm cord. Depth 0.77 D gives the squeeze; WIDTH is set from a FILL target,
# not the 1.15 D rule of thumb - that rule put 7.07 mm2 of cord in a 7.97 mm2
# groove, 89% full, and a cord that full in a joint that closes metal-to-metal
# has nowhere to go when it warms up: it hydraulically locks and the lid stops
# seating. 85% is the top of the safe band.
CORD_D, CORD_FILL = 3.0, 0.85
# THE GROOVE IS SPLIT BETWEEN THE TWO HALVES. It was all in the shell's brim,
# with the cover presenting a flat land - which is textbook for an O-ring in a
# machined face and wrong for a 2.3 m loop of cord being closed by hand. The
# cord is only captured on one side, so it rolls out of the groove as the cover
# comes down and you cannot see it happening: the lid still bolts flat, and the
# seal is half off its seat somewhere along the bottom rail.
#
# A shallow witness groove in the COVER captures the other side. The total
# depth is unchanged, so the squeeze is unchanged - what changes is that the
# cord has nowhere to go sideways while the joint is being closed.
GD_TOTAL = CORD_D*0.77
GD_COVER = 0.7                      # the cover's half: locate it, do not squeeze it
GD = GD_TOTAL - GD_COVER            # the shell's half, which still does the work
# from the COMBINED cavity, not the shell's half: the cord sits in a slot
# GW wide and GD_TOTAL deep, spanning both parts.
GW = (math.pi*(CORD_D/2)**2) / (CORD_FILL*GD_TOTAL)
assert 1.10*CORD_D < GW < 1.30*CORD_D, f"groove width {GW:.2f} is off the cord"

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
# 3 mm ROUND CORD in a groove. This went to a flat foam band earlier and has
# come back, for the plainest reason there is: the cord is what is in the box on
# the bench, and flat closed-cell foam sheet in the right thickness is a thing
# you have to go and source. A seal you own beats a seal you have to find.
#
# The screws still sit OUTBOARD of it - that decision stands and is unrelated to
# which seal is in the groove. What changes is the geometry of the thing being
# squeezed, and a cord is actually the easier of the two here: it is narrower
# than the 4.4 band it replaces, so the brim gets MORE lip, not less.
GASKET_T = 3.0                      # cord diameter
GASKET_W, GASKET_D = GW, GD         # the SHELL's groove
GASKET_D_COVER = GD_COVER           # and the cover's
assert GD + GD_COVER < CORD_D - 0.4, (
    f"the two grooves are {GD + GD_COVER:.2f} deep against a {CORD_D} cord - "
    f"that leaves {CORD_D - GD - GD_COVER:.2f} of squeeze, which is not a seal")
# A CORD IN A GROOVE CLOSES METAL-TO-METAL. The cover lands on the brim face and
# the cord is squeezed into its groove - so the assembled gap is ZERO, where the
# foam band held the cover 1.5 mm off. That ripples: the display bearing posts
# and the conduction block both derive their length from this number, and both
# get 1.5 mm longer again.
GASKET_C = 0.0
# The wall is straight, so the brim face is exactly RIM wide - no taper fudge.
BRIM_CAVITY = RIM
# Each band does a different job and none of them is padding:
#   OUT  hoop for a thread-forming M3 - too little and the screw splits out to
#        the free edge, which is the failure you find while assembling
#   WEB  shell between bolt hole and groove, so the boss cannot bulge into the
#        groove wall and pinch the cord
#   GRV  the groove itself, sized off the cord at 1.15 x dia
#   IN   lip inboard of the groove, to the cavity edge
_MIN_OUT, _MIN_WEB, _MIN_IN = 2.00, 1.20, 1.50
RIM_FLOOR = _MIN_OUT + M3_PILOT + _MIN_WEB + GASKET_W + _MIN_IN
assert BRIM_CAVITY >= RIM_FLOOR, (
    f"brim too narrow at RIM={RIM}: face {BRIM_CAVITY:.2f} vs floor "
    f"{RIM_FLOOR:.2f}, short by {RIM_FLOOR - BRIM_CAVITY:.2f} mm.")
LAND_OUT, LAND_WEB = _MIN_OUT, _MIN_WEB
BOLT_INSET = LAND_OUT + M3_PILOT/2
GASKET_OUT = LAND_OUT + M3_PILOT + LAND_WEB     # groove's OUTER edge from the edge
LAND_IN = BRIM_CAVITY - GASKET_OUT - GASKET_W   # spare all goes to the inner lip
assert LAND_IN >= _MIN_IN, f"inner lip {LAND_IN:.2f} under {_MIN_IN}"
assert GASKET_D < COVER_T - 1.0, "groove deeper than the brim can carry"
assert GD_COVER < COVER_T - 3.0, "the cover's groove leaves too little plate"

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
# ============================================================ FRICTION PIVOTS
# THE DETENT IS GONE, from both joints. It was right for the geometry it was
# designed against: with the tilt axis under the bottom edge the CG sat 114.7 mm
# above it, and 6.19 N*m at 3g fore-and-aft is far too much to hold by friction
# on ASA. The teeth were the only honest answer to that number.
#
# Moving the tilt axis to the SIDES at mid-height drops the arm to ~1.4 mm and
# the moment to 0.47 N*m - a Simrad-style bail, and the reduction is geometric
# rather than bought. At 0.47 N*m friction wins on every axis that matters: the
# joint is set by hand, it has no detent steps to land between, and its failure
# mode is slipping rather than stripping a crown or splitting an ear.
#
# WHAT MAKES THE FRICTION HOLD. Not ASA on ASA - that is like-on-like, it
# stick-slips and polishes as it works, so the setting drifts. A 1.0 mm 316
# shim runs free between the two printed lands, giving ASA/316 on both faces.
# The two faces are in SERIES: the stack slips at whichever is weaker and the
# other never sees more, so ONE face carries the torque. Counting two is the
# standard way this calculation gets inflated 2x.
# R1 is NOT a free choice - it is set by the shell's own depth. The side pivot
# land sits on a wall that is only DEPTH (22) tall in z, so a land bigger than
# ~10.5 runs off the front face at one edge and the brim at the other. That cap
# is what sets the holding torque, which is why R0 is opened up to 5.5 as well:
# on an annulus the effective radius rises faster by lifting the INNER edge than
# by chasing an outer edge there is no room for.
FRIC_R0, FRIC_R1 = 5.5, 10.5
FRIC_SHIM = 1.0                     # 316 shim thickness, free between the lands
FRIC_MU = 0.30                      # ASA on 316, handbook. THE SOFTEST NUMBER HERE.
FRIC_CLAMP = 550.0                  # N, set by what ASA bears long-term, not the bolt
# Uniform-pressure effective radius of an annulus - NOT the mean radius, which
# overstates it. (2/3)(b^3-a^3)/(b^2-a^2).
FRIC_REFF = (2/3)*(FRIC_R1**3 - FRIC_R0**3)/(FRIC_R1**2 - FRIC_R0**2)
FRIC_T = FRIC_MU * FRIC_CLAMP * FRIC_REFF / 1000.0      # N*m, ONE joint
# THIS IS THE VISOR'S JOINT. It used to be asserted against the whole unit's
# mass on a 10 mm arm - the deleted side-wall tilt pivot's case - which is not
# this joint's load and never was. The visor is ~120 g on a 60 mm hood; the
# unit's tilt joint is the cover trunnion with a 316 SERRATED pair, which holds
# by tooth engagement, not friction, and is sized in bail.py.
VISOR_M, VISOR_ARM = 0.12, 0.060          # kg, m
FRIC_NEED = VISOR_M * 9.81 * 6 * VISOR_ARM
assert 2*FRIC_T > 2.5 * FRIC_NEED, (
    f"visor friction pair holds {2*FRIC_T:.2f} N*m against {FRIC_NEED:.2f} needed")

PIV_X = [-148.0, 148.0]
# R_EAR was R_T1 + 1.5 = 14.5, and it was that size ONLY to keep the detent
# crown from running off the rim. With no crown the ear just has to hold the
# friction land plus an edge, so it comes down to FRIC_R1 + 1.5 = 11.5 - an ear
# O29 -> O23. UPS_T was 9.0 to give a thread-forming M5 enough ASA; the thread
# is in a nut now, so it only has to carry bearing, and 6.0 does that.
# TWO CHANGES HERE AND BOTH OF THEM ARE THE FOLD-FLAT VISOR.
#
# 1. THE HOOD HANGS ABOVE ITS AXIS, NOT BELOW IT. A plate slung under its pivot
#    can only ever swing round to the BACK of the front face - work the rotation
#    both ways and it lands at z = PIV_Z + 12, inside the box. That is geometry,
#    not tuning. Hung ABOVE the axis it swings down to z = PIV_Z - 12, in front
#    of the glass, which is where a folded visor belongs. See cad/helm_visor.py.
#
# 2. R_EAR 12 -> 8, because the ear is no longer sized round a FRICTION land.
#    The visor joint takes the same 316 SERRATED WASHER PAIR as the bail: teeth
#    hold mechanically, so the land does not have to be big enough to hold by
#    friction. The smaller ear is what lets PIV_Z rise far enough to clear the
#    glass when folded while its own rim stays above the bed - at r12 the ear
#    dipped below the front face, which is the surface this part prints on.
UPS_T, R_EAR = 6.0, 8.0
# The axis still sits ABOVE the top wall: the front face has to stay dead flat
# (it is the bed) so nothing can stand proud of it, which rules out mounting the
# pivot on the bezel. z is set by where the hood has to come to rest.
PIV_Y, PIV_Z = OUT_H/2 + R_EAR + 1.5, 8.0
assert PIV_Y - OUT_H/2 > R_EAR, "pivot ears would sink into the top wall"
assert PIV_Z >= R_EAR, (
    f"an r{R_EAR} ear on a {PIV_Z} axis dips {R_EAR - PIV_Z:.1f} mm in front of "
    f"the face - which is the bed this part prints on")
# WHERE THE HOOD COMES TO REST when it is folded down. The plate is tangent to
# the ear, so its underside stops PIV_Z - R_EAR off the bezel; the glass sits at
# FACE_T + the bond line. A visor that rests ON the screen is how you scratch one.
# z INCREASES INTO THE BOX - the front face is 0 and the glass sits BEHIND it at
# FACE_T + the bond line. So a folded visor has to come to rest at NEGATIVE z,
# in front of the bezel, and the first cut of this folded it to z=+7, which is
# inside the housing. The visor's own HOOD_RISE is set from this number.
VIS_STOW_Z = -2.0                   # hood's inner face, in front of the bezel
assert PIV_Z >= 5.4/2 + 2.0, (
    f"a O5.4 bolt on a {PIV_Z} axis breaks out through the front face")
PIV_BOLT = 5.4                      # clearance both sides
# THE NUT MOVED TO THE VISOR. It used to be pocketed in this upstand, which was
# fine at UPS_T 9.0 but leaves 0.7 mm behind a 5.3 deep nyloc pocket at 6.0.
# Rather than keep the shell thick to house a nut, the nut goes into the VISOR's
# ear - a free part, above the top wall, with nothing near it and no bed
# constraint. The shell keeps the slim pad; the visor carries the hardware.
# See PIV_NUT_* in cad/helm_visor.py.

# ============================================================ TILT AXIS HEIGHT
# The tilt axis runs through TRUNNIONS GROWN FROM THE REAR COVER (see the cover
# section below). The one number the shell contributes is the axis HEIGHT, set
# to the assembled centre of mass so vertical load puts no moment on the joint.
#
# Everything else that used to live here - PIV2_PROUD, PIV2_R, PIV2_BORE,
# PIV2_WALL, TILT_Z and their asserts - described a pivot boss on the SHELL'S
# SIDE WALL. That boss was deleted when the pivot moved to the cover, but its
# constants survived, kept being exported, and bail.py and assembly.py kept
# building the bracket against them: a pivot 32 mm in front of the real one.
TILT_Y = 8.7                        # the assembled CG in y. NOT a free number.



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
# BOTH BUMPS THE SAME, mirrored about the centreline. They used to disagree -
# the Pi's was 108x78 landscape, the driver's 65x125 portrait - which made the
# back of the unit visibly lopsided for no reason either board required. Both
# are portrait now, because portrait is the one that fits either board: the
# driver is 55x113 and only goes that way, while the Pi at 85x56 fits on its
# side. So the PI ROTATES 90 DEG in its bay and its connector stack faces up
# rather than outboard - the one real cost of the symmetry.
# 68 -> 88 wide. Rotated portrait, the Pi's 85 mm runs along the bay's 125 and
# its 56 across the 68 - which left 6 mm each side, and that is the side the
# micro-HDMI and USB-C sit on. A micro-HDMI plug needs about 20 mm to turn its
# cable, so 6 was a bay you could not actually wire. USB and Ethernet are on a
# short edge and face the 40 mm direction, so they were never the problem.
# Bay depth is INDEPENDENT of the shroud. They were briefly tied together to
# make the back one flat plane, but nothing requires it - the shroud is whatever
# the fan needs and the bays are whatever the boards need, and forcing them
# equal only means one of them is carrying depth it has no use for.
# -- tilt trunnions: declared here because the bumps are sized off them ----
# The geometry is further down. The numbers live up here because PI_BUMP_H is
# DERIVED from them: the trunnion tip is the rear-most point on the cover, and
# if the bumps do not reach the same plane the part balances on two r13 tips
# when you try to print it - 429 mm2 of bed contact on a 334 x 177 ASA plate.
SHROUD_ENVELOPE = 112.0             # ceiling the finished shroud must fit
# THE TRUNNION CARRIES THE WHOLE UNIT on two joints, in ASA, on a boat. It was
# an 8 mm web with a r13 land and a thread formed straight into the plastic -
# adequate on paper and thin everywhere it mattered. Heavier now, in all three
# directions that matter, and each one is bounded by something real:
#   WEB 8 -> 12   the root is in cross-layer bending at 60 C; section modulus
#                 goes as the thickness, so this is the cheapest strength on
#                 the part. Bounded inboard by the bay bump.
#   STAND 18 -> 22  a longer neck, which costs nothing in width and buys the
#                 arm's eye its clearance (EYE_R must stay under it).
#   LAND r13 -> r15  the disc the serrated washer bites: bearing area goes as
#                 r^2, so 15 is a third more face for 2 mm of radius.
# And the joint stops being a thread in plastic: a 316 NYLOC sits captive in a
# hex pocket in the web's inboard face and the bolt pulls against steel.
TRUN_X, TRUN_WEB_T = 156.0, 12.0
TRUN_STAND, TRUN_R, TRUN_LAND = 22.0, 15.0, 3.0
TRUN_BORE = 5.4                     # M5 316 clearance, through to the nut
TRUN_NUT_AF, TRUN_NUT_DEEP = 8.0, 6.0     # M5 316 nyloc, captive in the web
TRUN_GUSSET = 16.0                  # root fillet, fore and aft of the web

# 18 -> 31, DERIVED. Three faults, one number. At 18 the cover had no flat face
# to print on, the Pi stack did not fit the bay it bolts into, and the three
# bulkhead fittings had nowhere on the part to go. At TRUN_STAND + TRUN_R the
# bumps' backs are coplanar with the trunnion tips, the bay is 13 mm deeper, and
# the dead pockets beside each bump end become tall enough to take a flange.
# 88 -> 82. The web thickened inboard by 4 mm and the bumps reached to 146
# against a web that now starts at 144. 82 is the floor the Pi's own connector
# clearance sets, asserted below - so this is the whole of the room there is.
PI_BUMP_L, PI_BUMP_W = 82.0, 125.0
PI_BUMP_H = TRUN_STAND + TRUN_R
PI_BOARD_L, PI_BOARD_W = 56.0, 85.0         # Pi 4, on its side
PI_CONN = 20.0                              # cable turn clearance at HDMI/USB-C
assert PI_BUMP_L >= PI_BOARD_L + PI_CONN + 6.0, (
    f"bay {PI_BUMP_L:.0f} leaves {(PI_BUMP_L - PI_BOARD_L)/2:.0f} mm a side for "
    f"a plug that needs {PI_CONN:.0f}")
assert PI_BUMP_W >= PI_BOARD_W + 12.0, "bay too short for the board plus its stack"
# 81 -> 99. At 81 the 88-wide bays spanned 37..125 and the shroud is +/-53.5,
# so they overlapped by 4329 mm3 - the bump and the fan housing occupying the
# same air. Nothing checked the two against each other; the assembled bounding
# boxes did.
PI_BUMP_CX, PI_BUMP_CY = -102.0, 0.0
DRV_CX, DRV_CY = 102.0, 0.0
# THE BUMP AND THE BOARD ARE NOT THE SAME CENTRE. The bumps must stay mirrored -
# that is the owner's symmetry requirement and the assert below enforces it - but
# the BOARD inside the +x bay shifts 6 mm inboard so the Gore vent's bore, which
# enters that bay horizontally, passes over open air instead of over the board's
# outboard corner. Sharing one constant for both meant moving the board moved the
# bump, and moving the bump broke the symmetry.
DRV_BOARD_CX = 96.0
PI_BOARD_CX = PI_BUMP_CX
DRV_BUMP_L, DRV_BUMP_W, DRV_BUMP_H = PI_BUMP_L, PI_BUMP_W, PI_BUMP_H
# AP_CX 103 -> 80. The fan shroud is 138 wide and centres on this aperture, so
# at 103 it spanned x 34..172 and reached 5 mm PAST the bezel edge at 167 - the
# cooling was already breaking the width rule before any bracket existed. It
# also occupied the whole back between those x, which is where the bail arms
# have to run now that the pivot is on the cover. At 80 the shroud spans 11..149
# and leaves the outer strip clear.
# THE HEATSINK CLOSES THE COVER. There is no separate 6 mm alloy plate any
# more - the heatsink's own base seals the aperture and carries the tapped
# holes, which takes 6 mm out of the stack and deletes a part and an interface.
#
# So the aperture is sized off the HEATSINK, not the other way round: 74 wide
# less a sealing land each side. It was 84 square when a 114 plate covered it.
# FINS POINT OUTWARD, base flush on the INSIDE. This paragraph said the exact
# opposite of the geometry below it for three revisions - it argued the fins
# reach into the box, while the seat is cut from the inner face and HS_PROUD
# puts 4 mm of fin outside, under the shroud, in the fans' airstream. The
# geometry was right and the prose was wrong, which is the dangerous way round:
# two reviews quoted the comment.
#
# The cost of this orientation is real and is recorded at the assembly check:
# the box's inside sees a flat plate, so internal air-to-metal is the weak step.
#
# The aperture is the base footprint less a sealing land each side. The fins
# inside that land have to be TRIMMED OFF the bought part, an 8 mm band all
# round, or they foul the cover: a standard extrusion carries fins right to the
# edge of its base, so there is otherwise no flange to seal or glue against.
AP_SEAL = 8.0
# +1.0 clearance on each axis: the aperture was EXACTLY the trimmed fin field,
# so any slop in the seat put a fin against the aperture edge.
AP_CLR = 1.0
AP_L = 74.0 - 2*AP_SEAL + AP_CLR            # 59
AP_W = 150.0 - 2*AP_SEAL + AP_CLR           # 135
AP = AP_L                                   # legacy scalar, the short axis
# CENTRED. The aperture wandered 103 -> 96 -> 80 -> 75 -> 72 across one session,
# each move chasing a different constraint, and ended up inside the driver bump.
# Centred it is fixed by the part rather than by whatever moved last, the fan is
# centred with it, and the shroud sits 72 mm clear of both trunnions.
# The two bumps go either side of it.
AP_CX = 0.0
# Bolt ring must land INSIDE the heatsink base, since that base is now what the
# bolts thread into. It was 49, which put them 12 mm outside a 74-wide part.
AP_PITCH = 30.0
# THE CONDUCTION BLOCK IS GONE, and so are its constants. It bridged the
# panel's metal back to the alloy plate across the aperture; the heatsink's fins
# now reach into that same 10.5 mm and do the job directly, and better, because
# they pick up the whole internal air volume rather than one 56 mm window.
# The numbers hung on as TC_L/TC_W/TC_T/TC_PAD and the build page went on
# quoting a part that is not in the model, is not in the BOM and cannot be
# fitted - there is nothing for it to bolt to. Only the GAP is real, and it is
# the space the fins stand in.
FIN_GAP = (DEPTH + GASKET_C + COVER_T) - (FACE_T + MOD_D)

# -- heatsink on the plate's outer face ------------------------------------
# ONE 150 x 74 x 10, turned 90 deg so the 150 runs vertically. Four 100x25x10
# strips fitted the old square plate but left gaps between them; one base
# spreads better and gives ~12% more fin in a single part.
#
# Vertical because the cover is 177 tall and only 334 wide, and the shroud has
# to clear the tilt trunnions at x 145. Lying flat, a 150-long block forces the
# shroud into them; stood up, the length goes where there is room.
HS_L, HS_W, HS_H = 74.0, 150.0, 10.0        # x, y, height
HS_N = 1
HS_CY = [0.0]
HS_SPAN = HS_W
HS_FIT = 0.4                                # per side, in the gluing jig
# Plate and fixings sized round the block: the fixings clear it in X (block is
# +/-37, they sit at +/-45) so they never land on fins.
HS_PLATE_X, HS_PLATE_Y = 100.0, 160.0
HS_PLATE = HS_PLATE_X                       # legacy scalar, the short axis
# AT THE SHROUD'S CORNERS. The fixings were at (+/-45, +/-62) - inside the
# shroud, against the cover, in the 6 mm between the fan backs and the plate -
# and no driver reaches them once the fans are in. They are now at the four
# corners of the shroud's outline, where a boss can run the shroud's full depth
# and the screw goes in from the LOUVRED FACE, straight through to the cover.
# Derived from the shroud's own box so they cannot drift.
# 96 -> 104 in X. At 96 the corner fixing bosses sat at x = +/-42.5 with r5, so
# their inner edge was 37.5 - and an 80 mm fan reaches 40. The bosses were
# occupying the fans' own frame corners: the shroud could be printed, bolted on
# and admired, and the fans could not be put into it.
SHROUD_W, SHROUD_H = 104.0, 168.0   # the shroud BOX
# THE SHROUD SITS OVER FOUR BRIM SCREW HEADS and that is now deliberate. Its rim
# reaches y = +/-84 and the screws at (+/-30.5, +/-85.2) carry O6 heads on
# bonded washers reaching y = 82.2, so the two overlap by 1.8 mm - the shroud was
# resting on two screw heads at each end and rocking on them. Nothing checked
# it: the fastener ring and the shroud outline are placed in different files.
#
# Shrinking the shroud to 160 to clear them does not work - two 80 mm fans span
# exactly 160 and need 162 of cavity - and moving those four screws leaves a
# 104 mm gap in the fastener ring across the middle of the long edge, which is
# the worst place on the part to lose clamp. So the SHROUD is relieved instead:
# four pockets in its landing face, placed from the bolt list below. A shroud is
# a rain shield, not a pressure boundary, and it can afford the pockets.
# Separate insets. In X the boss has to stay off the 74 wide heatsink, which
# pins it to 5.5 from the edge. In Y it has to keep its BLIND PILOT clear of the
# cord's sealing land at |y| 79.25 - a thread-formed M3 swells the plate around
# it, and doing that under the seal is how a waterproof box stops being one.
# At 5.5 the pilot reached y 79.8 and crossed into the land.
# X inset is now set by the FAN, not the heatsink: the boss's inner edge has to
# clear the 80 mm frame corner at x=40 by a real margin, and the heatsink at 37
# is no longer the binding constraint.
HS_HOLE_IN_X, HS_HOLE_IN_Y = 5.5, 9.0
FAN_HALF = 40.0                     # the 80 mm frame, from heatsink_shroud.py
HS_HOLES = [(sx*(SHROUD_W/2 - HS_HOLE_IN_X), sy*(SHROUD_H/2 - HS_HOLE_IN_Y))
            for sx in (-1, 1) for sy in (-1, 1)]
assert all(abs(hx) - 5.0 > HS_L/2 for hx, _ in HS_HOLES), (
    f"a shroud fixing boss lands on the {HS_L:.0f} wide heatsink")
assert all(abs(hx) - 5.0 > FAN_HALF + 1.0 for hx, _ in HS_HOLES), (
    f"a shroud fixing boss reaches x={min(abs(hx) for hx,_ in HS_HOLES) - 5.0:.1f}, "
    f"inside the {2*FAN_HALF:.0f} mm fan frame - the fans cannot be seated")
assert HS_L < HS_PLATE_X and HS_W <= HS_PLATE_Y, "heatsink overhangs the plate"
assert HS_PLATE_X >= AP and HS_PLATE_Y >= AP, "plate does not cover the aperture"

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
# them, and the jig that positions them while the thermal adhesive cures. When
# FOUR 100 x 25 x 10 strips tiled into a 100 x 100 block, replacing two
# 100 x 40 x 20. Half the fin height, so the shroud loses 10 mm and the unit
# goes 83 -> 73. Fin area falls to ~83% of the old pair, which is the price and
# that the base area goes UP, 8000 -> 10000 mm2, so the plate is worked harder
# even as the fins get shorter.
#
# Tiled strips rather than one 100x100 block because 100x25x10 is a thing you
# can buy today and a low-profile 100x100 is not. Pin fins would suit an axial
# fan blowing straight down far better than any extrusion, but they are a
# thermal-vendor part, not a marketplace one.
# FIXINGS MOVE TO THE EDGE MIDPOINTS. They were at the four corners (+/-48,
# +/-48), which sat under a 100-wide block - the old pair of 40-wide strips left
# the corners clear and this one does not. Midpoints sit outside the block in
# one axis each, which is the only pattern that clears a square footprint on a
# square plate.
# Plate 114 -> 120. At 114 the midpoint fixings had nowhere to sit: they must
# clear a 100-wide block on one side and leave edge material on the other, and
# 114 gives 7 mm to do both in. The plate is a sawn piece of 6 mm aluminium, so
# 6 mm more of it costs nothing and the shroud already covers it.
# -- cover-frame conversion ------------------------------------------------
# assembly.py places the cover as Rot(180,0,0) then z += DEPTH+COVER_T, so the
# cover MIRRORS IN Y: cover +y is shell -y. rev B specified the GPS cradle at
# cover y +63.5..72.5 with a comment saying it sits under the TOP wall - it
# actually landed on the BOTTOM one. Everything below is written in SHELL
# coordinates and converted here, so that cannot happen again.
# Cover packaging, all in SHELL coordinates. The bumps protrude OUTWARD, so
# they only have to clear each other, the bolt ring and the heat aperture.
# AP_CX 103 -> 80. The fan shroud is 138 wide and centres on this aperture, so
# at 103 it spanned x 34..172 and reached 5 mm PAST the bezel edge at 167 - the
# cooling was already breaking the width rule before any bracket existed. It
# also occupied the whole back between those x, which is where the bail arms
# have to run now that the pivot is on the cover. At 80 the shroud spans 11..149
# and leaves the outer strip clear.
# Thickness is DERIVED from the assembled z-stack: the panel's back sits at
# FACE_T + MOD_D, the alloy plate's inner face at DEPTH + GASKET_C + COVER_T
# (the plate bolts to the cover's OUTER face, so the aperture is a window onto
# it). Everything in that chain has moved at least once today - the foam alone
# shifted the cover 1.5 - so this is derived, never typed.
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
# them, and the jig that positions them while the thermal adhesive cures. When
# -- the three bulkhead fittings, and where they finally go ----------------
# THEY WERE ALL IN MID AIR. The cable gland at (-120,-56), the Gore vent at
# (-55,-64) and the SMA bulkhead at (-140,50) were placed on the cover's flat
# outer face - and the two bay bumps own that face from |x| 58 to 146 and |y| up
# to 62.5, hollowed right through. Two of the three bosses were built inside
# that void, fused to a bay side wall by whatever part of them happened to
# overlap it; 31.6% of the SMA's nut face hung over nothing. The checks in this
# file compared cover features to OTHER COVER FEATURES and to the seal, never to
# the bays, so all three passed for three revisions.
#
# There is no room on the face. Outside the bays, inside the seal and clear of
# the shroud, what is left is a 10 mm strip and a 15 mm band - nothing 20 mm
# across fits, and the smallest of these fittings needs 19.
#
# THE FACE IS FULL; THE PART IS NOT. Each bump stops at |y| 62.5 while the cover
# runs to 88.5, so beside each bump end there is a pocket 88 wide, 15 deep and
# PI_BUMP_H tall with nothing in it. A block filling the two BOTTOM pockets
# gives three flat, downward-facing seats, and a bore driven horizontally
# through one costs nothing in width or depth because it never reaches past the
# bumps' back plane. Downward-facing also means: no standing water, no sun on a
# nylon gland, and an automatic drip loop on the cable.
# DERIVED from the bump, not typed: the block is fused to the bump's end wall,
# so when the bump moved 4 mm the block has to move with it or it hangs in air.
BLK_X0 = abs(PI_BUMP_CX) - PI_BUMP_L/2 + 34.0
BLK_X1 = abs(PI_BUMP_CX) + PI_BUMP_L/2 + 6.0
BLK_Y0, BLK_Y1 = -76.0, -62.5       # from the bump's end wall outward
# AND THE SAME AGAIN AT THE TOP. Each bump leaves a pocket at BOTH ends, and
# only the bottom pair was being used. The top pair is where the aerial belongs:
# a bore through it exits UPWARD, so a whip screwed straight onto the bulkhead
# stands up at the sky instead of pointing into the dash - which is the whole
# reason it came off the flat cover face in the first place.
BLK_TY0, BLK_TY1 = 76.0, 62.5

# -- INTERNAL GPS, in a shielded chimney in the -x top block ---------------
# The GPS went EXTERNAL two revisions ago and that is still the better answer:
# a ceramic patch behind a metre of dash sees no sky, and a display's LVDS
# ribbon radiates hard at L1. Nothing below changes that recommendation. What it
# does is make the internal option BUILDABLE, because "put it somewhere inside"
# is the request and somewhere inside is a decision with exactly one good answer
# on this housing.
#
# WHERE. The patch has to face the sky, and the only upward-facing real estate
# on the unit is the two TOP blocks. The +x one has the whip's bulkhead in it -
# a 400-470 MHz transmitter whose third harmonic lands on top of L1 at 1575, and
# no amount of foil fixes a transmitter 40 mm away - so the GPS takes the -x
# block, 242 mm from the whip. That puts it over the Pi, which is broadband
# digital hash rather than a transmitter, and broadband hash is exactly what a
# shielded cup and a ground plane are for.
#
# WHAT IT IS. A chimney: open DOWNWARD into the Pi bay so the module can be
# pushed up into it and reached again, closed at the top by a thin ASA window.
# ASA is RF-transparent, so the window is the radome; it is also the only thing
# between the patch and the weather, which is why it is printed solid rather
# than left as a hole with a cover over it.
#
# WHAT YOU LINE WITH COPPER. The four walls and the shelf UNDER the module -
# never the window. That cup is both the EMI shield and the patch's ground
# plane, which a patch antenna needs and which it has not got inside a plastic
# box. Bond the foil to system ground at one point only: foil that is not
# grounded is a reflector, and foil grounded at two points is a loop.
GPS_INTERNAL = True
GPS_L, GPS_W, GPS_T = 18.0, 18.0, 8.0      # MEASURED: SEQURE M10-18
GPS_FIT = 0.4                               # per side
GPS_WIN_T = 1.2                             # the ASA radome over the patch
GPS_SHELF = 2.0                             # the ledge the module sits on
GPS_X = -(BLK_X0 + BLK_X1)/2                # centred in the -x top block
GPS_Z = -PI_BUMP_H/2                        # mid-height, as the fittings are
BLK_CHAM = 2.0
BORE_Z = -PI_BUMP_H/2               # bores on the block's mid-height

# STRAIGHT M16, not an M20 elbow. The elbow existed to turn the cable parallel
# to the mounting face; a -y bore already points it where it needs to go, so the
# elbow is a swivel joint and 15 mm of bulk bought for nothing. And M20 never
# fitted: the limit is not the tapping bore but the gland's 24 A/F hex, which
# wants 27.7 mm of flat seat on a face that is PI_BUMP_H tall.
# COST: M16 clamps 5-10 mm, so the tail has to be <= 10 mm OD. A 24 x 24 AWG
# overall-shielded cable is about that; parallel three pins each for +12 V and
# ground on the LP-24 rather than running heavier cores.
GL_X, GL_TAP, GL_FLANGE = -110.0, 14.5, 22.0
CABLE_D = 10.0                      # the most an M16 gland clamps; the LP-24 parts read this
# Gore M12x1.5, TAPPED rather than clearance + locknut: a O19 locknut pocket at
# this x reaches the bay void's wall with 0.00 mm to spare.
VENT_X, VENT_TAP, VENT_FLANGE = 133.0, 10.5, 19.0
# THE WHIP COMES OFF THE HOUSING. This is a refusal, not a relocation, and it is
# the same call the GPS patch got: a 185 mm whip grown off the back of a display
# that TILTS points into the dash, sweeps an arc through the bail arms and the
# visor, and sits 10 mm from the Pi behind an alloy heatsink - the worst RF
# address on the boat. It goes on a rail or hardtop mount with a coax run, and
# what the housing gets is a COAX ENTRY, which is the honest name for what this
# always was. That collapses the biggest of the three penetrations into the
# smallest: a plain M8x0.75 IP67 SMA bulkhead in a sheltered, downward-facing
# seat, with no raised sealing pad needed on either side because the block's
# faces are flat by construction.
# ON TOP OF THE DRIVER BUMP, pointing UP. It was on the -x block's underside,
# alongside the gland, where a whip could not have been fitted to it at all -
# it would have gone straight down into the dash. +x rather than -x because
# that is the far side from the Pi and the display's ribbon, which is the RF
# argument that has been in this file since the GPS went external.
# ITS NUT IS CAPTIVE, like the trunnion's. A plain counterbore put the nut in
# the bay, where the driver board leaves 5.9 mm of clear air - you cannot turn a
# spanner in that, and moving the bulkhead to where you could put it through the
# bay's own wall. A hex pocket in the block's INNER face holds the nut instead:
# drop it in, screw the bulkhead down from outside, nothing to hold.
SMA_X, SMA_D = 120.0, 8.2
SMA_NUT_AF, SMA_NUT_DEEP = 12.0, 4.0
ANT_MOUNT = True                    # now means "coax entry", not "whip mount"
# All of these lie in the 4.5 mm behind the display panel (1.5 standoff +
# 1.6 board = 3.1), and all must stay INBOARD of the cover's sealing face.
SENSORS = [                      # (name, shell x, shell y, pitch x, pitch y)
    # ALL FOUR MOVED OUT OF THE BAYS. They used to stand on the cover's inner
    # face at x +/-60..100, which is inside the Pi and driver bays - and they only
    # had a face to stand on because those bays were accidentally capped. Opening
    # the bays through left every one of them floating in mid air.
    #
    # They live in the two strips between the aperture and the bays now: x 32..56
    # and -56..-32, which is the only inner face left that is neither a bay nor
    # the heatsink seat.
    # The strips beside the heatsink seat are only 21 mm wide and the MCP23017
    # alone needs 38 of pitch, so they go to the TOP AND BOTTOM bands instead:
    # the bays stop at y +/-62.5 and the seal starts at 78.3, which leaves a
    # clear run the full width of the cover.
    ("MCP23017", -100.0,  68.0, 38.10, 12.70),
    ("MCP9808",   100.0,  68.0, 20.32, 12.70),
    ("ADXL345",   100.0, -68.0, 20.32, 12.70),
    ("ICM20948", -100.0, -68.0, 20.32, 12.70),
]
# Anchor x's are picked to clear what shares those bands: the bottom row must
# miss the gland boss at GL_X (-120) and the Gore vent at -60. That said -150
# for two revisions while the boss was actually at -120; two independent
# reviewers read the comment instead of the code and both computed the cable
# swing off the wrong point. A number written twice is a number that drifts. The top row used to
# have to dodge the GPS cradle at x 128..152 as well; that is gone, and the
# anchors are left where they are rather than re-spaced for nothing.
# Clear of the heatsink SEAT, which is cut into this face and spans x +/-37.
# The old pattern put anchors at 0 and -40, inside it, and the seat sheared them
# off their own face - caught by the floating-feature check, not by a clash test.
# Clear of the heatsink seat (x +/-37) AND of the bays (x 58..146 each side).
# ONE PER SIDE, at 48, not two at 42 and 50. A 13 mm anchor centred at 42 spans
# x 35.5..48.5 and the heatsink's seat reaches 37.6 - so the anchors were inside
# the seat, and the heatsink's own base corners hit them on the way in. The
# clear strip is between the seat (37.6) and the bay (58), which is 20 mm wide:
# it takes one 13 mm anchor, not two.
TIE_TOP = [-48.0, 48.0]
TIE_BOT = [-48.0, 48.0]
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
# THE BOND LINE HAS A THICKNESS. The panel sat with its front ON the land and
# the posts reached exactly its back, so the adhesive between panel and land was
# squeezed to nothing - which is a joint that peels, not one that holds. 0.5 mm
# of silicone is the number; the panel moves back by it and everything behind
# the panel is derived from the same stack, so the posts follow.
GLUE_T = 0.5
DSP_POST_H = DEPTH + GASKET_C - FACE_T - GLUE_T - MOD_D
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

# PITCH 45, not 60. The cover is a 6 mm ASA plate and a cord seal needs its
# squeeze held everywhere, not just at the screws: at 60 mm pitch the plate bows
# between them and the review put the mid-span squeeze at a third of the design
# value. The Gore vent means the gasket never sees pressure, only water, so this
# is stiffness, not clamp load - and stiffness is the pitch.
#
# These screws are OUTBOARD of the cord and go into BLIND pilots in the brim,
# so none of them is a path into the box. They still get a bonded washer each,
# for the opposite reason: a 2.6 x 11 blind hole in ASA, horizontal in service
# and open to spray, is a chloride crevice around a 316 thread with no way to
# drain. The washer keeps the pilot dry. Pack them with Tef-Gel as well.
BOLT_PITCH = 45.0
BOLTS = rrect_pts(OUT_W/2 - BOLT_INSET, OUT_H/2 - BOLT_INSET,
                  R_OUT - BOLT_INSET, BOLT_PITCH)

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
# THE GROOVE. Cut into the brim face, outer edge GASKET_OUT in from the shell's
# edge. rev C had no groove at all (GROOVE = None) because the seal was a flat
# band squeezed on the face; a cord needs to be captured or it rolls out of the
# joint as the cover goes down.
GROOVE = None
_g_out = RectangleRounded(OUT_W - 2*GASKET_OUT, OUT_H - 2*GASKET_OUT,
                          max(R_OUT - GASKET_OUT, 1.0))
_g_in = RectangleRounded(OUT_W - 2*(GASKET_OUT + GASKET_W),
                         OUT_H - 2*(GASKET_OUT + GASKET_W),
                         max(R_OUT - GASKET_OUT - GASKET_W, 1.0))
_v0 = f.volume
f -= extrude(Plane.XY.offset(DEPTH - GASKET_D) * (_g_out - _g_in), amount=GASKET_D + 1)
assert f.volume < _v0 - 1000, (
    f"gasket groove removed only {_v0 - f.volume:.0f} mm3 - it is not landing "
    f"on the brim face")

# visor pivot upstands. Undersides chamfered 45 deg so they print as part of
# the top wall rather than as an unsupported cantilever.
for px, outward in ((PIV_X[0] - UPS_T/2, +1), (PIV_X[1] + UPS_T/2, -1)):
    ups = Pos(px, 0, 0) * Rot(0, 90, 0) * Cylinder(R_EAR, UPS_T,
              align=(Align.CENTER, Align.CENTER, Align.CENTER))
    ups = Pos(0, PIV_Y, PIV_Z) * ups
    ups += Pos(px, (PIV_Y + OUT_H/2)/2 - 6, PIV_Z) * Box(
        UPS_T, PIV_Y - OUT_H/2 + 12, 2*R_EAR,
        align=(Align.CENTER, Align.CENTER, Align.CENTER))
    f += ups
    # The inboard face is the FRICTION LAND now, not a crown. It is left as
    # printed: a plain annulus that the 316 shim runs against. Nothing is built
    # on it, and nothing should be - a texture or a knurl works by digging in,
    # and digging in is creep by another name.
    f -= Pos(px, PIV_Y, PIV_Z) * Rot(0, 90, 0) * Cylinder(PIV_BOLT/2, 26)

# (antenna is on the rear cover - see the note at SMA_D)

# The tilt pivot is NOT on this part. It used to be a boss on each side wall,
# which put the axis 1.4 mm from the CG and was mechanically the best place for
# it - but it hung hardware off the front shell and stood proud of the bezel
# line. It now lives on the REAR COVER instead; see cad/trunnion.py, and the
# margin note there, because moving it back cost most of that advantage.

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
print(f"       brim @ RIM {RIM}: {GASKET_T:.0f} mm CORD in a {GASKET_W:.2f} x "
      f"{GASKET_D:.2f} groove + {GASKET_D_COVER:.2f} in the COVER = {GASKET_D + GASKET_D_COVER:.2f} "
      f"of a {CORD_D} cord captured, {CORD_D - GASKET_D - GASKET_D_COVER:.2f} of squeeze; "
      f"screws OUTBOARD of it")
print(f"       bands out {LAND_OUT:.2f} / M3 {M3_PILOT} / web {LAND_WEB:.2f} / "
      f"groove {GASKET_W:.2f} / lip {LAND_IN:.2f}; bolt inset {BOLT_INSET:.2f}")
print(f"       bezel {(OUT_W-APER_W)/2:.1f} side / {OUT_H/2-(APER_Y+APER_H/2):.1f} top")

# ============================================================ REAR COVER
c = extrude(Plane.XY * RectangleRounded(OUT_W, OUT_H, R_OUT), amount=COVER_T)
for bx, by in BOLTS:
    c -= Pos(bx, cy(by)) * Cylinder(M3_CLEAR/2, 3*COVER_T)
# (the vent, the gland and the SMA are cut further down, after the bumps -
#  they live in blocks fused to the bumps' end walls and need them to exist.)

# -- Pi and driver bumps, both OUTWARD (-z on this part) -------------------
for _cx, _cyy, _l, _w, _h in ((PI_BUMP_CX, PI_BUMP_CY, PI_BUMP_L, PI_BUMP_W, PI_BUMP_H),
                              (DRV_CX, DRV_CY, DRV_BUMP_L, DRV_BUMP_W, DRV_BUMP_H)):
    c += Pos(_cx, cy(_cyy), -_h) * Box(_l, _w, _h,
                                       align=(Align.CENTER, Align.CENTER, Align.MIN))
    # Hollowed THROUGH to the inner face. The cut used to be _h tall starting at
    # -_h + WALL, which ends at z=WALL - three millimetres short of the inner
    # face at COVER_T. That left a floor across each bay: a sealed pocket the
    # boards could not be put into, on a feature whose entire purpose is to make
    # room for them. It looked right from outside and from any section that
    # missed the floor.
    c -= Pos(_cx, cy(_cyy), -_h + WALL) * Box(
        _l - 2*WALL, _w - 2*WALL, _h + COVER_T,
        align=(Align.CENTER, Align.CENTER, Align.MIN))

# board lies with its 113.25 along Y; holes from the confirmed centres
DRV_HOLES = [(-55.25/2 + 3.75,  113.25/2 - 9.0),
             (-55.25/2 + 3.75, -113.25/2 + 4.0),
             ( 55.25/2 - 7.25,  113.25/2 - 9.0),
             ( 55.25/2 - 3.75, -113.25/2 + 4.0)]
for _hx, _hy in DRV_HOLES:
    _p = Pos(DRV_BOARD_CX + _hx, cy(DRV_CY + _hy), -DRV_BUMP_H + WALL)
    c += _p * Cylinder(6.0/2 + 1.6, 5.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= _p * Cylinder(M25_PILOT/2 + 0.3, 5.5, align=(Align.CENTER, Align.CENTER, Align.MIN))

# -- Pi bay: the SAME treatment, which it did not have --------------------
# The driver bay has had bosses since the bay existed. The Pi bay had none: an
# 88 x 125 pocket with a Raspberry Pi loose in it. It was invisible because
# every render draws the Pi floating at the right height, and every review read
# "boards in their bays" as if mounting them were solved. (It was added once and
# then lost inside a block replacement, which is why it is asserted below now.)
#
# Pi 4: 85 x 56, holes 58 x 49 on 3.5 mm edge margins. It lies PORTRAIT here -
# 85 along y - so the 58 pitch runs in y and the 49 in x.
PI_HOLES = [(sx*49.0/2, sy*58.0/2) for sx in (-1, 1) for sy in (-1, 1)]
PI_STANDOFF_H = 5.0                 # clears the solder side and the SD card
_v_before = c.volume
for _hx, _hy in PI_HOLES:
    _p = Pos(PI_BOARD_CX + _hx, cy(PI_BUMP_CY + _hy), -PI_BUMP_H + WALL)
    c += _p * Cylinder(6.0/2 + 1.6, PI_STANDOFF_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= _p * Cylinder(M25_PILOT/2 + 0.3, PI_STANDOFF_H + 0.5,
                       align=(Align.CENTER, Align.CENTER, Align.MIN))
assert c.volume > _v_before, (
    "the Pi bay's mounting bosses added no material - the board has nothing to "
    "bolt to, which is exactly the fault this block was written to fix")
# The stack has to fit the hole it is bolted into: bay floor to the display's
# back is the bay depth, plus the window through the plate, plus the gap behind
# the panel. Pi + Armor Lite is the tall case.
_PI_STACK = PI_STANDOFF_H + 1.6 + 17.0          # standoff + board + Armor Lite
_PI_ROOM = (PI_BUMP_H - WALL) + COVER_T + (DEPTH - FACE_T - GLUE_T - MOD_D)
assert _PI_STACK < _PI_ROOM, (
    f"Pi stack is {_PI_STACK:.1f} tall and there is {_PI_ROOM:.1f} from the bay "
    f"floor to the back of the display")

# -- tie-wrap anchors, inner face ------------------------------------------
for _xs, _sgn in ((TIE_TOP, 1), (TIE_BOT, -1)):
    for _tx in _xs:
        c += Pos(_tx, cy(_sgn*TIE_Y), COVER_T - 0.3) * Box(
            TIE_L, TIE_W, TIE_H + 0.3, align=(Align.CENTER, Align.CENTER, Align.MIN))
        c -= Pos(_tx, cy(_sgn*TIE_Y), COVER_T + TIE_H - TIE_SLOT/2 - 0.4) * Box(
            TIE_L + 2, TIE_SLOT, TIE_SLOT, align=(Align.CENTER,)*3)

# -- tie-wrap anchors INSIDE the Pi bay, beside the gland mouth ------------
# The cable comes through the gland into this bay and turns toward the Pi. The
# gland's clamp should not be the only thing holding it: two anchors on the bay
# floor, in the clear band between the gland's mouth and the board.
for _ax in (GL_X - 12.0, GL_X + 12.0):
    _ay = -(PI_BUMP_W/2 - WALL) + 9.0            # 9 mm in from the end wall
    c += Pos(_ax, cy(_ay), -PI_BUMP_H + WALL - 0.3) * Box(
        TIE_W, TIE_L, TIE_H + 0.3, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= Pos(_ax, cy(_ay), -PI_BUMP_H + WALL + TIE_H - TIE_SLOT/2 - 0.4) * Box(
        TIE_SLOT, TIE_L + 2, TIE_SLOT, align=(Align.CENTER,)*3)

# ...and the same two inside the DRIVER bay, so the two bays stay alike and the
# anchor count the cable work needs comes back.
for _ax in (VENT_X - 12.0, VENT_X + 12.0):
    _ay = -(PI_BUMP_W/2 - WALL) + 9.0
    c += Pos(_ax, cy(_ay), -PI_BUMP_H + WALL - 0.3) * Box(
        TIE_W, TIE_L, TIE_H + 0.3, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= Pos(_ax, cy(_ay), -PI_BUMP_H + WALL + TIE_H - TIE_SLOT/2 - 0.4) * Box(
        TIE_SLOT, TIE_L + 2, TIE_SLOT, align=(Align.CENTER,)*3)

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
# CANDIDATES, not a final list. Which of the panel's rear standoffs can be used
# is decided by what is behind them on the cover, and two things are behind
# large parts of it: the heat aperture and the two board bays. A post over
# either has no inner face to stand on.
# The two top candidates were at x -140 / +143, which is under the TOP fitting
# blocks now that those exist - a screw driven from behind would hit 1158 mm3
# of block. Inboard of BLK_X0 instead, where the band is still open face.
DSP_CAND = [(-85.0,        _T - 8.25),    # top band, inboard of the blocks
            ( 85.0,        _T - 8.25),
            (_L + 30.5,   _B + 13.0),    # lower - these two were IN THE BAYS
            (_R - 26.5,   _B + 13.0),
            (-53.0, APER_Y - 51.0),      # strip between the seat and the bay
            ( 53.0, APER_Y - 51.0)]

def _bay_hit(px, py):
    """True if this cover point is over one of the two bump-out bays, which are
    hollowed right through and have no inner face to grow a post from."""
    return (abs(abs(px) - abs(PI_BUMP_CX)) < PI_BUMP_L/2 + DSP_POST_D/2
            and abs(py) < PI_BUMP_W/2 + DSP_POST_D/2)

def _post_problem(px, py):
    if (abs(px - AP_CX) < AP_L/2 + DSP_POST_D/2
            and abs(py) < AP_W/2 + DSP_POST_D/2):
        return "inside the heat aperture"
    if _bay_hit(px, py):
        return "over a board bay"
    for _b0, _b1 in ((BLK_Y0, BLK_Y1), (BLK_TY0, BLK_TY1)):
        if (BLK_X0 - DSP_POST_D/2 < abs(px) < BLK_X1 + DSP_POST_D/2
                and min(abs(_b0), abs(_b1)) - DSP_POST_D/2 < abs(py)
                    < max(abs(_b0), abs(_b1)) + DSP_POST_D/2):
            return "under a fitting block"
    if abs(px) + DSP_POST_D/2 > OUT_W/2 - BRIM_CAVITY:
        return "across the sealing face"
    return None

DSP_POSTS = [p for p in DSP_CAND if _post_problem(*p) is None]
_DROPPED = [(p, _post_problem(*p)) for p in DSP_CAND if _post_problem(*p) is not None]
if _DROPPED:
    print("       display posts dropped: "
          + "; ".join(f"({x:.0f},{y:.0f}) {w}" for (x, y), w in _DROPPED)
          + f"  -> {len(DSP_POSTS)} posts carry the panel")
assert len(DSP_POSTS) >= 3, (
    f"only {len(DSP_POSTS)} usable display posts - the panel would hang on "
    f"adhesive plus {len(DSP_POSTS)} screws")
# Two of these were standing INSIDE the Pi and driver bays, in the boards' own
# footprints, growing up from the bay skin - and the screw bore was cut centred
# on z=0, so it did not even pass through them. They were solid pillars through
# the middle of where the Raspberry Pi goes. The bay test is new; the previous
# one only knew about the aperture.

def _in_bay(px, py):
    """True if this point is over one of the two bump-out bays."""
    return (abs(abs(px) - abs(PI_BUMP_CX)) < PI_BUMP_L/2 - WALL
            and abs(py) < PI_BUMP_W/2 - WALL)

for _px, _py in DSP_POSTS:
    # A post over a BAY has no inner face to stand on - the bay is hollowed right
    # through - so it grows from the bay's outer skin instead and is that much
    # longer. Standing them all on COVER_T left two of them floating in mid air
    # the moment the bays were opened up.
    _z0 = (-PI_BUMP_H + WALL) if _in_bay(_px, cy(_py)) else (COVER_T - 0.3)
    _len = (COVER_T - 0.3 + DSP_POST_H + 0.3) - _z0
    c += Pos(_px, cy(_py), _z0) * Cylinder(
        DSP_POST_D/2, _len, align=(Align.CENTER, Align.CENTER, Align.MIN))
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


# -- the three bulkhead fittings, in blocks beside the bumps ---------------
# Two blocks, one per bottom pocket, mirrored - so the back stays symmetric.
# Each is fused to the cover plate above it and to its bump's end wall inboard,
# and its underside is coplanar with the bump's back. Every face is vertical in
# print, on the bed, or fused to the plate: no support, no overhang.
_BORE_R_MAX = max(GL_TAP, VENT_TAP, SMA_NUT_AF) / 2
BLOCKS = [(BLK_Y0, BLK_Y1), (BLK_TY0, BLK_TY1)]     # bottom pair, top pair
for _by0, _by1 in BLOCKS:
    for _bs in (-1, 1):
        c += Pos(_bs*(BLK_X0 + BLK_X1)/2, cy((_by0 + _by1)/2), -PI_BUMP_H) * Box(
            BLK_X1 - BLK_X0, abs(_by1 - _by0), PI_BUMP_H,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
# the block's outboard corners are chamfered so water runs off rather than
# collecting in the step between block and bump
for _by0, _by1 in BLOCKS:
  for _bs in (-1, 1):
    for _ex in (BLK_X0, BLK_X1):
        c -= (Pos(_bs*_ex, cy(_by0), -PI_BUMP_H/2) * Rot(0, 0, 45)
              * Box(BLK_CHAM*1.42, BLK_CHAM*1.42, PI_BUMP_H + 2,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER)))

SEAT_LAND = 3.0                     # round-crown collar at the flange face

def _ybore(x, dia, y0, y1, teardrop=True):
    """A horizontal bore along -y through a block, printed without support.

    The crown of a horizontal hole sags, and a 45 deg teardrop apex above it
    turns that crown into two walls that bridge themselves. But the apex is a
    NOTCH, and the first cut of this ran it the full length of the bore - i.e.
    straight out through the face the fitting's O-ring seats on. All three
    fittings had a V-groove 0.25 x D deep cut across their sealing land: the
    gland's and the vent's face seals had nothing to seal against.

    So the teardrop stops SEAT_LAND short of the face. That leaves a short
    round-crown collar for the O-ring - 3 mm of unsupported 14.5 crown, which
    is a bridge ASA spans without thinking about it, and which the tap trues
    on its way in anyway."""
    _b = (Pos(x, cy((y0 + y1)/2), BORE_Z) * Rot(90, 0, 0)
          * Cylinder(dia/2, abs(y1 - y0) + 2, align=(Align.CENTER,)*3))
    if teardrop:
        # y0 is the OUTER (face) end; hold the apex back from it
        _td0 = y0 + SEAT_LAND if y0 < y1 else y0 - SEAT_LAND
        _b += (Pos(x, cy((_td0 + y1)/2), BORE_Z + dia*0.25) * Rot(90, 0, 0) * Rot(0, 0, 45)
               * Box(dia*0.707, dia*0.707, abs(y1 - _td0) + 2, align=(Align.CENTER,)*3))
    return _b

# cable gland: tapped straight through into the Pi bay
c -= _ybore(GL_X, GL_TAP, BLK_Y0, BLK_Y1)
# Gore vent: tapped, into the driver bay
c -= _ybore(VENT_X, VENT_TAP, BLK_Y0, BLK_Y1)
# SMA coax entry: a short threaded section, then a counterbore so the inner nut
# lands in open bay rather than being buried in the block
# the coax entry bores the OTHER way, out through the TOP block, so a whip
# screwed straight onto it stands up
c -= _ybore(SMA_X, SMA_D, BLK_TY0, BLK_TY1)
_v0 = c.volume
_sma_cr = SMA_NUT_AF/2/math.cos(math.pi/6)
# cut from the block's INNER face going OUTWARD into the block. Rot(-90) sent
# it the other way, into the bay, where the whole point was not to be.
c -= (Pos(SMA_X, cy(BLK_TY1), BORE_Z) * Rot(90, 0, 0)
      * extrude(RegularPolygon(_sma_cr, 6), SMA_NUT_DEEP))
_want = (math.sqrt(3)/2*SMA_NUT_AF**2 - math.pi*(SMA_D/2)**2) * SMA_NUT_DEEP
assert abs((_v0 - c.volume) - _want) < 0.3*_want, (
    f"the SMA nut pocket removed {_v0 - c.volume:.0f} mm3, expected {_want:.0f} "
    f"- it is cutting into the bay instead of into the block")
assert SMA_NUT_DEEP < abs(BLK_TY0 - BLK_TY1) - 6.0, (
    f"a {SMA_NUT_DEEP} mm nut pocket leaves too little thread in a "
    f"{abs(BLK_TY0 - BLK_TY1):.1f} mm block")

# THE SEATING FACES MUST BE FLAT ANNULI. Probed, not reasoned about: take a
# thin slab at the block's outer face, intersect it with the ring the flange's
# O-ring lands on, and demand the ring is solid all the way round. A notch
# anywhere in it - from a teardrop, a chamfer, a neighbour's counterbore - is a
# leak path straight up the bore and into the box.
for _n, _x, _d, _fl, _need in [("cable gland", GL_X, GL_TAP, GL_FLANGE, 0),
                               ("Gore vent", VENT_X, VENT_TAP, VENT_FLANGE, 0),
                               ("SMA coax entry", SMA_X, SMA_D, 12.7, 0)]:
    _slab = Pos(_x, cy(BLK_Y0 + 0.25), BORE_Z) * Rot(90, 0, 0) * Cylinder(
        _fl/2, 0.5, align=(Align.CENTER,)*3)
    _ring = _slab - (Pos(_x, cy(BLK_Y0 + 0.25), BORE_Z) * Rot(90, 0, 0)
                     * Cylinder(_d/2 + 0.2, 1.0, align=(Align.CENTER,)*3))
    _got = c & _ring
    _have = 0.0 if _got is None else _got.volume
    assert _have > 0.98 * _ring.volume, (
        f"{_n}'s O-ring land is {100*(1 - _have/_ring.volume):.0f}% cut away at "
        f"the seating face - it has nothing to seal against")

# -- the GPS chimney -------------------------------------------------------
if GPS_INTERNAL:
    _gy_top = BLK_TY0 - GPS_WIN_T                  # under the radome
    _gy_bot = BLK_TY1 - WALL - 2.0                 # through into the Pi bay
    _pl, _pw = GPS_L + 2*GPS_FIT, GPS_W + 2*GPS_FIT
    _v0 = c.volume
    c -= Pos(GPS_X, cy((_gy_top + _gy_bot)/2), GPS_Z) * Box(
        _pl, abs(_gy_top - _gy_bot), _pw, align=(Align.CENTER,)*3)
    assert c.volume < _v0 - 1000, (
        "the GPS chimney removed almost nothing - it is not landing in the block")
    # the shelf the module sits on, so the patch ends up square under the
    # window with a known air gap rather than wherever it was pushed to
    for _sx in (-1, 1):
        c += Pos(GPS_X + _sx*(_pl/2 - GPS_SHELF/2),
                 cy(_gy_top - GPS_T - 0.5 - 1.0), GPS_Z) * Box(
            GPS_SHELF, 2.0, _pw, align=(Align.CENTER,)*3)
    # the lead goes down the chimney into the bay; it is already open, so all
    # this needs is that the chimney actually reaches the bay
    assert _gy_bot < PI_BUMP_W/2 - WALL + 0.01, (
        f"the GPS chimney stops at y={_gy_bot:.1f} and the bay's void starts at "
        f"{PI_BUMP_W/2 - WALL:.1f} - the module could never be fitted or reached")
    # and that a real shield can be built in it: walls thick enough to take
    # foil and still hold, and a window thin enough to see through at L1
    _wall_x = (BLK_X1 - BLK_X0)/2 - _pl/2
    assert _wall_x > 4.0, (
        f"only {_wall_x:.1f} mm of block either side of the chimney - not enough "
        f"to line with foil and still have a wall")
    assert GPS_WIN_T <= 1.6, (
        f"a {GPS_WIN_T} mm ASA radome is thicker than it needs to be; every "
        f"millimetre is loss at 1575 MHz")
    # the whole point: distance from the transmitting whip
    _sep = abs(GPS_X - SMA_X)
    assert _sep > 150.0, (
        f"the GPS patch is {_sep:.0f} mm from the whip's bulkhead - a 400-470 MHz "
        f"transmitter that close will desense it on every transmission")
    print(f"       GPS: {GPS_L:.0f} sq patch in a shielded chimney at x={GPS_X:.0f}, "
          f"under a {GPS_WIN_T} mm ASA radome, {_sep:.0f} mm from the whip")

# ---- and the checks that would have caught the original fault -------------
# Every one of these compares a fitting to something OUTSIDE its own family -
# the bay void, the board in it, the block's own faces, the seal, the fastener
# ring. That is the class of check the old placement had none of.
_VOID_X0, _VOID_X1 = abs(PI_BUMP_CX) - PI_BUMP_L/2 + WALL, abs(PI_BUMP_CX) + PI_BUMP_L/2 - WALL
# (name, x, bore, flange O, mm of clear bay it needs INSIDE). The last number
# is per-fitting because the three want completely different things of the
# space they open into: the gland has to turn a 10 mm cable, the SMA needs its
# nut and a coax bend, and the vent needs nothing at all - it only has to
# breathe. One shared number failed the vent for a reason that does not apply
# to it.
# (name, x, bore, flange O, mm of clear bay it needs inside, which block face)
_FITTINGS = [("cable gland",    GL_X,   GL_TAP,   GL_FLANGE,   12.0, BLK_Y0),
             ("Gore vent",      VENT_X, VENT_TAP, VENT_FLANGE,  2.0, BLK_Y0),
             ("SMA coax entry", SMA_X,  SMA_NUT_AF, 15.0,        3.0, BLK_TY0)]
for _n, _x, _d, _fl, _need, _face in _FITTINGS:
    assert BLK_X0 + BLK_CHAM < abs(_x) - _fl/2 and abs(_x) + _fl/2 < BLK_X1 - BLK_CHAM, (
        f"{_n} flange O{_fl} at x={_x} hangs off its block (x {BLK_X0}..{BLK_X1})")
    assert _fl < PI_BUMP_H - 2.0, (
        f"{_n} flange O{_fl} does not fit a {PI_BUMP_H:.0f} mm tall seat")
    assert abs(BORE_Z) + _d/2 + 3.0 < PI_BUMP_H, (
        f"{_n} bore leaves under 3 mm of block below it")
    assert _VOID_X0 < abs(_x) - _d/2 and abs(_x) + _d/2 < _VOID_X1, (
        f"{_n} bore at x={_x} does not open into the bay void "
        f"(x {_VOID_X0:.1f}..{_VOID_X1:.1f}) - it would break out through a wall")
# ...and the board each one opens toward has to be far enough away in Y to
# dress a cable into. The bore stops at the bay's end wall, so it never passes
# OVER a board - what matters is the gap between where it emerges and where the
# board starts. Nothing in this file had ever compared a cover feature to a
# board envelope at all.
# The RTL-SDR belongs on this list too. It is a 68 x 27 x 12 dongle with no
# mounting holes, and it had no home in the model at all - a BOM line and
# nothing else - so nothing ever checked whether the bay still had room for it.
# It STANDS ON EDGE in the +x bay beside the driver board, strapped to the two
# tie anchors on that bay's floor, directly under the SMA it feeds.
SDR_L, SDR_W, SDR_T = 68.0, 27.0, 12.0
SDR_X = DRV_CX + 30.0
_void_out = abs(DRV_CX) + PI_BUMP_L/2 - WALL
assert SDR_X + SDR_T/2 < _void_out - 1.0, (
    f"the SDR reaches x={SDR_X + SDR_T/2:.1f} and the bay wall is at "
    f"{_void_out:.1f}")
assert SDR_X - SDR_T/2 > abs(DRV_BOARD_CX) + 55.25/2 + 1.0, (
    f"the SDR overlaps the driver board it stands beside")
assert SDR_W < PI_BUMP_H - WALL - 1.0, (
    f"a {SDR_W:.0f} mm dongle on edge does not fit a {PI_BUMP_H - WALL:.1f} mm bay")
_BOARDS = [("Pi 4", PI_BOARD_CX, 56.0, 85.0), ("driver board", DRV_BOARD_CX, 55.25, 113.25),
           ("RTL-SDR", SDR_X, SDR_T, SDR_L)]
for _n, _x, _d, _fl, _need, _face in _FITTINGS:
    for _bn, _bcx, _bl, _bw in _BOARDS:
        if (_x < 0) != (_bcx < 0):
            continue
        _gap = abs(_face) - 13.5 - _bw/2
        assert _gap > _need, (
            f"{_n} emerges {_gap:.1f} mm from the {_bn}'s edge and needs "
            f"{_need:.0f}")
        assert abs(abs(_x) - abs(_bcx)) < _bl/2 + 20.0, (
            f"{_n} at x={_x} is nowhere near the {_bn} it is supposed to serve")

# clear of each other
for _i in range(len(_FITTINGS)):
    for _j in range(_i + 1, len(_FITTINGS)):
        _a, _b = _FITTINGS[_i], _FITTINGS[_j]
        if (_a[1] < 0) != (_b[1] < 0) or _a[5] != _b[5]:
            continue                        # different blocks
        assert abs(_a[1] - _b[1]) > (_a[3] + _b[3])/2 + 2.0, (
            f"{_a[0]} and {_b[0]} flanges overlap on the same block")
# clear of the seal and of the brim screws
for _by0, _by1 in BLOCKS:
    assert abs(_by0) < OUT_H/2 - GASKET_OUT - GASKET_W, (
        f"a fitting block reaches y={_by0}, into the cord's sealing land")
for _bx, _by in BOLTS:
    _dx = max(BLK_X0 - abs(_bx), abs(_bx) - BLK_X1, 0.0)
    _dy = max(abs(_by) - abs(BLK_Y0), abs(BLK_Y1) - abs(_by), 0.0)
    assert math.hypot(_dx, _dy) > 4.5 + 2.0, (
        f"brim screw at ({_bx:.0f},{_by:.0f}) is inside the fitting block - no "
        f"driver reaches it")

# -- fan shroud fixings: BLIND pilots in the outer face ---------------------
# The shroud carries four M3 clearance holes at HS_HOLES. Blind pilots, not
# through-holes: a screw through this plate is a hole in the pressure boundary
# the cord seals, and a fan shroud is not worth one. They stop
# SHROUD_PILOT_FLOOR short of the inner face. Thread-forming M3 into ASA is
# adequate for a ~130 g shroud; the upgrade is a 316 M3 threaded insert in the
# same hole, which is why the pilot is on the insert's OD rather than the
# screw's.
SHROUD_PILOT_D, SHROUD_PILOT_DEEP = 2.6, 4.5
SHROUD_PILOT_FLOOR = COVER_T - SHROUD_PILOT_DEEP
assert SHROUD_PILOT_FLOOR >= 1.5, (
    f"shroud pilot leaves {SHROUD_PILOT_FLOOR:.1f} mm of plate - too close to "
    f"breaking through into the sealed cavity")
M3_HEAD_R = 3.2                     # M3 pan head + bonded washer, worst case
# Which brim screw heads the shroud has to be relieved for. Reported, not
# forbidden - and asserted in heatsink_shroud.py, which cuts a pocket for each.
_UNDER = [(bx, by) for bx, by in BOLTS
          if abs(bx) < SHROUD_W/2 + M3_HEAD_R and abs(by) < SHROUD_H/2 + M3_HEAD_R]
print(f"       shroud lands over {len(_UNDER)} brim screw heads: "
      + ", ".join(f"({x:.0f},{y:.0f})" for x, y in _UNDER)
      + " - relieved in the shroud")
# The pilots are blind, so they cannot leak, but they are drilled from the
# WEATHER face and leave only SHROUD_PILOT_FLOOR of plate. Under the gasket land
# that floor is the sealing face itself, and a thread-forming screw swells it.
# A PILOT BOSS AT EACH CORNER, and it is not decoration. 4.5 mm is all the
# thread a 6 mm plate can give without breaking through, and the screw has to
# cross 43.6 mm of shroud before it gets there - so the length that reaches is
# 45 and the length that stops in time is 40, and neither exists. The boss adds
# SHROUD_PILOT_BOSS of thread OUTSIDE the pressure boundary and shortens the
# shroud's own boss by the same amount, which turns one impossible screw into a
# stock M3 x 40 with 6.4 mm of engagement.
SHROUD_PILOT_BOSS = 6.0
SHROUD_PILOT_TOTAL = SHROUD_PILOT_BOSS + SHROUD_PILOT_DEEP
_gask_in = OUT_H/2 - GASKET_OUT - GASKET_W
for _hx, _hy in HS_HOLES:
    assert abs(_hy) + SHROUD_PILOT_D/2 + 1.5 < _gask_in, (
        f"shroud pilot at y={_hy:.1f} is within 1.5 mm of the gasket land at "
        f"{_gask_in:.1f} - forming a thread there bulges the sealing face")
    c += Pos(_hx, cy(_hy), -SHROUD_PILOT_BOSS) * Cylinder(
        6.0, SHROUD_PILOT_BOSS, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= Pos(_hx, cy(_hy), -SHROUD_PILOT_BOSS - 1.0) * Cylinder(
        SHROUD_PILOT_D/2, SHROUD_PILOT_TOTAL + 1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN))

# -- fan wire pass-through, UNDER THE SHROUD -------------------------------
# The two fans live outside the sealed box and are driven from inside it, so
# their leads have to cross the boundary somewhere. Until now they crossed it
# through a grommet in the 6 mm ALLOY PLATE - and that plate was deleted when
# the heatsink started closing the cover itself. The route went with it, and
# nothing complained, because a wire is not geometry: the shroud still cut a
# O7 hole for it at x=52 on a part only 96 wide, i.e. in mid air.
#
# It is a hole in the pressure boundary and there is no way round that - the
# alternative is running 12 V and PWM out through the cable gland and back up
# the outside of the cover, which trades one sealed penetration for two
# unsealed metres of exposed lead. So: ONE hole, in the most sheltered square
# centimetre on the part, POTTED.
#
# WHERE. Inside the shroud's footprint (|x|<48, |y|<80) but clear of the
# heatsink seat (|x|<37.3, |y|<75.3) and clear of both fan bodies (|x|<40),
# which leaves the 10.7 mm strip at |x| 37.3..48. The collar stands on the
# INNER face, where it gives the potting compound a cup to sit in instead of a
# flat face to run off, and the leads are dressed down the inside of the bay.
# Only 10.7 mm of strip, so the potting dam is a RECTANGLE, not a collar: a
# round boss big enough to hold compound (O11) does not fit between the seat and
# the shroud wall, and chasing the last 0.7 mm with margins is how a feature ends
# up 0.3 mm from something it must not touch.
# X is DERIVED: the mid-line of the strip between the heatsink seat and the
# shroud wall. Typed, it was 0.1 mm out and the assert caught it.
WIRE_D, WIRE_Y = 6.0, 20.0
WIRE_X = (HS_L/2 + SHROUD_W/2) / 2
WIRE_DAM_X, WIRE_DAM_Y, WIRE_DAM_H = 9.0, 16.0, 3.0
assert abs(WIRE_X) - WIRE_DAM_X/2 > HS_L/2 + 0.5, (
    f"wire dam reaches x={abs(WIRE_X) - WIRE_DAM_X/2:.1f}, into the heatsink "
    f"seat at {HS_L/2:.1f}")
assert abs(WIRE_X) + WIRE_DAM_X/2 < SHROUD_W/2 - 0.5, (
    f"wire pass at x={WIRE_X} is not under the shroud, so it is not sheltered")
for _tx in TIE_TOP:
    assert abs(_tx - WIRE_X) > TIE_L/2 + WIRE_DAM_X/2 or abs(TIE_Y - WIRE_Y) > (TIE_W + WIRE_DAM_Y)/2, (
        f"wire dam collides with the tie-wrap anchor at ({_tx:.0f},{TIE_Y:.0f})")
c += Pos(WIRE_X, cy(WIRE_Y), COVER_T - 0.3) * Box(
        WIRE_DAM_X, WIRE_DAM_Y, WIRE_DAM_H + 0.3,
        align=(Align.CENTER, Align.CENTER, Align.MIN))
c -= Pos(WIRE_X, cy(WIRE_Y), -1.0) * Cylinder(
        WIRE_D/2, COVER_T + WIRE_DAM_H + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
# countersink on the WEATHER side so the potting has a fillet to key into
c -= Pos(WIRE_X, cy(WIRE_Y)) * Cone(
        WIRE_D/2 + 1.5, WIRE_D/2, 1.5, align=(Align.CENTER, Align.CENTER, Align.MIN))

# -- tilt trunnions, INTEGRAL to the cover ---------------------------------
# Grown from the cover, not bolted to it. A separate bracket would need screws
# through this plate, and every one of them is a hole in the pressure boundary
# the 3 mm cord is there to seal - so the plate simply grows the feature instead.
# No fasteners, no penetrations, nothing to back out.
#
# It sits INSIDE the bezel width. That costs mechanically: the axis ends up
# TRUN_STAND behind the cover's outer face and therefore well behind the CG at
# z=12.4, where a side-wall pivot sat 1.4 mm off it. That is why the interface
# is a 316 SERRATED washer pair rather than a plain friction shim - teeth hold
# mechanically, so the margin stops depending on the lever arm and on an
# unmeasured friction coefficient.
#
# The room for these only exists because the fan shroud came in from 138 to 132
# and the aperture moved to AP_CX - before that the shroud ran to x=149 and the
# outer strip was 18 mm against the 26 this needs.
# HS_PROUD, not HS_H. The shroud used to allow the heatsink's full 10 mm, but
# the base is now sunk flush into the cover's inner face and only the fins clear
# the plate - HS_H - (COVER_T - HS_BASE) of them. Allowing the full height cost
# 6 mm of depth for fins that are inside the box.
# (SHROUD_ENVELOPE, TRUN_X/WEB_T/STAND/R/LAND and TRUN_BORE are declared up in
#  the packaging section - the bumps' depth is derived from them.)
# 15 -> 18. The bail arm's eye is a disc centred on the axis and it reaches its
# own radius IN FRONT of the axis too, so the stand has to be bigger than the
# eye or the arm is inside the cover. At 15 against an r17 eye it was, by 2 mm
# a side - and both parts passed every check they had, because neither was ever
# intersected with the other.
assert TRUN_X + TRUN_LAND + 8.0 <= OUT_W/2, (
    f"trunnion plus an 8 mm arm reaches {TRUN_X + TRUN_LAND + 8.0:.1f}, past the "
    f"bezel edge at {OUT_W/2:.1f}")
# Declared here and ASSERTED in heatsink_shroud.py, because this file runs
# first and cannot read the shroud it has to clear. A retyped 132 was already
# stale once when the fixing pads moved outboard.
_sh_edge = AP_CX + SHROUD_ENVELOPE/2
assert TRUN_X - TRUN_WEB_T > _sh_edge, (
    f"trunnion web at {TRUN_X - TRUN_WEB_T:.1f} clashes with the fan shroud, "
    f"which reaches {_sh_edge:.1f}")
for sx in (-1, 1):
    _tx = sx * (TRUN_X - TRUN_WEB_T/2)
    _ty = cy(TILT_Y)
    # The web has to reach PAST the axis, not just to it. The land is a r13 disc
    # centred on the axis, so it spans TRUN_R either side of it; a web that stops
    # at the axis leaves the lower half of the disc unsupported and the bore
    # breaks out into air. The volume check below is what caught that.
    c += Pos(_tx, _ty, -(TRUN_STAND + TRUN_R)) * Box(
        TRUN_WEB_T, 2*TRUN_R, TRUN_STAND + TRUN_R + COVER_T,
        align=(Align.CENTER, Align.CENTER, Align.MIN))
    # GUSSETS at the root, fore and aft of the web. The web is 8 mm of ASA in
    # cross-layer bending at the plate, on a dash that sees 60 C; the review put
    # the interlayer safety factor near 1.5 there. A 10 x 10 triangular fillet
    # either side triples the root section for a few grams and prints as a
    # 45 deg overhang, which needs nothing.
    for _gs in (-1, 1):
        # a right triangle in the y-z plane, legs on the web face and the plate,
        # overlapping both by 0.3 so it fuses instead of touching along a line -
        # the first cut of this was a rotated box tangent to both, and it came
        # out as four loose 400 mm3 prisms
        _yf = _ty + _gs*TRUN_R
        _tri = Polygon((_yf - _gs*0.3, 0.3), (_yf + _gs*TRUN_GUSSET, 0.3),
                       (_yf - _gs*0.3, -TRUN_GUSSET), align=None)
        # The gusset has to land ON the web, and the first two attempts put it
        # 8 mm either side of it - outboard, where it overhung the brim screw at
        # (-164,-2) and stood in its driver's path. Built from the web's own
        # centre and asserted, rather than offset by a sign nobody can predict.
        _g = extrude(Plane.YZ * _tri, amount=TRUN_WEB_T, both=True)
        _g = Pos(_tx, 0, 0) * scale(_g, (0.5, 1, 1))
        _gb = _g.bounding_box()
        assert abs(_gb.min.X - (_tx - TRUN_WEB_T/2)) < 1e-6, (
            f"gusset sits at x {_gb.min.X:.1f}..{_gb.max.X:.1f}, not on the web at "
            f"{_tx - TRUN_WEB_T/2:.1f}..{_tx + TRUN_WEB_T/2:.1f}")
        c += _g
    c += (Pos(sx*TRUN_X, _ty, -TRUN_STAND) * Rot(0, 90*sx, 0)
          * Cylinder(TRUN_R, TRUN_LAND, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    # ---- the pivot bolt's path, and the nut at the end of it -------------
    # It used to be a O7 blind pocket 9 deep, meant for a heat-set insert - an
    # insert that does not exist at that size, in a hole that was a stagnant
    # salt pocket behind it. It is a THROUGH BORE now, from the land's face all
    # the way to the web's inboard face, with a captive M5 316 NYLOC in a hex
    # pocket at the far end. The bolt pulls steel against steel; the ASA is only
    # in compression between them, which is the one thing it is good at.
    _v0 = c.volume
    _thru = TRUN_LAND + TRUN_WEB_T
    c -= (Pos(sx*(TRUN_X + TRUN_LAND), _ty, -TRUN_STAND) * Rot(0, -90*sx, 0)
          * Cylinder(TRUN_BORE/2, _thru, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    # TEARDROP. The cover prints BUMPS DOWN, so the bed is at -z and "up" in the
    # print is increasing z: a horizontal bore's crown sags, and a 45 deg apex
    # ABOVE the axis bridges it. The apex pointed at the bed once, which is not
    # a teardrop, it is a drip.
    c -= (Pos(sx*(TRUN_X + TRUN_LAND), _ty, -TRUN_STAND + TRUN_BORE*0.25)
          * Rot(0, -90*sx, 0) * Rot(0, 0, 45)
          * Box(TRUN_BORE*0.707, TRUN_BORE*0.707, _thru,
                align=(Align.CENTER, Align.CENTER, Align.MIN)))
    _want = math.pi*(TRUN_BORE/2)**2 * _thru
    _got = _v0 - c.volume
    assert _want*0.95 < _got < _want*1.45, (
        f"trunnion bore removed {_got:.0f} mm3, expected {_want:.0f} plus a "
        f"teardrop - it is cutting outward into air instead of through the boss")
    # the hex pocket, cut from the web's INBOARD face so the nut drops in from
    # the middle of the back where your fingers are, not from inside the box
    _v0 = c.volume
    _nut_cr = TRUN_NUT_AF/2/math.cos(math.pi/6)
    c -= (Pos(sx*(TRUN_X - TRUN_WEB_T), _ty, -TRUN_STAND) * Rot(0, 90*sx, 0)
          * extrude(RegularPolygon(_nut_cr, 6), TRUN_NUT_DEEP))
    _want = (math.sqrt(3)/2*TRUN_NUT_AF**2 - math.pi*(TRUN_BORE/2)**2) * TRUN_NUT_DEEP
    _got = _v0 - c.volume
    assert abs(_got - _want) < 0.25*_want, (
        f"the nyloc pocket removed {_got:.0f} mm3, expected {_want:.0f} - it is "
        f"cutting outboard into air, which leaves a joint with no nut in it")
    assert TRUN_NUT_DEEP < TRUN_WEB_T - 3.0, (
        f"a {TRUN_NUT_DEEP} mm nut pocket in a {TRUN_WEB_T} mm web leaves "
        f"{TRUN_WEB_T - TRUN_NUT_DEEP:.1f} mm of ASA for the bolt to pull on")

# -- heatsink aperture and seat --------------------------------------------
# No internal boss: the shell interior is DEPTH-FACE_T and the panel takes MOD_D
# of it, so anything protruding inward fouls the panel.
#
# THE HEATSINK SEATS FLUSH ON THE INSIDE. Its base drops into a pocket in the
# INNER face, so the base is level with the cavity wall and the fins pass through
# the aperture to stand proud outside. Two things come from that: the glue line is a flat captured
# joint instead of a bead squeezed between two surfaces that can rock apart, and
# the pocket walls INDEX the heatsink while the adhesive cures - no jig needed
# for this part any more.
HS_BASE = 3.0                               # base thickness below the fins
# 0.3 -> 0.6 per side. ASA shrinks about 0.5%, and over the 150 mm axis that is
# 0.75 mm - more than the whole 0.6 of clearance the old number allowed. The
# pocket would have printed SMALLER than the part it locates. 0.6 a side lands
# the sink with a few tenths to spare after shrinkage; the adhesive fills the
# rest, which is what a bonded joint wants anyway.
HS_SEAT_FIT = 0.6
assert HS_BASE < COVER_T - 2.0, (
    f"a {HS_BASE} seat in a {COVER_T} cover leaves under 2 mm of plate")
# z=0 is the OUTER face here and COVER_T the inner one - bumps grow -z, standoffs
# +z. The seat is cut from the INNER face down, so the base lands flush with the
# cavity wall. That leaves COVER_T - HS_BASE of plate for the fins to pass
# through, and they stand HS_H - COVER_T + HS_BASE proud on the outside.
c -= Pos(AP_CX, 0, COVER_T - HS_BASE) * Box(
    HS_L + 2*HS_SEAT_FIT, HS_W + 2*HS_SEAT_FIT, HS_BASE + 1,
    align=(Align.CENTER, Align.CENTER, Align.MIN))
# Fin length is HS_H - HS_BASE, and COVER_T - HS_BASE of that is buried in the
# plate, so what stands proud is simply HS_H - COVER_T.
HS_PROUD = HS_H - COVER_T              # fin standing clear of the rear face
assert abs(PI_BUMP_CX) == abs(DRV_CX) and PI_BUMP_L == DRV_BUMP_L, (
    "the two bumps are meant to mirror - they have drifted apart again")
assert abs(PI_BUMP_CX) - PI_BUMP_L/2 > SHROUD_ENVELOPE/2, (
    f"bump inner edge {abs(PI_BUMP_CX) - PI_BUMP_L/2:.1f} is inside the shroud "
    f"envelope {SHROUD_ENVELOPE/2:.1f} - they would occupy the same space")
assert abs(PI_BUMP_CX) + PI_BUMP_L/2 < TRUN_X - TRUN_WEB_T, (
    f"bump reaches {abs(PI_BUMP_CX) + PI_BUMP_L/2:.1f}, into the trunnion web")
assert HS_PROUD > 2.0, (
    f"only {HS_PROUD:.1f} mm of fin clears the plate - the seat has swallowed it")
c -= Pos(AP_CX, 0) * Box(AP_L, AP_W, 3*COVER_T, align=(Align.CENTER,)*3)
# THE EIGHT M3 HOLES ROUND THE APERTURE ARE GONE. They clamped the 114 mm alloy
# heat plate to the cover's outer face. There is no alloy plate any more - the
# heatsink's own base closes the aperture and is BONDED into a recess - so every
# one of those eight was a through-hole in the weather face into the sealed
# cavity, held shut by nothing.
#
# Two of them were worse than redundant. At AP_PITCH 30 the pair at x = +/-30
# had their O3.4 bores spanning 28.3..31.7 while the aperture edge is at 29, so
# they cut a notch out of the 8 mm sealing land the heatsink is glued to - the
# one surface the thermal joint depends on. The pair at (0, +/-30) was cut
# entirely inside the aperture, i.e. in air, which is why the ring looked
# harmless in every render.

# -- the cover's half of the cord groove -----------------------------------
# Same path as the shell's, on the cover's INNER face, and only GD_COVER deep:
# it locates the cord while the joint is closed, it does not do the squeezing.
# Cutting it here also means the cord cannot be pinched outside its seat by a
# lid that went down a millimetre out of line.
_cg_out = RectangleRounded(OUT_W - 2*GASKET_OUT, OUT_H - 2*GASKET_OUT,
                           max(R_OUT - GASKET_OUT, 1.0))
_cg_in = RectangleRounded(OUT_W - 2*(GASKET_OUT + GASKET_W),
                          OUT_H - 2*(GASKET_OUT + GASKET_W),
                          max(R_OUT - GASKET_OUT - GASKET_W, 1.0))
_v0 = c.volume
c -= extrude(Plane.XY.offset(COVER_T - GASKET_D_COVER) * (_cg_out - _cg_in),
             amount=GASKET_D_COVER + 1)
assert c.volume < _v0 - 500, (
    f"the cover's groove removed only {_v0 - c.volume:.0f} mm3 - it is not "
    f"landing on the sealing face")

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
        assert abs(_tx) - TIE_L/2 > HS_L/2 + HS_SEAT_FIT + 1.0, (
            f"tie anchor at x={_tx:.0f} reaches {abs(_tx) - TIE_L/2:.1f}, inside the "
            f"heatsink seat at {HS_L/2 + HS_SEAT_FIT:.1f} - the sink hits it going in")
        assert abs(_tx) + TIE_L/2 < abs(PI_BUMP_CX) - PI_BUMP_L/2 - 1.0, (
            f"tie anchor at x={_tx:.0f} runs into the bay wall")
for _px_, _py_ in DSP_POSTS:
    _seal_ok(_px_, _py_, DSP_POST_D/2, None, "display post")
for _by0, _by1 in BLOCKS:
    for _bs in (-1, 1):
        _seal_ok(_bs*(BLK_X0 + BLK_X1)/2, (_by0 + _by1)/2,
                 (BLK_X1 - BLK_X0)/2, abs(_by1 - _by0)/2, "fitting block")
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
           "GASKET_T":GASKET_T,"GASKET_C":GASKET_C,"GASKET_D_COVER":GASKET_D_COVER,
           "CORD_D":CORD_D,"GASKET_D":GASKET_D,
           "N_BRIM_BOLTS":len(BOLTS),"BOLT_PITCH":BOLT_PITCH,"AP_SEAL":AP_SEAL,"BRIM_BOLT":M3_PILOT,"BOLTS":[[round(x,3),round(y,3)] for x,y in BOLTS],
           "M3_HEAD_R":M3_HEAD_R,
           "AP":AP,"AP_L":AP_L,"AP_W":AP_W,"AP_CX":AP_CX,"AP_PITCH":AP_PITCH,"HS_PLATE":HS_PLATE,
           "HS_L":HS_L,"HS_W":HS_W,"HS_H":HS_H,"HS_PROUD":HS_PROUD,"HS_CY":HS_CY,"HS_N":HS_N,
           "HS_SPAN":HS_SPAN,"HS_HOLES":HS_HOLES,"HS_PLATE_X":HS_PLATE_X,
           "HS_PLATE_Y":HS_PLATE_Y,"SHROUD_H":SHROUD_H,
           "HS_FIT":HS_FIT,"SHROUD_PILOT_D":SHROUD_PILOT_D,
           "SHROUD_PILOT_DEEP":SHROUD_PILOT_DEEP,"SHROUD_PILOT_BOSS":SHROUD_PILOT_BOSS,
           "SHROUD_PILOT_TOTAL":SHROUD_PILOT_TOTAL,
           "WIRE_D":WIRE_D,"WIRE_X":WIRE_X,"WIRE_Y":WIRE_Y,
           "FIN_GAP":FIN_GAP,"GASKET_OUT":GASKET_OUT,
           "APER_W":APER_W,"APER_H":APER_H,"APER_X":APER_X,"APER_Y":APER_Y,
           "BTN_X":BTN_X,"ENC_X":ENC_X,"ROW_CY":ROW_CY,"BTN_D":BTN_D,"ENC_D":ENC_D,
           "GPS_X":GPS_X,"GPS_Z":GPS_Z,"GPS_L":GPS_L,"GPS_W":GPS_W,"GPS_T":GPS_T,"GPS_WIN_T":GPS_WIN_T,
           "SMA_X":SMA_X,"SMA_D":SMA_D,"SMA_NUT_AF":SMA_NUT_AF,"SMA_NUT_DEEP":SMA_NUT_DEEP,"GL_X":GL_X,"GL_TAP":GL_TAP,
           "CABLE_D":CABLE_D,"SEAT_LAND":SEAT_LAND,
           "VENT_X":VENT_X,"VENT_TAP":VENT_TAP,"BORE_Z":BORE_Z,
           "BLK_X0":BLK_X0,"BLK_X1":BLK_X1,"BLK_Y0":BLK_Y0,"BLK_Y1":BLK_Y1,
           "BLK_TY0":BLK_TY0,"BLK_TY1":BLK_TY1,
           "PI_BUMP_H":PI_BUMP_H,"PI_BUMP_L":PI_BUMP_L,"PI_BUMP_W":PI_BUMP_W,
           "PI_BUMP_CX":PI_BUMP_CX,"DRV_CX":DRV_CX,"DRV_BOARD_CX":DRV_BOARD_CX,"SDR_X":SDR_X,"SDR_L":SDR_L,"SDR_W":SDR_W,"SDR_T":SDR_T,"PI_STANDOFF_H":PI_STANDOFF_H,
           "PI_BOARD_CX":PI_BOARD_CX,"PI_HOLES":PI_HOLES,"DRV_HOLES":DRV_HOLES,
           "PIV_X":PIV_X,"PIV_Y":PIV_Y,"PIV_Z":PIV_Z,
           # mating dimensions - the visor and the bracket read these rather
           # than keeping their own copies, which is how rev B ended up with
           # visor teeth at r5.0-9.5 against shell teeth at r4.5-8.2.
           "FRIC_R0":FRIC_R0,"FRIC_R1":FRIC_R1,"FRIC_SHIM":FRIC_SHIM,
           "FRIC_T":FRIC_T,"FRIC_CLAMP":FRIC_CLAMP,
           "TILT_Y":TILT_Y,"TRUN_X":TRUN_X,"TRUN_STAND":TRUN_STAND,
           "TRUN_R":TRUN_R,"TRUN_LAND":TRUN_LAND,"TRUN_WEB_T":TRUN_WEB_T,
           "TRUN_BORE":TRUN_BORE,"TRUN_NUT_AF":TRUN_NUT_AF,"TRUN_NUT_DEEP":TRUN_NUT_DEEP,"SHROUD_W":SHROUD_W,"SHROUD_ENVELOPE":SHROUD_ENVELOPE,
           "R_EAR":R_EAR,"UPS_T":UPS_T,"VIS_STOW_Z":VIS_STOW_Z,"PIV_BOLT":PIV_BOLT,
                      "DISP_CX":DISP_CX,"DISP_CY":DISP_CY,
           # --- published for cad/build_review.py -------------------------
           # The build page used to keep its own copy of every one of these and
           # went stale on all of them. It states no dimension it cannot read
           # from this file; anything it needs and cannot find here is a key
           # that belongs in this dict, not a number typed into the page.
           "FACE_T":FACE_T,"WALL":WALL,"R_OUT":R_OUT,"BED":BED,
           "INT_W":INT_W,"INT_H":INT_H,
           "PILOT_L":PILOT_L,"M3_CLEAR":M3_CLEAR,
           "BRIM_SCREW_L":COVER_T + PILOT_L - 1.0,
           "MOD_W":MOD_W,"MOD_H":MOD_H,"MOD_D":MOD_D,"CLR":CLR,"GLUE_T":GLUE_T,
           "ACT_W":ACT_W,"ACT_H":ACT_H,
           "BTN_PITCH":BTN_PITCH,"BTN_DOME":BTN_DOME,"KNOB_OD":KNOB_OD,
           "PI_BUMP_L":PI_BUMP_L,"PI_BUMP_W":PI_BUMP_W,
           "AP_SEAL":AP_SEAL,"HS_BASE":HS_BASE,
           "SENSORS":[{"name":_s[0],"x":_s[1],"y":_s[2],
                       "pitch_x":_s[3],"pitch_y":_s[4]} for _s in SENSORS],
           "N_SENSOR_SCREWS":4*len(SENSORS),"N_DRV_SCREWS":len(DRV_HOLES),
           "STANDOFF_H":STANDOFF_H,
           "DSP_POSTS":[[_p[0],_p[1]] for _p in DSP_POSTS],
           "N_DSP_POSTS":len(DSP_POSTS),"DSP_POST_H":DSP_POST_H,
           "DSP_CB_D":DSP_CB_D,
           "DSP_SCREW_L":(COVER_T - DSP_CB_DEEP) + DSP_POST_H + 5.0,
           "TIE_N":len(TIE_TOP) + len(TIE_BOT),"TIE_SLOT":TIE_SLOT,
           "VENT_D":VENT_D,
           "WIRE_DAM_X":WIRE_DAM_X,"WIRE_DAM_Y":WIRE_DAM_Y,
           "SHELL_CM3":f.volume/1000.0,"COVER_CM3":c.volume/1000.0},
          open("cad/out/housing.json","w"), indent=1)


# ==================================================== ASSEMBLY REALITY CHECK
# Not "do the solids look right" - can a person put this together, in order,
# with the parts touching what they are supposed to touch. Every number below
# is the assembled stack, measured from the front face at z=0.
_z_land   = FACE_T                        # panel sits on this
_z_panel  = FACE_T + GLUE_T + MOD_D       # ...and its back is here, on its glue
_z_brim   = DEPTH                         # foam sits on this
_z_cover  = DEPTH + GASKET_C              # cover inner face, foam compressed
_z_tip    = _z_cover - DSP_POST_H         # where a bearing post reaches to

# 1. the posts have to actually land on the panel - not short, not through it
assert abs(_z_tip - _z_panel) < 1e-9, (
    f"bearing posts reach z={_z_tip:.2f} but the panel's back is z={_z_panel:.2f}"
    f" - {'a ' + format(_z_tip - _z_panel, '.2f') + ' mm gap' if _z_tip > _z_panel else 'they press INTO it by ' + format(_z_panel - _z_tip, '.2f')}")

# 2. the cover, in its assembled place, must not foul the panel anywhere else
_cov_asm = Pos(0, 0, DEPTH + COVER_T + GASKET_C) * Rot(180, 0, 0) * c
_panel_solid = Pos(APER_X, APER_Y, FACE_T + GLUE_T) * Box(
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

# 3. WHAT THE HEATSINK PRESENTS TO EACH SIDE. Base flush in the seat, fins out
#    the back: the box's inside sees a FLAT PLATE, the weather side sees fins
#    under the shroud. So nothing protrudes into the 10.5 mm behind the panel -
#    which is what makes the display screws and the fins compatible at all - and
#    the internal air-to-metal path is a bare 74 x 150 face.
#
#    THAT FACE IS THE THERMAL BOTTLENECK and it is worth saying out loud rather
#    than burying: the fan, the fins and the shroud all work on the easy half of
#    the problem. Getting the watts OUT OF THE INTERNAL AIR and into this plate
#    is the hard half, and it is currently natural convection plus whatever the
#    Pi's own fan stirs. The cheap fix if it throttles is a second finned block
#    bonded to the INSIDE of this base - the offcut from trimming this one's
#    sealing land is very nearly the right part.
assert HS_BASE < COVER_T, "the heatsink base is thicker than the plate it sits in"
_plate_in_cm2 = HS_L * HS_W / 100.0
assert FIN_GAP > 6.0, (
    f"only {FIN_GAP:.1f} mm of air behind the panel - the fins' seat is eating "
    f"into the display")

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
print(f"       through the pressure boundary: {len(DSP_POSTS)} panel screws + 1 potted "
      f"fan-lead pass. The {len(BOLTS)} brim screws are outboard of the cord in blind "
      f"pilots - washered and Tef-Gelled to keep the crevice dry, not to seal")
print(f"THERM  panel back {_z_panel} -> cover inner {DEPTH + GASKET_C}: "
      f"{FIN_GAP:.1f} mm of dead air, all of it")
print(f"       heatsink {HS_L:.0f} x {HS_W:.0f} x {HS_H:.0f} bonded base-out in the "
      f"seat: base flush INSIDE, {HS_PROUD:.0f} mm of fin proud OUTSIDE under the shroud")
print(f"       inside face is a bare {_plate_in_cm2:.0f} cm2 plate - the internal "
      f"air-to-metal step is the bottleneck, not the fan")
print(f"       fittings: M16 gland x{GL_X:.0f} and M12 Gore vent x{VENT_X:.0f} face DOWN "
      f"through the bottom blocks; M8 SMA coax x{SMA_X:.0f} faces UP through the top of "
      f"the driver bump, so the whip stands at the sky")
print(f"       fan leads cross at ({WIRE_X:.1f}, {WIRE_Y:.0f}) - O{WIRE_D:.0f} potted, "
      f"under the shroud")
