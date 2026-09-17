"""
Build Manual -- print it, then build it, in the order that works.

This is the document for somebody who is NOT the designer: they have the STLs,
a printer, a bag of 316 hardware and no memory of why any of it is shaped the
way it is. The build page (cad/build_review.py) argues the design. This one
does not argue anything - it tells you what to buy, what to set the slicer to,
and what to do first.

THE ORDER IS NOT AN OPINION. cad/assembly_check.py sweeps a real driver down
every fastener's axis and slides every part along the line it travels, stepped
through this exact sequence, and refuses to pass if a step is blocked by the
parts already fitted. The order below is that sequence. Where a step says a
thing must happen before another, it is because doing it the other way round
fails a check, not because it reads better.

Everything dimensional is read from cad/out/*.json. There are no typed
dimensions in this file, and that is the point: a manual that disagrees with
the part is worse than no manual.
"""
import json, math, base64, os

H = json.load(open("cad/out/housing.json"))
S = json.load(open("cad/out/shroud.json"))
B = json.load(open("cad/out/bail.json"))
V = json.load(open("cad/out/visor.json")) if os.path.exists("cad/out/visor.json") else {}

OUT_W, OUT_H, DEPTH, COVER_T = H["OUT_W"], H["OUT_H"], H["DEPTH"], H["COVER_T"]
NBOLT = H["N_BRIM_BOLTS"]
REAR = DEPTH + H["GASKET_C"] + COVER_T + S["REAR_PROUD"]


def img(name, cap, note="", wide=False):
    p = f"cad/out/{name}.png"
    if not os.path.exists(p):
        return (f'<figure class="{"wide" if wide else ""}"><div class="missing">'
                f'{name} not built</div><figcaption>{cap}</figcaption></figure>')
    b64 = base64.b64encode(open(p, "rb").read()).decode()
    return (f'<figure class="{"wide" if wide else ""}">'
            f'<img src="data:image/png;base64,{b64}" alt="{cap}">'
            f'<figcaption><b>{cap}</b>{" &mdash; " + note if note else ""}</figcaption></figure>')


# ══════════════════════════════════════════════════════════ 1. TOOLS
TOOLS = [
    ("3D printer", f"{H['BED']:.0f} &times; {H['BED']:.0f} bed minimum, enclosed, "
                   f"bed to 100&nbsp;&deg;C. The shell and cover are {OUT_W:.0f} mm long "
                   f"with 8&nbsp;mm a side to spare"),
    ("Hex driver, 2.5&nbsp;mm", "every M3 on the unit"),
    ("Hex driver, 4&nbsp;mm", "the arm feet"),
    ("5-lobe knobs, M5 &times; 20 stud &times;2", "the tilt joints &mdash; buy the "
     "<b>20&nbsp;mm</b> stud, not 25: 25 drives into the bay wall"),
    ("Spanner / socket, 22&nbsp;mm A/F", "the M16 cable gland"),
    ("Spanner / socket, 19&nbsp;mm A/F", "the M12 Gore vent"),
    ("Spanner, 12&nbsp;mm A/F", "the M8 SMA bulkhead"),
    ("Taps: M16&times;1.5, M12&times;1.5, M8&times;0.75",
     "the three fittings thread straight into printed bosses"),
    ("Soldering iron with an insert tip", "4 &times; M5 heat-set inserts in the bail arms"),
    ("Torque driver, 0.5&ndash;2&nbsp;N&middot;m", "optional but it is how you avoid "
     "stripping a thread-formed M3 in ASA"),
    ("Caulking gun", "for the display bond and the potting"),
    ("Isopropyl alcohol, lint-free cloth", "every bonded surface, twice"),
]

