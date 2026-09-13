"""
Heatsink Shroud  (rev F)  -- TWO 80 mm IP67 AXIAL FANS
=======================================================
Covers the heatsink fins that stand proud of the rear cover, carries both fans,
and keeps sun and salt spray off them.

THE DOCSTRING USED TO DESCRIBE A DIFFERENT PART, TWICE. Through revs B-D it
argued for a 5015 blower while the code built a 120 mm axial mount; rev E then
described that 120 mm axial with a O114 bore and an alloy heat plate, while the
code below had already been rebuilt for two 80 mm fans over a heatsink that
closes the cover itself. Both times the prose was quoted back in review as if
it were the design. It is written from the code now, and the code is checked
against cad/out/housing.json rather than against remembered numbers.

WHAT IT ACTUALLY IS. A 96 x 168 x 40 open-backed box. The outer face is one
louvred rectangle - no round bores, no divider between the fans - and the
louvres are the ONLY opening in the back. Two Coolerguys CG8025H12-IP67 fans
(80 x 80 x 25, 71.5 pitch) sit inside it on eight pads, clamping a 316 mesh
sheet against the inside of that face with their own screws. Air is drawn in
through the louvres, pushed down the fin channels, and leaves through side
louvres and a drain slot at the bottom.

DEPTH IS DERIVED FROM THE FAN: WALL + FAN_T + HS_H + PLENUM, where HS_H is only
the fin that stands PROUD of the cover (4 mm), not the heatsink's full 10. A
hardcoded depth was stale within a revision every time.

TWO THINGS IT HAS TO DODGE, both read from housing.json rather than retyped:
  * FOUR BRIM SCREW HEADS. The unit's fastener ring runs at |y| = 85.2 and this
    part reaches 84, so four O6 heads land under its rim. It sat on them and
    rocked. Each gets a relief pocket in the landing face.
  * THE CORD SEAL. The four corner bosses take M3s into BLIND pilots in the
    cover; their y inset is set so those pilots stay clear of the sealing land.

DRAINAGE. Anything that gets past the louvres lands on the cover INSIDE this
box. Assembled, this part is flown Rot(180,0,0), so its local +y is DOWN - and
until now every exhaust slot was on the local +/-x ends, leaving the low edge
solid and the shroud a tray. There is a full-width slot along the low edge now,
at the cover face, and it is the drain as much as it is exhaust.

WIRE ROUTE: the fans' leads leave through the gap at the drain slot and cross
into the housing through the POTTED O6 pass in the cover at (WIRE_X, WIRE_Y) -
which is under this shroud, sheltered, and the only penetration they make. The
O7 pass-through that used to be cut here was at x=52 on a part 96 wide: it was
cutting air, and it was aimed at a grommet in an alloy plate that no longer
exists.

Material : ASA (blue)   Orientation : OUTER FACE ON THE BED, walls up
Supports : none - the louvre awnings are 45 deg and the slots are vertical
"""
from build123d import *

import json
H = json.load(open("cad/out/housing.json"))
# No alloy plate any more - the heatsink closes the cover itself.
HS_L, HS_W = H["HS_L"], H["HS_W"]
# Only the part of the heatsink that STANDS PROUD of the cover needs covering.
# The base is sunk flush into the inner face, so the shroud allows the fins
# that actually clear the plate, not the part's full height.
HS_H = H["HS_PROUD"]
WALL, R_OUT = 3.0, 6.0
PLENUM = 2.0                      # air gap between fan face and fin tops
FILT_MESH = 0.6                   # 316 woven mesh sheet, ~20-40 mesh
FAN_BOSS = 3.0                    # pad the fan lands on, over the wall
# 5.0 -> 3.0. The boss only has to give an M4 enough ASA to form a thread in,
# and it gets WALL as well - 6 mm of engagement, 1.5 x D, which is plenty for a
# 120 g fan in a sheltered pocket. Every millimetre here is a millimetre of unit
# depth, and this one was set by habit rather than by the screw.
# Pads must reach the walls to fuse, but their HOLES must land well inside the
# 114 plate. So the pad is a gusset from the wall inward, hole at 48.
MOUNT_D = 3.4
HOLES = [tuple(h) for h in H["HS_HOLES"]]   # edge midpoints now, not corners

