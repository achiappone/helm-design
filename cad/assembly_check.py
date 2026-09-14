"""
Assembly Reality Check -- can a person actually build this, with hands and tools?

Every other check in this repo asks whether the SOLIDS are right: one body, no
floating features, nothing intersecting. That is necessary and it is not the
question. A part can be geometrically perfect and impossible to fit, and this
project has shipped that three times now - shroud fixings reachable only from a
place no driver goes, fans whose backs stood inside the heatsink fins, display
posts with no screw passage standing in the middle of where the Pi lives.

So this file asks the other question, and it asks it with solids rather than
with reasoning:

  DRIVER ACCESS   For every fastener, sweep the tool that has to turn it - a
                  shank of a real diameter, a real length, along the screw's own
                  axis, from the head outward - and intersect it with everything
                  else in the assembled unit. Any volume is a screw you cannot
                  reach.
  INSERTION       For every part that has to go somewhere, sweep it along the
                  straight line it travels and subtract where it ends up. Any
                  volume left inside another part is a part you cannot get in.
  GRIP            For every fastener, the arithmetic: how much material it
                  passes through, how much thread it finds, whether a stock
                  length exists, and whether the next length up breaks through
                  into the sealed cavity.

It prints a table and raises on the first thing that is impossible. Run it after
cad/bail.py, since it reads all three JSONs.

Nothing here is modelled twice: every position comes from housing.json,
shroud.json or bail.json.
"""
import sys, json, math
sys.path.insert(0, "cad")
from build123d import *

H = json.load(open("cad/out/housing.json"))
S = json.load(open("cad/out/shroud.json"))
B = json.load(open("cad/out/bail.json"))

SHELL  = import_step("cad/out/helm_shell_revC.stp")
COVER  = import_step("cad/out/helm_cover_revC.stp")
SHROUD = import_step("cad/out/heatsink_shroud_revD.stp")
ARM    = import_step("cad/out/bail_arm_revA.stp")
BASE   = import_step("cad/out/bail_base_revA.stp")
VISOR  = import_step("cad/out/helm_visor_revC.stp")

BACK   = H["DEPTH"] + H["GASKET_C"] + H["COVER_T"]
OD     = S["SHROUD_OD"]
COV    = Pos(0, 0, BACK) * Rot(180, 0, 0) * COVER
SHR    = Pos(H["AP_CX"], 0, BACK + OD) * Rot(180, 0, 0) * SHROUD
_O     = B["ARM_ORIGIN"]
def _arm(sx):
    org = _O["pos"] if sx > 0 else _O["neg"]
    return Plane(origin=tuple(org), x_dir=tuple(_O["x_dir"]),
                 z_dir=tuple(_O["z_dir"])) * ARM
ARMS   = Compound([_arm(-1), _arm(1)])
DASH_Y = H["TILT_Y"] - B["RISE"]
PLATE  = Plane(origin=(0, DASH_Y - B["BASE_T"], B["AXIS_Z"]),
               x_dir=(1, 0, 0), z_dir=(0, 1, 0)) * BASE
# The dash itself. A screw you can only reach by drilling through the boat is
# not a screw you can reach.
DASH   = Pos(0, DASH_Y - B["BASE_T"] - 6, 0) * Box(900, 12, 900, align=(Align.CENTER,)*3)

fails, rows = [], []


def clash(a, b):
    """OCC hands back an empty shape, not None, for a miss."""
    if a is None or b is None:
        return 0.0
    h = a & b
    return 0.0 if h is None else h.volume


def access(name, at, axis, r, length, obstacles, start=1.0, budget=1.0):
    """Can a tool of radius r reach this fastener along `axis`?"""
    t = Location(Plane(origin=tuple(Vector(*at) + Vector(*axis).normalized()*start),
                       z_dir=axis)) * Cylinder(
        r, length, align=(Align.CENTER, Align.CENTER, Align.MIN))
    worst, who = 0.0, ""
    for oname, o in obstacles:
        v = clash(t, o)
        if v > worst:
            worst, who = v, oname
    ok = worst <= budget
    rows.append((("OK " if ok else "BLOCKED"), f"{name}",
                 f"O{2*r:.0f} driver x {length:.0f}",
                 "clear" if ok else f"{worst:.0f} mm3 of {who}"))
    if not ok:
        fails.append(f"{name}: {worst:.0f} mm3 of {who} is in the driver's path")
    return ok