# ══════════════════════════════════════════════════════════ 2. PRINTED PARTS
PRINTED = [
    ("Front shell", "helm_shell_revD", "front A-surface down", "none",
     "The face is the bed. Nothing stands proud of it, which is why it prints "
     "with no support at all &mdash; keep it that way if you modify anything."),
    ("Rear cover", "helm_cover_revD", "bumps down", "under the plate",
     f"The one part that needs support. It rests on the two bay bumps and the "
     f"fitting blocks &mdash; about 24,000&nbsp;mm&sup2; &mdash; and its plate is then a flat "
     f"roof {H['PI_BUMP_H']:.0f}&nbsp;mm up spanning between them. The support interface "
     f"lands on the weather face, where a witness mark does not matter, and the "
     f"cord&rsquo;s sealing face ends up as the top surface where it prints smooth."),
    ("Sun visor", "helm_visor_revD", "hood underside down, ears up", "none",
     "The hood hangs below the ear rims by design so the part lies flat."),
    ("Fan shroud", "heatsink_shroud_revD", "louvre tips + rim on the bed, walls up", "none",
     "The louvre slats are 45&deg; on purpose and print unaided. Open-end-down "
     "would turn the two internal ribs into 162&nbsp;mm bridges."),
    ("Bail base plate", "bail_base_revA", "plate flat on the bed", "none",
     "98% of its footprint on the bed. Nothing to think about."),
    ("Bail arm &times;2", "bail_arm_revA", "blade and pad flat", "none",
     "Print TWO. The foot pad thickens the blade on one side only, so one face "
     "is flat &mdash; that face goes down."),
]

# Field names are ORCA SLICER's, because that is what is being used. Orca calls
# perimeters "wall loops" and infill "sparse infill", which is the one thing that
# makes a settings list from anywhere else unreadable at the machine.
SLICER = [
    ("Material", "ASA. Not PETG: this lives on a sun-baked dash and PETG creeps"),
    ("Nozzle", "0.4&nbsp;mm"),
    ("Layer", "0.2&nbsp;mm, first layer 0.24 &mdash; <i>Quality &rsaquo; Layer height</i>"),
    ("Wall loops", "<b>5 on the shell and cover</b>, 4 elsewhere. The cover is the "
                   "pressure boundary and walls are what stop a leak path. "
                   "<i>Strength &rsaquo; Wall loops</i> (Orca&rsquo;s name for perimeters)"),
    ("Sparse infill", "<b>40%</b> on the shell, cover and bail arms; 25% elsewhere. "
                      "Pattern <b>Gyroid</b>. <i>Strength &rsaquo; Sparse infill density / "
                      "Sparse infill pattern</i>. Right-click a part on the plate for "
                      "<i>per-object settings</i> so one plate can hold both numbers. "
                      "<b>Gyroid is a SPARSE pattern only</b> &mdash; it is not offered for "
                      "solid layers, and should not be"),
    ("Top / bottom surface", "Leave both on <b>Monotonic</b>. <i>Strength &rsaquo; Top surface "
                             "pattern / Bottom surface pattern</i>. These are solid-layer "
                             "patterns and share nothing with the gyroid above"),
    ("Ironing", "<b>Top surfaces</b> on the shell and cover &mdash; <i>Quality &rsaquo; Ironing "
                "&rsaquo; Ironing type</i>. This is the setting that answers &ldquo;the printed "
                "sealing face leaks through layer lines&rdquo;, because on this build <b>both "
                "sealing faces print facing UP</b>: the shell goes A-surface down so its brim and "
                "cord groove are the top, and the cover goes bumps-down so its mating face points "
                "up too. Pick <b>Top surfaces</b>, not <i>Topmost surface only</i> &mdash; the "
                "cover&rsquo;s mating face is 37 mm below its own outer face, so "
                "&ldquo;topmost&rdquo; would skip the one that matters"),
    ("A-surface finish", "The bezel&rsquo;s weather face is the <b>first layer</b> &mdash; it "
                         "prints A-surface down, so what you see on the finished part is the "
                         "bed. <b>Bed surface and Z-offset decide this, not flow.</b> Smooth "
                         "PEI or glass for gloss; textured PEI stamps its texture into the "
                         "face you look at every day. If you still want to close the extrusion "
                         "lines, nudge <i>Quality &rsaquo; Precision &rsaquo; Bottom surface "
                         "flow ratio</i> to ~1.02&ndash;1.05 &mdash; that touches bottom solid "
                         "layers only, where the global flow ratio would move the walls and "
                         "every bore with them. Expect elephant&rsquo;s foot and trim it with "
                         "<i>Elephant foot compensation</i>"),
    ("&#9888; ORDER", "<b>Any flow or first-layer change invalidates the fit coupon.</b> Flow "
                      "and squish move hole size, so the coupon&rsquo;s &Oslash;8.00 ladder only "
                      "reads true for the settings it was printed with. Settle bed, Z-offset and "
                      "flow FIRST, then print the coupon, then read X-Y hole compensation off it. "
                      "Do it the other way round and you have calibrated a profile you are no "
                      "longer using"),
    ("Hole compensation", "<b>Set this from the fit coupon, not from a guess.</b> The coupon "
                          "prints a ladder of five nominally &Oslash;8.00 holes at +0.0 to "
                          "+0.4. Measure all five, see which reads 8.00, and put that offset "
                          "in <i>Quality &rsaquo; Precision &rsaquo; X-Y hole compensation</i>. "
                          "Every bore on this build &mdash; encoder, buttons, gland, vent "
                          "&mdash; depends on it"),
    ("Enclosure", f"Required. A {H['OUT_W']:.0f}&nbsp;mm ASA plate will lift its corners in a draught. "
                  "Part cooling fan low (ASA wants the heat), <i>Filament &rsaquo; Cooling</i>"),
    ("Bed", f"90&ndash;100&nbsp;&deg;C, brim on both big plates &mdash; "
            f"<i>Others &rsaquo; Brim type: Outer brim only</i>. <b>Brim width 5&nbsp;mm "
            f"maximum on the shell and cover.</b> They are {H['OUT_W']:.0f} wide on a "
            f"{H['BED']:.0f} bed, so {H['OUT_W']:.0f} + 2&times;brim has to stay under "
            f"{H['BED']:.0f} &mdash; that leaves {(H['BED']-H['OUT_W'])/2:.1f}&nbsp;mm a side"),
    ("Supports", "Only the rear cover, and only under the plate"),
]