# TWO 80 mm fans, stacked, not one 120. The heatsink is 74 x 150 - narrow and
# tall - and a single 120 round was covering a square area over a strip, wasting
# most of its swept circle on shroud wall. Two 80s cover 160 of the 150 and the
# shroud comes in from 150 x 164 x 36 to 88 x 168 x 34.
#
# Coolerguys CG8025H12-IP67: 80 x 80 x 25, 71.5 hole pitch, 3500 rpm, dual ball
# bearing, -40..+70 C. Every IP-rated 80 is 25 thick - the slim 15 mm ones are
# not made sealed - so the rating costs 10 mm of depth here.
FAN_W, FAN_T, FAN_PITCH, FAN_BORE = 80.0, 25.0, 71.5, 74.0
FAN_N = 2
FAN_CY = [(-FAN_N/2 + 0.5 + i) * FAN_W for i in range(FAN_N)]   # stacked in y
FAN_PILOT = 3.6
OW = H["SHROUD_W"]
OH = H["SHROUD_H"]
# DEPTH, counted through the stack that is actually in it. It used to be
# WALL + FAN_T + HS_H + PLENUM and it left out the two things the fan physically
# sits on: the boss that holds it off the wall, and the mesh clamped under it.
# So the fans' backs stood 3 mm INSIDE the heatsink fins. The shroud bolted down
# and the renders looked right, because nothing compared the fan's z extent to
# the fins'.
OD = WALL + FAN_BOSS + FILT_MESH + FAN_T + PLENUM + HS_H
# There is no alloy plate any more - the heatsink closes the cover itself - so
# what the shroud has to cover is the HEATSINK, and what it bolts to is the
# cover. PLATE_X/Y are vestigial and the assert was still checking them.
assert OW >= HS_L + 8.0 and OH >= HS_W + 8.0, (
    f"shroud {OW:.0f}x{OH:.0f} does not cover the {HS_L:.0f}x{HS_W:.0f} heatsink")
assert FAN_BORE <= FAN_W, "intake bore is wider than the fan"
FAN_PILOT = 3.6                    # M4 thread-forming into ASA

s = extrude(Plane.XY * RectangleRounded(OW, OH, R_OUT), amount=OD)
s -= extrude(Plane.XY.offset(WALL) * RectangleRounded(OW - 2*WALL, OH - 2*WALL, R_OUT - WALL),
             amount=OD)

# ── two 80 mm axial fans on the outer face, blowing onto the fins ─────────
# Both sit INSIDE the shroud so nothing corrodible is exposed. Each draws
# through its own bore, guarded by cross spokes, and pushes down the fin
# channels to the louvres.
import math as _m
# NO ROUND BORES. The louvred rectangle IS the intake - the outer wall is cut
# away under it and the slats are what stands between the weather and the fans.
# Two O74 bores used to be cut here with the louvres laid over them, which made
# the fan holes visible through the slats and left a solid divider between them.
# What survives of the wall inside the opening is eight pads, one under each fan
# boss, so the fans still have something to bolt to; from outside they are
# behind the slats and read as nothing.
LOUV_RIM = 3.0
_LX, _LY = OW - 2*LOUV_RIM, OH - 2*LOUV_RIM
s -= Pos(0, 0, WALL/2) * Box(_LX, _LY, 3*WALL, align=(Align.CENTER,)*3)
# Two ribs, one along each fan's edge at x = +/-FAN_PITCH/2, rim to rim in the
# wall plane. They tie the boss pads together and to the rim - without them the
# four pads between the fans were islands and the shroud came out as five
# solids. They sit under the fan frames' edges and behind the slats, so they
# are not a divider between the fans; that would run along y=0, and there is
# nothing there.
for sx in (-1, 1):
    s += Pos(sx*FAN_PITCH/2, 0, 0) * Box(3.0, _LY + 2*LOUV_RIM, WALL,
                                        align=(Align.CENTER, Align.CENTER, Align.MIN))