def insert(name, part, axis, distance, obstacles, steps=24, budget=5.0):
    """Slide `part` back along `axis` and check the path it travels is clear.

    Each step is tested on its own rather than unioned into one swept solid:
    unioning 24 copies of a Compound the size of this unit made OCC hand back
    the whole obstacle as the intersection - a 9.7 litre "clash" with a dash
    the assembly never goes near. Per-step is also far faster.

    The budget is 5 mm3, not 0: parts that MATE touch, and a touching face
    integrates to a few cubic millimetres of numerical noise."""
    _n = math.sqrt(sum(a*a for a in axis))
    ux, uy, uz = (a/_n for a in axis)
    worst, who = 0.0, ""
    for i in range(1, steps + 1):
        d = distance * i / steps
        step = Pos(ux*d, uy*d, uz*d) * part
        for oname, o in obstacles:
            v = clash(step, o)
            if v > worst:
                worst, who = v, oname
    ok = worst <= budget
    rows.append((("OK " if ok else "BLOCKED"), f"{name}",
                 f"slide {distance:.0f} mm", "clear" if ok else f"{worst:.0f} mm3 of {who}"))
    if not ok:
        fails.append(f"{name}: {worst:.0f} mm3 of {who} blocks the insertion path")
    return ok


def grip(name, stock, passes, pilot, floor, min_thread=4.0):
    """Is there a STOCK length that reaches the thread and stops in time?

    Not "round the requirement up" - that picked M3x45 for a 42.1 requirement
    and drove 2.9 mm into a 1.5 mm floor. A fastener has to land its engagement
    inside a window: deep enough to hold, shallow enough not to bottom out in a
    blind hole or break through into the sealed box."""
    STOCK = [6, 8, 10, 12, 14, 16, 20, 25, 30, 35, 40, 45, 50, 55, 60]
    lo, hi = min_thread, pilot - 1.0
    pick = next((L for L in STOCK if lo <= L - passes <= hi), None)
    if pick is None:
        note = (f"passes {passes:.1f}, needs {lo:.0f}-{hi:.1f} of thread: "
                f"NO STOCK LENGTH LANDS IN THAT WINDOW")
        rows.append(("BAD    ", name, stock, note))
        fails.append(f"{name}: {note}")
        return False
    rows.append(("OK ", name, stock,
                 f"M3 x {pick}: crosses {passes:.1f}, {pick - passes:.1f} of thread "
                 f"in a {pilot:.1f} pilot ({floor:.1f} of plate under it)"))
    return True


# ══════════════════════════════════════════════════════ THE BUILD, IN ORDER
# ORDER IS THE WHOLE POINT. Almost every fastener on this unit is blocked by
# something if you ask the question against the FINISHED assembly - and almost
# none of them is blocked at the moment you actually turn it. The first version
# of this file asked the finished-assembly question and reported 16 impossible
# steps, of which three were real. So each step below sees only the parts that
# are already on at that point in the build, and the ones that would be blocked
# LATER are reported separately as what you have to take off to service it.
step = 0
def stage(title):
    global step
    step += 1
    rows.append(("", f"-- {step}. {title}", "", ""))

# ---------------------------------------------------------------- bare cover
stage("fittings into the bare cover, on the bench")
_FIT_Z = BACK - H["BORE_Z"]
for _n, _x, _af in (("cable gland M16", H["GL_X"], 22.0),
                    ("Gore vent M12", H["VENT_X"], 19.0),
                    ("SMA bulkhead M8", H["SMA_X"], 12.7)):
    access(f"{_n} spanner", (_x, H["BLK_Y0"], _FIT_Z), (0, -1, 0),
           _af/2 + 4.0, 45.0, [("the cover", COV)])