# ══════════════════════════════════════════════════════════ 3. THE ORDER
# Lifted from cad/assembly_check.py's stages, which is the sequence it verifies.
STEPS = [
 ("Tap the three fittings, cover on the bench",
  [f"The gland, the vent and the coax entry all thread into printed blocks beside "
   f"the bay bumps. <b>Do this first, with the cover bare.</b> Once the boards, the "
   f"heatsink or the shroud are on, nothing reaches them.",
   f"Tap the <b>&minus;x bottom block</b> M16&times;1.5 at x={H['GL_X']:.0f} for the cable "
   f"gland (drill is already {H['GL_TAP']}).",
   f"Tap the <b>+x bottom block</b> M12&times;1.5 at x={H['VENT_X']:.0f} for the Gore vent.",
   f"Tap the <b>+x TOP block</b> M8&times;0.75 at x={H['SMA_X']:.0f} for the SMA. Drop the "
   f"bulkhead&rsquo;s nut into the {H['SMA_NUT_AF']:.0f}&nbsp;mm hex pocket on the inner face "
   f"first &mdash; it is captive there and you will not be able to hold it later.",
   "Run a smear of thread sealant on each and nip them up. All three point "
   "<b>downward or upward, never aft</b>, so none of them can stand in water."],
  "sub_fittings_context", "the three fittings and which way each one faces"),

 ("Bond the heatsink into its seat",
  [f"The heatsink goes in <b>from the inside</b>: its base drops into the "
   f"{H['HS_L']:.0f} &times; {H['HS_W']:.0f} pocket in the cover&rsquo;s inner face and its "
   f"fins pass through the aperture to stand {H['HS_PROUD']:.0f}&nbsp;mm proud outside.",
   f"<b>Trim the fins back {H['AP_SEAL']:.0f}&nbsp;mm all round first.</b> A bought extrusion "
   f"carries fins to the edge of its base; those outer fins are what the seat and "
   f"the bond land on.",
   "Degrease both faces with IPA. Use a <b>flexible</b> adhesive &mdash; MS polymer or "
   "Sikaflex 291i &mdash; not epoxy: aluminium and ASA move 0.9&nbsp;mm differently over "
   "150&nbsp;mm and 50&nbsp;&deg;C, and a rigid bond will let go.",
   f"The pocket walls index it, so there is no jig. Clamp light and leave it."],
  "sub_thermal_exploded", "cover, heatsink, mesh, two fans, shroud &mdash; in fitting order"),

 ("Boards into their bays",
  [f"Both boards drop in <b>from the inside</b> of the cover and sit on printed bosses.",
   f"<b>&minus;x bay:</b> Raspberry Pi 4 on four M2.5 &times; 6 into the "
   f"{H['PI_STANDOFF_H']:.0f}&nbsp;mm bosses, connector stack facing the bay&rsquo;s long axis.",
   f"<b>+x bay:</b> the {H['SDR_L']:.0f} &times; {H['SDR_W']:.0f} LCD driver board on its four "
   f"M2.5, then the RTL-SDR <b>standing on edge</b> in the 19&nbsp;mm strip beside it, "
   f"strapped to the two tie anchors on the bay floor.",
   "Pot the fan leads now if you are running them: the &Oslash;6 pass is in the "
   "strip between the heatsink seat and the shroud wall, with a dam on the inner "
   "face to hold the compound."],
  "sub_wire_pass", "the only penetration that is not a screw"),

 ("Display into the shell, then the cover on",
  [f"Bond the panel into the front shell&rsquo;s seat. The rails and side pads locate "
   f"it; leave the {H['GLUE_T']} mm bond line &mdash; do not squeeze it to nothing.",
   f"Lay the <b>3&nbsp;mm cord</b> into the groove in the shell&rsquo;s brim. Scarf the ends "
   f"and glue the joint away from the bottom edge. The groove is <b>split between "
   f"the two halves</b> &mdash; {H['GASKET_D']:.2f} in the brim and {H['GASKET_D_COVER']:.2f} in the "
   f"cover &mdash; so the cord is captured on both sides and cannot roll out as the lid "
   f"goes down.",
   f"Cover on. <b>{len(H['DSP_POSTS'])} &times; M3 panel screws first</b>, through the cover&rsquo;s "
   f"bearing posts into the display&rsquo;s own standoffs, each with a bonded washer.",
   f"Then <b>{NBOLT} &times; M3 brim screws</b> at {H['BOLT_PITCH']:.0f}&nbsp;mm pitch. These are "
   f"outboard of the cord and go into blind pilots, so they are not a leak path &mdash; "
   f"but pack each one with Tef-Gel: a blind hole full of seawater around a 316 "
   f"thread is a crevice.",
   "<b>Do this before the shroud.</b> Four of the brim screws end up underneath it."],
  "asm_exploded", "the housing stack"),

 ("Fans and mesh into the shroud, shroud onto the cover",
  [f"Lay the 316 mesh on the eight fan bosses inside the shroud, then both "
   f"{S['FAN_W']:.0f}&nbsp;mm fans on top of it. The fan screws clamp the mesh &mdash; there "
   f"is no separate retainer.",
   "Check the fans blow <b>inward</b>, onto the fins. The louvres are the intake.",
   f"Shroud onto the cover and <b>4 &times; M3 &times; {S['SCREW_L']:.0f}</b> from the "
   f"<b>louvred face</b> &mdash; the only face you can still reach &mdash; down the corner "
   f"bosses into the cover&rsquo;s pilot bosses. They stop blind; they never enter the box."],
  "sub_shroud_fixing", "sectioned through two corner bosses"),

 ("Bail arms onto the trunnions",
  [f"<b>The unit does not drop between the arms.</b> It is {OUT_W:.0f}&nbsp;mm wide and the "
   f"arms&rsquo; inner faces are {2*B['ARM_FACE']:.0f} apart. Each arm goes on "
   f"<b>sideways, from outboard</b>, and the unit + arms assembly then goes onto the base.",
   f"Per side, outboard to inboard: knob or cap screw &rarr; arm eye &rarr; "
   f"<b>316 serrated washer pair</b> &rarr; trunnion land &rarr; the M5 nyloc captive in "
   f"the {H['TRUN_NUT_AF']:.0f}&nbsp;mm hex pocket in the web. The eye is counterbored "
   f"{B['EYE_CB']:.0f}&nbsp;mm so a stock M5 &times; {B['KNOB_STUD']:.0f} knob stud engages the "
   f"whole nut and still stops 1&nbsp;mm short of the bay wall.",
   "The serrated pair is what holds the tilt &mdash; teeth, not friction. Set it by "
   "hand: firm enough to stay, loose enough to move.",
   f"Fit the <b>M5 heat-set inserts</b> into the arms&rsquo; foot pads now, while the arms "
   f"are still loose and you can get an iron square to them."],
  "asm_housing_rear", "arms on the trunnions, inside the bezel line"),

 ("Onto the base plate, then the dash",
  [f"Lower the unit and arms onto the base plate. <b>Bolt the feet from "
   f"underneath</b> &mdash; M5 &times; 16 up through the plate into the inserts in the pads. "
   f"This is why the arms go on the plate before the plate goes on the dash.",
   f"Then the plate to the dash through its {B['N_DASH']} slots, in two rows "
   f"{B['DASH_ROWS']:.0f}&nbsp;mm apart so the rows take the peel moment.",
   f"Screw the whip onto the SMA on top of the +x bump.",
   f"Tilt range is <b>{B['TILT_DOWN']:.0f}&deg; to {B['TILT_UP']:.0f}&deg;, face up only.</b> "
   f"The arms run inside the bezel width, so face-down swings the unit into them."],
  "asm_visor_deployed", "on the bail, visor deployed"),
]

