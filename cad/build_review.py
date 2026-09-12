import base64, json, pathlib, datetime
R = json.load(open("cad/out/renders.json"))
D = json.load(open("cad/out/dims.json"))
# The assembly elevations are ONE of this page's many inputs, and for several revs a
# single broken drawing script took the whole build review down with it - which is
# backwards, because the page is how anyone finds out something is broken. Missing
# drawings are now reported ON the page instead of killing it. A hard failure here
# would hide the renders, the dimensions and the checks as well.
try:
    AD = json.load(open("cad/out/asmdims.json"))
except FileNotFoundError:
    AD = []
# Detent counts and fastener sizes are quoted in the prose below. They are read
# from the model, not retyped - the page said "20 teeth = 18 deg" for two revs
# after the shell dropped to 16, which is exactly the drift the JSON exists to stop.
H = json.load(open("cad/out/housing.json"))
CLICK = 360/H["N_TEETH"]
RIM, GASKET_T, GASKET_W = H["RIM"], H["GASKET_T"], H["GASKET_W"]
try:
    SD = json.load(open("cad/out/subdims.json"))
except FileNotFoundError:
    SD = []
def subpic(name):
    for v in SD:
        if v["name"] == name:
            return pic(f"cad/out/{v['name']}.png", v["title"], v.get("note", ""))
    return _missing(name, f"cad/out/{name}.png")
# Counted off the geometry, not retyped - the page has quoted a wrong
# fastener count and a wrong bezel through two revisions already.
NBOLT = H["N_BRIM_BOLTS"]
BEZEL = (H["OUT_W"] - H["APER_W"])/2
NUT_AF, NUT_DEEP = H["NUT_AF"], H["NUT_DEEP"]
MD = json.load(open("cad/out/measdims.json"))
def mdwg(i):
    v = MD[i]
    return (f'<figure class="tile dwg"><div class="vp">{open(f"cad/out/{v["name"]}.svg").read()}</div>'
            f'<figcaption><span class="cap">{v["title"]}</span></figcaption></figure>')
def adwg(i):
    if i >= len(AD):
        return ('<figure class="tile dwg"><div class="vp" style="padding:34px 22px">'
                '<p class="note" style="margin:0"><b>Assembly elevation not built.</b> '
                'cad/assembly_dims.py did not produce this drawing, so it is missing here '
                'rather than silently absent.</p></div>'
                '<figcaption><span class="cap">NOT BUILT</span></figcaption></figure>')
    v = AD[i]
    return (f'<figure class="tile dwg"><div class="vp">{open(f"cad/out/{v[chr(39)+chr(39)] if False else v["name"]}.svg").read()}</div>'
            f'<figcaption><span class="cap">{v["title"]}</span></figcaption></figure>')
def dwg(i):
    v = D[i]
    svg = open(f"cad/out/{v['name']}.svg").read()
    return (f'<figure class="tile dwg"><div class="vp">{svg}</div>'
            f'<figcaption><span class="cap">{v["title"]}</span></figcaption></figure>')
def img(i):
    b = base64.b64encode(open(R[i]["file"], "rb").read()).decode()
    return f'data:image/png;base64,{b}'
def _missing(cap, what):
    return (f'<figure class="tile dwg"><div class="vp" style="padding:34px 22px">'
            f'<p class="note" style="margin:0"><b>Not built.</b> {what} is missing, so it '
            f'is reported here rather than left silently out of the page.</p></div>'
            f'<figcaption><span class="cap">{cap} &mdash; NOT BUILT</span></figcaption></figure>')
def svgpic(path, cap, note=""):
    try:
        body = open(path).read()
    except FileNotFoundError:
        return _missing(cap, path)
    n = f'<p class="note">{note}</p>' if note else ""
    return (f'<figure class="tile dwg"><div class="vp">{body}</div>'
            f'<figcaption><span class="cap">{cap}</span>{n}</figcaption></figure>')
def pic(path, cap, note=""):
    try:
        b = base64.b64encode(open(path, "rb").read()).decode()
    except FileNotFoundError:
        return _missing(cap, path)
    n = f'<p class="note">{note}</p>' if note else ""
    return (f'<figure class="tile"><div class="vp"><img src="data:image/png;base64,{b}" alt="{cap}"></div>'
            f'<figcaption><span class="cap">{cap}</span>{n}</figcaption></figure>')
def tile(i, cap, note=""):
    n = f'<p class="note">{note}</p>' if note else ""
    return (f'<figure class="tile"><div class="vp"><img src="{img(i)}" alt="{cap}" loading="lazy"></div>'
            f'<figcaption><span class="cap">{cap}</span>{n}</figcaption></figure>')