stage("heatsink bonded into its seat, from inside")
_HS_Z0 = H["DEPTH"] + H["GASKET_C"]
from parts_lib import finned
_HS = (Pos(H["AP_CX"], 0, _HS_Z0) * Box(H["HS_L"], H["HS_W"], 3.0,
                                        align=(Align.CENTER, Align.CENTER, Align.MIN))
       + Pos(H["AP_CX"], 0, _HS_Z0 + 3.0) * finned(
           H["AP_L"] - 1.0, H["AP_W"] - 1.0, H["HS_H"] - 3.0 + 0.01,
           base=0.01, fin_t=1.4, gap=2.6, along_x=False))
insert("heatsink into its seat", _HS, (0, 0, -1), 45.0, [("the cover", COV)])

stage("boards into their bays, from inside")
for _n, _cx, _l, _w in (("Raspberry Pi", H["PI_BUMP_CX"], 56.0, 85.0),
                        ("driver board", H["DRV_BOARD_CX"], 55.25, 113.25)):
    _brd = Pos(_cx, 0, BACK - H["PI_BUMP_H"] + H["WALL"] + 5.0) * Box(
        _l, _w, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    insert(f"{_n} into its bay", _brd, (0, 0, -1), 40.0, [("the cover", COV)])
    for _sx in (-1, 1):
        for _sy in (-1, 1):
            _hx = _cx + _sx*(49.0/2 if "Pi" in _n else 55.25/2 - 5.0)
            _hy = _sy*(58.0/2 if "Pi" in _n else 113.25/2 - 6.0)
            access(f"{_n} screw ({_hx:.0f},{_hy:.0f})", (_hx, _hy, BACK - H["PI_BUMP_H"] + 9.0),
                   (0, 0, -1), 3.2, 45.0, [("the cover", COV)], budget=1.0)

# ------------------------------------------------------------ cover on shell
stage("cover onto the shell, then its screws (no shroud yet)")
_ON = [("the shell", SHELL), ("the cover", COV)]
for px, py in H["DSP_POSTS"]:
    access(f"panel screw ({px:.0f},{py:.0f})", (px, py, BACK), (0, 0, 1), 3.2, 55.0, _ON)
_bad = sum(0 if access(f"brim screw ({bx:.0f},{by:.0f})", (bx, by, BACK), (0, 0, 1),
                       4.0, 55.0, _ON) else 1 for bx, by in H["BOLTS"])
rows.append(("", f"   ({len(H['BOLTS'])} brim screws, {_bad} blocked)", "", ""))

# ---------------------------------------------------------------- the shroud
stage("fans and mesh into the shroud, then the shroud onto the cover")
_FAN_Z0 = BACK + OD - (S["FILT_Z"] + S["FILT_MESH"]) - S["FAN_T"]
for fy in S["FAN_CY"]:
    _f = Pos(H["AP_CX"], -fy, _FAN_Z0) * Box(
        S["FAN_W"], S["FAN_W"], S["FAN_T"], align=(Align.CENTER, Align.CENTER, Align.MIN))
    insert(f"80 mm fan at y{-fy:+.0f}", _f, (0, 0, -1), 40.0, [("the fan shroud", SHR)])
insert("the shroud onto the cover", SHR, (0, 0, 1), 50.0, _ON)
_LOUV = BACK + OD + S["LOUV_H"]
for hx, hy in H["HS_HOLES"]:
    access(f"shroud screw ({hx:.0f},{hy:.0f})", (hx, hy, _LOUV), (0, 0, 1), 3.2, 55.0,
           _ON + [("the fan shroud", SHR)])

# ------------------------------------------------------------------ the bail
stage("arms onto the trunnions, sideways from outboard")
# NOT down between fixed arms: the unit is 334 wide and the arms' inner faces
# are 320 apart, so it cannot pass between them at all. Each arm goes on from
# outboard instead, and the unit+arms assembly then lowers onto the base.
_UNIT = [("the unit", Compound([SHELL, COV, SHR]))]
for _sx in (-1, 1):
    insert(f"{'+' if _sx > 0 else '-'}x arm onto its trunnion", _arm(_sx),
           (_sx, 0, 0), 40.0, _UNIT, steps=16)
    access(f"bail pivot M5 ({'+' if _sx > 0 else '-'}x)",
           (_sx*(B["ARM_FACE"] + B["ARM_T"]), H["TILT_Y"], B["AXIS_Z"]),
           (_sx, 0, 0), 11.0, 60.0, _UNIT + [("the visor", VISOR)])

stage("unit and arms lowered onto the base plate")
insert("the assembly down onto the plate", Compound([SHELL, COV, SHR, ARMS]),
       (0, 1, 0), 50.0, [("the bail base plate", PLATE), ("the dash", DASH)], steps=16)
# The foot bolts come UP from UNDER the plate into the arm's pad, which is why
# the arms go on the plate before the plate goes on the dash. Checked with the
# dash absent, because at that point in the build it is.
_FOOT_X = B["ARM_FACE"] + B["ARM_T"] - B["FOOT_PAD_T"]/2
for _sx in (-1, 1):
    for _sy in (-1, 1):
        access(f"foot bolt ({_sx*int(_FOOT_X)},{_sy*int(B['FOOT_BOLT_X'])})",
               (_sx*_FOOT_X, DASH_Y - B["BASE_T"], B["AXIS_Z"] + _sy*B["FOOT_BOLT_X"]),
               (0, -1, 0), 9.0, 40.0,
               [("the unit", Compound([SHELL, COV, SHR])),
                ("a bail arm", ARMS), ("the bail base plate", PLATE)])

# ══════════════════════════════════════════════════════ FASTENER GRIP
stage("fastener lengths")
grip("brim screw", "M3 pan, 316", passes=H["COVER_T"],
     pilot=H["PILOT_L"], floor=H["DEPTH"] - H["PILOT_L"])
grip("panel screw", "M3 pan, 316", passes=H["COVER_T"] + H["DSP_POST_H"],
     pilot=6.0, floor=99.0)
grip("shroud screw", "M3 pan, 316",
     passes=OD - H["SHROUD_PILOT_BOSS"] + S["LOUV_H"] - 4.0,
     pilot=H["SHROUD_PILOT_TOTAL"], floor=H["COVER_T"] - H["SHROUD_PILOT_DEEP"])

# ══════════════════════════════════════════════════════ SERVICE, NOT ASSEMBLY
# What you have to take off to get back in. Reported, never asserted - a screw
# that is buried once the unit is on its mount is normal; a screw that is buried
# when you need to turn it is not.
stage("service access, with everything on (report only)")
ALL = [("the fan shroud", SHR), ("a bail arm", ARMS),
       ("the bail base plate", PLATE), ("the dash", DASH)]
_n_shroud = sum(1 for bx, by in H["BOLTS"]
                if clash(Location(Plane(origin=(bx, by, BACK + 1), z_dir=(0, 0, 1)))
                         * Cylinder(3.2, 55.0, align=(Align.CENTER, Align.CENTER, Align.MIN)), SHR) > 1)
_n_arm = sum(1 for bx, by in H["BOLTS"]
             if clash(Location(Plane(origin=(bx, by, BACK + 1), z_dir=(0, 0, 1)))
                      * Cylinder(3.2, 55.0, align=(Align.CENTER, Align.CENTER, Align.MIN)), ARMS) > 1)
rows.append(("NOTE", f"  {_n_shroud} brim screws sit under the shroud", "",
             "take the shroud off (4 screws) before opening the box"))
rows.append(("NOTE", f"  {_n_arm} brim screws sit under a bail arm", "",
             "lift the unit off the bail before opening the box"))
rows.append(("NOTE", "  the three fittings face the dash", "",
             "fit and seal them on the bench; no spanner reaches them mounted"))

# ══════════════════════════════════════════════════════ REPORT
w = max(len(r[1]) for r in rows)
print("ASSEMBLY REALITY CHECK -- in build order")
for st, what, how, note in rows:
    print(f"  {st:8s} {what:{w}s}  {how:22s} {note}")
if fails:
    raise AssertionError("this cannot be assembled:\n  - " + "\n  - ".join(fails))
_checks = sum(1 for r in rows if r[0].strip() in ("OK", "NOTE"))
print(f"  -- {_checks} checks, every step passable in the order given")