SERVICE = [
    ("To open the box", "Shroud off (4 screws), then the unit off the bail &mdash; "
     "4 brim screws sit under the shroud and 5 under the arms."),
    ("To change the mesh or a fan", "Shroud off. Everything else stays."),
    ("To re-seal", "New cord every time the cover comes off. It is a 3&nbsp;mm cord "
     "at 85% groove fill; a reused one has taken a set."),
    ("Never", "reach the three fittings with the unit mounted. Nothing does. "
     "They are bench-fit and bench-sealed."),
]

# ══════════════════════════════════════════════════════════ RENDER
CSS = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#12171d;--ink2:#48566a;--line:#d8dee7;
 --accent:#1f5fa6;--accent-soft:#e6eefa;--warn:#8a4b00;--warn-soft:#fdf1de}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
 --bg:#0d1218;--card:#151c25;--ink:#dce4ee;--ink2:#94a3b6;--line:#242f3c;
 --accent:#63a0dd;--accent-soft:#152a41;--warn:#d59a54;--warn-soft:#2c2113}}
:root[data-theme=dark]{--bg:#0d1218;--card:#151c25;--ink:#dce4ee;--ink2:#94a3b6;
 --line:#242f3c;--accent:#63a0dd;--accent-soft:#152a41;--warn:#d59a54;--warn-soft:#2c2113}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
 font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.wrap{max-width:1000px;margin:0 auto;padding:0 20px 100px}
header{padding:56px 0 28px;border-bottom:3px solid var(--ink);margin-bottom:40px}
h1{margin:0;font-size:38px;letter-spacing:-.02em;line-height:1.1}
.sub{color:var(--ink2);margin-top:10px;font-size:17px;max-width:62ch}
h2{margin:52px 0 6px;font-size:25px;letter-spacing:-.01em}
h2 .n{color:var(--accent);font-variant-numeric:tabular-nums}
h3{margin:26px 0 6px;font-size:18px}
p{margin:10px 0}
ol.steps{list-style:none;counter-reset:s;padding:0;margin:0}
ol.steps>li{counter-increment:s;background:var(--card);border:1px solid var(--line);
 border-radius:10px;padding:22px 24px;margin:18px 0}
ol.steps>li>h2{margin:0 0 10px;font-size:22px;display:flex;gap:12px;align-items:baseline}
ol.steps>li>h2::before{content:counter(s);background:var(--accent);color:#fff;
 min-width:34px;height:34px;border-radius:8px;display:inline-grid;place-items:center;
 font-size:17px;font-weight:700;flex:none}
ul{margin:8px 0;padding-left:22px}
li{margin:6px 0}
table{width:100%;border-collapse:collapse;margin:14px 0;font-size:15px}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:var(--accent-soft);font-weight:600}
td:first-child{font-weight:600;white-space:nowrap}
figure{margin:18px 0;background:var(--card);border:1px solid var(--line);
 border-radius:10px;overflow:hidden}