for _fy in FAN_CY:
    for sx in (-1, 1):
        for sy in (-1, 1):
            _bx, _by = sx*FAN_PITCH/2, _fy + sy*FAN_PITCH/2
            s += Pos(_bx, _by, 0) * Cylinder(7.0, WALL, align=(Align.CENTER, Align.CENTER, Align.MIN))
            s += Pos(_bx, _by, WALL) * Cylinder(7.0, FAN_BOSS, align=(Align.CENTER, Align.CENTER, Align.MIN))
            s -= Pos(_bx, _by, WALL) * Cylinder(FAN_PILOT/2, FAN_BOSS + WALL - 0.5,
                                                align=(Align.CENTER, Align.CENTER, Align.MIN))

# ── intake louvres ───────────────────────────────────────────────────────
# Angled slats over each bore, standing LOUV_H proud of the outer face. Two jobs:
# keep direct sun off the fan hub (a black IP67 fan behind a bare bore sits in
# full sun on a dash) and keep spray out. Each slat tilts 45 deg so its OUTBOARD
# edge is its LOW edge - water that lands on it runs outward and drips off,
# never inward. At 45 deg a slat LOUV_H tall covers exactly LOUV_H of height in
# projection, so with the pitch set equal to LOUV_H there is no straight line of
# sight through the stack at all.
#
# ORIENTATION: this part is placed on the unit with Rot(180,0,0), which turns
# local +y into assembled DOWN. So "low edge outboard" means the slat's -z end
# sits at greater local y. Get that sign wrong and the louvres become gutters
# that funnel spray INTO the fan.
#
# They replace the cross spokes that used to guard each bore - louvres are a
# better finger guard than spokes were, and spokes on top of louvres would just
# be restriction. COST: LOUV_H of depth, and roughly half the open intake area.
LOUV_H = 6.0                       # proud of the outer face; also the pitch
LOUV_T = 2.0                       # slat thickness - 1.2 was a print-quality gamble
LOUV_ANG = 45.0
assert LOUV_H * _m.tan(_m.radians(LOUV_ANG)) >= LOUV_H - 0.01, (
    "slats no longer overlap in projection - spray has a straight path in")
# ONE louvred face across the whole shroud, not a collar per fan. The first
# pass put a round louvred collar over each bore with a solid divider between
# them; the owner wanted a single continuous face. The bores are still there in
# the wall behind it, one per fan - the louvres just do not know about them.
s += Pos(0, 0, -LOUV_H) * extrude(
    Plane.XY * RectangleRounded(OW, OH, R_OUT), amount=LOUV_H)
s -= Pos(0, 0, -LOUV_H - 1) * Box(_LX, _LY, LOUV_H + 2,
                                  align=(Align.CENTER, Align.CENTER, Align.MIN))
_clip = Pos(0, 0, -LOUV_H) * Box(_LX + 1, _LY + 1, LOUV_H,
                                 align=(Align.CENTER, Align.CENTER, Align.MIN))
