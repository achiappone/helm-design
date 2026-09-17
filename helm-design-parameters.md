# Helm Design — Component Dimension Reference

**Project**: DIY SignalK / OpenPlotter glass helm. Raspberry Pi 4 + PiCAN-M, 12.3" sunlight-readable bar display, N2K bus, custom button/encoder panel.
**Enclosure**: Fusion 360 → FDM, **ASA (blue)**, 316 SS hardware, saltwater + full-sun service.

Legend: ✅ confirmed from supplied drawing · ⚠️ needs measurement or datasheet · ❌ missing entirely

---

## 1. CNLINKO LP-24 24-pin flange socket ✅
Source: `71mbBj6U0aL._SL1500_.jpg` — a proper panel-cutout drawing. This is the best-documented part in the set.

| Feature | Value |
|---|---|
| Panel bore | **Ø24.4 +0.2 / −0** |
| Mounting holes | **4 × Ø3.2 +0.2 / −0** |
| Hole pattern | **26.0 ±0.1 square** (symmetric about bore) |
| Flange envelope | 33.0 ±0.3 square |
| Depth behind panel | 10.5 ±0.15 |
| Socket body depth | 29.8 ±0.3 |
| Mated plug length | 72.5 REF |
| Mated plug height | 40.7 REF |
| Dust cap lanyard | 92.8 REF (needs swing clearance) |

**Print note**: Ø24.4 is a *machining* tolerance. FDM will not hold +0.2/−0 on a vertical bore. Model at Ø24.4, print a test coupon, and adjust `PRINT_HOLE_COMP` — or model Ø23.5 and ream to size. The 4 × Ø3.2 holes: print Ø3.0 and drill Ø3.2.

## 2. Twidec PBS-33B momentary push button ✅
Source: `71VGWZ1HwxL._SL1500_.jpg`

| Feature | Value |
|---|---|
| Panel cutout | **Ø12.0** |
| Bezel OD | 21.0 across dome / ~15 at flange |
| Height above panel | 5.7 |
| Threaded barrel behind panel | **13.0 total** |
| Rating | 3A 125VAC, momentary (push=ON) |
| Pigtails | 120 mm pre-soldered |

⚠️ **Panel thickness constraint**: 13 mm of barrel must cover panel thickness + nut + washer. A nut is ~4 mm, so **max printed panel thickness ≈ 7–8 mm at the button bosses.** If the panel is thicker for stiffness, counterbore from behind. Verify with the actual part before committing.
⚠️ Claimed waterproof — that is the *button*, not the button-to-panel joint. Bed it in silicone or design an O-ring seat.

## 3. Guitar knob (rotary encoder knob) ✅
Source: `71IsBo0t4CL._AC_SL1500_.jpg`