figure img{display:block;width:100%}
figcaption{padding:10px 14px;font-size:14px;color:var(--ink2);border-top:1px solid var(--line)}
.missing{padding:60px;text-align:center;color:var(--ink2);font-style:italic}
.flag{background:var(--warn-soft);border-left:4px solid var(--warn);
 padding:14px 18px;border-radius:0 8px 8px 0;margin:16px 0}
.flag b{color:var(--warn)}
.kv{display:grid;grid-template-columns:auto 1fr;gap:2px 18px;font-size:15px}
.kv dt{font-weight:600;color:var(--ink2)}
.kv dd{margin:0}
code{background:var(--accent-soft);padding:1px 6px;border-radius:4px;font-size:14px}
"""

html = [f"""<title>Helm Display &mdash; Build Manual</title>
<style>{CSS}</style>
<div class="wrap">
<header>
<h1>Marine Helm Display<br>Build Manual</h1>
<p class="sub">A 12.3&Prime; sunlight-readable glass helm in a printed ASA enclosure:
Raspberry&nbsp;Pi&nbsp;4, NMEA&nbsp;2000, sealed to a 3&nbsp;mm cord, fan-cooled, on a
tilting bail. Everything below is generated from the CAD, so it cannot disagree
with the parts you are holding.</p>
<dl class="kv">
<dt>Unit</dt><dd>{OUT_W:.0f} &times; {OUT_H:.0f} &times; {REAR:.0f}&nbsp;mm over the fan shroud</dd>
<dt>On the dash</dt><dd>{B['RISE'] + OUT_H/2 - H['TILT_Y']:.0f}&nbsp;mm tall, axis {B['RISE']:.0f}&nbsp;mm up</dd>
<dt>Printed parts</dt><dd>{len(PRINTED)} designs, 7 pieces</dd>
<dt>Tilt</dt><dd>{B['TILT_DOWN']:.0f}&deg; to {B['TILT_UP']:.0f}&deg;, face up</dd>
</dl>
</header>
"""]

html.append('<h2><span class="n">A.</span> Tools</h2><table><tr><th>Tool</th><th>What for</th></tr>')
for t, w in TOOLS:
    html.append(f"<tr><td>{t}</td><td>{w}</td></tr>")
html.append("</table>")

html.append('<h2><span class="n">B.</span> Printing</h2>')
html.append('<table><tr><th>Setting</th><th></th></tr>')
for k, v in SLICER:
    html.append(f"<tr><td>{k}</td><td>{v}</td></tr>")
html.append("</table>")
html.append("<h3>The seven pieces</h3><table><tr><th>Part</th><th>Lay it</th>"
            "<th>Support</th><th>Notes</th></tr>")
for name, stem, orient, sup, note in PRINTED:
    html.append(f"<tr><td>{name}</td><td>{orient}</td><td>{sup}</td><td>{note}</td></tr>")
html.append("</table>")
html.append('<div class="flag"><b>The cover is the only part that needs support.</b> '
            'Everything else lies flat on a real face. If you change a part and it '
            'stops doing that, <code>cad/print_check.py</code> will say so &mdash; it '
            'measures first-layer contact rather than trusting the orientation note.</div>')

html.append('<h2><span class="n">C.</span> Assembly, in order</h2>')
html.append('<p>This sequence is verified by <code>cad/assembly_check.py</code>, which '
            'sweeps a real driver down every fastener and slides every part along the '
            'path it travels, judging each step against only the parts already fitted. '
            'Steps that must come first are marked; they are the ones that fail if you '
            'swap them.</p>')
html.append('<ol class="steps">')
for title, bullets, pic, cap in STEPS:
    html.append(f"<li><h2>{title}</h2><ul>")
    for b in bullets:
        html.append(f"<li>{b}</li>")
    html.append("</ul>")
    html.append(img(pic, cap))
    html.append("</li>")
html.append("</ol>")

html.append('<h2><span class="n">D.</span> The exploded view</h2>')
html.append(img("exp_a", "Exploded, from the front", "every numbered item in the bill of materials", wide=True))
html.append(img("exp_rear", "Exploded, from behind",
                "the bumps, the fitting blocks, the shroud and the bail only read from this side", wide=True))

html.append('<h2><span class="n">E.</span> Service</h2><table><tr><th>Job</th><th>What it costs</th></tr>')
for k, v in SERVICE:
    html.append(f"<tr><td>{k}</td><td>{v}</td></tr>")
html.append("</table>")
html.append(f'<p style="color:var(--ink2);font-size:14px;margin-top:50px">'
            f'Generated from the CAD by <code>cad/build_manual.py</code>. '
            f'Rev {H["REV"]}. Every dimension on this page is read from '
            f'<code>cad/out/*.json</code>.</p>')
html.append("</div>")

open("cad/out/manual.html", "w").write("\n".join(html))
print(f"  manual.html  {len('\n'.join(html))//1024} KB, {len(STEPS)} steps")