_n = int(_LY // LOUV_H) + 2
for i in range(_n):
    _y = -_LY/2 + (i + 0.5) * LOUV_H
    # Tilt about x so the OUTER (-z) end sits at GREATER local y, which is
    # assembled DOWN. Rot(a) about x maps (y,z) -> (y cos a - z sin a,
    # y sin a + z cos a); the outer end at z=-1 lands at y' = +sin a, so the
    # angle must be POSITIVE. The first pass used -a and every slat pitched the
    # wrong way, funnelling spray into the fan; the assert below checks direction.
    _slat = (Pos(0, _y, -LOUV_H/2) * Rot(+LOUV_ANG, 0, 0)
             * Box(_LX + 2, LOUV_T, LOUV_H*1.5, align=(Align.CENTER,)*3))
    if i == 0:
        _vs = [(v.Y, v.Z) for v in _slat.vertices()]
        _outer = min(_vs, key=lambda t: t[1])
        _inner = max(_vs, key=lambda t: t[1])
        assert _outer[0] > _inner[0], (
            f"louvre slat pitched the wrong way: outer y={_outer[0]:.1f}, inner "
            f"{_inner[0]:.1f} - outer must be GREATER or spray runs into the fan")
    s += _slat & _clip

# ── 316 SS mesh intake filter, under the fan screws ──────────────────────
# NO RIM. The mesh used to sit in a raised collar standing FILT_T proud of the
# outer face, which cost that depth on a part whose depth is the whole argument.
# It is now clamped by the fan's own four screws: they pass from OUTSIDE through
# the mesh, through this wall, and into the fan's mounting holes on the inside.
# One set of fasteners does both jobs and nothing stands proud.
#
# A shallow recess takes the mesh so it sits flush rather than proud, and gives
# it a shoulder to locate against while you start the screws.
#
# MESH, NOT FOAM. Open-cell foam in salt air becomes a sponge that holds
# moisture against the fins between rinses - worse than the unfiltered air it
# was fitted to stop. Woven 316 sheds, dries, rinses clean and outlives the
# boat. What foam would buy is finer aerosol capture, and it is not worth a
# salt poultice. The fan's IP67 rating does not help here either: the air path
# IS the point, and salt-laden air goes through it regardless.
# CLAMPED UNDER THE FANS, not let into the wall. It sat in a 0.8 mm recess in
# the inner face of the outer wall, which put it 8 mm away from the fan frames
# that were supposed to clamp it - so it was a loose sheet lying in a groove,
# held by nothing, on a part that gets shaken by a boat. The recess also thinned
# the one wall the louvres are cut into.
#
# It lies on the eight FAN BOSSES instead, with a hole at each, and the two fan
# frames screw down on top of it. Same screws, same sheet, and now the clamp is
# real. Nothing else is needed: the fans pressurise the shroud, so every leak
# path around them blows OUTWARD and the only way in is through the mesh.
# To change it: fans out, sheet out.
FILT_LX, FILT_LY = _LX + 2*LOUV_RIM - 1.0, _LY + 2*LOUV_RIM - 1.0
FILT_Z = WALL + FAN_BOSS           # the plane it lies in
# The sheet is a bought consumable, not printed - nothing is cut for it here
# beyond the bosses it locates on. Recorded so the BOM and the assembly order
# can quote the same number.

# ── exhaust: side louvres, and a DRAIN along the low edge ─────────────────
# The fans blow IN through the louvred face, so this air has to leave. It left
# through two overlapping loops of slots that both cut at x = +/-OW/2 while
# their comment called them "the +x end and both flanks" - the +x end was cut
# twice and the low edge, the one that matters, was never cut at all.
#
# ORIENTATION. This part is flown Rot(180,0,0), so LOCAL +y IS ASSEMBLED DOWN.
# Everything below is written in local y and that sign is the whole point: the
# drain has to be on +y or it is a gutter.
EXH_W  = 4.5                       # slot width, in z (i.e. in depth)
EXH_P  = 9.0                       # pitch in z
EXH_LEN = OH - 2*R_OUT - 12.0      # slot length in y
N_EXH = max(1, int((OD - 12.0) // EXH_P))
for sx in (-1, 1):
    for i in range(N_EXH):
        z = 9.0 + i*EXH_P
        if z + EXH_W/2 > OD - 3.0:
            break
        s -= Pos(sx*OW/2, 0, z) * Box(3*WALL, EXH_LEN, EXH_W, align=(Align.CENTER,)*3)
        # 45 deg blade standing proud outboard, overhanging the slot on the
        # WEATHER side (smaller z) so spray driven from astern cannot see in.
        s += Pos(sx*(OW/2 - 2.6), 0, z + 4.2) * Rot(0, sx*45, 0) * Box(
            9.0, EXH_LEN, 3.0, align=(Align.CENTER,)*3)

# ── the drain ─────────────────────────────────────────────────────────────
# Whatever gets past the louvres lands on the COVER, inside this box. With a
# solid low edge that is a tray holding salt water against the heatsink's glue
# line for the life of the boat. The slot runs the full width at the cover face
# on the +y (low) wall, in three bays so the landing rim stays continuous enough
# to sit flat.
DRAIN_H = 5.0                      # how far up from the landing face
DRAIN_BAYS, DRAIN_BRIDGE = 3, 8.0
_span = OW - 2*R_OUT
_bay = (_span - (DRAIN_BAYS - 1)*DRAIN_BRIDGE) / DRAIN_BAYS
assert _bay > 10.0, f"drain bays are only {_bay:.1f} wide - water will bridge them"
for i in range(DRAIN_BAYS):
    _cx = -_span/2 + _bay/2 + i*(_bay + DRAIN_BRIDGE)
    s -= Pos(_cx, OH/2, OD - DRAIN_H/2 + 0.5) * Box(
        _bay, 3*WALL, DRAIN_H + 1.0, align=(Align.CENTER,)*3)

# ── relief for the brim screw heads this part lands over ──────────────────
# Read from housing.json, not retyped: the shroud's rim reaches |y| 84 and the
# unit's fastener ring runs at |y| 85.2 with O6 heads on bonded washers, so four
# heads sit under the landing face. Without these pockets the shroud rests on
# two heads at each end and rocks on them.
HEAD_R = H["M3_HEAD_R"]
HEAD_RELIEF = 3.5                  # head + bonded washer, plus a little
_relieved = 0
for _bx, _by in H["BOLTS"]:
    if abs(_bx) < OW/2 + HEAD_R and abs(_by) < OH/2 + HEAD_R:
        # cover x maps straight through; cover y is this part's -y under the flip
        s -= Pos(_bx, -_by, OD - HEAD_RELIEF/2 + 0.5) * Cylinder(
            HEAD_R + 1.5, HEAD_RELIEF + 1.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        _relieved += 1
assert _relieved == 4, (
    f"relieved {_relieved} brim screw heads, expected 4 - the fastener ring or "
    f"this outline has moved and the two are placed in different files")

# ── mounting pads at the open edge -> tapped holes in the alloy plate ─────
PAD_C = OW/2 - 14.0
# FOUR CORNER BOSSES, full depth. The screw enters at the LOUVRED FACE - the
# only face reachable once the shroud is on the cover - runs down the boss and
# threads into a blind pilot in the cover. The pads that used to sit at the
# open end were reachable only from inside, between the fan backs and the
# cover, which is a place no driver goes.
BOSS_R = 5.0
for hx, hy in HOLES:
    s += Pos(hx, hy, -LOUV_H) * Cylinder(BOSS_R, OD + LOUV_H,
                                          align=(Align.CENTER, Align.CENTER, Align.MIN))
    s -= Pos(hx, hy, -LOUV_H - 1) * Cylinder(MOUNT_D/2, OD + LOUV_H + 2,
                                              align=(Align.CENTER, Align.CENTER, Align.MIN))
    s -= Pos(hx, hy, -LOUV_H - 1) * Cylinder(3.2, 4.0,          # head counterbore
                                              align=(Align.CENTER, Align.CENTER, Align.MIN))
SCREW_L = OD + LOUV_H - 3.0 + H["SHROUD_PILOT_DEEP"]

# The housing reserves clearance for this width to place the tilt trunnions.
# If the shroud grows past what it was told, the trunnions foul it - so the
# two are checked against each other rather than trusted.
# ── does a fan actually go in? ────────────────────────────────────────────
# Asserted with a solid, not with arithmetic. The last three faults in this part
# - fans inside the fins, corner bosses inside the fan frames, a mesh 8 mm from
# the thing meant to clamp it - were all "the numbers looked fine" faults.
for _fy in FAN_CY:
    _env = Pos(0, _fy, FILT_Z + FILT_MESH) * Box(
        FAN_W, FAN_W, FAN_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    _hit = s & _env
    _v = 0.0 if _hit is None else _hit.volume
    assert _v < 1e-6, (
        f"the fan at y={_fy:+.0f} cannot be seated - {_v:.0f} mm3 of shroud is "
        f"inside its 80 x 80 x {FAN_T:.0f} envelope")
assert FILT_Z + FILT_MESH + FAN_T + PLENUM <= OD - HS_H + 1e-9, (
    f"fan backs reach z={FILT_Z + FILT_MESH + FAN_T:.1f} and the heatsink fins "
    f"start at {OD - HS_H:.1f} - they are in the same space")

_w = s.bounding_box().size.X
# A CEILING, not an equality. Awnings and fixing ribs stand proud of the box by
# an amount that changes with the geometry, and chasing it with a fudge constant
# failed four times - each new value was stale as soon as the layout moved. The
# housing reserves a generous envelope; this only has to fit inside it.
assert _w <= H["SHROUD_ENVELOPE"], (
    f"shroud is {_w:.1f} wide against a {H['SHROUD_ENVELOPE']:.0f} envelope - "
    f"the tilt trunnions are placed against that number")
if len(s.solids()) != 1:
    for _sol in sorted(s.solids(), key=lambda t: -t.volume):
        _b = _sol.bounding_box()
        print(f"   solid {_sol.volume:8.0f} mm3  x {_b.min.X:6.1f}..{_b.max.X:6.1f}  "
              f"y {_b.min.Y:6.1f}..{_b.max.Y:6.1f}  z {_b.min.Z:5.1f}..{_b.max.Z:5.1f}")
assert len(s.solids()) == 1, f"shroud is {len(s.solids())} solids, not 1"
export_step(s, "cad/out/heatsink_shroud_revD.stp")
bb = s.bounding_box()
print(f"SHROUD vol={s.volume/1000:6.1f} cm3 solids={len(s.solids())} "
      f"bbox={bb.size.X:.0f}x{bb.size.Y:.0f}x{bb.size.Z:.0f}")
print(f"       covers the {HS_L:.0f}x{HS_W:.0f} heatsink, bolts to the cover")
print(f"       {FAN_N}x Coolerguys IP67 {FAN_W:.0f}x{FAN_T:.0f} at y "
      f"{FAN_CY[0]:+.0f}/{FAN_CY[-1]:+.0f}, 4 x O{FAN_PILOT} at {FAN_PITCH} pitch each; "
      f"no round bores - the louvres are the only opening")
print(f"       {_relieved} screw-head reliefs, {DRAIN_BAYS} drain bays at the low edge")
print(f"       intake louvres: one face, {_n} slats x {_LX:.0f} wide at {LOUV_ANG:.0f} deg, "
      f"{LOUV_H:.0f} proud - blind to line of sight, sheds outward")
print(f"       316 mesh sheet {FILT_LX:.0f}x{FILT_LY:.0f} x {FILT_MESH}, lying on the fan "
      f"bosses at z={FILT_Z:.1f} and clamped by both fan frames")
print(f"       depth {OD:.1f} = {WALL:.0f} wall + {FAN_BOSS:.0f} boss + {FILT_MESH} mesh + "
      f"{FAN_T:.0f} fan + {PLENUM:.0f} plenum + {HS_H:.0f} fin")
print(f"       4 corner bosses, M3 x {SCREW_L:.0f} from the louvred face into blind "
      f"cover pilots ({H['SHROUD_PILOT_DEEP']} deep, never through)")

# What the REAR OF THE UNIT actually reaches, for anything that has to swing it.
# bail.py sized its standoff off BACK (the cover face, z=28) and the unit now
# stands 40 mm further out than that - the arms were solving the wrong sweep.
import json as _json
_json.dump({"SHROUD_OD": OD, "LOUV_H": LOUV_H,
            "REAR_PROUD": OD + LOUV_H,   # the louvres stand proud of the box
            "OW": OW, "OH": OH, "SCREW_L": SCREW_L,
            "FAN_W": FAN_W, "FAN_T": FAN_T, "FAN_N": FAN_N, "FAN_CY": FAN_CY,
            "FAN_BOSS": FAN_BOSS, "FILT_MESH": FILT_MESH, "FILT_Z": FILT_Z,
            "FILT_LX": FILT_LX, "FILT_LY": FILT_LY, "WALL": WALL,
            # the build page quotes this part's size and mass; both come from
            # the solid, never from a number typed into the page
            "FAN_PITCH": FAN_PITCH, "MOUNT_D": MOUNT_D,
            "DRAIN_BAYS": DRAIN_BAYS, "LOUV_ANG": LOUV_ANG, "LOUV_N": _n,
            "SHROUD_CM3": s.volume/1000.0},
           open("cad/out/shroud.json", "w"), indent=1)