| Feature | Value |
|---|---|
| Knob OD | Ø20.50 |
| Height | 17.50 |
| Shaft bore | **Ø6.50** (fits 1/4" shaft), 13.00 deep |
| Skirt recess | Ø15.50 × 3.00 deep |
| Set screw | **M4** grub, 7.00 down from top |

🚨 **Shaft mismatch risk**: this knob is bored **Ø6.5 mm for a 1/4" (6.35 mm) guitar pot**. Most rotary encoders (EC11 and friends) are **6.0 mm D-shaft**. A 6.0 mm shaft in a 6.5 mm bore wobbles. Either source a 1/4"-shaft encoder, or print/turn a 6.0→6.5 adapter sleeve. **Confirm your encoder's shaft before modeling the panel.**
Panel clearance needed: Ø21 min, plus the 3 mm skirt recess sits over the panel — leave the bezel face flat around it.

## 4. DROK buck-boost converter (9–36 V → 12 V 5 A) ✅ envelope / ⚠️ holes
Source: `71SjDq5GS3L._AC_SL1500_.jpg`

| Feature | Value |
|---|---|
| Overall footprint | **65.0 × 58.0 mm** (incl. mounting ears) |
| Height | **20.0 mm** |
| Case | Aluminum, potted, waterproof |

⚠️ Mounting hole **diameter and center-to-center spacing are not dimensioned** — measure with calipers before modeling the mount. Ears are at opposite corners; holes look ~Ø4.5 near the outer edges.
💡 The aluminum shell is a heat source *and* a usable heat path. Do not bury it in the middle of a sealed ASA box.

## 5. SEQURE M10-18 GPS module ✅
Source: `61Gqjmd4RNL._AC_SL1500_.jpg`

| Feature | Value |
|---|---|
| Board | **18 × 18 × 8 mm**, 7.2 g |
| Interface | GND / TX / RX / V (UART) + PPS pad |
| Antenna | Integrated ceramic patch, **top-facing** |

🚨 **Placement is a real engineering problem, not a mounting problem.** A ceramic patch GPS behind a large LCD with an HDMI/LVDS link is a classic self-jamming case — display ribbon cables radiate hard in the GPS L1 band (1575 MHz) and will crush your fix quality. Mitigations, best first:
1. Move GPS **out of the enclosure entirely** (external puck on a cable) — most reliable
2. Mount it at the top of the case, patch facing sky, with a **grounded shield plate** between it and the display electronics
3. At minimum: maximum physical separation, ferrites on the display cabling, and shielded/short GPS leads
Design the mount so option 1 or 2 is possible without a reprint. ASA is RF-transparent, so the case itself is fine.

## 6. HYS SMA dual-band antenna ✅ partial
Source: `41M7jsgv-qL._AC_SL1500_.jpg`, `61ZZvwWDaWL._AC_SL1500_.jpg`

| Feature | Value |
|---|---|
| Length | **185 mm** |
| Connector | **SMA male** (mates to SMA female bulkhead) |
| Band | 136–174 / 400–470 MHz |

⚠️ Antenna base diameter not dimensioned — measure the knurled collar OD for the mount/strain relief.
📻 Note: a handheld whip needs a ground plane to work properly. Mounted on a plastic helm box it will perform poorly. Consider a proper marine VHF antenna and treat the SMA bulkhead as a feed-through only.

## 7. Rubber cord — enclosure gasket ✅ MEASURED
**Measured: Ø3.0 mm.** The listing said *3mm (3/32")* and those are 0.6 mm apart; the cord on the bench is the 3 mm one. The 2.38 mm row below is dead — kept only so the ratio rules stay visible. **Gland is 3.45 W × 2.31 D and does not change.**

Static face-seal gland, ~20–25% squeeze:

| Cord Ø | Groove depth | Groove width |
|---|---|---|
| 3.00 mm | **2.30 mm** | **3.50 mm** |
| 2.38 mm | **1.85 mm** | **2.80 mm** |

Rules: groove depth ≈ 0.75–0.80 × cord Ø; width ≈ 1.15 × cord Ø (fill 70–85%, never 100%). Radius the groove corners. Keep the run **continuous with no corners tighter than ~5 × cord Ø**. Splice the loop with a scarf joint + cyanoacrylate, positioned away from the lowest point.
🚨 Do **not** rely on the gasket alone — the printed sealing face itself leaks through layer lines. Print the flange face with ≥6 perimeters, or seal it.

---

## Missing — needed before enclosure modeling ❌

These are the parts that actually drive the design, and none are dimensioned yet:

1. **12.3" 1920×720 stretched bar LCD** — 🚨 *the single most important missing item.* Need: outer glass/module L×W×D, **active area** L×W, bezel-to-active offsets on all four sides, mounting boss/bracket pattern, driver board footprint, ribbon cable length and exit side, and **operating temperature range**.
2. **Raspberry Pi 4** — 85 × 56 mm, 4 × M2.5 holes on 58 × 49 mm, 3.5 mm from board edges (verify). Need stack height with HAT.
3. **PiCAN-M HAT** — footprint, connector positions, N2K terminal/M12 orientation, standoff height above the Pi.
4. **M12×1.5 breather vent** — thread length, required boss thickness, wrench flats, sealing washer OD.
5. **SMA waterproof box, M16** — panel bore, thread length, flats.
6. ~~**PCM1808 audio ADC board** — footprint and hole pattern.~~ ✅ measured: 34.5 × 8.25 × 9.5. Strap-down, no holes.
7. **Helm geometry** — dash cutout size available, dash thickness/material, rake angle, and rear clearance depth.

---

## 🚨 The Dominant Risk: Thermal

Before any geometry, this needs an answer.

You are putting a **Raspberry Pi 4** (~5–7 W under load, throttles at 80–85 °C) plus a **1000-nit backlight** (a 12.3" panel at that brightness dissipates real wattage) plus a **buck converter** inside a **sealed, insulating ASA box**, mounted on a **boat dash in direct sun where surface temps reach 60–80 °C**.

A sealed plastic enclosure has essentially no convective path. The M12 breather vent equalizes *pressure*, not *heat* — it moves negligible air. As drawn, this design thermally throttles or shuts down on the first sunny day.

Design responses, in order of effectiveness:
1. **Conductive path to an external metal plate.** Aluminum backplate as a structural + thermal member; Pi SoC and the DROK shell coupled to it with thermal pads. The plate is also your GPS ground plane and your stiffener. This is the right answer.
2. **External finned heatsink** through a sealed penetration.
3. **Light-colored enclosure** — you chose **blue ASA**, which is good: far better solar gain than black. Keep it light.
4. **Sun shade / shroud** over the whole unit — also fixes screen glare, which you want anyway.
5. **Underdeck or shaded mounting** if the helm layout allows.
6. Filtered forced-air with IP-rated fans — last resort; it fights the waterproofing.

ASA's glass transition (~100–110 °C) means the *housing* is fine. The **Pi and the LCD** are the parts that quit first. Get the LCD's max operating temp from its spec sheet — many automotive bar displays top out at 70–85 °C, and yours will exceed that in a sealed box.

---

## Fusion 360 User Parameters (starting set)

```
# Print / process
WALL              = 3.2 mm    # 8 x 0.4 nozzle, structural
WALL_THIN         = 2.4 mm    # non-structural panels
PRINT_CLEAR       = 0.3 mm    # free fit
PRINT_CLEAR_SNUG  = 0.2 mm    # located fit
PRINT_HOLE_COMP   = 0.3 mm    # add to vertical bore diameters
FIRST_LAYER_CHAM  = 0.5 mm    # elephant's foot relief
INSERT_D_M3       = 4.0 mm    # M3 316SS heat-set minor dia - VERIFY vs datasheet
INSERT_D_M4       = 5.6 mm    # M4 316SS heat-set minor dia - VERIFY vs datasheet
BOSS_WALL         = 2.0 mm    # min material around a heat-set insert

# Gasket  (SET AFTER MEASURING CORD)
GASKET_CORD_D     = 3.0 mm
GASKET_GROOVE_W   = GASKET_CORD_D * 1.15
GASKET_GROOVE_D   = GASKET_CORD_D * 0.77

# Confirmed component interfaces
LP24_BORE         = 24.4 mm
LP24_HOLE_D       = 3.2 mm
LP24_HOLE_PITCH   = 26.0 mm
LP24_DEPTH_BEHIND = 10.5 mm
BTN_BORE          = 12.0 mm
BTN_BARREL_L      = 13.0 mm
BTN_BEZEL_OD      = 21.0 mm
KNOB_OD           = 20.5 mm
KNOB_SHAFT_D      = 6.5 mm
DROK_L            = 65.0 mm
DROK_W            = 58.0 mm
DROK_H            = 20.0 mm
GPS_L             = 18.0 mm
GPS_W             = 18.0 mm
GPS_H             = 8.0 mm

# Helm interface (MEASURE ON THE BOAT)
DASH_THICKNESS    = 0 mm      # TBD
DASH_RAKE         = 0 deg     # TBD
REAR_CLEARANCE    = 0 mm      # TBD - must exceed LP24 mated 72.5 + cable bend
```

---

## Export Workflow

**Slice from 3MF. Archive as STEP.**

| Format | Role |
|---|---|
| **3MF** | → the slicer. Carries units, multiple bodies, colors, per-object settings. Native in Orca / Bambu / Prusa / Cura. |
| **STEP (.stp)** | → archive + handoff. Exact BREP geometry, editable by any CAD. Modern slicers can import it, but they tessellate it at their own resolution — don't slice from it by choice. |
| STL | → fallback only. No units (mm/inch scaling bugs), no color, one body per file. |

Fusion: `Utilities → Make → 3D Print` → uncheck "Send to 3D Print Utility" → save as 3MF.
🚨 Set **Refinement: High**. The default coarse setting visibly facets curved features — enough to keep the Ø24.4 LP-24 bore from seating.

Release package per part: `partname_revA.3mf` (sliced) + `partname_revA.stp` (archive) + print card (material, orientation, layer height, perimeters, infill, supports).

---

# Sealed Housing Architecture

Requirement: **fully enclosed watertight housing with a Gore-style M12×1.5 pressure vent.**

## Why the vent is not optional

A sealed box is a pressure vessel. Heat it and it inflates; cool it and it inhales.

```
Sealed at 20 °C, heated to 70 °C on a sunny dash:
  P2/P1 = T2/T1 = 343 K / 293 K = 1.17     -> +0.17 bar internal
Then cooled by rain or nightfall to 5 °C:
  P2/P1 = 278 K / 343 K = 0.81             -> -0.19 bar (vacuum)
```

That **negative** cycle is what actually sinks sealed electronics: the box pulls water in past every seal, connector, and layer line. It happens overnight, silently, and repeats daily. A gasket alone cannot stop it — the pressure differential is doing the pumping.

The Gore-style ePTFE vent breaks that cycle: air passes, liquid water does not.

🚨 **The vent equalizes pressure. It does not cool.** Airflow is on the order of tens of mL/min — thermally irrelevant. The Pi 4 heat problem (§ above) is still unsolved and still needs a conductive path to an external metal plate.

## Vent installation

| Item | Spec |
|---|---|
| Thread | M12×1.5 |
| Boss face | Flat, smooth, **perpendicular to thread axis** — seals on a washer, not on threads |
| Boss thickness | Must be **less** than the vent's thread length minus its nut. ⚠️ Measure the actual part. |
| Hole | Print Ø11.6, tap M12×1.5 — or print Ø12.3 clearance and use the vent's own nut + O-ring |
| Placement | **Rear or downward-facing wall.** Never a top surface, never where spray hits directly or water can stand |
| Never | Paint it, sealant on the membrane, or block it with a cable |

Don't print M12×1.5 threads at 0.4 mm nozzle if you can avoid it — 1.5 mm pitch is printable but the flanks are weak in ASA and the seal is the whole point. Prefer the clearance hole + captive nut.

## The gasket flange — where printed boxes actually leak

🚨 **Bolt spacing is the #1 failure mode of printed sealed enclosures.** A printed ASA flange is far more flexible than the aluminum ones these design rules were written for. Space bolts too far apart and the flange **bows outward between them**, opening the gland in the middle of each span. It passes a hose test on the bench and leaks in service.

Rules:

| Parameter | Value |
|---|---|
| Bolt spacing | **≤ 50 mm, target 40 mm** around the entire perimeter |
| Bolt-to-gland offset | ~1.5 × bolt Ø from the groove edge — as close as the boss allows |
| Flange thickness | **≥ 5 mm**, or 4 mm with a stiffening rib along the outer edge |
| Corners | A bolt within 25 mm of every corner. Corners bow worst. |
| Fasteners | M4 × 316 SS into 316 SS heat-set inserts |
| Compression stops | Model **positive stops** (bosses bottoming out) so the gasket can't be crushed past ~25% squeeze |

Joint form: **tongue-and-groove, not a flat butt joint.** A butt seam is a straight-line path from outside to inside. A tongue with 0.3 mm side clearance forces a labyrinth and locates the lid during assembly.

## Wall porosity — the leak nobody plans for

A raw FDM wall is **not** watertight, gasket or no gasket. Water wicks through layer-line voids under pressure differential.

Countermeasures, in order:
1. **≥ 6 perimeters** on all pressure-boundary walls (≥ 5 elsewhere)
2. **Flow / extrusion multiplier 102–105 %** on the outer walls
3. **0.15–0.20 mm layers** — thinner layers, better fusion, fewer voids
4. **Print hot** — ASA at the upper end of its range, in an enclosure, for maximum interlayer bonding
5. **Post-process**: ASA vapor-smooths with acetone, which fuses the outer skin and is genuinely effective. Or brush-coat the interior with epoxy.
6. No thin unsupported spans in the pressure boundary

Also: **all screw bosses must be blind.** A boss that breaks through the wall is a direct leak path, and this is easy to do accidentally when you deepen a boss for insert clearance. Check with Section Analysis before release.

## Penetration inventory — every one is a leak candidate

| Penetration | Seal method | Risk |
|---|---|---|
| **LP-24 connector** | Own IP67 flange gasket, 4 × M3 | Low — designed for this. Face must be flat and smooth. |
| **M12×1.5 Gore vent** | Own O-ring washer on a flat boss | Low |
| **SMA bulkhead (M16 box)** | Own gasket + nut | Low ⚠️ dimensions still needed |
| **12 mm push buttons ×6** | Built-in O-ring under bezel | ⚠️ **Medium.** The seal needs a *flat, smooth* panel face. Layer lines on that face are a leak path — orient the panel so the button face is a top/bottom surface, not a stepped one. Add a thin gasket washer if unsure. |
| **12.3" display** | See below | 🚨 **High — the hardest seal in the build** |

## 🚨 The display is the real sealing problem

A 12.3" bar LCD makes the **glass itself part of the pressure boundary**, and it's the largest, flattest, least forgiving seal in the design.

Two compounding issues:

1. **Glass-to-bezel seal.** You need a continuous compressed gasket around a ~300 mm × 130 mm perimeter, with even pressure and no point loads. Over-clamp a corner and you crack the panel. Options: closed-cell foam tape (PORON/VHB) around the perimeter with a clamping frame, or a moulded gasket in a groove. A clamp frame with the same **≤ 40 mm fastener spacing** rule applies.

2. **The display module is itself not sealed.** Most automotive bar LCDs have a metal frame around the glass that is *not* watertight — water that reaches the module edge wicks in behind the polarizer and into the backlight. Sealing at the outer bezel is not enough; you must seal *to the glass face*, not to the module frame.

Get the panel's **glass dimensions and bezel-to-active offsets** before designing anything here. This is the item blocking enclosure design.

## Realistic IP target

| Rating | Achievable? |
|---|---|
| IP65 (dust tight, low-pressure jets) | ✅ Yes with the above |
| IP66 (powerful jets / washdown) | ✅ Likely, with vapor smoothing |
| IP67 (30 min at 1 m immersion) | ⚠️ Hard with FDM. Possible with epoxy coating + a display seal you trust. Test it. |
| IP68 | ❌ Don't claim it |

For a helm unit under a windshield or T-top, **IP65/66 is the honest target** — it survives spray, rain, and washdown. Test with a hose before installing electronics, and put a **water-detect strip or moisture indicator card** inside so a slow leak announces itself before it kills the Pi.

---

## 8. LISTENJIALE NPT 3/4" cable gland (item 16) ⚠️
Source: `612fY41yqjL._SL1500_.jpg` — **product photo, no dimensions.** Values below are standard NPT 3/4 references, not measured from your part.

| Feature | Value | Status |
|---|---|---|
| Thread | **NPT 3/4"** — major Ø ≈ 26.67 mm, 14 TPI, **tapered 1:16** | standard |
| Panel bore | **Ø28.0** clearance | ⚠️ verify |
| Flat pad for O-ring + locknut | Ø44 min | ⚠️ verify hex + locknut A/F |
| Cable range | 12.5 – 18 mm OD | ✅ listed |
| Body | Nylon, integral spiral strain relief |  |

🚨 **NPT is a tapered pipe thread — do not model it into the housing.** Tapered threads seal by thread-flank interference, which printed ASA cannot hold reliably, and cutting an NPT taper in a printed boss is a poor use of effort. Use a **plain Ø28 through-hole**: the gland's own O-ring seals against the *outside* face and its locknut clamps from inside.

That makes the **panel face around the bore a sealing surface**. It must be flat, smooth, and perpendicular to the bore. Layer-line texture there is a leak path — model a raised flat pad and orient the print so that face is a clean top or bottom surface.

⚠️ **Question worth answering before modeling**: you now have both an LP-24 24-pin connector *and* a 3/4" gland. Both are large penetrations (Ø24.4 and Ø28) and every penetration is a leak candidate. Is the gland a second cable run, or is it redundant with the LP-24? Deleting one is the cheapest reliability win available.

---

# Pi + PiCAN-M Mounting — Use a Chassis Plate

You asked to mount the Pi + PiCAN HAT **on the back of the display**. Do it via an intermediate plate, not directly.

## Why not straight onto the display

1. **Thermally it is the worst available location.** The back of the display is already the hottest surface in the box — that's where a 1000-nit backlight dumps its heat. Bolting the Pi there stacks a second heat source onto the first, inside an insulating sealed ASA shell, with no path out. That combination is what turns into a thermal shutdown on the first sunny day.
2. **GPS self-jamming gets worse.** It clusters the Pi, the HDMI/LVDS link, and the display driver board into one tight volume — exactly the radiators that swamp GPS L1. See §5.
3. **Display backs usually have no rated mounting.** Automotive bar LCD rear housings are typically thin stamped sheet with no bosses, and hanging ~100 g of Pi + HAT + cabling off them on a vibrating boat is an unsupported load path.

## Do this instead: an aluminum chassis plate

A single **3–4 mm aluminum plate** behind the display, standing off from it, that does five jobs at once:

| Job | How |
|---|---|
| **Mounts the Pi stack** | M2.5 standoffs on the 58 × 49 mm pattern — you get the rear mounting you wanted |
| **Solves the thermal problem** | Thermal pad from the Pi SoC (and the DROK's aluminum shell) to the plate; couple the plate to an exterior surface or external fins |
| **GPS ground plane** | A grounded metal plane between the display electronics and the GPS patch — directly mitigates §5 |
| **Structural spine** | Stiffens a large printed enclosure, which is what makes the ≤ 40 mm gasket bolt spacing achievable |
| **Assembly fixture** | The whole electronics stack drops in and out as one unit for service |

Mount the plate to **printed bosses in the enclosure**, with the display mounted to the plate — not the plate to the display. Load path goes electronics → plate → enclosure, and the display carries only itself.

Air gap the plate off the display back (8–12 mm) so the backlight's heat isn't conducted straight into the Pi. The plate's job is to move heat *out*, not to shuttle it between components.

## Stack dimensions ⚠️ verify all

| Item | Value | Status |
|---|---|---|
| Pi 4B board | 85.0 × 56.0 mm | standard |
| Pi 4B mount holes | 4 × Ø2.7 (M2.5), **58.0 × 49.0 mm** pattern, 3.5 mm from edges | standard, verify |
| Pi 4B tallest parts | USB / Ethernet ≈ 13.5 mm above PCB | verify |
| PiCAN-M HAT | 65 × 56.5 mm nominal HAT outline | ❌ **needs measurement** |
| HAT standoff height | 11 mm typical GPIO stack | ❌ verify |
| Total stack height | ~30 mm est. incl. connectors | ❌ verify |
| PiCAN-M N2K connector | Position + orientation drives the LP-24 pinout and cable routing | ❌ **needs measurement** |

The PiCAN-M's terminal/connector position is on the critical path — it determines where the LP-24 has to sit and how the harness routes. Measure it before the enclosure is modeled.

---

# Part 2 — LP-24 Upright Mount (90°)

Architecture you specified: helm enclosure → NPT 3/4 gland on back/side → cable run → **separate upright mount** carrying the LP-24 as a serviceable disconnect.

**Files**: `cad/out/lp24_upright_mount_revB.stp` (128 × 96 × 64 mm, 142 cm³) + `cad/out/lp24_upright_clamp_revB.stp` (20 × 36 × 13 mm, 7 cm³)

## 🚨 Errors in the ChatGPT concept — corrected here

| Concept said | Reality | Consequence if built as drawn |
|---|---|---|
| "Bolt Circle: **61 mm** (2.40")", "Mounting Holes: **M6**" for the LP-24 | LP-24 is **4 × Ø3.2 on a 26.0 mm SQUARE**, bore Ø24.4 (per CNLINKO drawing) | 🚨 **The connector does not fit. At all.** This is a fabricated spec — it conflates the mount's own base holes with the connector's pattern |
| "Brass heat-set inserts recommended" | Brass **dezincifies in saltwater** | Inserts corrode and strip out; the classic printed-marine-part failure |
| 4 × M6 base screws at the corners | 114 mm between bolts on a printed flange | Flange bows mid-span, gasket opens. Changed to **6 × M5** at ≤53 mm spacing |
| 40° angle, "water shedding" | On a horizontal surface a 40° face aims the connector **skyward** | Rain collects in the connector face. **Your 90° call fixes this properly** |
| "Supports: No (as oriented)" | A horizontal Ø24.4 bore droops without support | Bore printed out-of-round. Fixed with a **teardrop** bore (peak at 1.25 × r, ~38° overhang, self-supporting). The LP-24's 33 mm flange covers the teardrop completely |

Treat that sheet as a styling reference, not a drawing. The renders are convincing and the numbers behind them are not real.

## Why 90° is the right call

Your instinct is correct and it's better than the 45° I was going to build. A vertical connector face:
- **Cannot pool water**, at any mounting orientation — nothing to collect in the receptacle when unmated
- Makes the bore **teardroppable**, which removes supports entirely
- Puts the unmated dust cap hanging **downward**, where it belongs

## As modelled

| Feature | Value |
|---|---|
| Base | 128 × 96 × 6 mm, R10 corners |
| Base bolts | **6 × Ø5.5** (M5 316 SS) at ±53 / ±37 and 0 / ±37 — 53 mm max spacing |
| Body | 68 mm deep × 70 mm wide × 58 mm tall, front face vertical |
| Back wall | **12° taper** — sheds water, self-supporting |
| Walls | 4.5 mm, shelled, open bottom |
| LP-24 bore | **Ø24.4, teardropped** |
| LP-24 fixing | 4 × Ø4.0 insert bores on 26.0 square, into 8.5 mm bosses on the **inside** of the front wall (a 4.5 mm wall alone is too thin for an insert) — **316 SS M3 heat-sets** |
| Gasket | 3 mm rubber cord (**measured**) in a groove cut into the shell brim, 3.60 W × 2.31 D (85% fill), 22 × M3 outboard of it into blind pilots — no washers needed there; the 4 panel screws are the sealed penetrations |
| Cable opening | 36 × 34 in the base, with a **5 mm anti-wick lip** so floor water can't run down into the deck penetration |
| Strain relief | 20 × 36 pad + 2 × M4 316 SS inserts at 24 mm pitch, with the separate clamp block (Ø14.8 saddle, countersunk) |
| Drain | 20 × 14 × 3.5 slot at the front low point — **leave it open, no sealant** |

⚠️ `CABLE_D = 14.0` is a placeholder. Set it to your actual cable OD (the gland accepts 12.5–18 mm) and re-run — the clamp saddle is parametric.
⚠️ Verify the LP-24's body depth behind the flange fits the 58 mm internal height before printing.

---

# Display Bezel — Flexible Black Adhesive

Good choice, and better than a foam gasket for this joint. Silicone-type adhesive stays flexible, which matters because **glass and ASA have very different thermal expansion** — a rigid bond around a 300 mm perimeter would put the panel in tension every heat cycle. Flexible absorbs that. Black hides at the bezel edge.

Design the joint for it:

1. **Give it a real bond gap.** Silicone gets its flexibility from thickness. A joint squeezed to nothing is a rigid, weak joint. Model a **1.5–2 mm** glue channel and add **moulded standoff pips** (3–4 per side, 1.5 mm tall) so you physically cannot over-clamp it.
2. **Model a glue dam** on the inboard side of the channel — a 1 mm rib that stops squeeze-out from reaching the active area. You cannot clean silicone off a polarizer.
3. **Surface prep is the whole game.** Silicone adhesion to ASA is mediocre bare. Abrade the channel, clean with IPA, and use the primer if your product has one. Printed texture actually helps here — more mechanical key.
4. **Cure needs moisture.** Most one-part black silicones are moisture-cure. A fully sealed box with the vent installed will cure very slowly in the bond line's interior. Assemble the display **before** final sealing, and give it days, not hours.
5. **Accept it's semi-permanent.** Plan a cut line — a thin slot or access notch — so a blade can separate the display later without destroying the bezel.
6. ⚠️ **Check for acetic-cure.** Cheap silicones release acetic acid while curing, which corrodes electronics and etches some coatings. Use a **neutral-cure (oxime/alkoxy)** product in an electronics enclosure. If it smells like vinegar, don't use it here.

---

# Foil Tape on the Pi Plate — Useful, But Not the Fix

Worth doing, for reasons partly different from the one you gave.

**What it genuinely buys you:**
- ✅ **Radiant barrier.** It does reflect infrared from the display back. Real, measurable, worth having.
- ✅ **GPS ground plane** — *if you bond it to system ground.* Ungrounded foil does little for RF. Grounded, it's a shield between the display electronics and the GPS patch, which attacks the §5 self-jamming problem directly. This may be the bigger win.
- ✅ Some lateral heat spreading across the plate face.

**What it does not do:**
- ❌ **It does not remove the Pi's own heat.** The Pi still dissipates 5–7 W, and foil tape on an ASA plate is ~0.05 mm of aluminum bonded to an insulator. There's no path to outside air. Radiant blocking helps with heat coming *from* the display; it does nothing for heat generated *by* the Pi.
- ❌ It doesn't change that a sealed ASA box has no convective exit.

**So:** foil tape is a good addition to a metal chassis plate, not a replacement for one. If you want to skip the aluminum plate, the Pi still needs *some* conductive route to an exterior surface — a heatsink bonded through the wall, or a metal insert under the SoC that reaches outside.

🚨 **Two safety notes on foil tape:**
1. It is **conductive and it will short a Pi.** Put an insulating layer (Kapton, or the printed plate itself) between foil and any PCB, and keep it well clear of the GPIO header and HAT underside.
2. Foil tape adhesive softens at sustained high temperature — exactly the condition you're designing for. Use a proper aluminum foil tape with acrylic adhesive rated ≥120 °C, not HVAC duct tape.

---

# Rev B.1 — Service Access Fix

**Found in review**: the strain relief clamp (36 mm) could not pass the base opening (34 mm). Fouled by 2 mm, and still zero clearance rotated 90°.

**The larger problem behind it**: the solid base plate sealed off the entire interior. Body cavity is 59 × 61 mm, reachable only through a 36 × 34 letterbox. You could not set a heat-set insert, hold the connector while driving its screws, or get a soldering iron to 24 solder cups. A part that cannot be assembled is not a part.

## Changes

| | rev B | rev B.1 |
|---|---|---|
| Base | 128 × 96 | **132 × 102** |
| Body width | 70 | **62** |
| Service opening | 36 × 34 | **40 × 42** (+37% area) |
| Gasket loop | 92 × 58 | **98 × 70** (moved outboard) |
| Base bolts | 6 × M5 | **8 × M5** at ±56 / ±43 |
| Clamp | 20 × 36 | **18 × 36** |
| Clamp clearance in opening | −2.0 (interference) | **+6.0** |

All 12 assembly clearances now checked programmatically, 0 failures. Volume 139.4 cm³.

## Assembly sequence — mount

1. **Heat-set inserts first**, shell inverted: 4 × M3 316 SS in the connector-wall bosses, 2 × M4 in the strain-relief pad. Nothing else is in the way at this point, and this is the step the old opening made impossible.
2. **Solder all 24 conductors** to the LP-24 rear cups on the bench, with the cable already run through the deck penetration.
3. **Feed connector + cable up through the 40 × 42 opening.** Hold the connector against the inside of the front wall.
4. **4 × M3 from outside** — through the LP-24 flange, through the wall, into the inserts. Driving from outside is why the bosses are on the inside.
5. **Clamp the cable jacket** on the strain-relief pad, 2 × M4. Jacket only — no load path to the pins, ever.
6. **Leave a service loop below deck** so the whole mount can be unbolted and lifted clear without tensioning anything.
7. **Gasket, bed with 4200, 8 × M5**, tightened opposite corners.

## Assembly sequence — NPT 3/4 gland (helm enclosure end)

1. Panel bore is a **plain Ø28 hole**. Do not model or cut an NPT taper in printed ASA — tapered threads seal by flank interference and ASA will not hold it.
2. **Gland body outside**, its O-ring sealing against the flat raised pad; **locknut inside**.
3. That pad must be flat, smooth, and square to the bore. Orient the print so it is a clean face, not stepped layer lines.
4. Fit the gland **before** pulling cable; tighten the compression nut **last**.
5. Point it **down or aft**. Leave the spiral relief free to flex — do not cable-tie it straight, that defeats the entire part.

⚠️ Still open: confirm the LP-24 body depth behind its flange fits the 58 mm internal height, and set `CABLE_D` from your actual jacket OD.

---

# Rev D.2 — LP-24 Shroud, Final Architecture

One piece, sitting directly on the helm shelf. No base plate. Open bottom. All threads formed directly in ASA by 316 SS screws — no inserts.

## Files
- `cad/out/lp24_shroud_revD.stp` — 132 × 102 × 63, 132.4 cm³
- `cad/out/lp24_clamp_revD.stp` — 22 × 58 × 16, 16.4 cm³

## Strain relief — cross-beam, pilots facing the open end

| Feature | Value |
|---|---|
| Beam | spans wall to wall, x 12–33, z 26–39 |
| Pilots | 2 × **Ø3.5 × 11 deep**, at `(22.5, ±22, 26)`, **opening downward** |
| Screws | **M4 × 25** 316 SS, driven **upward** from the open face |
| Squeeze stop | saddle depth = `CABLE_D − 1` → 1.0 mm on the jacket |
| Headroom under beam | 26 mm |

🚨 **The rule this part taught**: pilot holes must open toward an opening, not into a closed volume. Three revisions failed on this. D.1 had the pilots facing the roof with 31 mm of headroom against a ~55 mm driver.

**Verification that catches it**: ray-cast a **9 mm driver corridor** (centre + 8 points at r=4.5) from each pilot mouth to the open face, sampling every 0.5 mm for solid material. "No material above the feature" is not the same test — empty space inside a closed box is not access. The check now runs on every rebuild.

## Direct threading — pilot sizes

| Screw | Pilot | Engagement | Est. pullout (interlayer) |
|---|---|---|---|
| M4 | Ø3.5 | 11 mm | ~1070 N |
| M3 | Ø2.6 | 8 mm | — |

LP-24 wall is **Ø3.2 clearance**, thread only in the boss — forming 12.5 mm of thread through wall + boss would split it. Lead-in cones at every pilot mouth.

Two screws, 3× safety → ~710 N working vs a 200–400 N cable yank. Printed threads last ~5–10 assembly cycles; the Ø10 boss can be drilled out for an M4 insert later if one strips.

⚠️ Still open: actual **cable OD** (`CABLE_D = 14.0` is a placeholder), and **LP-24 body depth behind the flange** vs the 63 mm cavity.

---

# Sensor Payload (behind the touchscreen)

| Device | Bus | Job | Siting verdict |
|---|---|---|---|
| **MCP23017** | I²C 0x20–0x27 | 16-ch GPIO expander — the 6 buttons | ✅ Fine. Put it near the buttons, keep the runs short |
| **MCP9808** | I²C 0x18–0x1F | Temperature | ⚠️ **Depends what you're measuring** — see below |
| **ADXL345** | I²C 0x53 / 0x1D | 3-axis accelerometer | ✅ Fine inside, if rigidly mounted and axis-aligned |
| **ICM20948** | I²C 0x68 / 0x69 | 9-DoF IMU **incl. magnetometer** | 🚨 **Magnetometer will not work here** |
| **RTL-SDR** | USB | Receiver — AIS / ADS-B / weather | ⚠️ Hot, and needs the SMA bulkhead |
| **Oak Grigsby encoder** | GPIO | Panel control | ✅ Likely resolves the knob shaft mismatch |

**No I²C address collisions** — all four sensors coexist on one bus. Keep the runs short; long I²C on a boat is marginal, and if the RTL-SDR sits between them use shielded/twisted pairs.

## 🚨 The magnetometer cannot live behind the display

A magnetometer needs distance from ferrous metal and from current-carrying conductors. Behind a 1000-nit LCD, next to a backlight driver, a Pi, and a DC/DC converter, is close to the worst possible location. The backlight current alone will swamp it, and it varies with brightness — so the error moves as you dim the screen.

Options, best first:
1. **Put the ICM20948 in a small external pod** on a non-ferrous mount, well away from the display. Compass then works.
2. **Give up magnetic heading** and take course from GPS (COG). Fine underway, useless at rest or when setting an anchor alarm.
3. Keep the ICM20948 inside for its gyro and accelerometer only, and ignore the magnetometer. Same as option 2, but you already own the part.

If you go with option 1, the pod needs its own cable run — worth deciding before the enclosure penetrations are fixed.

## ⚠️ Where the temperature sensor goes depends on what you want

- **Measuring the enclosure** (health monitoring, thermal-shutdown warning) → behind the display is exactly right, and given the thermal risk below, genuinely useful. Put it near the Pi.
- **Measuring cabin or outside air** → it will read the backlight, not ambient. It has to go outside the box or in a vented pocket isolated from the electronics.

## ⚠️ RTL-SDR

Runs warm on its own (~1.3 W concentrated in a small metal stick, 50–60 °C surface unaided) and lands in an already-marginal thermal budget. It also needs:
- A **USB port** on the Pi, and its dongle body is ~68 × 27 × 12 mm plus the connector
- The **SMA bulkhead** (parts list item 7, M16 waterproof box) as its antenna feed
- Its shell is the heatsink — do not bury it in a pocket. Strap it to the chassis plate with a thermal pad.

## 🚨 Thermal budget, updated

| Load | Power |
|---|---|
| Raspberry Pi 4 | 6.0 W |
| 12.3″ LCD @ 1000 nits | 14.0 W |
| RTL-SDR | 1.3 W |
| DROK converter loss | 2.0 W |
| Sensors + encoder | 0.4 W |
| **Total** | **≈ 24 W** |

A sealed box of 0.213 m² dissipates that at roughly **+12 °C above its own surface temperature** — and on a sun-baked dash that surface is already 60–70 °C. That puts internal air near 75–85 °C before you count hot spots, against a Pi 4 that throttles at 80–85 °C.

**24 W in a sealed insulating box is not survivable without a metal heat path.** This is now the top design constraint, ahead of the display dimensions. The aluminum chassis plate is no longer optional, and it likely needs external fins or a metal panel bonded through the rear wall.

## Dimensions still needed ❌
Board outlines and mounting hole patterns for all six. Adafruit publishes them per product, but they vary and I will not guess them into a mounting plate.

Also for the **Oak Grigsby encoder**: shaft diameter and bushing thread. If it is the common **1/4″ shaft with 3/8″-32 bushing**, it fits your guitar knob (Ø6.5 bore) and closes out the mismatch flagged in §3 — the panel hole becomes **Ø9.9**, not the Ø10 previously assumed.

---

# Audio Subsystem — PCM1808 (ADC) + PCM5102A (DAC)

| Board | Direction | Bus | Pi pins |
|---|---|---|---|
| PCM1808 | analog in → digital | I²S | BCLK / LRCLK / **DIN** |
| PCM5102A | digital → analog out | I²S | BCLK / LRCLK / **DOUT** |

## 🚨 The Pi has only ONE I²S peripheral

You cannot treat these as two independent sound cards. What *does* work: the Pi is I²S **master**, both boards slave to the **same BCLK and LRCLK**, the ADC feeds PCM_DIN and the DAC listens on PCM_DOUT. The Pi's I²S is full-duplex, so simultaneous capture and playback is achievable — this is the same pattern HiFiBerry's DAC+ADC boards use.

Practical consequences:
- You need a **device-tree overlay that declares simultaneous I²S in and out**. A plain `hifiberry-dac` overlay gives you playback only. The `googlevoicehat-soundcard` overlay is the usual generic route for a PCM5102-style DAC plus an I²S mic/ADC on one bus.
- **Sample rate is shared.** Both devices sit on one LRCLK, so capture and playback run at the same rate by construction. Fine, but you cannot record at 48 k and play at 44.1 k.
- The **PCM5102A must not drive the clocks.** Set it to slave; some GY-PCM5102 modules have solder jumpers (FLT / DEMP / XSMT / FMT) that need setting.

## ⚠️ Pin coexistence with the PiCAN-M

I²S uses **GPIO 18–21**. The PiCAN-M is a CAN HAT on the same 40-pin header and normally uses **SPI0 (GPIO 8–11)** plus an interrupt line. Those should not collide — but **verify against the PiCAN-M pinout before committing the stack**, because if they do clash the fix is a different audio path, not a mechanical change, and you want to know that before the enclosure is printed.

## ⚠️ Analog noise

Both boards carry line-level analog in a box containing a switching DC/DC converter and a 1000-nit backlight driver. Keep the analog runs short and shielded, and site both boards **away from the DROK**. Ground the shields at one end only. This is the easiest noise problem to create and the most tedious to chase afterwards.

Also note the PCM5102A is **line level** — it will not drive a speaker. If audio goes to a speaker you need an amplifier stage that is not yet in the parts list.

## ✅ Board outlines — MEASURED

| Module | L × W | H over caps | Bay (L × W, +1.5 clear) |
|---|---|---|---|
| **PCM1808** | **34.5 × 8.25** | **9.5** | 36.0 × 9.75 |
| **PCM5102A** | **32.0 × 17.25** | **6.5** | 33.5 × 18.75 |

Both old bays were wrong, in opposite directions:

- **PCM1808** had a **40 × 32** bay for an 8.25 mm board. The corner pips sat 12 mm off centre — **8 mm outboard of the board's own edge** — so the board touched none of them, and the cable tie had 24 mm of slop.
- **PCM5102A** had a **32.0** long bay for a **32.0** long board. Zero clearance is not a fit, it is an interference; the board could not be dropped in.

No hole pattern is needed — these are strap-down bays. The tie slots and kerbs now derive from the measured board, with asserts that the pips land under it and that adjacent bays keep ≥3 mm apart.

🚨 **Height is the new constraint.** Tray floor 4.0 + pip 1.5 + 9.5 of PCM1808 = **15.0 mm above the tray's bed face** (the 5102A pair reach 12.0). The air gap behind the display module is **4.0 mm**. The tray has no placement in the assembly yet, and this rules out the cavity directly behind the panel — it now picks where the tray goes.

## Pi + PiCAN-M stack ✅ MEASURED — 14.5 mm

Pi 4 PCB bottom to the top of the HAT: 1.6 board + 11 standoff + 1.6 HAT. The model had been carrying **17.0 mm (Pi + Armor Lite case)** as the governing case; the Armor Lite stays in the assert as the alternative, but 14.5 is what is being built.

| | mm |
|---|---|
| Bay standoff (clears solder side + SD card) | 5.0 |
| Pi + PiCAN-M | **14.5** |
| **As-built stack** | **19.5** |
| Room, bay floor to display back | **43.5** |
| Spare | **24.0** |

**The bay does not get shallower.** `PI_BUMP_H = TRUN_STAND + TRUN_R` keeps the bumps' backs coplanar with the trunnion tips, which is what gives the cover ~24,000 mm² of bed contact instead of two r15 tips. The spare depth is somewhere to put something, not a saving to take — and note it is **not** where the sensor tray needs it: the tray is 196 × 118 and the Pi bay is 82 × 125.

---

# Oak Grigsby 91Q128 — Decoded (900 Series datasheet, p0104-4126.pdf)

| Feature | Value | Source |
|---|---|---|
| Bushing thread | **3/8-32 UNEF Class 2A** | ✅ drawing |
| Panel bore | **Ø9.7** clearance | ✅ derived |
| Shaft | **Ø6.299** (0.2480 ±0.0005″), stainless | ✅ drawing |
| Body | 25.4 mm square, R6.35 | ✅ drawing |
| Panel seal groove | ID Ø11.9, OD Ø16.4, depth 0.51 | ✅ drawing |
| Nut / lockwasher | 2.36 / 0.56 mm | ✅ notes |
| Max mounting torque | 10 in·lb | ✅ specs |
| Operating temp | −40 to +85 °C (128 PPR) | ✅ specs |
| Output | 2-bit gray, A leads B CW, 5 V TTL | ✅ specs |
| **Bushing length** | **≈ 8.0 mm** | ✅ **measured on the part** (datasheet does not dimension it) |

## ⚠️ Correction

I previously read `.375 FMS` / `.875 FMS` as bushing-length options giving 6.60 / 19.30 mm of usable panel. **That was wrong** — FMS is *from mounting surface*, and those are **shaft length** options. The bushing length is not dimensioned anywhere in the datasheet.

**Consequence**: the bezel thickness limit is unconfirmed. With nut + lockwasher taking 2.92 mm, a 6.0 mm bezel needs **≥ 8.92 mm of bushing**.

| Bushing | Max panel | 6.0 mm bezel? |
|---|---|---|
| 0.250″ (6.35) | 3.43 | ✗ |
| 0.300″ (7.62) | 4.70 | ✗ |
| 0.350″ (8.89) | 5.97 | ✗ (just) |
| 0.375″ (9.52) | 6.60 | ✓ |

## ✅ Resolved — bushing measured at ≈ 8.0 mm

Nut 2.36 + lockwasher 0.56 = **2.92 mm** of stack, so 8.0 mm of bushing clamps **5.08 mm of panel, max**.
The shell face is **2.5 mm**. It fits with **2.58 mm to spare — no counterbore at the encoder.**
The 8.92 figure was for a 6.0 mm panel and never applied to this face; 2.5 mm needs only 5.42 mm.

**The shaft and knob fixing are set aside.** The stack was run and the grub screw does not land on a .375″ FMS shaft — but the owner is handling the knob at assembly, so this is not a design constraint and does not come back as a blocker. The panel result above is what the model needs.

## Two electrical notes

1. **5 V TTL output into 3.3 V Pi GPIO.** The Pi is not 5 V tolerant — needs level shifting or a divider on A and B.
2. **Do not run the encoder through the MCP23017.** 128 PPR in full quadrature is 512 edges/rev; I²C polling through an expander will drop counts. Wire A/B to Pi GPIO and use an edge-triggered handler.

Also confirms: the **panel seal groove** means the encoder can seal to the bezel — the bezel face in that Ø11.9–16.4 annulus must be flat and smooth. It prints face-down, so it is.

---

# ★ CURRENT STATE — supersedes everything above

Earlier sections are kept as history. Where they conflict with this, **this wins**.

## Printed parts (8)

| File | Size | ASA |
|---|---|---|
| `helm_shell_revB.stp` | 384 × 190 × 25 | 200 g |
| `helm_cover_revB.stp` | 384 × 174 × 35 | 322 g |
| `helm_visor_revB.stp` | 304 × 22 × 69 | 55 g |
| `heatsink_shroud_revA.stp` | 129 × 101 × 47 | 59 g |
| `sensor_tray_revA.stp` | 196 × 118 × 9 | 40 g |
| `lp24_shroud_revD.stp` | 132 × 102 × 63 | 98 g |
| `lp24_clamp_revD.stp` | 28 × 58 × 13 | 11 g |
| `helm_fit_coupon_revA.stp` | 190 × 115 × 12 | 55 g |
| | | **0.84 kg** |

## Housing — key dimensions

| | |
|---|---|
| Body | 384 × 174 × 30 |
| Depth at the Pi bump | **48 mm** (limit 50) |
| Front face | **2.5 mm** |
| Interior | 352 × 142 × 21.5 |
| Display + standoffs | 17.5 mm → 4 mm free |
| Pi bump-out | 108 × 78 × 18, protrudes **outward** |
| Aperture | 293.5 × 110.7, glue dams **raised** 2.0 mm |
| Controls | 4 buttons Ø12 at 26 mm pitch + encoder Ø9.7, right side |
| Brim | 12 × M4, 88 mm spacing, SF 4.5 |
| Visor | 58 mm hood, 45° bevel, 20 teeth @ 18°/click, M5 pivots |
| Rear | gland (−150,−55), vent (−95,−58), antenna (−160, 52), heatsink aperture 90 sq @ x=118, VESA 100 |

## Cooling — settled

All cooling is **outside** the cover. The 4 mm interior clearance cannot take a fan or inner sink.

- ONE 150 × 74 × 10 heatsink, base bonded INTO a 3 mm recess in the cover's inner face, fins out through a 59 × 135 aperture — **flexible adhesive (MS polymer / Sikaflex 291i), not epoxy**: 0.9 mm of CTE differential over 150 mm and 50 °C, and the seat walls index it so no jig is needed. Inside face is a bare plate; if it throttles, bond a second finned block to it
- 2 × Easycargo 100 × 40 × 20 outside, 1 inside on the plate
- 1 × WINSINN 5015 blower aimed at the inner fins
- Expected ≈ **56 °C internal at 45 °C ambient**; Pi throttles at 80–85

🚨 The heatsink shroud adds **45 mm behind the cover** — total stack ~93 mm at that point.

## Rules this project has produced

1. **Pilots must open toward an opening**, never into a closed volume. Verify by ray-casting a 9 mm driver corridor, not by checking for empty space.
2. **Assembly order beats geometry.** Every fastener needs a reachable path with the parts that precede it already fitted.
3. **Thread-forming pilots**: Ø2.6 for M3, Ø3.5 for M4, Ø2.2 for M2.5. Blind, with a lead-in cone.
4. **Never cut a channel deeper than the wall.** Build it up instead.
5. **Assert every string replacement.** A silent no-op patch reported success and changed nothing, twice.

## Printer ✅ — Creality K2 Plus, 350 × 350 × 350

The old "384 mm needs ≥400, or a designed split" blocker was **rev B geometry** (`helm_shell_revB` at 384 × 190) and died with rev B. Rev C's largest footprint is the shell at **334 × 194**, and `cad/print_check.py` has been asserting against a 350 bed all along. Everything fits:

| Part | Footprint | Margin on 350 |
|---|---|---|
| Front shell | 334 × 194 | 8 mm a side |
| Rear cover | 334 × 177 | 8 mm a side |
| Bail base | 327 × 96 | 11 mm a side |
| Visor | 294 × 66 | 28 mm a side |

⚠️ **The brim is what eats the margin.** 334 + 2 × brim has to stay under 350, so the shell and cover take a **5 mm brim maximum** — at 8 mm you are exactly on the limit. Outer brim only, which the slicer card already specifies.

No split needed. No larger printer needed.

## rev D — first printed shell, and what it said ⚠️

The rev C front shell came off the bed on 2026-09-17 and the display would not go in.

| | was | now | source |
|---|---|---|---|
| `MOD_H` | 130 | **131** | measured on the module |
| `MOD_D` | 15 | **12** | measured on the module |
| `CLR` | 1.0 | **1.5** | restored — see below |
| `MOD_FIT` | 0.35 | **0.80** | the index features were the binding constraint |

**The index positions were what jammed, not the cavity.** `MOD_FIT` was 0.35 per side over a **310 mm** span. ASA moves 0.4–0.7% on cooling, which is 1.2–2.2 mm across this part, so a 0.35 index fit is inside the noise — the panel hit the rails and pads before it ever reached a cavity wall. An index locates; at this length it must not also be a press fit.

`CLR` 1.0 → 1.5 for the same reason. A 1 mm cavity clearance on a 310 mm span is a number that only works on paper, and nothing anywhere in the model budgeted for shrinkage.

**Fallout:** `DIVIDER` was the typed constant `RIM - 6.0`, where the 6 was silently `BOND_BAND + CLR` evaluated at `CLR = 1.0`. Moving CLR unbalanced the bezel round the control row — 10.25 above, 9.75 below — and the balance assert caught it. It is now the identity `DIVIDER = RIM - BOND_BAND - CLR`.

`MOD_D` 15 → 12 opens the air gap behind the panel from **4.0 to 7.0 mm**. Still not the 15.0 the sensor tray needs, so that stays blocked.

🚨 **The width is NOT settled, and the model has not been changed for it.** `MOD_W` is still 310. The 1.5 mm shortfall is 0.48% of 310, which is exactly ASA's shrinkage range — so widening the CAD could be fixing a slicer problem in the wrong place, and would leave the pocket loose once compensation is set correctly.

**One measurement settles it: caliper the printed rev C shell across its overall width.** Nominal was 334.0.

- Reads **~332.4** → shrinkage. Fix it in Orca (*Filament → Advanced → Shrinkage compensation XY*, ~100.5% for ASA), not in CAD.
- Reads **~334.0** → the print is true and the module really is wider than 310. Then `MOD_W` moves.

## Still blocking

- **Display module WIDTH** — height 131 and depth 12 are now measured; width is still the assumed 310, and the first printed shell says it is out by ~1.5. See the rev D section: that 1.5 may be ASA shrinkage, not the module
- **Panel thickness + on-face or recessed** — blocks the bottom hinge
- **Sensor tray placement** — the PCM1808 stack is 15.0 mm tall and the cavity behind the display is 4.0. The 24 mm of spare depth is in the Pi bay, which is 82 × 125 against a 196 × 118 tray, so it does not solve it. The tray outline was always provisional and this is what re-cuts it
- Cable OD, PiCAN-M footprint