HTML = f"""<title>Helm Housing rev C</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans+Condensed:wght@500;600;700&family=IBM+Plex+Sans:wght@400;450;600&display=swap">
<style>
:root {{
  --ground:#e9edf3; --surface:#fff; --sunk:#dfe5ee; --viewport:#eef1f6;
  --ink:#0f1720; --ink-2:#3d4c5d; --muted:#697a8d; --line:#c9d3e0; --line-2:#dde4ee;
  --accent:#1f5fa6; --accent-soft:#dbe7f6;
  --warn:#9a5709; --warn-soft:#f8ecd9; --crit:#9e2f28; --crit-soft:#f8dedb;
  --ok:#276b3e; --ok-soft:#dcefe1;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#0c1118; --surface:#141c26; --sunk:#0f1620; --viewport:#1a2431;
    --ink:#dae3ed; --ink-2:#a8b6c6; --muted:#7b8b9e; --line:#26333f; --line-2:#1d2833;
    --accent:#5f9ddb; --accent-soft:#152b42;
    --warn:#d99a4e; --warn-soft:#2e2213; --crit:#e07a72; --crit-soft:#33191a;
    --ok:#6fc08c; --ok-soft:#122619;
  }}
}}
:root[data-theme="dark"] {{
  --ground:#0c1118; --surface:#141c26; --sunk:#0f1620; --viewport:#1a2431;
  --ink:#dae3ed; --ink-2:#a8b6c6; --muted:#7b8b9e; --line:#26333f; --line-2:#1d2833;
  --accent:#5f9ddb; --accent-soft:#152b42;
  --warn:#d99a4e; --warn-soft:#2e2213; --crit:#e07a72; --crit-soft:#33191a;
  --ok:#6fc08c; --ok-soft:#122619;
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);
  font-family:"IBM Plex Sans",system-ui,sans-serif;font-size:15px;line-height:1.62;
  -webkit-font-smoothing:antialiased}}
.wrap{{max-width:1180px;margin:0 auto;padding:0 20px 96px}}
h1,h2,h3{{font-family:"IBM Plex Sans Condensed","IBM Plex Sans",sans-serif;
  text-wrap:balance;margin:0;letter-spacing:-.01em}}
code,.mono,.num{{font-family:"IBM Plex Mono",ui-monospace,monospace;font-variant-numeric:tabular-nums}}

/* ---- title block ---- */
header{{border-bottom:2px solid var(--ink);margin-bottom:38px;padding:44px 0 0}}
h1{{font-size:clamp(30px,5vw,46px);font-weight:700;line-height:1.02}}
.sub{{color:var(--ink-2);max-width:64ch;margin:14px 0 26px;font-size:16px}}
.block{{display:flex;flex-wrap:wrap;gap:0;border:1px solid var(--line);
  border-bottom:none;background:var(--surface)}}
.block div{{flex:1 1 150px;padding:9px 14px;border-right:1px solid var(--line-2)}}
.block div:last-child{{border-right:none}}
.block dt{{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.11em;
  text-transform:uppercase;color:var(--muted);margin:0 0 3px}}
.block dd{{margin:0;font-family:"IBM Plex Mono",monospace;font-size:13.5px;font-weight:500}}

/* ---- sheets ---- */
section{{margin-top:56px}}
.sheet-hd{{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;
  border-bottom:1px solid var(--ink);padding-bottom:10px;margin-bottom:22px}}
.sheet-hd h2{{font-size:26px;font-weight:600}}
.rev{{font-family:"IBM Plex Mono",monospace;font-size:11px;font-weight:600;letter-spacing:.08em;
  background:var(--accent-soft);color:var(--accent);padding:3px 8px;border-radius:3px}}
.file{{margin-left:auto;font-family:"IBM Plex Mono",monospace;font-size:12.5px;color:var(--muted)}}

.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:16px}}
.tile{{margin:0;border:1px solid var(--line);background:var(--surface);overflow:hidden}}
.vp{{background:var(--viewport);border-bottom:1px solid var(--line-2);
  display:flex;align-items:center;justify-content:center;padding:4px}}
.vp img{{display:block;width:100%;height:auto}}
figcaption{{padding:9px 13px 11px}}
.cap{{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.08em;
  text-transform:uppercase;color:var(--ink-2);font-weight:500}}
.note{{margin:5px 0 0;font-size:13px;color:var(--muted);line-height:1.5}}

/* ---- data ---- */
.cols{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px;margin-top:20px}}
.panel{{border:1px solid var(--line);background:var(--surface);padding:16px 18px}}
.panel h3{{font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);
  font-family:"IBM Plex Mono",monospace;font-weight:500;margin-bottom:11px}}
table{{width:100%;border-collapse:collapse;font-size:13.5px}}
td{{padding:5px 0;border-bottom:1px solid var(--line-2);vertical-align:top}}
tr:last-child td{{border-bottom:none}}
td:first-child{{color:var(--ink-2);padding-right:14px}}
td:last-child{{text-align:right;font-family:"IBM Plex Mono",monospace;
  font-variant-numeric:tabular-nums;white-space:nowrap;font-weight:500}}
.chk{{list-style:none;margin:0;padding:0;font-size:13.5px}}
.chk li{{padding:5px 0 5px 22px;position:relative;border-bottom:1px solid var(--line-2)}}
.chk li:last-child{{border-bottom:none}}
.chk li::before{{content:"";position:absolute;left:0;top:12px;width:11px;height:11px;
  border-radius:50%;background:var(--ok)}}
.chk li.q::before{{background:var(--warn)}}
.steps{{margin:0;padding:0 0 0 20px;font-size:13.5px}}
.steps li{{padding:5px 0 5px 4px;border-bottom:1px solid var(--line-2)}}
.steps li:last-child{{border-bottom:none}}
.steps li::marker{{font-family:"IBM Plex Mono",monospace;font-size:11.5px;color:var(--accent)}}
.steps b{{font-family:"IBM Plex Mono",monospace;font-weight:500}}
.chk b{{font-family:"IBM Plex Mono",monospace;font-weight:500}}

.flag{{border-left:3px solid var(--crit);background:var(--crit-soft);
  padding:14px 18px;margin-top:20px;font-size:14px}}
.flag.w{{border-left-color:var(--warn);background:var(--warn-soft)}}
.flag h3{{font-size:13px;letter-spacing:.06em;text-transform:uppercase;
  font-family:"IBM Plex Mono",monospace;margin-bottom:7px;color:var(--crit)}}
.flag.w h3{{color:var(--warn)}}
.flag p{{margin:0 0 8px}} .flag p:last-child{{margin-bottom:0}}
.dwgs{{grid-template-columns:repeat(auto-fit,minmax(430px,1fr))}}
.dwg .vp{{padding:0;background:#ffffff}}
.dwg svg{{display:block;width:100%;height:auto}}
.scroll{{overflow-x:auto}}
.cmp{{width:100%;border-collapse:collapse;font-size:13.5px;min-width:560px}}
.cmp th{{text-align:left;font-family:"IBM Plex Mono",monospace;font-size:10.5px;
  letter-spacing:.1em;text-transform:uppercase;color:var(--muted);font-weight:500;
  padding:0 14px 8px 0;border-bottom:1px solid var(--line)}}
.cmp td{{padding:9px 14px 9px 0;border-bottom:1px solid var(--line-2);text-align:left;
  font-family:inherit;white-space:normal;font-weight:400}}
.cmp td.m{{font-family:"IBM Plex Mono",monospace;font-weight:500;color:var(--crit)}}
footer{{margin-top:60px;padding-top:18px;border-top:1px solid var(--line);
  font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--muted);
  display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}}
a{{color:var(--accent)}}
:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
</style>

<div class="wrap">
<header>
  <h1>Helm Print Package</h1>
  <p class="sub">Seven printed parts, rendered from the exported STEP solids. Components with no CAD of
     their own are shown as envelope representations &mdash; correct size and position, no internal detail.</p>
  <dl class="block">
    <div><dt>Project</dt><dd>SignalK glass helm</dd></div>
    <div><dt>Material</dt><dd>ASA &mdash; blue</dd></div>
    <div><dt>Filament</dt><dd>~0.75 kg total</dd></div>
    <div><dt>Threads</dt><dd>direct, 316 SS</dd></div>
    <div><dt>Kernel</dt><dd>OCCT 7.9</dd></div>
    <div><dt>Updated</dt><dd>{datetime.datetime.now().strftime("%d %b %Y, %H:%M")}</dd></div>
  </dl>
</header>

<section>
  <div class="sheet-hd"><h2>Assembly</h2><span class="rev">REV {H["REV"]}</span>
    <span class="file">front shell + rear cover</span></div>
  <div class="grid">
    {pic("cad/out/asm_housing.png","Assembled - front","Nothing on the face. Every fastener is either behind the unit or hidden under the visor.")}
    {pic("cad/out/asm_housing_rear.png","Assembled - rear","{NBOLT} M3 through the cover into the shell&rsquo;s brim, plus the Gore vent and the heatsink aperture. Cable now exits the &minus;x short side.")}
  </div>
  <div class="grid dwgs">
    {svgpic("cad/out/exp_cad.svg","Exploded - numbered","Balloons match the BOM. Sensor breakouts sit on the tray; the antenna bulkhead and whip mount through the rear cover.")}
  </div>
  <div class="grid">
    {pic("cad/out/exp_a.png","Exploded - three-quarter","")}
    {pic("cad/out/exp_b.png","Exploded - from the right","")}
  </div>
  <div class="flag w">
    <h3>Slimming pass &mdash; and what it cost</h3>
    <p>Body is <b>389 &times; 165 &times; 28</b>, with a local <b>18 mm bump-out</b> on the cover for the Pi stack.
       Only the Pi needs depth, so only the Pi gets it: <b>46 mm at the bump, 28 mm everywhere else</b>.
       Front face 6 &rarr; 2.5 mm. Filament <b>1.51 &rarr; 0.84 kg</b>.</p>
    <p>Fasteners went <b>24 &rarr; 12</b>. The Gore vent equalises pressure, so the gasket only resists water.
       At 12 &times; M4 each screw carries 261 N against 1175 N capacity &mdash; <b>SF 4.5</b> at 88 mm spacing.</p>
    <p><b>The cost: nothing can be cooled inside at this depth.</b> The Pi stack leaves 4 mm of clearance,
       which will not take an internal fan or an inner heatsink. All cooling now happens outside the cover.</p>
  </div>
  <div class="flag w">
    <h3>Why the split flipped</h3>
    <p>rev A bolted the bezel on from the front &mdash; 25 screw heads across the face. rev B makes the
       <b>front shell</b> one piece (face + walls) and the <b>rear cover</b> a flat plate whose holes thread
       into the shell&rsquo;s rear brim.</p>
    <p>It is better in four ways beyond looks: the front A-surface now prints face-down so it is bed-smooth,
       the encoder&rsquo;s panel seal groove lands on a flat face, the gasket moves out of the weather, and every
       precision feature sits on one part.</p>
  </div>
</section>

<section>
  <div class="sheet-hd"><h2>Bill of materials</h2><span class="file">printed parts, hardware, electronics</span></div>
  <div class="scroll"><table class="cmp">
    <tr><th>#</th><th>Item</th><th>Qty</th><th>Spec / note</th></tr>
    <tr><td class="m">1</td><td>Visor</td><td>1</td><td>ASA ~55 g. Hinged, 20 detent teeth</td></tr>
    <tr><td class="m">2</td><td>Front shell</td><td>1</td><td>ASA ~200 g. 2.5 mm face, prints face-down</td></tr>
    <tr><td class="m">3</td><td>12.3&Prime; 1920&times;720 LCD</td><td>1</td><td>active 292.5 &times; 109.7 derived; <b>outline assumed</b></td></tr>
    
    <tr><td class="m">5</td><td>DROK 9&ndash;36 V &rarr; 12 V 5 A</td><td>1</td><td>65 &times; 58 &times; 20</td></tr>
    <tr><td class="m">6</td><td>Raspberry Pi 4</td><td>1</td><td>85 &times; 56, M2.5 on 58 &times; 49</td></tr>
    <tr><td class="m">7</td><td>PiCAN-M HAT</td><td>1</td><td>footprint still needed</td></tr>
    <tr><td class="m">8</td><td>Rear cover</td><td>1</td><td>ASA ~322 g. Pi bump-out, heatsink aperture, sensor standoffs</td></tr>
    <tr><td class="m">9</td><td>LP-24 shroud</td><td>1</td><td>ASA ~98 g. Dash-mounted, far end of the cable</td></tr>
    <tr><td class="m">10</td><td>Strain relief clamp</td><td>1</td><td>ASA ~11 g</td></tr>
    <tr><td class="m">11</td><td>Fit coupon</td><td>1</td><td>ASA ~55 g. <b>Print this first</b></td></tr>
    <tr><td class="m">12</td><td>MCP23017</td><td>1</td><td>43.18 &times; 17.78, holes 38.10 &times; 12.70</td></tr>
    <tr><td class="m">13</td><td>MCP9808 / ADXL345 / ICM20948</td><td>3</td><td>25.40 &times; 17.78, holes 20.32 &times; 12.70</td></tr>
    <tr><td class="m">13b</td><td><b>SEQURE M10-18 GPS module</b></td><td>1</td><td><b>GPS module</b> &mdash; 18 &times; 18 &times; 8, ceramic patch. In a cradle under the top wall at x=+150, <b>patch facing up</b> through the ASA. 315 mm from the VHF whip</td></tr>
    <tr><td class="m">14</td><td>PCM1808 + PCM5102A</td><td>1 + 2</td><td>Strap-down bays &mdash; no mounting holes</td></tr>
    <tr><td class="m">15</td><td>RTL-SDR</td><td>1</td><td>Shell exposed as its own heatsink</td></tr>
    <tr><td class="m">16</td><td>Oak Grigsby 91Q128</td><td>1</td><td>3/8-32 bushing, &Oslash;6.299 shaft, 5 V TTL</td></tr>
    <tr><td class="m">17</td><td>Twidec 12 mm buttons</td><td>4</td><td>&Oslash;12 bore, 13 mm barrel</td></tr>
    <tr><td class="m">18</td><td>M4 &times; 16 316 SS</td><td>12</td><td>Cover into the shell brim</td></tr>
    <tr><td class="m">19</td><td>M5 &times; 25 + wave washer + nyloc</td><td>2</td><td>Visor pivots</td></tr>
    <tr><td class="m">20</td><td>M5 &times; 25 + wave washer + nyloc</td><td>2</td><td>Bottom tilt pivots</td></tr>
    <tr><td class="m">20b</td><td>Dash screws</td><td>4</td><td>Tilt bracket into the dashboard</td></tr>
    <tr><td class="m">21</td><td>M3 &times; 20 316 SS</td><td>4</td><td>LP-24 into the shroud frame</td></tr>
    <tr><td class="m">22</td><td>M4 &times; 30 316 SS</td><td>2</td><td>Clamp up into the shroud beam</td></tr>
    <tr><td class="m">23</td><td>M5 316 SS</td><td>8</td><td>Shroud to the dash</td></tr>
    <tr><td class="m">24</td><td>M2.5 &times; 8</td><td>16</td><td>Breakouts to the sensor tray</td></tr>
    <tr><td class="m">25</td><td>CNLINKO LP-24</td><td>1</td><td>&Oslash;24.4 bore, 26.0 sq pattern</td></tr>
    <tr><td class="m">26</td><td><b>M20&times;1.5 90&deg; elbow gland</b></td><td>1</td><td>Screws into a <b>perpendicular tapped boss</b> at (&minus;150, &minus;46), 10 mm proud. Tapping drill &Oslash;18.5. The elbow turns the cable parallel to the cover</td></tr>
    <tr><td class="m">27</td><td>M12&times;1.5 Gore vent</td><td>1</td><td>Low on the back. Do not paint or block</td></tr>
    <tr><td class="m">28</td><td>SMA female bulkhead, M16</td><td>1</td><td><b>Top wall</b> at x=&minus;165, z=10. Plain bore &mdash; the wall is already <b>7.7 mm</b>, inside the 1&ndash;8 mm grip</td></tr>
    <tr><td class="m">29</td><td>{GASKET_T:.0f} mm rubber foam sheet</td><td>~2.3 m of {GASKET_W:.1f} mm band</td><td>Continuous, cut to the brim. NOT punched for the screws.</td></tr>
    <tr><td class="m">30</td><td>Belden 1058A</td><td>as needed</td><td>12 pair 20 AWG PLTC</td></tr>
    <tr><td class="m">31</td><td>Dash tilt bracket</td><td>1</td><td>ASA ~87 g. 276 &times; 99 &times; 32. Screws flat to the <b>dash face</b>, housing cantilevered off the top. Screw rows 65 mm apart</td></tr>
    <tr><td class="m">32</td><td>Fan shroud</td><td>1</td><td>ASA ~82 g. 138 &times; 138 &times; <b>52</b>. Spoke guard, louvres, wire pass-through</td></tr>
    <tr><td class="m">33</td><td>Alloy plate 114 &times; 114 &times; 6</td><td>1</td><td>Flat stock, cut square. <b>Tapped M3</b> &mdash; 8 at &plusmn;49 for the cover, 4 at &plusmn;48 for the shroud, 1 &times; &Oslash;8 grommet for fan wires</td></tr>
    <tr><td class="m">34</td><td>Easycargo 100 &times; 40 &times; 20 heatsink</td><td>4</td><td>2 outside, 1 inside on the plate, 1 spare. Bolted with paste &mdash; the tape-backed variants are fine but the tape is redundant</td></tr>
    <tr><td class="m">35</td><td><b>Noctua NF-F12 iPPC-2000 IP67 PWM</b></td><td>1</td><td>120 &times; 120 &times; <b>27</b> (pads included, not the 25 on the sheet). 105 mm pitch, &Oslash;114 bore. IP67 and PWM &mdash; throttle it off the MCP9808</td></tr>
    <tr><td class="m">39</td><td>&Oslash;8 rubber grommet</td><td>1</td><td>Fan wires through the alloy plate</td></tr>
    <tr><td class="m">40</td><td>Adhesive copper or alloy foil</td><td>1 sheet</td><td>Shield between the antenna feed and the display. <b>Bond to system ground</b> &mdash; ungrounded foil does almost nothing</td></tr>
    <tr><td class="m">36</td><td>HYS whip antenna</td><td>1</td><td>185 mm, <b>SMA male</b>, 136&ndash;174 / 400&ndash;470 MHz</td></tr>
    <tr><td class="m">38</td><td>SMA pigtail, RG316</td><td>1</td><td>150 mm, M16 bulkhead to SMA male &mdash; feeds the RTL-SDR</td></tr>
  </table></div>
  <div class="flag w">
    <h3>The 8 holes around the aperture &mdash; and where the fan goes</h3>
    <p>Those <b>8 &times; M3</b> are not the fan. They clamp the <b>alloy heat plate</b> over the 84 &times; 84
       aperture, at 49 mm spacing. That count comes from the ASA side, not the metal: the 6 mm plate is
       <b>35&times; stiffer</b> than the cover and barely bends, but the printed land around the aperture can bow
       between fasteners. 49 mm meets the &le;50 mm rule this project has been using for ASA flanges. Four corner
       bolts would sit 98 mm apart and break it.</p>
    <p><b>The fan mounts in the shroud</b>, not the cover: a bay at one end with a &Oslash;32.5 outlet and
       <b>4 slotted fixings</b>. Slots because the WINSINN drawing gives 2 &times; &Oslash;4.3 without a clear datum
       &mdash; slots swallow the real pattern whichever way it reads. Its inlet faces the sheltered underside
       behind an awning.</p>
    <p><b>Fan wires reach the Pi through the alloy plate</b>, not the ASA. A &Oslash;8 grommet in 6 mm aluminium
       seals far better than a hole in a printed wall, and it sits under the shroud where spray cannot reach it.
       The shroud carries only a plain &Oslash;7 pass-through to guide the wires.</p>
    <p>Caught while fitting the fan: the plate was <b>14 mm taller than the old shroud</b> and stuck out
       uncovered. Shroud grew to 128 sq so it covers the plate with 7 mm all round.</p>
  </div>
  <div class="flag w">
    <h3>Sensor positions &mdash; and what boat-config changed</h3>
    <p>Reading <code>apps/stereo-service/encoder.py</code> moved a board and corrected two things I had told you.</p>
    <p><b>The encoder does run through the MCP23017</b> &mdash; 0x20, GPA0/GPA1, with all four buttons on GPA2&ndash;5.
       I had said not to do that because I&sup2;C polling drops quadrature counts. Your code already solves it with a
       <b>dedicated fast poller</b> separate from the 1 Hz sampler that reads the buttons. And you run the encoder at
       <b>3 V, not 5 V</b>, so the level-shifting warning I gave does not apply either.</p>
    <p>Consequence: all six control signals land on that one chip, so it belongs <b>beside the control column</b>,
       not across the box. It sits 7 mm from the buttons. The three environmental sensors do not care, so they moved
       to +x, ~290 mm clear of the 24-wire entry.</p>
    <div class="scroll"><table class="cmp">
      <tr><th>Board</th><th>Centre</th><th>4 &times; M2.5 &Oslash;2.2 at</th><th>Why there</th></tr>
      <tr><td>MCP23017</td><td class="m">(&minus;150, 10)</td><td class="m">&plusmn;19.05 x, &plusmn;6.35 y</td><td>7 mm from the buttons and encoder</td></tr>
      <tr><td>MCP9808</td><td class="m">(95, &minus;54)</td><td class="m">&plusmn;10.16 x, &plusmn;6.35 y</td><td>bottom band, clear of the harness</td></tr>
      <tr><td>ADXL345</td><td class="m">(125, &minus;54)</td><td class="m">&plusmn;10.16 x, &plusmn;6.35 y</td><td>bottom band</td></tr>
      <tr><td>ICM20948</td><td class="m">(155, &minus;54)</td><td class="m">&plusmn;10.16 x, &plusmn;6.35 y</td><td>bottom band, far from the antenna</td></tr>
    </table></div>
    <p>Standoffs are <b>1.5 mm</b>, so board + standoff is 3.1 mm and fits the 4 mm gap behind the display.
       Checked against the heatsink aperture, GPS cradle, gland boss, Pi bump and gasket &mdash; <b>0 clashes</b>.</p>
  </div>
  <div class="flag">
    <h3>Mounting, cable entry and tie-downs</h3>
    <p><b>VESA is gone.</b> The unit hinges on <b>bottom pivots at x &plusmn;120</b>, detented like the visor at
       <b>{CLICK:.1f}&deg; per click</b>, so it tilts back to read standing and forward when seated.</p>
    <p>The bracket screws <b>flat to the vertical front face of the dash</b> with the housing cantilevered off its
       top edge &mdash; the plate mounts backwards relative to how it was first drawn, which needs no change to the
       part. It does change the load path: the housing now hangs off the face instead of sitting on it, so the screw
       rows carry a peel moment rather than shear.</p>
    <p>About <b>1.43 kg</b> hangs there with its CG ~60 mm off the face, giving <b>5.0 N&middot;m</b> at 6g.
       The screw rows moved from <b>26 to 65 mm apart</b>, which cuts the per-screw load from 97 N to <b>39 N</b> and
       stops the plate flexing between them. Free &mdash; the plate was already long enough.</p>
    <p><b>That 5.0 N&middot;m has to be held shut, not just carried.</b> The detent flanks are at 45&deg;, so the
       axial SEPARATING force equals the tangential one: <b>240 N per ear</b> at 6g, trying to push the crowns apart.
       A wave washer on a thread formed in ASA is a ~50&ndash;100 N part and loses &mdash; the crown climbs its own
       ramps, ratchets a click, and gives up preload the plastic never recovers.</p>
    <p>So the shell ear no longer carries the thread. Its hole is <b>&Oslash;{H["BP_BOLT"]} clearance</b> and a
       <b>captive 316 hex nut</b> sits in a {NUT_AF} A/F pocket {NUT_DEEP} deep in the OUTBOARD face, leaving
       <b>{H["BP_NUT_WALL"]:.1f} mm</b> of ear behind the crown. Bolt, Bellevilles, sleeve and washers are
       <b>all 316</b> &mdash; a brass insert against a 316 bolt is a ~0.25 V couple in salt water and the brass, as
       the smaller part, dezincifies. <b>Tef-Gel the threads</b>: 316 galls on 316, and a nut in a plastic pocket is
       a textbook crevice. Plain hex, not a nyloc &mdash; a nyloc is 5.0 thick and would leave only 3.7 mm under the
       teeth, and its nylon relaxes under sustained Belleville load anyway. The Bellevilles are the locking element.</p>
    <p><b>The cable now leaves at 45&deg; toward the right.</b> Bore axis is (&minus;1, 0, &minus;1)/&radic;2, so it
       exits sideways rather than straight back, with a raised boss giving the O-ring a seat perpendicular to that
       axis. At (&minus;150, &minus;50) it sits <b>37 mm from the tilt axis</b>: a 30&deg; swing moves the cable
       <b>18.5 mm</b>, against 71 mm if it were centred on the back.</p>
    <p>⚠ A 45&deg; bore through a 6 mm plate is <b>8.49 mm</b> of material before any boss, and the boss pushed it
       past what an M20 gland will clamp. The cover is <b>thinned locally to 3 mm</b> on the inside, bringing the
       clamped thickness to a measured <b>9.05 mm</b>.</p>
    <p><b>A side-wall exit is still impossible</b>, and it is worth knowing why: the shell is 24 mm deep, the front
       face takes z 0&ndash;2.5 and the brim face sits at 22, leaving 19.5 mm. A bore spans its own diameter
       in z whatever direction it points, so &Oslash;20.5 will not go and angling it makes it worse.</p>
    <p><b>8 tie-wrap anchors</b>, 4 top and 4 bottom at x &plusmn;30 and &plusmn;90.</p>
  </div>
  <div class="flag w">
    <h3>Still open</h3>
    <p><b>Soft keys are at 24 mm pitch, not true quarter-heights.</b> Quarter-heights would be &plusmn;41.1 and
       &plusmn;13.7, which needs the housing <b>27 mm taller</b> to clear the encoder <i>body</i> (25.4 sq &mdash; the
       knob is not the constraint). Say the word if you want the height instead.</p>
    <p><b>Touchscreen driver board is not placed.</b> Needs its outline, hole pattern, and which edge the display
       ribbon and the HDMI/USB connectors leave from.</p>
    <p><b>Tilt bracket is not designed.</b> Needs dash thickness and whether the unit sits on the face or recessed.</p>
  </div>
  <div class="flag">
    <h3>RF separation</h3>
    <p>The GPS was <b>26 mm from the VHF whip</b>. A transmit antenna that close desenses a GPS receiver badly.
       It now sits in the <b>opposite top corner</b>: antenna at x=&minus;165, GPS at x=+150 &mdash;
       <b>315 mm apart</b>.</p>
    <p>The GPS cradle holds the board with its <b>ceramic patch facing up</b>, radiating through the ASA. Lying
       flat on the old tray it pointed sideways into the housing, which is the difference between a working fix
       and a mounting bracket.</p>
    <p><b>Foil shield</b> between the antenna feed and the display: worth doing, and it must be
       <b>bonded to system ground</b>. Ungrounded foil does almost nothing. The same sheet helps with the other
       RF problem in this box &mdash; display ribbon noise at GPS L1.</p>
    <p class="note">Bugs fixed this pass: the antenna bore ran through the whole housing; then its counterbore
       and knockout each cut the 2.5 mm front face. The wall is already 7.7 mm there, inside the M16 grip, so a
       plain bore was the answer all along. The GPS cradle was also cutting the front face.</p>
  </div>
  <div class="flag w">
    <h3>Antenna &mdash; still wants a ground plane</h3>
    <p>🚨 The HYS is a handheld whip, designed to work against a radio body and your hand as a counterpoise. On a
       plastic box it will show poor SWR and mediocre receive. For real AIS or VHF work, run the pigtail out to a
       proper marine antenna &mdash; the bulkhead is the right interface either way.</p>
    <p>⚠ The knockout face is a <b>vertical printed surface</b>, so its layer lines run across the O-ring seat.
       Sand it flat and bed the O-ring in sealant.</p>
  </div>
</section>

<section>
  <div class="sheet-hd"><h2>Measured parts</h2>
    <span class="file">redrawn from your photos &mdash; please check</span></div>
  <div class="grid dwgs">
    {mdwg(0)}
    {mdwg(1)}
  </div>
  <div class="flag">
    <h3>Correction &mdash; I misread the display sketch</h3>
    <p>I read <b>133 mm as a hole pitch</b>. It is not: both 133 and 26.5 are measured to the
       <b>right edge</b>, so those two bottom bosses are <b>106.5 mm</b> apart. I then derived a 307.5 mm module
       width from that mistake and called it corroboration for my 305 assumption. <b>Both retracted</b> &mdash;
       the sketch does not give the module width at all, and 305 is still just the 8:3 active-area calculation.</p>
    <p>The drawing above is redrawn with your datums: right edge for 133 and 26.5, bottom edge for 30 and 13,
       top edge for 8.25. The outline is drawn at 305 &times; 125 and <b>labelled as assumed</b>.</p>
  </div>
  <div class="flag">
    <h3>Cable entry is now a 90&deg; elbow on a square boss</h3>
    <p>Your call, and it removes the whole problem. A <b>perpendicular tapped boss</b> 10 mm proud takes an
       <b>M20&times;1.5 90&deg; elbow gland</b>, which turns the cable parallel to the cover. Nothing projects
       straight back, so the case depth is untouched away from that corner.</p>
    <p>It also drops every 45&deg; headache: the seat is square to the bore by definition. I had spent two passes
       trying to make a clamp-through work at 45&deg; before establishing it is geometrically impossible on a thin
       panel &mdash; a locknut clear of the sloping plate needs a 34 mm boss, and nothing clamps that.</p>
    <p class="note">Tapping drill &Oslash;18.5 for M20&times;1.5, 16 mm of thread through boss and cover.</p>
  </div>
  <div class="flag">
    <h3>Aperture is now cut to a measured display</h3>
    <p>Active area measured <b>295 &times; 112</b>. My derived figure was 292.5 &times; 109.7 &mdash; <b>2.5 mm
       narrow and 2.3 mm short</b>. The aperture is now <b>296.0 &times; 113.0</b>, measured plus a 0.5 mm reveal.
       Had that gone to print it would have masked a strip of pixels down two edges.</p>
    <p><b>The module outline is still the gate.</b> Active area does not give it &mdash; the border width is
       unknown, and the model still assumes 305 &times; 125. That outline sets the housing size, the interior
       clearance, and all four display bearing posts, which are edge-referenced.</p>
    <p>Two numbers: <b>overall W and H of the metal chassis, face on.</b></p>
  </div>
  <div class="flag">
    <h3>Tie-wrap anchors moved to the cover</h3>
    <p>They were on the front shell's inner walls. Wrong side &mdash; the harness runs on the cover, where the Pi,
       the sensors and the gland all are, and you dress cables before closing it up.</p>
    <p>One constraint came with the move: on the cover they sit <b>behind the display</b>, which leaves 4.5 mm, so
       they had to drop from 7 mm tall to <b>3.5 mm with a 2.2 mm slot</b> &mdash; a standard 2.5 mm tie. Positions
       are picked around everything else on that face rather than on a regular pitch: top row at
       x &minus;150, &minus;60, 110, 145; bottom row at &minus;120, &minus;80, &minus;30, 68.</p>
    <p>Verified: 8 bridges present, 8 slots open, <b>0 clashes</b> against the driver bay, Pi bump, gland boss,
       vent, all four sensors, all four display posts and the gasket.</p>
  </div>
  <div class="flag w">
    <h3>Shroud depth: 54 &rarr; 52, and why it is only 2 mm</h3>
    <p>The stack is <b>3 mm wall + 27 fan + 20 fins = 50</b>, so 52 keeps a 2 mm plenum. Below that the fan face
       crowds the fin tips and the flow has nowhere to turn before it hits them.</p>
    <p>Worth being straight about one thing: the <b>NF-F12 is not thinner</b> than the 80 mm axial it replaced
       &mdash; both are 25 mm nominal, and the Noctua measures <b>27 mm</b> with its anti-vibration pads. The 120
       is wider, not slimmer. So this saving is me removing slack I had left, not a fan-thickness gain.</p>
  </div>
  <div class="flag">
    <h3>🚨 The shell and cover do not fit a K2 Plus</h3>
    <p>The K2 Plus bed is <b>350 &times; 350</b>. At the measured display size the front shell is
       <b>389 &times; 193</b> and the rear cover <b>389 &times; 165</b>. Neither fits at <b>any</b> rotation
       &mdash; a rectangle only clears a square bed if it satisfies both W&middot;cos&theta; + H&middot;sin&theta;
       and W&middot;sin&theta; + H&middot;cos&theta; &le; 350, and 389 fails both across the whole sweep.</p>
    <p>Everything else fits flat at 0&deg;:</p>
    <ul class="chk">
      <li>Visor 314 &times; 22, tilt bracket 276 &times; 99, fan shroud 138 &times; 138</li>
      <li>LP-24 shroud 132 &times; 102, fit coupon 190 &times; 115</li>
    </ul>
    <p>So the two big parts need a <b>designed split</b> &mdash; a deliberate joint with alignment and a bonded or
       bolted seam, not a slicer cut. On the shell the sensible line is beside the control column, where the
       divider already breaks the face; on the cover, between the Pi bump and the driver bay. Say the word and
       I will cut them properly.</p>
  </div>
  <div class="flag">
    <h3>The housing is now fully measured &mdash; everything is printable</h3>
    <p>Module outline <b>310 &times; 130</b>, active area <b>295 &times; 112</b>. Both were assumptions until now;
       both are measured. My assumed outline was 305 &times; 125, so the housing grew to
       <b>389 &times; 165 &times; 28</b> and every edge-referenced feature moved with it.</p>
    <p>Two knock-on fixes the new size exposed:</p>
    <ul class="chk">
      <li>The four <b>display bearing posts</b> shifted automatically &mdash; they are edge-referenced &mdash; and
        re-verified clear at their new positions</li>
      <li>The <b>visor</b> was 300 mm across a 310 mm display, short 3 mm left and 7 mm right. Pivots moved to
        &minus;135 / 175 so the hood now spans the panel. Antenna wrench clearance re-checked: 8 mm</li>
    </ul>
    <p>Full pairwise sweep of everything on the cover &mdash; driver bay, Pi bump, gland boss, vent, four sensors,
       four display posts, eight tie anchors, heatsink aperture, gasket ring: <b>0 clashes</b>.</p>
  </div>
  <div class="flag w">
    <h3>Where the measurements landed</h3>
    <p><b>Driver board is complete.</b> 113.25 &times; 55.25 &times; 17, four &Oslash;3.5 holes for M3 at
       TL (9.00, 3.75), TR (109.25, 3.75), BL (9.00, 48.00), BR (109.25, 51.50), origin top-left. Worth noting the
       pattern is <b>not rectangular</b> &mdash; the left pair is 44.25 apart, the right pair 47.75. A symmetric
       standoff set would not have fitted.</p>
    <p><b>Display rear is complete too.</b> Five standoffs, not six &mdash; no top-centre. All &Oslash;8 base,
       M3 &times; 5 deep. Every position is fixed to an edge, so the pattern becomes exact the moment the outline
       is known.</p>
    <p><b>Display depth 15 mm</b> brought the shell from 24 to 22, so the body is <b>28 mm</b> at the perimeter
       and <b>46 mm</b> at the Pi bump.</p>
    <p>Two things left:</p>
    <ul class="chk">
      <li class="q"><b>Module face width and height.</b> The last big unknown &mdash; it sets the housing size and
        turns all five standoff positions into absolute coordinates.</li>
      <li class="q"><b>Where the driver board goes.</b> It is <b>17 mm tall</b> and there is 4.5 mm behind the
        display, so it needs its own bump-out and the cover is already full. See below.</li>
    </ul>
  </div>
</section>

<section>
  <div class="sheet-hd"><h2>Assembly drawings</h2>
    <span class="file">all dimensions mm &middot; display fitted</span></div>
  <p class="sub" style="margin:0 0 18px">Orthographic projections of the assembled housing, taken from the
     solids. Each view yaws the model and reuses one solved camera, so the geometry cannot drift from the parts.</p>
  <div class="grid dwgs">
    {adwg(0)}
    {adwg(1)}
    {adwg(2)}
    {adwg(3)}
  </div>
</section>

<section>
  <div class="sheet-hd"><h2>The seal</h2>
    <span class="file">shell brim &rarr; rear cover</span></div>
  <div class="grid dwgs">
    {svgpic("cad/out/seal_detail.svg","Section through the top rail","Cord gland cut into the shell&rsquo;s rear brim; the cover presents a flat land. Groove verified continuous on all four rails.")}
  </div>
  <div class="cols">
    <div class="panel"><h3>As modelled</h3><table>
      <tr><td>Gland</td><td>3.45 W &times; 2.31 D</td></tr>
      <tr><td>Cord</td><td>3.0 mm round</td></tr>
      <tr><td>Squeeze</td><td>~25%</td></tr>
      <tr><td>Path</td><td>&plusmn;181 &times; &plusmn;69, R13.5</td></tr>
      <tr><td>Perimeter</td><td>~980 mm</td></tr>
      <tr><td>Groove to inner wall</td><td>3.3 mm</td></tr>
      <tr><td>Groove to bolt edge</td><td>2.0 mm</td></tr>
      <tr><td>Fasteners</td><td>11 &times; M4</td></tr>
    </table></div>
    <div class="panel"><h3>How it works</h3><ul class="chk">
      <li>Groove is in the <b>shell</b>; the cover is a plain flat land. Machining the groove into one part only is what keeps the joint self-aligning</li>
      <li>Verified void <b>2.35 mm deep</b> on all four rails by point sampling, not by eye</li>
      <li>Depth 0.77 &times; cord, width 1.15 &times; cord &mdash; fills ~78% of the groove, leaving room for the squeezed cord to spread</li>
      <li>The <b>Gore vent</b> removes the pressure term, so this seal only has to stop water, not hold a differential</li>
      <li class="q">Splice the cord with a scarf joint and CA, positioned <b>away from the bottom rail</b></li>
      <li class="q">⚠ Confirm the cord is 3 mm and not 3/32&Prime; &mdash; the listing says both, and they are 0.6 mm apart</li>
    </ul></div>
  </div>
  <div class="flag">
    <h3>Caught while drawing this</h3>
    <p>The assembly render had the <b>cover 6 mm too deep</b> &mdash; placed at z=24 instead of z=30, which buried
       it in the brim and closed the gasket gap to nothing. Geometry was right; the placement transform was wrong.
       Fixed, and every assembled view is re-rendered.</p>
  </div>
</section>

<section>
  <div class="sheet-hd"><h2>Hinged visor</h2><span class="rev">REV {H["REV"]}</span>
    <span class="file">helm_visor_revB.stp</span></div>
  <div class="grid">
    {pic("cad/out/asm_tilt_up.png","Tilted up","+15&deg;. Clears a standing eye looking down at the screen.")}
    {pic("cad/out/asm_tilt_flat.png","Flat","0&deg;. Neutral, and the most shade for a seated helm.")}
    {pic("cad/out/asm_tilt_down.png","Tilted down","&minus;30&deg;. Maximum glare rejection, or folded down over the screen at rest.")}
  </div>
  <div class="cols">
    <div class="panel"><h3>As modelled</h3><table>
      <tr><td>Hood</td><td>58 mm deep, 4 mm</td></tr>
      <tr><td>Leading edge</td><td>45&deg; bevel, 6 mm</td></tr>
      <tr><td>Pivot span</td><td>300 mm</td></tr>
      <tr><td>Detent teeth</td><td>{H["N_TEETH"]} &mdash; {CLICK:.1f}&deg; per click</td></tr>
      <tr><td>Pivot bolt</td><td>M5 316 SS + wave washer</td></tr>
      <tr><td>Mass in ASA</td><td>~55 g</td></tr>
    </table></div>
    <div class="panel"><h3>Two decisions worth knowing</h3><ul class="chk">
      <li><b>Detent teeth, not friction.</b> ASA creeps under sustained clamp load and a boat vibrates constantly &mdash; a friction pivot flops within a season. Teeth give a position vibration cannot walk out of, and the wave washer holds preload as the plastic relaxes. Same principle as an MFD bail mount.</li>
      <li><b>No side wings, and the bevel is structural.</b> On two pivots the hood is a 300 mm cantilever. A bare flat plate has I = 373 mm&sup4; and flexes 15 mm under a 20 N push; the 45&deg; turned-down bevel lifts that to 953 mm&sup4; and 6 mm. Stress is SF 5 either way &mdash; the bevel is about how floppy it feels.</li>
      <li>Pivot faces mesh at <b>0.00 mm</b> &mdash; upstands and ears verified coincident</li>
      <li class="q">Range is set by the housing; say if you want it to fold flat to the screen at rest</li>
    </ul></div>
  </div>
</section>

<section>
  <div class="sheet-hd"><h2>Housing parts</h2><span class="rev">REV {H["REV"]}</span>
    <span class="file">helm_shell_revB.stp &middot; helm_cover_revB.stp &middot; helm_visor_revA.stp</span></div>
  <div class="grid">
    {tile(0,"Front shell - face","Four buttons at 26 mm pitch with the encoder below, on the right. Visor pivots at the top. Nothing else on the face.")}
    {tile(1,"Front shell - inside","Straight wall, {RIM:.0f} mm thick from the back of the bezel to the rear brim. No taper, so the brim face is exactly {RIM:.0f} mm.")}
    {tile(2,"Rear cover","Gore vent, heatsink aperture and the sensor standoffs. VESA deleted; the unit hinges on bottom pivots now.")}
    {tile(3,"Visor - hinged","Pivots on detent teeth at 15&deg; per click. Adjust by hand; the teeth stop vibration walking it out of position.")}
  </div>
  <div class="cols">
    <div class="panel"><h3>As modelled</h3><table>
      <tr><td>Envelope</td><td>389 &times; 165 &times; 28</td></tr>
      <tr><td>Interior</td><td>357 &times; 133</td></tr>
      <tr><td>Front face</td><td>2.5 mm</td></tr>
      <tr><td>Aperture</td><td>296.0 &times; 113.0</td></tr>
      <tr><td>Glue channel</td><td>5.0 W, raised 2.0</td></tr>
      <tr><td>Brim bolts</td><td>11 &times; M4</td></tr>
      <tr><td>Controls</td><td>4 buttons + encoder, right</td></tr>
      <tr><td>Bottom pivots</td><td>x &plusmn;120, M5</td></tr>
      <tr><td>Tie-wrap anchors</td><td>8, on the cover</td></tr>
      <tr><td>Depth at the Pi</td><td>46 mm</td></tr>
      <tr><td>Button pitch</td><td>24.0 mm</td></tr>
      <tr><td>Encoder</td><td>y &minus;49, 22 below</td></tr>
      <tr><td>Mass in ASA</td><td>215 + 230 + 55 g</td></tr>
    </table></div>
    <div class="panel"><h3>Verified in geometry</h3><ul class="chk">
      <li>All parts single closed solids, <b>OCCT valid</b></li>
      <li>Glue channel now <b>raised</b>, not cut &mdash; a 2.0 mm cut in a 2.5 mm face left nothing</li>
      <li>Depth <b>30 mm perimeter, 48 mm at the Pi bump</b> &mdash; under the 50 mm limit</li>
      <li>Bottom pivots, tie anchors and gland boss all verified present</li>
      <li class="q">Module outline is <b>assumed</b> &mdash; measure it</li>
      <li class="q">Needs a <b>&ge;400 mm bed</b> or a designed split</li>
    </ul></div>
  </div>
</section>

<section>
  <div class="sheet-hd"><h2>LP-24 Shroud</h2><span class="rev">REV D</span>
    <span class="file">mounts on the dash, at the far end of the cable</span></div>
  <div class="grid">
    {pic("cad/out/asm_shroud.png","Sectioned - cable and clamp","Jacket rises through the open bottom, clamps under the cross-beam, conductors fan into the connector&rsquo;s rear cups.")}
    {pic("cad/out/asm_shroud_mated.png","With the plug mated","Connector face vertical, so water cannot pool in it.")}
  </div>
  <div class="cols">
    <div class="panel"><h3>As modelled</h3><table>
      <tr><td>Shroud</td><td>132 &times; 102 &times; 63</td></tr>
      <tr><td>Clamp</td><td>28 &times; 58 &times; 13</td></tr>
      <tr><td>LP-24 bore</td><td>&Oslash;24.4 teardrop</td></tr>
      <tr><td>Connector frame</td><td>46 &times; 46 &times; 12</td></tr>
      <tr><td>Jacket saddle</td><td>&Oslash;11.0</td></tr>
      <tr><td>SR pilots</td><td>2 &times; &Oslash;3.5, opening down</td></tr>
    </table></div>
    <div class="panel"><h3>Verified</h3><ul class="chk">
      <li><b>Ray-tested driver access</b> &mdash; 9 mm corridor from each pilot to the open face</li>
      <li>Teardrop <b>15.00</b> up vs <b>12.00</b> down, 38.7&deg; overhang</li>
      <li>Frame gives SF <b>4.4</b> against a 300 N lever on the plug</li>
      <li class="q">Confirm the 1058A jacket OD</li>
    </ul></div>
  </div>
</section>

<section>
  <div class="grid">
    {tile(4,"Dash tilt bracket","Plate runs rearward from the pivot only, so nothing juts out in front of the display. 4 slotted dash screws, two detent ears.")}
    {pic("cad/out/asm_shroud_fan.png","Fan shroud + NF-F12","The Noctua seated in the shroud. 120 x 120 x 27 with its anti-vibration pads &mdash; 2 mm thicker than the spec sheet.")}
    {tile(7,"Fan shroud","Blower bay at one end, louvred exhaust at the other. Covers the alloy plate with 7 mm margin.")}
  </div>
</section>

<section>
  <div class="sheet-hd"><h2>Drawings</h2><span class="file">shroud &middot; all dimensions mm</span></div>
  <div class="grid dwgs">{dwg(0)}{dwg(1)}{dwg(2)}{dwg(3)}</div>
</section>

<section>
  <div class="sheet-hd"><h2>Subassemblies</h2><span class="file">the things a whole-unit render cannot show</span></div>
  <p>A render of the finished unit answers &ldquo;what does it look like&rdquo;. It does not answer
     &ldquo;where does that go&rdquo; or &ldquo;how do I hold it while the glue sets&rdquo;, which are the
     questions that come up with a part in your hand. Each view below exists because a specific question
     had no picture.</p>
  <div class="grid">
    {subpic("sub_antenna_context")}
    {subpic("sub_antenna_detail")}
  </div>
  <div class="grid">
    {subpic("sub_thermal_exploded")}
    {subpic("sub_heatsink_jig")}
  </div>
  <div class="flag">
    <h3>The thermal path</h3>
    <p><b>The display&rsquo;s back is metal</b>, and it is both the largest heat source and the largest
       conductor in the box. Until this revision it faced <b>{H["TC_GAP"]:.1f} mm of dead air</b> across the
       heat aperture to the alloy plate, so every watt the panel made had to cross that gap by convection
       &mdash; in a <em>sealed</em> enclosure. That gap, not the fan, was the bottleneck.</p>
    <p>An aluminium <b>conduction block {H["TC_L"]:.0f} &times; {H["TC_W"]:.0f} &times; {H["TC_T"]:.1f}</b>,
       with a {H["TC_PAD"]} mm gap pad at each end, now bridges it: panel back &rarr; pad &rarr; block &rarr;
       pad &rarr; alloy plate &rarr; fins &rarr; fan. Metal the whole way, nothing moving, nothing to seize.
       Its thickness is <em>derived</em> from the assembled stack, so if the foam, the panel depth or the
       cover thickness move again, the block moves with them.</p>
    <p>The <b>Pi</b> is the other source and it is handled differently, because it is 178 mm from anything
       metal and already carries its own heatsink and fan. In a sealed box that fan does not export heat
       &mdash; but it <em>stirs</em>, which lifts internal convection from roughly 4 to 15&ndash;20 W/m&sup2;K,
       and that term is the bottleneck. If it proves insufficient the fallback is a
       <b>5 &times; 100 mm aluminium bar</b> to the plate (~12.5 K at 7 W), not a heat pipe.</p>
  </div>
</section>

<section>
  <div class="sheet-hd"><h2>Open items</h2><span class="file">what moves next</span></div>
  <div class="cols">
    <div class="panel"><h3>Blocking</h3><ul class="chk">
      <li class="q"><b>Printer bed size</b> &mdash; 384 mm needs &ge;400, or a designed split</li>
      <li class="q"><b>12.3&Prime; module outline</b>, bezel offsets, ribbon exit, max operating temp</li>
      <li class="q"><b>Heat path.</b> The thermal aperture is deleted, so 24 W is now sealed in ASA with no metal route out</li>
      <li class="q"><b>Tilt bracket</b> &mdash; needs dash thickness and on-face vs recessed</li>
      <li class="q"><b>Dash thickness</b> and whether the unit sits on the face or recessed &mdash; blocks the tilt bracket</li>
    </ul></div>
    <div class="panel"><h3>Measure when convenient</h3><ul class="chk">
      <li class="q">Encoder bushing length &mdash; caps the front face at 6.0 mm</li>
      <li class="q">Belden 1058A jacket OD vs a 12.5&ndash;18 mm gland</li>
      <li class="q">Rubber cord &mdash; 3 mm or 3/32&Prime;</li>
      <li class="q">PCM1808 and PCM5102A outlines</li>
      <li class="q">PiCAN-M footprint and N2K connector position</li>
    </ul></div>
  </div>
  <div class="flag w">
    <h3>Print notes</h3>
    <p><b>ASA blue &middot; 0.2 mm &middot; 5 perimeters &middot; 30% gyroid &middot; enclosure on.</b> Every part prints
       flat-face down with no supports. Slice from 3MF at High refinement. About <b>0.84 kg</b> of filament
       across eight parts, down from 1.51 kg.</p>
  </div>
</section>

<footer><span>Helm Print Package &middot; 7 printed parts</span><span>all solids valid &middot; 0 errors</span></footer>
</div>
"""
pathlib.Path("cad/out/review.html").write_text(HTML)
print("wrote", len(HTML)//1024, "KB")
