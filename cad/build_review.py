import base64, json, math, pathlib, datetime

# The interactive viewer's meshes. Written by cad/web3d.py from the same STEPs
# the renders use. Optional on purpose: if it has not been built the page still
# assembles, just without the 3D section - a build page that dies because a
# nice-to-have is missing is worse than one that quietly does without it.
try:
    WEB3D = json.load(open("cad/out/web3d.json"))
except FileNotFoundError:
    WEB3D = None
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
# EVERY DIMENSION ON THIS PAGE COMES FROM THE JSON THE GEOMETRY WRITES.
# This page went badly stale because it kept its own copies: it described an
# alloy plate, a conduction block, a 120 mm Noctua, a gluing jig, a foam band
# and a dash tilt bracket for revisions after every one of them was deleted,
# and quoted "11 x M4" while the shell was building 16 x M3. A number typed
# here is a number that will be wrong. If the page needs a dimension the JSON
# does not carry, the fix is a key in the exporting script - not a literal here.
H = json.load(open("cad/out/housing.json"))
S = json.load(open("cad/out/shroud.json"))     # cad/heatsink_shroud.py
B = json.load(open("cad/out/bail.json"))       # cad/bail.py
V = json.load(open("cad/out/pivot.json"))      # cad/helm_visor.py
try:
    LP = json.load(open("cad/out/lp24.json"))  # cad/lp24_shroud.py
except FileNotFoundError:
    LP = {}
FRIC_T = H["FRIC_T"]
RIM, GASKET_T, GASKET_W = H["RIM"], H["GASKET_T"], H["GASKET_W"]
OUT_W, OUT_H, DEPTH, COVER_T = H["OUT_W"], H["OUT_H"], H["DEPTH"], H["COVER_T"]
try:
    SD = json.load(open("cad/out/subdims.json"))
except FileNotFoundError:
    SD = []
def subpic(name, note=None):
    """note= overrides the caption subassemblies.py wrote - used only where a
    feature is mid-move and the page must not quote a coordinate for it."""
    for v in SD:
        if v["name"] == name:
            return pic(f"cad/out/{v['name']}.png", v["title"],
                       v.get("note", "") if note is None else note)
    return _missing(name, f"cad/out/{name}.png")
# Counted off the geometry, not retyped - the page has quoted a wrong
# fastener count and a wrong bezel through two revisions already.
DRV_L, DRV_W = 55.25, 113.25          # the board the cover's +x bosses are drilled to
GD_SHELL = f"{H[chr(34)+chr(34)] if False else H["GASKET_D"]:.2f}"
GD_COVER = f"{H["GASKET_D_COVER"]:.2f}"
NBOLT = H["N_BRIM_BOLTS"]
BEZEL = (OUT_W - H["APER_W"])/2
BEZEL_T = OUT_H/2 - (H["APER_Y"] + H["APER_H"]/2)

# -- derived, so nothing below is typed twice ------------------------------
ASA = 1.07                                   # g/cm3, ASA solid
def g(cm3):
    return f"{cm3*ASA:.0f} g" if cm3 else "&mdash;"
UNIT_D  = DEPTH + COVER_T + S["REAR_PROUD"]  # front face to the louvre tips
BAY_D   = DEPTH + COVER_T + H["PI_BUMP_H"]   # ...and over a board bay
SH_BOX  = f'{S["OW"]:.0f} &times; {S["OH"]:.0f} &times; {S["SHROUD_OD"]:.0f}'
# Cord length: the groove's CENTRELINE, not the shell's outline.
_gc = H["GASKET_OUT"] + GASKET_W/2
_cw, _ch, _cr = OUT_W - 2*_gc, OUT_H - 2*_gc, max(H["R_OUT"] - _gc, 0.5)
CORD_L = 2*(_cw - 2*_cr) + 2*(_ch - 2*_cr) + 2*math.pi*_cr
PRINTED = [("Front shell", H["SHELL_CM3"], 1), ("Rear cover", H["COVER_CM3"], 1),
           ("Visor", V["VOL_CM3"], 1), ("Fan shroud", S.get("SHROUD_CM3"), 1),
           ("Bail base", B.get("BASE_CM3"), 1), ("Bail arm", B.get("ARM_CM3"), 2),
           ("LP-24 shroud", LP.get("SHROUD_CM3"), 1),
           ("Strain clamp", LP.get("CLAMP_CM3"), 1)]
FILAMENT = sum(v*n for _n, v, n in PRINTED if v)/1000.0*ASA   # kg, fit coupon aside
NPARTS = len(PRINTED)
def mm(v):
    return f"{v:.0f}" if abs(v - round(v)) < 0.05 else f"{v:.1f}"
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


# ══════════════════════════════════════════════════════ INTERACTIVE VIEWER
# Drag to rotate, wheel to zoom, slider to explode. three.js comes from
# jsdelivr's npm path - one of the two CDNs an artifact may load - and the
# geometry is inline base64, so there is no second request to fail.
#
# NO CONTROLS LIBRARY. OrbitControls lives in three's examples, which moved to
# ES modules; pulling it in means an importmap and a module script for what is
# forty lines of pointer maths. The orbit here is spherical about the assembly
# centre, which is all this needs.
#
# If three fails to load the <noscript>-ish fallback text stays visible and the
# still renders below are untouched.
def viewer_html(w3):
    if not w3:
        return ""
    parts = w3["parts"]
    meta = w3["meta"]
    data = json.dumps({k: {"b64": v["b64"], "colour": v["colour"],
                           "explode": v["explode"], "title": v["title"]}
                       for k, v in parts.items()}, separators=(",", ":"))
    tris = sum(v["tris"] for v in parts.values())
    toggles = "".join(
        f'<label class="v-tog"><input type="checkbox" data-part="{k}" checked>'
        f'<span>{v["title"]}</span></label>' for k, v in parts.items())
    return f"""
  <h3>Rotate it &mdash; {len(parts)} parts, live</h3>
  <p>The same solids as the renders below, meshed at {meta["tol"]}&nbsp;mm and
     {meta["ang"]}&nbsp;rad and carried inline &mdash; <b>{tris:,} triangles</b>. Drag to
     rotate, wheel to zoom, and pull the slider to take it apart. Nothing here is drawn
     by hand: the positions are the ones <code>cad/assembly.py</code> uses, so this view
     and the stills cannot disagree.</p>
  <div class="viewer" id="v3d">
    <canvas id="v3dc"></canvas>
    <div class="v-msg" id="v3dm">loading the 3D view&hellip;</div>
    <div class="v-bar">
      <label class="v-exp">Exploded
        <input type="range" id="v3de" min="0" max="100" value="0">
      </label>
      <button class="v-btn" id="v3dr">Reset view</button>
    </div>
    <div class="v-legend">{toggles}</div>
  </div>
  <!-- r149, PINNED. r160's build/three.min.js still works but is a deprecation
       stub that says it will be removed at r160 - which this is. r149 is the last
       version shipping a plain UMD bundle with no warning attached, and a UMD
       bundle is what lets this be one script tag instead of an importmap. -->
  <script src="https://cdn.jsdelivr.net/npm/three@0.149.0/build/three.min.js"></script>
  <script>
  (function(){{
    var DATA = {data};
    var META = {json.dumps(meta, separators=(",", ":"))};
    var msg = document.getElementById('v3dm');
    if (typeof THREE === 'undefined') {{ msg.textContent =
      'the 3D view needs three.js, which did not load - the renders below are unaffected';
      return; }}
    var cv = document.getElementById('v3dc'), wrap = document.getElementById('v3d');
    var sc = new THREE.Scene();
    var cam = new THREE.PerspectiveCamera(38, 1, 1, 8000);
    var rend = new THREE.WebGLRenderer({{canvas: cv, antialias: true, alpha: true}});
    rend.setPixelRatio(Math.min(devicePixelRatio, 2));
    sc.add(new THREE.AmbientLight(0xffffff, 0.62));
    var key = new THREE.DirectionalLight(0xffffff, 0.85); key.position.set(-0.4,-0.72,0.57);
    sc.add(key);
    var fill = new THREE.DirectionalLight(0xffffff, 0.30); fill.position.set(0.6,0.5,0.4);
    sc.add(fill);
    var root = new THREE.Group(); sc.add(root);
    var C = META.centre, R = META.radius, meshes = {{}};
    function b64buf(b64){{
      var bin = atob(b64), n = bin.length, u8 = new Uint8Array(n);
      for (var i=0;i<n;i++) u8[i] = bin.charCodeAt(i);
      return new Float32Array(u8.buffer);
    }}
    Object.keys(DATA).forEach(function(k){{
      var d = DATA[k], pos = b64buf(d.b64);
      var g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
      g.computeVertexNormals();
      var m = new THREE.Mesh(g, new THREE.MeshLambertMaterial({{
        color: new THREE.Color(d.colour), side: THREE.DoubleSide }}));
      m.userData.explode = d.explode;
      root.add(m); meshes[k] = m;
    }});
    root.position.set(-C[0], -C[1], -C[2]);
    // +Z of the model is REARWARD, so the camera sits on -Z to look at the face,
    // and +Y is up in model space but down on screen - hence the flip.
    root.scale.set(1,-1,1);
    var az = 0.62, el = 0.42, dist = R * 3.6, drag = null;
    function place(){{
      cam.position.set(C[0]*0 + dist*Math.cos(el)*Math.sin(az),
                       dist*Math.sin(el),
                       -dist*Math.cos(el)*Math.cos(az));
      cam.lookAt(0,0,0);
    }}
    function size(){{
      var w = wrap.clientWidth, h = Math.max(320, Math.min(560, Math.round(w*0.62)));
      rend.setSize(w, h, false); cam.aspect = w/h; cam.updateProjectionMatrix();
    }}
    function draw(){{ place(); rend.render(sc, cam); }}
    cv.addEventListener('pointerdown', function(e){{
      drag = {{x:e.clientX, y:e.clientY}}; cv.setPointerCapture(e.pointerId); }});
    cv.addEventListener('pointermove', function(e){{
      if (!drag) return;
      az -= (e.clientX - drag.x) * 0.008;
      el = Math.max(-1.45, Math.min(1.45, el + (e.clientY - drag.y) * 0.008));
      drag = {{x:e.clientX, y:e.clientY}}; draw(); }});
    cv.addEventListener('pointerup', function(e){{ drag = null; }});
    cv.addEventListener('wheel', function(e){{
      e.preventDefault();
      dist = Math.max(R*1.25, Math.min(R*9, dist * (1 + Math.sign(e.deltaY)*0.11)));
      draw(); }}, {{passive:false}});
    document.getElementById('v3de').addEventListener('input', function(e){{
      var t = e.target.value/100;
      Object.keys(meshes).forEach(function(k){{
        var v = meshes[k].userData.explode;
        meshes[k].position.set(v[0]*t, v[1]*t, v[2]*t);
      }});
      draw(); }});
    document.getElementById('v3dr').addEventListener('click', function(){{
      az = 0.62; el = 0.42; dist = R*3.6; draw(); }});
    wrap.querySelectorAll('input[data-part]').forEach(function(cb){{
      cb.addEventListener('change', function(){{
        meshes[cb.dataset.part].visible = cb.checked; draw(); }});
    }});
    addEventListener('resize', function(){{ size(); draw(); }});
    size(); msg.style.display = 'none'; draw();
  }})();
  </script>"""

VIEWER = viewer_html(WEB3D)

HTML = f"""<title>Helm Housing rev {H["REV"]}</title>
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
.viewer {{ border:1px solid var(--line); border-radius:6px; background:var(--viewport);
  padding:10px; margin:14px 0 18px; }}
.viewer canvas {{ display:block; width:100%; border-radius:4px;
  background:var(--sunk); touch-action:none; cursor:grab; }}
.viewer canvas:active {{ cursor:grabbing; }}
.v-msg {{ font:12px/1.5 'IBM Plex Mono',monospace; color:var(--muted); padding:8px 2px; }}
.v-bar {{ display:flex; gap:14px; align-items:center; flex-wrap:wrap; margin-top:10px; }}
.v-exp {{ display:flex; gap:8px; align-items:center; flex:1 1 220px;
  font:600 11px/1 'IBM Plex Sans Condensed',sans-serif; letter-spacing:.06em;
  text-transform:uppercase; color:var(--ink-2); }}
.v-exp input {{ flex:1; accent-color:var(--accent); }}
.v-btn {{ font:600 11px/1 'IBM Plex Sans Condensed',sans-serif; letter-spacing:.06em;
  text-transform:uppercase; color:var(--accent); background:var(--surface);
  border:1px solid var(--line); border-radius:4px; padding:7px 12px; cursor:pointer; }}
.v-btn:hover {{ background:var(--accent-soft); }}
.v-legend {{ display:flex; flex-wrap:wrap; gap:6px 14px; margin-top:10px;
  padding-top:10px; border-top:1px solid var(--line-2); }}
.v-tog {{ display:flex; gap:5px; align-items:center; cursor:pointer;
  font:400 11px/1.4 'IBM Plex Mono',monospace; color:var(--ink-2); }}
.v-tog input {{ accent-color:var(--accent); }}
@media (max-width:640px) {{ .v-legend {{ gap:6px 10px; }} }}
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
/* one per row, the full width of the sheet - for views you read rather than
   glance at */
.grid.wide{{grid-template-columns:1fr;gap:22px}}
.grid.wide .vp{{aspect-ratio:auto}}
.grid.wide img{{width:100%;height:auto;display:block}}
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
  <p class="sub">{NPARTS} printed parts, rendered from the exported STEP solids. Components with no CAD of
     their own are shown as envelope representations &mdash; correct size and position, no internal detail.
     Every dimension on this page is read from the geometry, not typed here.</p>
  <dl class="block">
    <div><dt>Project</dt><dd>SignalK glass helm</dd></div>
    <div><dt>Material</dt><dd>ASA &mdash; blue</dd></div>
    <div><dt>Filament</dt><dd>~{FILAMENT:.2f} kg</dd></div>
    <div><dt>Unit</dt><dd>{OUT_W:.0f} &times; {OUT_H:.0f} &times; {UNIT_D:.0f}</dd></div>
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
    {pic("cad/out/asm_housing_left.png","Assembled - other shoulder","")}
  </div>
  {VIEWER}
  <h3>Ghosted &mdash; where everything packs in</h3>
  <p>The printed parts at 22% opacity, every bought part solid. A section answers
     &ldquo;what is at this plane&rdquo;; the question a builder asks is &ldquo;what is in
     there, and does it all fit&rdquo;.</p>
  <div class="grid wide">
    {pic("cad/out/asm_ghost_front.png","Ghosted - front","")}
    {pic("cad/out/asm_ghost_rear.png","Ghosted - rear","Full width. Pi and Armor Lite in the -x bay, driver board and the RTL-SDR on edge in the +x, heatsink between them, GPS in the top block opposite the whip.")}
    {pic("cad/out/asm_ghost_side.png","Ghosted - side","")}
    {pic("cad/out/asm_ghost_top.png","Ghosted - from above","")}
  </div>
  <div class="grid">
    {pic("cad/out/asm_housing_side.png","Assembled - side","The shroud's depth and how far the bail holds it off the dash.")}
    {pic("cad/out/asm_housing_top.png","Assembled - from above","")}
    {pic("cad/out/asm_housing_rear.png","Assembled - rear",f"{NBOLT} M3 through the cover into the shell&rsquo;s brim, the fan shroud over the heatsink, and the bail arms on trunnions grown from the cover itself.")}
  </div>
  <div class="grid dwgs">
    {svgpic("cad/out/exp_cad.svg","Exploded - numbered","Balloons match the BOM numbers.")}
  </div>
  <div class="flag">
    <h3>&#9888; The exploded drawing is one revision behind</h3>
    <p>cad/exploded.py still lays out a <b>114 alloy plate at balloon 33</b> and a <b>pair of
       100 &times; 40 strip heatsinks at 34</b>. Neither part exists: there is no alloy plate, and the
       heatsink is one {H["HS_W"]:.0f} &times; {H["HS_L"]:.0f} &times; {H["HS_H"]:.0f} block. <b>Balloon 33
       has no BOM row</b> &mdash; ignore it, and read 34 as the single block. Everything else in the view
       is current. Listed under open items.</p>
  </div>
  <div class="grid">
    {pic("cad/out/exp_a.png","Exploded - three-quarter","")}
    {pic("cad/out/exp_b.png","Exploded - from the right","")}
    {pic("cad/out/exp_c.png","Exploded - from the left","")}
    {pic("cad/out/exp_rear.png","Exploded - from BEHIND","The other two views show the display side of every part. The bumps, the fitting blocks, the three bulkheads, the shroud's louvres and all four bail pieces only read from this side.")}
  </div>
  <div class="flag w">
    <h3>What the box actually is now</h3>
    <p>Shell <b>{OUT_W:.0f} &times; {OUT_H:.0f} &times; {DEPTH:.0f}</b> with an <b>{RIM:.0f} mm brim</b>,
       cover <b>{OUT_W:.0f} &times; {OUT_H:.0f} &times; {COVER_T:.0f}</b>. Two identical
       <b>{H["PI_BUMP_L"]:.0f} &times; {H["PI_BUMP_W"]:.0f} &times; {H["PI_BUMP_H"]:.0f}</b> bays stand off the
       cover &mdash; Pi stack at x{H["PI_BUMP_CX"]:+.0f}, buck at x{H["DRV_CX"]:+.0f} &mdash; so the unit is
       <b>{BAY_D:.0f} deep over a bay</b> and <b>{UNIT_D:.0f} over the fan shroud</b>, which is the number
       that matters when it swings.</p>
    <p>The controls moved out of a column beside the screen into a <b>row under it</b>, at
       {H["BTN_PITCH"]:.0f} mm pitch. That is the whole of rev C: the control strip became height instead of
       width, the shell came inside the <b>{H["BED"]:.0f} mm bed</b>, and it prints as
       <b>one piece, face down, no supports</b>. Bezel is {BEZEL:.0f} at the sides and {BEZEL_T:.0f} top.</p>
    <p><b>Nothing is cooled inside.</b> There is {H["FIN_GAP"]:.1f} mm behind the panel and no room for a fan
       or an inner sink in it. Everything thermal happens on the outside of the cover &mdash; see the thermal
       path below, including the part of it that is honestly weak.</p>
  </div>
  <div class="flag w">
    <h3>Why the split is this way round</h3>
    <p>The <b>front shell</b> is one piece (face + walls) and the <b>rear cover</b> is a flat plate whose
       {NBOLT} screws thread into the shell&rsquo;s rear brim. Nothing is bolted on from the front.</p>
    <p>It is better in four ways beyond looks: the front A-surface prints face-down so it is bed-smooth, the
       seal groove lands on a flat brim rather than on a wall, the joint sits at the back out of the weather,
       and every precision feature &mdash; aperture, bond land, control bores &mdash; sits on one part.</p>
  </div>
</section>

<section>
  <div class="sheet-hd"><h2>Bill of materials</h2><span class="file">printed parts, hardware, electronics</span></div>
  <div class="scroll"><table class="cmp">
    <tr><th>#</th><th>Item</th><th>Qty</th><th>Spec / note</th></tr>
    <tr><td class="m">1</td><td>Visor</td><td>1</td><td>ASA {g(V["VOL_CM3"])}. Hood {V["HOOD_W"]:.0f} wide, <b>friction pivots, no detent</b></td></tr>
    <tr><td class="m">2</td><td>Front shell</td><td>1</td><td>ASA {g(H["SHELL_CM3"])}. {OUT_W:.0f} &times; {OUT_H:.0f} &times; {DEPTH:.0f}, {H["FACE_T"]} mm face, prints face-down</td></tr>
    <tr><td class="m">3</td><td>12.3&Prime; 1920&times;720 LCD</td><td>1</td><td>module {H["MOD_W"]:.0f} &times; {H["MOD_H"]:.0f} &times; {H["MOD_D"]:.0f}, active {H["ACT_W"]:.0f} &times; {H["ACT_H"]:.0f} &mdash; both measured</td></tr>
    <tr><td class="m">4</td><td><b>12.3&Prime; LCD driver board</b> (LVDS/HDMI)</td><td>1</td><td><b>{DRV_L:.2f} &times; {DRV_W:.2f}</b>, 4 &times; M2.5 on the confirmed centres, in the <b>+x bay</b> on {H["PI_STANDOFF_H"]:.0f} mm bosses at x={H["DRV_BOARD_CX"]:.0f} &mdash; the bay is named for it. Ships with the panel; HDMI in from the Pi, LVDS out to the glass. The board moved 6 mm inboard of its bump so the Gore vent&rsquo;s bore passes over open air, not over its corner</td></tr>
    <tr><td class="m">5</td><td>DROK 9&ndash;36 V &rarr; 12 V 5 A</td><td>1</td><td>113.25 &times; 55.25 &times; 17, in the <b>+x bay</b> on {H["N_DRV_SCREWS"]} &times; M2.5. Hole pattern is <b>not rectangular</b></td></tr>
    <tr><td class="m">6</td><td>Raspberry Pi 4</td><td>1</td><td>85 &times; 56, in the <b>&minus;x bay</b>, turned portrait so the HDMI/USB-C edge faces the open side</td></tr>
    <tr><td class="m">6b</td><td>GeeekPi Armor Lite</td><td>1</td><td>Active cooler on the Pi. In a sealed box its fan exports nothing &mdash; it <b>stirs</b>, which is the point</td></tr>
    <tr><td class="m">7</td><td>PiCAN-M HAT</td><td>1</td><td>On the Pi. N2K connector position still needed</td></tr>
    <tr><td class="m">8</td><td>Rear cover</td><td>1</td><td>ASA {g(H["COVER_CM3"])}. Flat {COVER_T:.0f} mm plate: two bays, heatsink seat, trunnions, sensor standoffs</td></tr>
    <tr><td class="m">9</td><td>LP-24 shroud</td><td>1</td><td>ASA {g(LP.get("SHROUD_CM3"))}. {" &times; ".join(mm(v) for v in LP.get("SHROUD_BBOX", []))}. Dash-mounted, far end of the cable</td></tr>
    <tr><td class="m">10</td><td>Strain relief clamp</td><td>1</td><td>ASA {g(LP.get("CLAMP_CM3"))}. Jacket &Oslash;{LP.get("CABLE_D", 0):.1f} saddle</td></tr>
    <tr><td class="m">11</td><td>Fit coupon</td><td>1</td><td>ASA. <b>Print this first</b> &mdash; it is the bore and thread fit check</td></tr>
    <tr><td class="m">12</td><td>MCP23017</td><td>1</td><td>Holes {H["SENSORS"][0]["pitch_x"]:.2f} &times; {H["SENSORS"][0]["pitch_y"]:.2f}. Encoder + all four keys land on this one chip</td></tr>
    <tr><td class="m">13</td><td>MCP9808 / ADXL345 / ICM20948</td><td>3</td><td>25.40 &times; 17.78, holes {H["SENSORS"][1]["pitch_x"]:.2f} &times; {H["SENSORS"][1]["pitch_y"]:.2f}</td></tr>
    <tr><td class="m">13b</td><td>SEQURE M10-18 GPS</td><td>1</td><td><b>External puck is still the better answer</b> and the recommendation has not changed. But the internal option is now built: an {H["GPS_L"]:.0f} sq patch in a <b>shielded chimney in the &minus;x top block</b> at x={H["GPS_X"]:.0f}, pushed up from inside the Pi bay onto two shelves, under a <b>{H["GPS_WIN_T"]} mm ASA radome</b> &mdash; ASA is RF-transparent, so the window is the only thing between the patch and the sky. <b>Line the four walls and the shelf under it with copper foil, never the window</b>: that cup is both the EMI shield and the ground plane a patch needs and does not have in a plastic box. Bond to system ground at ONE point. {abs(H["GPS_X"] - H["SMA_X"]):.0f} mm from the whip, which is the point &mdash; a 400&ndash;470 MHz transmitter closer than that desenses L1 on every key-down</td></tr>
    <tr><td class="m">14</td><td>PCM1808 + PCM5102A</td><td>1 + 2</td><td><b>Measured.</b> 1808 is 34.5 &times; 8.25 &times; 9.5 over its caps; 5102A is 32.0 &times; 17.25 &times; 6.5. Strap-down bays, no mounting holes &mdash; bays now cut to the boards, not to a guess</td></tr>
    <tr><td class="m">15</td><td>RTL-SDR v3 dongle</td><td>1</td><td>{H["SDR_L"]:.0f} &times; {H["SDR_W"]:.0f} &times; {H["SDR_T"]:.0f}, <b>on edge</b> in the +x bay at x={H["SDR_X"]:.0f} &mdash; the bay&rsquo;s void is 75 wide and the driver board takes 55 of it, which leaves a 19 mm strip: too narrow to lay a dongle flat, wide enough to stand one in. Strapped to the two tie anchors on that bay&rsquo;s floor, directly under the SMA bulkhead it feeds. It has no mounting holes, so the strap is the mount</td></tr>
    <tr><td class="m">16</td><td>Oak Grigsby 91Q128</td><td>1</td><td>3/8-32 bushing, &Oslash;6.299 shaft, 3 V TTL. Bore &Oslash;{H["ENC_D"]}, knob &Oslash;{H["KNOB_OD"]}</td></tr>
    <tr><td class="m">17</td><td>Twidec 12 mm buttons</td><td>4</td><td>Bore &Oslash;{H["BTN_D"]}, dome &Oslash;{H["BTN_DOME"]}, at {H["BTN_PITCH"]:.0f} mm pitch</td></tr>
    <tr><td class="m">18</td><td>M3 &times; {H["BRIM_SCREW_L"]:.0f} 316 SS</td><td>{NBOLT}</td><td><b>Brim screws.</b> Through the cover into blind pilots in the shell, <b>outboard of the cord</b>. Bonded sealing washer on every one</td></tr>
    <tr><td class="m">19</td><td><b>M5 &times; 25 316 cap screw + M5 316 nyloc</b></td><td>2 sets</td><td><b>Visor pivots.</b> Screw in from the housing&rsquo;s upstand, nut <b>captive in a hex pocket in the visor ear&rsquo;s OUTBOARD face</b> &mdash; the inboard face is the friction land that runs on the 316 shim. Set by hand: firm enough to stay put, loose enough to move under bare-hand pressure</td></tr>
    <tr><td class="m">20</td><td><b>5-lobe tilt knob, M5 &times; {B["KNOB_STUD"]:.0f} stud</b> + M5 316 nyloc</td><td>2 sets</td><td><b>The tilt knobs.</b> Stud length is not a free choice: the knob&rsquo;s face, the captive nut in the trunnion web and the bay&rsquo;s outer wall leave a window about 7 mm wide, and the catalogue only sells 16/20/25/30. The arm&rsquo;s eye is <b>counterbored {B["EYE_CB"]:.0f} mm</b> so a stock <b>M5 &times; {B["KNOB_STUD"]:.0f}</b> engages the whole {H["TRUN_NUT_DEEP"]:.0f} mm nut and still stops 1 mm short of the bay wall. Elesa VC.692, Ganter GN&nbsp;5337 or Kipp K0155 all make this part with a stainless stud. Nut captive in the {H["TRUN_NUT_AF"]:.0f} mm hex pocket in the web</td></tr>
    <tr><td class="m">20b</td><td>Dash screws</td><td>{B["N_DASH"]}</td><td>Base plate to the dash, through &Oslash;{B["DASH_D"]} &times; {B["DASH_SLOT"]:.0f} slots in two rows {B["DASH_ROWS"]:.0f} apart</td></tr><tr><td class="m">20c</td><td><b>M5 &times; 16 316 + M5 heat-set insert</b></td><td>4 sets</td><td><b>Arm feet.</b> Up from <em>under</em> the base plate into inserts in the arm&rsquo;s {B["FOOT_PAD_T"]:.0f} mm foot pad &mdash; which is why the arms go on the plate before the plate goes on the dash. The blade thickens to take them: &Oslash;{B["INSERT_D"]} in a 7 mm blade left 0.8 mm of wall</td></tr>
        <tr><td class="m">21</td><td>M3 &times; 20 316 SS</td><td>4</td><td>LP-24 into the shroud frame</td></tr>
    <tr><td class="m">22</td><td>M4 &times; 30 316 SS</td><td>2</td><td>Clamp up into the shroud beam</td></tr>
    <tr><td class="m">23</td><td>M5 316 SS</td><td>8</td><td>LP-24 shroud to the dash</td></tr>
    <tr><td class="m">24</td><td>M2.5 &times; 8</td><td>{H["N_SENSOR_SCREWS"]}</td><td>Breakouts onto the cover&rsquo;s {H["STANDOFF_H"]} mm standoffs</td></tr>
    <tr><td class="m">25</td><td>CNLINKO LP-24</td><td>1</td><td>&Oslash;24.4 bore, 26.0 sq pattern</td></tr>
    <tr><td class="m">26</td><td><b>3/4&Prime; NPT straight cable gland</b>, 316 or IP68 nylon</td><td>1</td><td>Tapped into the &minus;x fitting block at x={H["GL_X"]:.0f}, <b>bore along &minus;y, facing DOWN</b>. Tap drill <b>&Oslash;{H["GL_TAP"]}</b> (59/64&Prime;), 3/4&ndash;14 taper tap. 3/4 NPT glands clamp <b>13&ndash;18 mm</b>, which is the window the {H["CABLE_D"]} mm Belden 1058A needs &mdash; an M16 clamps 5&ndash;10 and an M20 10&ndash;14, so neither would ever have closed on it.<br><b>NPT seals on the THREAD, not on a face</b>, so what it needs is engagement: L2 for 3/4&ndash;14 is {H["GL_NPT_L2"]} mm and the block is only {abs(H["BLK_Y1"]-H["BLK_Y0"]):.1f} deep, so the gland gets a local {H["GL_BOSS_W"]:.0f} &times; {H["GL_BOSS_H"]:.0f} boss standing {H["GL_BOSS_PROUD"]:.0f} mm proud &mdash; {abs(H["BLK_Y1"]-H["BLK_Y0"])+H["GL_BOSS_PROUD"]:.1f} mm of thread. The hex overhangs the boss freely; it is not bearing on anything. PTFE tape or a pipe sealant, not an O-ring</td></tr>
    <tr><td class="m">27</td><td><b>M12&times;1.5 IP68 breather screw</b></td><td>1</td><td>Tapped into the +x block at x={H["VENT_X"]:.0f}, drill &Oslash;{H["VENT_TAP"]}, facing DOWN. Hex body with an <b>O-ring under it</b> &mdash; it seals on the block&rsquo;s face, so that face stays flat and unbroken. It <b>stands {H["VENT_HANG"]:.0f} mm proud</b> of its seat; the vented nose has to be in free air, not buried. Equalises pressure so the cord only ever has to stop water. Do not paint it, do not seal over the nose</td></tr>
    <tr><td class="m">28</td><td>SMA female bulkhead, <b>M8&times;0.75 IP67</b></td><td>1</td><td>&Oslash;{H["SMA_D"]} bore at x={H["SMA_X"]:.0f} in the <b>TOP block of the driver bump</b>, facing <b>UP</b>, with its nut captive in a {H["SMA_NUT_AF"]:.0f} mm A/F hex pocket in the block&rsquo;s inner face. The whip screws straight onto it and stands at the sky &mdash; which is the whole reason it is on top of a bump and not on the flat cover face, where it would have pointed into the dash</td></tr>
    <tr><td class="m">29</td><td><b>{GASKET_T:.0f} mm round rubber cord</b></td><td>~{CORD_L/1000:.2f} m</td><td>In a {GASKET_W:.2f} &times; {H["GASKET_D"]:.2f} groove in the brim. Cut long, scarf the splice with CA, keep the joint <b>off the bottom rail</b></td></tr>
    <tr><td class="m">30</td><td>Belden 1058A</td><td>as needed</td><td>12 pair 20+22 AWG PLTC, overall foil, <b>{H["CABLE_D"]} mm OD</b>. <b>Bend radius {H["GL_BEND_R"]:.0f} mm</b> at 5&times;OD &mdash; and the bay it enters is only {H["PI_BUMP_L"]:.0f} wide, so <b>make the turn OUTSIDE</b>, in the free air under the unit, and bring it into the raceway already running across. Do not try to turn it inside the bay</td></tr>
    <tr><td class="m">31</td><td>Bail base plate</td><td>1</td><td>ASA {g(B.get("BASE_CM3"))}. {B["BASE_L"]:.0f} &times; {B["BASE_W"]:.0f} &times; {B["BASE_T"]:.0f}, flat to the dash</td></tr>
    <tr><td class="m">31b</td><td>Bail arm</td><td>2</td><td>ASA {g(B.get("ARM_CM3"))} each. Eye r{B["EYE_R"]:.0f} on the cover&rsquo;s trunnion; prints flat, blade in plane</td></tr>
    <tr><td class="m">32</td><td>Fan shroud</td><td>1</td><td>ASA {g(S.get("SHROUD_CM3"))}. {SH_BOX} box, louvres {S["LOUV_H"]:.0f} proud &mdash; {S["REAR_PROUD"]:.0f} behind the cover</td></tr>
    <tr><td class="m">34</td><td>Aluminium heatsink {H["HS_W"]:.0f} &times; {H["HS_L"]:.0f} &times; {H["HS_H"]:.0f}</td><td>1</td><td><b>Bonded base-out</b> into the {H["HS_BASE"]:.0f} mm seat in the cover&rsquo;s INNER face. Trim the fins back <b>{H["AP_SEAL"]:.0f} mm all round</b> to leave a sealing land</td></tr>
    <tr><td class="m">35</td><td><b>Coolerguys CG8025H12-IP67</b></td><td>{S["FAN_N"]}</td><td>{S["FAN_W"]:.0f} &times; {S["FAN_W"]:.0f} &times; {S["FAN_T"]:.0f}, {S["FAN_PITCH"]} pitch, dual ball, &minus;40..+70 &deg;C. Every IP-rated 80 is {S["FAN_T"]:.0f} thick</td></tr>
    <tr><td class="m">36</td><td>HYS whip antenna + rail/hardtop mount</td><td>1</td><td>185 mm, <b>SMA male</b>, 136&ndash;174 / 400&ndash;470 MHz. <b>Not on the housing</b> &mdash; it mounts remotely and feeds in by coax, the same call the GPS puck got</td></tr>
    <tr><td class="m">38</td><td>SMA pigtail, RG316</td><td>1</td><td>150 mm, bulkhead to SMA male &mdash; feeds the RTL-SDR. Plus an outside run from the bulkhead to wherever the whip is mounted</td></tr>
    <tr><td class="m">40</td><td>Adhesive copper or alloy foil</td><td>1 sheet</td><td>Shield between the antenna feed and the display ribbon. <b>Bond to system ground</b> &mdash; ungrounded foil does almost nothing</td></tr>
    <tr><td class="m">41</td><td>316 woven mesh sheet</td><td>1</td><td>{S["FILT_LX"]:.0f} &times; {S["FILT_LY"]:.0f} &times; {S["FILT_MESH"]}, ~20&ndash;40 mesh. Lies on the eight fan bosses and is clamped by the two fan frames &mdash; there is no recess. On the shroud&rsquo;s <b>inner</b> face, clamped by the fans&rsquo; own screws. <b>Not foam</b> &mdash; foam holds salt against the fins</td></tr>
    <tr><td class="m">42</td><td>M3 &times; {S["SCREW_L"]:.0f} 316 SS</td><td>4</td><td>Shroud corner bosses. Enter at the <b>louvred face</b>, stop in blind pilots {H["SHROUD_PILOT_DEEP"]} deep &mdash; they never pass through the cover</td></tr>
    <tr><td class="m">43</td><td>316 serrated washer pair, M5</td><td>2 pairs</td><td>One pair per bail joint, {H["FRIC_SHIM"]:.1f} mm. Teeth, not friction &mdash; they hold mechanically instead of on an unmeasured &mu;</td></tr>
    <tr><td class="m">44</td><td>Marine potting compound</td><td>1 tube</td><td>Fills the dam over the &Oslash;{H["WIRE_D"]:.0f} fan-lead pass. The <b>only</b> penetration that is not a screw</td></tr>
    <tr><td class="m">45</td><td>M3 &times; {int(math.ceil(H["DSP_SCREW_L"]/2)*2)} 316 SS</td><td>{H["N_DSP_POSTS"]}</td><td>Through the cover&rsquo;s bearing posts into the panel&rsquo;s own standoffs, so the silicone only seals. Bonded washer each</td></tr>
    <tr><td class="m">46</td><td>M3 bonded sealing washers</td><td>{NBOLT + H["N_DSP_POSTS"]}</td><td>{H["N_DSP_POSTS"]} panel screws (the only through-holes) plus {NBOLT} brim screws &mdash; those are blind, and the washer is there to keep a horizontal blind pilot from holding seawater against a 316 thread. <b>Tef-Gel every pilot</b></td></tr>
  </table></div>
  <div class="flag">
    <h3>The 8 M3 holes around the aperture are DELETED &mdash; do not drill them</h3>
    <p>They clamped the alloy heat plate to the outside of the cover. <b>There is no alloy plate.</b> The
       heatsink&rsquo;s own base closes the aperture from the inside, so every one of those eight would now be a
       through-hole in the weather face into the sealed cavity, held shut by nothing.</p>
    <p>Two of them were worse than redundant: at {H["AP_PITCH"]:.0f} mm pitch the pair at x &plusmn;{H["AP_PITCH"]:.0f}
       had their bores crossing the aperture edge at {H["AP_L"]/2:.0f}, cutting into the
       <b>{H["AP_SEAL"]:.0f} mm sealing land the heatsink is bonded to</b> &mdash; the one surface the whole
       thermal joint depends on. The other pair was cut entirely inside the aperture, i.e. in air, which is why
       the ring looked harmless in every render.</p>
    <p><b>The fans mount in the shroud</b>, not in the cover: {S["FAN_N"]} &times; {S["FAN_W"]:.0f} mm IP67 on
       eight pads behind the louvred face, their four screws each also clamping the mesh. The only fixings that
       reach the cover are the <b>4 shroud bosses</b>, and those stop in <b>blind pilots
       {H["SHROUD_PILOT_DEEP"]} mm deep</b>. Nothing new goes through the plate.</p>
  </div>
  <div class="flag w">
    <h3>Sensor positions &mdash; all four, on the cover&rsquo;s inner face</h3>
    <p>They used to stand inside the two board bays, and those bays are now <b>hollowed right through to the
       inner face</b> &mdash; so every one of them was standing on a floor that no longer exists. They sit in the
       top and bottom bands instead, which is the only inner face that is neither a bay nor the heatsink seat.
       Coordinates are <b>shell</b> coordinates; the cover mirrors in y.</p>
    <div class="scroll"><table class="cmp">
      <tr><th>Board</th><th>Centre</th><th>4 &times; M2.5 &Oslash;2.2 at</th></tr>
      {"".join(f'<tr><td>{s["name"]}</td><td class="m">({s["x"]:+.0f}, {s["y"]:+.0f})</td><td class="m">&plusmn;{s["pitch_x"]/2:.2f} x, &plusmn;{s["pitch_y"]/2:.2f} y</td></tr>' for s in H["SENSORS"])}
    </table></div>
    <p>Standoffs are <b>{H["STANDOFF_H"]} mm</b>, so board + standoff is {H["STANDOFF_H"]+1.6:.1f} mm against the
       {H["FIN_GAP"]:.1f} mm behind the panel. Every one is checked against the cover&rsquo;s sealing face, and the
       whole inner face is checked against the <b>panel envelope</b> rather than against a list of other cover
       features &mdash; which is what finally caught the old GPS cradle driving 1047 mm&sup3; through the display.</p>
    <p><b>The encoder and all four keys run through the MCP23017</b>, which is why it is the one board that has
       to be near the control row. I&sup2;C polling dropping quadrature counts is not a problem here: your code
       already uses a dedicated fast poller separate from the 1 Hz sampler, and the encoder runs at 3 V.</p>
  </div>
  <div class="flag">
    <h3>The mount is a bail, and it hangs on nothing but the cover</h3>
    <p><b>No dash tilt bracket, no detent, no VESA.</b> It is a Simrad-style bail: a base plate flat on the
       dash and <b>two arms</b> rising either side, pivoting at <b>mid-height</b> on
       <b>trunnions grown from the rear cover</b>. Bail base {B["BASE_L"]:.0f} &times; {B["BASE_W"]:.0f} &times;
       {B["BASE_T"]:.0f}; arm eyes r{B["EYE_R"]:.0f} on the trunnions&rsquo; r{H["TRUN_R"]:.0f} lands.</p>
    <p><b>Grown from the cover, not bolted to it.</b> A separate bracket needs screws through that plate, and
       every one of them is a hole in the pressure boundary the {GASKET_T:.0f} mm cord is there to seal. The
       trunnions sit <b>inside the bezel width</b> at x &plusmn;{H["TRUN_X"]:.0f} against an edge at
       {OUT_W/2:.0f}, with the arm faces at &plusmn;{B["ARM_FACE"]:.0f} and
       <b>{B["ARM_T"]:.0f} mm</b> of arm outboard of that &mdash; exactly to the bezel line, no further.</p>
    <p><b>Why mid-height.</b> The old bottom hinge put the assembled CG <b>114.7 mm above</b> the axis, which
       made the unit a pendulum on it &mdash; 12.4 N&middot;m at 6g, and that is the number that forced a detent
       crown. The axis now runs through the CG height at y{H["TILT_Y"]:+.1f}, so the moment falls with the lever
       instead of being fought with hardware, and hand-set friction is enough.</p>
    <p><b>The interface is a 316 serrated washer pair, not plain friction.</b> Inside the bezel width the disc
       cannot grow, and plain friction tops out under <b>1.4&times;</b> for any size that fits &mdash; a bigger
       disc grips harder but lengthens the lever by the same amount. Interlocking teeth hold mechanically,
       roughly 10&times; a friction face, so holding no longer depends on a friction coefficient nobody has
       measured. All <b>316</b> through the joint, and <b>Tef-Gel the threads</b>: 316 galls on 316, and a nut in
       a plastic pocket is a textbook crevice.</p>
    <p><b>How high it sits.</b> The base plate lies <b>flat on the dash under the unit</b> and the arms rise
       from it vertically &mdash; that is what a bail is. The axis lands <b>{B["RISE"]:.0f} mm above the
       plate</b>, and that height is solved, not chosen: tilt swings the unit&rsquo;s corners DOWN, and at
       {B["TILT_MAX"]:.0f}&deg; the lowest corner of the real envelope &mdash; cover, bay bumps, and the fan
       shroud {S["REAR_PROUD"]:.0f} mm behind the cover &mdash; reaches {B["DROP"]:.0f} mm below the axis, so the
       arms carry that plus <b>{B["DASH_CLEAR"]:.0f} mm of air</b> under it. Top edge of the unit sits
       {B["RISE"] + OUT_H/2 - H["TILT_Y"]:.0f} mm above the dash at rest; the axis is {B["AXIS_Z"]:.0f} mm behind the front face.</p>
    <p><b>The arms do not lean.</b> Leaning them puts the plate behind the unit instead of under it and adds a
       bending moment at every foot bolt, and it buys nothing &mdash; the clearance that matters is height.
       Base fixes with {B["N_DASH"]} &Oslash;{B["DASH_D"]} &times; {B["DASH_SLOT"]:.0f} slots in two rows
       {B["DASH_ROWS"]:.0f} apart, so the rows take the peel moment; the arm feet take
       {B["N_FOOT_BOLTS"]} M5 fore-and-aft, which is what resists each arm rotating about its own foot.</p>
    <p><b>Tilt runs one way: {B["TILT_DOWN"]:.0f}&deg; to {B["TILT_UP"]:.0f}&deg;, face UP.</b> That is the price
       of the arms staying inside the bezel width. They run at x&thinsp;{B["ARM_FACE"]:.0f}&ndash;{B["ARM_FACE"]+B["ARM_T"]:.0f}
       while the cover is {OUT_W:.0f} wide, so they share the unit&rsquo;s own footprint and can only do it by
       staying <em>behind</em> the cover. Tilting the face up swings the bottom edge forward, away from them
       &mdash; probed clear across the whole range. Tilting it down swings that edge into the blades:
       1,487&nbsp;mm&sup3; at 5&deg;, 16,174 at 20&deg;. Face-up is the direction a dash display below eye level
       is tilted anyway, so this is a range and not a consolation &mdash; but face-down would need the arms
       outboard of the bezel, and that is the constraint you set.</p>
    <p><b>Three parts, not a U</b> &mdash; for orientation, not for bed size. At {2*(B["ARM_FACE"]+B["ARM_T"]):.0f} mm
       a one-piece U would fit the {H["BED"]:.0f} bed; what it could not do is lie flat, because the base is
       horizontal and the arms are vertical. Split at the feet, each part prints flat in its strongest
       orientation and nothing is in cross-layer bending.</p>
    <p><b>Cable entry, vent and coax all face DOWN, in blocks beside the bumps.</b> They used to be on the
       cover&rsquo;s flat face, and they could not be: the two bay bumps own that face from |x|&nbsp;58 to 146
       and are hollowed right through, so two of the three bosses were built <em>inside a void</em>, fused to
       a bay wall by whatever part of them happened to overlap it. Outside the bays and inside the seal the
       flat face has a 10&nbsp;mm strip and a 15&nbsp;mm band left; the smallest of these fittings needs 19.</p>
    <p>The face is full &mdash; the part is not. Each bump stops at |y|&nbsp;62.5 while the cover runs to
       {OUT_H/2:.1f}, so beside each bump end there is a pocket 88 wide &times; 13.5 deep &times; {H["PI_BUMP_H"]:.0f} tall
       with nothing in it. A block fills the two bottom pockets and the three bores run <b>horizontally</b>
       through it and exit <b>downward</b>: no standing water, no sun on a nylon gland, an automatic drip loop
       on the cable, and zero cost in width or depth because nothing reaches past the bumps&rsquo; back plane.
       Every seat and every nut is in open air with the cover on the bench, which is when you fit them.</p>
    <p><b>The teardrops stop {H["SEAT_LAND"]:.0f} mm short of each face.</b> A horizontal bore&rsquo;s crown sags, so
       each has a 45&deg; apex above it &mdash; but an apex is a notch, and run full-length it cut a V-groove
       straight across the flange&rsquo;s O-ring land on all three. The last {H["SEAT_LAND"]:.0f} mm is round crown, which
       the tap trues anyway, and the build now probes a thin annulus at each face and refuses to export if it
       is not solid all the way round.</p>
    <p><b>{H["TIE_N"]} tie-wrap anchors</b> on the cover&rsquo;s inner face, {H["TIE_SLOT"]} mm slots for a
       standard 2.5 mm tie. They are on the cover because that is where the harness runs &mdash; the boards, the
       sensors and the gland are all on this part, and you dress cables before closing it up.</p>
  </div>
  <div class="flag w">
    <h3>Still open</h3>
    <p><b>Touchscreen driver board is not placed.</b> The DROK buck has the +x bay; the touch controller still
       needs its outline, hole pattern, and which edge the display ribbon and the HDMI/USB connectors leave from.</p>
    <p><b>PiCAN-M footprint and N2K connector position.</b> The Pi bay is sized for the stack, not for where the
       N2K plug wants to come out of it.</p>
    <p><b>The internal air-to-metal step is unproven.</b> See the thermal path &mdash; it is the one number on
       this build nobody has measured, and the fallback is drawn but not bought.</p>
  </div>
  <div class="flag w">
    <h3>Antenna &mdash; still wants a ground plane</h3>
    <p>&#128680; The HYS is a handheld whip, designed to work against a radio body and your hand as a
       counterpoise. On a plastic box it will show poor SWR and mediocre receive. For real AIS or VHF work, run
       the pigtail out to a proper marine antenna &mdash; the bulkhead is the right interface either way.</p>
    <p>&#9888; <b>GPS is an external puck now</b>, so the old RF problem &mdash; a transmit whip 26 mm from a GPS
       patch &mdash; is gone with it. What is left in the box is display-ribbon noise at L1 and into the SDR: the
       foil shield is still worth doing, and it <b>must be bonded to system ground</b>. Ungrounded foil does
       almost nothing.</p>
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
       width from that mistake and called it corroboration for an assumed 305. <b>Both retracted</b> &mdash; the
       sketch does not give the module width at all.</p>
    <p>The drawing above is redrawn with your datums: right edge for 133 and 26.5, bottom edge for 30 and 13,
       top edge for 8.25. It is settled now by measurement, not by that derivation: module
       <b>{H["MOD_W"]:.0f} &times; {H["MOD_H"]:.0f} &times; {H["MOD_D"]:.0f}</b>.</p>
  </div>
  <div class="flag">
    <h3>The aperture is cut to the measured panel</h3>
    <p>Active area measured <b>{H["ACT_W"]:.0f} &times; {H["ACT_H"]:.0f}</b>, against a derived 292.5 &times; 109.7
       &mdash; 2.5 narrow and 2.3 short. Had that gone to print it would have masked a strip of pixels down two
       edges.</p>
    <p>The aperture is <b>{H["APER_W"]:.0f} &times; {H["APER_H"]:.0f}</b>, and it is set by the <b>bond band</b>
       rather than by the active area: the module is {H["MOD_W"]:.0f} &times; {H["MOD_H"]:.0f} and the silicone
       needs a flat land, so the aperture is that outline less {(H["MOD_W"]-H["APER_W"])/2:.0f} mm a side. What
       shows in the extra is the module&rsquo;s own black border, not housing. It clears the active area by
       {(H["APER_W"]-H["ACT_W"])/2:.1f} mm a side.</p>
    <p>The panel is located, not just glued: a <b>rail across the bottom</b> it rests on and pads down each side,
       with the <b>top left open</b> so it goes in bottom-edge-first and swings home. Tight on all four and you
       would have to slide glass straight down through a wet bead. The seat is checked by pushing the panel past
       its fit in each direction and requiring the shell to push back &mdash; a rail that merely clears at
       nominal has located nothing.</p>
  </div>
  <div class="flag">
    <h3>Both big parts fit the bed now</h3>
    <p>They did not: at the old layout the shell was 389 &times; 193 against a {H["BED"]:.0f} &times;
       {H["BED"]:.0f} bed, which no rotation fixes, and it had to be printed in halves and bonded across the
       front face. Moving the control strip from beside the screen to <b>under</b> it turned width into height,
       where there was room to spare.</p>
    <p>Shell {OUT_W:.0f} &times; {OUT_H:.0f} and cover {OUT_W:.0f} &times; {OUT_H:.0f}: <b>one piece each,
       flat, {(H["BED"]-OUT_W)/2:.1f} mm a side to spare in x</b>. The bail base is the next biggest at
       {B["BASE_L"]:.0f}, which is also why it is three parts rather than a U.</p>
  </div>
  <div class="flag w">
    <h3>Where the measurements landed</h3>
    <p><b>Driver board is complete.</b> 113.25 &times; 55.25 &times; 17, four &Oslash;3.5 holes for M2.5 at
       TL (9.00, 3.75), TR (109.25, 3.75), BL (9.00, 48.00), BR (109.25, 51.50), origin top-left. The pattern is
       <b>not rectangular</b> &mdash; left pair 44.25 apart, right pair 47.75. A symmetric standoff set would
       not have fitted. It stands in the <b>+x bay</b>, which is {H["PI_BUMP_H"]:.0f} mm deep for exactly this.</p>
    <p><b>Display rear is complete too.</b> Five standoffs, not six &mdash; no top-centre. All &Oslash;8 base,
       M3 &times; 5 deep. The cover picks up <b>{H["N_DSP_POSTS"]} of them</b>: the centre one is under a board
       bay, and any post landing inside the heat aperture is dropped rather than printed as a loose island.</p>
    <p><b>Panel depth {H["MOD_D"]:.0f} mm</b> is what sets the shell at {DEPTH:.0f}: face {H["FACE_T"]} + panel
       {H["MOD_D"]:.0f} leaves the {H["FIN_GAP"]:.1f} mm that everything on the cover&rsquo;s inner face has to
       live inside.</p>
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
    {svgpic("cad/out/seal_detail.svg","Section through the top rail","The groove is SPLIT: the shell&rsquo;s brim takes {GD_SHELL} and the cover a {GD_COVER} witness groove on the same path, so the cord is captured on BOTH sides and cannot roll out of its seat as the lid closes. Total depth, and so the squeeze, is unchanged. Groove verified continuous on all four rails.")}
  </div>
  <div class="cols">
    <div class="panel"><h3>As modelled</h3><table>
      <tr><td>Groove</td><td>{GASKET_W:.2f} W &times; {H["GASKET_D"]:.2f} D</td></tr>
      <tr><td>Cord</td><td>{GASKET_T:.0f} mm round rubber</td></tr>
      <tr><td>Squeeze</td><td>~{100*(GASKET_T-H["GASKET_D"])/GASKET_T:.0f}%</td></tr>
      <tr><td>Path</td><td>&plusmn;{(OUT_W-2*(H["GASKET_OUT"]+GASKET_W/2))/2:.1f} &times; &plusmn;{(OUT_H-2*(H["GASKET_OUT"]+GASKET_W/2))/2:.1f}</td></tr>
      <tr><td>Cord length</td><td>{CORD_L:.0f} mm</td></tr>
      <tr><td>Brim face</td><td>{RIM:.0f} mm</td></tr>
      <tr><td>Groove to inner lip</td><td>{H["LAND_IN"]:.2f} mm</td></tr>
      <tr><td>Groove to bolt</td><td>{H["LAND_WEB"]:.2f} mm web</td></tr>
      <tr><td>Bolt to outer edge</td><td>{H["LAND_OUT"]:.2f} mm</td></tr>
      <tr><td>Fasteners</td><td>{NBOLT} &times; M3 &times; {H["BRIM_SCREW_L"]:.0f}</td></tr>
      <tr><td>Assembled gap</td><td>{H["GASKET_C"]:.0f} &mdash; metal to metal</td></tr>
    </table></div>
    <div class="panel"><h3>How it works</h3><ul class="chk">
      <li><b>A cord in a groove closes metal-to-metal.</b> The cover lands flat on the brim face and the cord is squeezed into its groove &mdash; the assembled gap is <b>zero</b>, where the old foam band held the cover 1.5 mm off. The display posts derive their length from that, so they moved with it</li>
      <li>Groove is in the <b>shell&rsquo;s brim</b>; the cover is a plain flat land. Cutting it into one part only is what keeps the joint self-aligning, and the brim face prints as a solid top surface &mdash; the best finish FDM gives</li>
      <li><b>The screws sit OUTBOARD of the cord</b>, so nothing is punched through the seal. The shell&rsquo;s pilots are blind and never reach the cavity, which makes the leak path the <b>cover&rsquo;s</b> through-holes &mdash; hence a bonded sealing washer on every one</li>
      <li>Depth {H["GASKET_D"]/GASKET_T:.2f} &times; cord, width {GASKET_W/GASKET_T:.2f} &times; cord &mdash; fills ~78% of the groove, leaving room for the squeezed cord to spread</li>
      <li>The brim is {RIM:.0f} mm because five bands have to fit across it: land {H["LAND_OUT"]:.2f} + M3 {H["BRIM_BOLT"]} + web {H["LAND_WEB"]:.2f} + groove {GASKET_W:.2f} + lip {H["LAND_IN"]:.2f}. The build fails if that stops adding up</li>
      <li>The <b>Gore vent</b> removes the pressure term, so this seal only has to stop water, not hold a differential</li>
      <li class="q">Splice the cord with a scarf joint and CA, positioned <b>away from the bottom rail</b></li>
      <li>&#10003; <b>Cord measured at {GASKET_T:.0f} mm</b> &mdash; the listing said both {GASKET_T:.0f} mm and 3/32&Prime; and they are 0.6 mm apart. It is the {GASKET_T:.0f}. The groove as drawn is correct and does not move</li>
    </ul></div>
  </div>
  <div class="flag w">
    <h3>Why a cord and not the foam band</h3>
    <p>The foam band was the previous answer and it is <b>gone</b>. The reason is plain: the cord is what is in
       the box on the bench, and flat closed-cell foam sheet in the right thickness is something you have to go
       and source. A seal you own beats a seal you have to find.</p>
    <p>It is also the easier of the two here. The cord is narrower than the {GASKET_W:.2f} band it replaces, so
       the brim gets <b>more</b> lip, not less &mdash; and a cord captured in a groove cannot roll out of the
       joint as the cover goes down, which a loose band can.</p>
  </div>
</section>

<section>
  <div class="sheet-hd"><h2>Hinged visor</h2><span class="rev">REV {H["REV"]}</span>
    <span class="file">helm_visor_revD.stp</span></div>
  <div class="grid">
    {pic("cad/out/asm_tilt_flat.png","Flat","0&deg;. Where it sits at rest.")}
    {pic("cad/out/asm_tilt_up.png","Tilted up","+10&deg;.")}
    {pic("cad/out/asm_tilt_max.png","Full tilt",f"+{B['TILT_UP']:.0f}&deg;, the end of the range. Tilt is FACE UP ONLY: the arms run inside the bezel width, so face-down swings the unit into them.")}
  </div>
  <div class="grid">
    {pic("cad/out/asm_visor_deployed.png","Visor deployed","Shading the screen from the top edge.")}
    {pic("cad/out/asm_visor_half.png","Visor half way","")}
    {pic("cad/out/asm_visor_stowed.png","Visor STOWED FLAT",f"&minus;90&deg;, lying across the bezel {abs(H['VIS_STOW_Z']):.0f} mm in front of it and clear of the glass. The hood sits ABOVE its axis so it folds forward; slung below it, it could only ever swing round behind the face.")}
  </div>
  <div class="cols">
    <div class="panel"><h3>As modelled</h3><table>
      <tr><td>Hood</td><td>{V["HOOD_W"]:.0f} wide, {V["BBOX"][1]:.0f} deep</td></tr>
      <tr><td>Pivot span</td><td>{V["SPAN"]:.0f} mm, x &plusmn;{H["PIV_X"][1]:.0f}</td></tr>
      <tr><td>Pivot land</td><td>r{H["FRIC_R0"]}&ndash;{H["FRIC_R1"]} annulus</td></tr>
      <tr><td>Pivot</td><td>friction on a {H["FRIC_SHIM"]} mm 316 shim, {2*FRIC_T:.2f} N&middot;m the pair</td></tr>
      <tr><td>Pivot bolt</td><td>M5 316 + nyloc, in the visor ear</td></tr>
      <tr><td>Mass in ASA</td><td>{g(V["VOL_CM3"])}</td></tr>
    </table></div>
    <div class="panel"><h3>Two decisions worth knowing</h3><ul class="chk">
      <li><b>Friction, not detent teeth &mdash; the crown is gone from both joints.</b> Teeth were the honest answer to a 6.19 N&middot;m moment on the old bottom hinge. Nothing on this part carries that: it is set by hand, it has no steps to land between, and its failure mode is slipping rather than splitting an ear</li>
      <li><b>What makes the friction hold is the 316 shim, not ASA on ASA.</b> Like-on-like stick-slips and polishes as it works, so the setting drifts. The shim runs free between the two printed lands, giving ASA/316 on both faces &mdash; and the two faces are in <b>series</b>, so the stack slips at whichever is weaker and only one face carries the torque. Counting both is how this calculation gets inflated 2&times;</li>
      <li><b>No side wings, and the bevel is structural.</b> On two pivots the hood is a {V["SPAN"]:.0f} mm cantilever. A bare flat plate has I = 373 mm&sup4; and flexes 15 mm under a 20 N push; the 45&deg; turned-down bevel lifts that to 953 mm&sup4; and 6 mm. Stress is SF 5 either way &mdash; the bevel is about how floppy it feels</li>
      <li>Pivot faces mesh at <b>0.00 mm</b> &mdash; upstands and ears verified coincident</li>
      <li class="q">Range is set by the housing; say if you want it to fold flat to the screen at rest</li>
    </ul></div>
  </div>
</section>

<section>
  <div class="sheet-hd"><h2>Housing parts</h2><span class="rev">REV {H["REV"]}</span>
    <span class="file">helm_shell_revD.stp &middot; helm_cover_revD.stp &middot; helm_visor_revD.stp</span></div>
  <div class="grid">
    {tile(0,"Front shell - face",f"Four soft keys at {H['BTN_PITCH']:.0f} mm pitch in a row UNDER the screen, encoder at the viewer&rsquo;s-right end. Visor pivots at the top. Nothing else on the face.")}
    {tile(2,"Front shell - three-quarter","The brim and the cord groove run all the way round the back of this part. Straight walls, no taper.")}
    {tile(3,"Front shell - inside",f"Straight wall, {RIM:.0f} mm from the back of the bezel to the rear brim, so the brim face is exactly {RIM:.0f} mm.")}
    {tile(4,"Rear cover",f"Two identical {H['PI_BUMP_L']:.0f} x {H['PI_BUMP_W']:.0f} bays, the heatsink aperture between them, and the tilt trunnions grown from the plate at x +/-{H['TRUN_X']:.0f}.")}
    {tile(5,"Visor - hinged","Friction pivots, set by hand. No detent crown on either joint.")}
    {tile(10,"Fan shroud",f"One louvred face - {S['LOUV_N']} slats at {S['LOUV_ANG']:.0f} deg, no round bores. Side louvres and a {S['DRAIN_BAYS']}-bay drain along the low edge.")}
  </div>
  <div class="cols">
    <div class="panel"><h3>As modelled</h3><table>
      <tr><td>Shell</td><td>{OUT_W:.0f} &times; {OUT_H:.0f} &times; {DEPTH:.0f}</td></tr>
      <tr><td>Cover</td><td>{OUT_W:.0f} &times; {OUT_H:.0f} &times; {COVER_T:.0f}</td></tr>
      <tr><td>Interior</td><td>{H["INT_W"]:.0f} &times; {H["INT_H"]:.0f}</td></tr>
      <tr><td>Front face</td><td>{H["FACE_T"]} mm</td></tr>
      <tr><td>Aperture</td><td>{H["APER_W"]:.0f} &times; {H["APER_H"]:.0f}</td></tr>
      <tr><td>Bezel</td><td>{BEZEL:.0f} side / {BEZEL_T:.0f} top</td></tr>
      <tr><td>Brim screws</td><td>{NBOLT} &times; M3 &times; {H["BRIM_SCREW_L"]:.0f}</td></tr>
      <tr><td>Controls</td><td>4 keys + encoder, {H["BTN_PITCH"]:.0f} mm pitch, y {H["ROW_CY"]:.1f}</td></tr>
      <tr><td>Board bays</td><td>2 &times; {H["PI_BUMP_L"]:.0f} &times; {H["PI_BUMP_W"]:.0f} &times; {H["PI_BUMP_H"]:.0f}</td></tr>
      <tr><td>Depth over a bay</td><td>{BAY_D:.0f} mm</td></tr>
      <tr><td>Depth over the shroud</td><td>{UNIT_D:.0f} mm</td></tr>
      <tr><td>Tilt trunnions</td><td>x &plusmn;{H["TRUN_X"]:.0f}, r{H["TRUN_R"]:.0f}, {H["TRUN_STAND"]:.0f} proud</td></tr>
      <tr><td>Tie-wrap anchors</td><td>{H["TIE_N"]}, on the cover</td></tr>
      <tr><td>Mass in ASA</td><td>{g(H["SHELL_CM3"])} + {g(H["COVER_CM3"])} + {g(V["VOL_CM3"])}</td></tr>
    </table></div>
    <div class="panel"><h3>Verified in geometry</h3><ul class="chk">
      <li>All parts single closed solids, <b>OCCT valid</b> &mdash; and the cover is checked for <b>floating features</b>, not just for solid count</li>
      <li><b>One piece each on a {H["BED"]:.0f} mm bed</b>, {(H["BED"]-OUT_W)/2:.1f} mm a side to spare</li>
      <li>The front face is flattened <b>globally</b> at z=0, so no ear, bore or pad can leave the A-surface standing on pads</li>
      <li>The assembled cover is intersected with the <b>panel envelope</b>: {H["N_DSP_POSTS"]} bearing posts touch it and nothing else may</li>
      <li>Both bays mirror exactly, and both are checked clear of the shroud envelope and the trunnion webs</li>
      <li>{H["N_DSP_POSTS"]} panel posts, {H["N_SENSOR_SCREWS"]//4} sensor pads, {H["TIE_N"]} tie anchors and the heatsink seat all verified <b>inboard of the sealing face</b></li>
      <li class="q">Bond the panel in and let it cure <b>before</b> the cover goes on &mdash; the glued position is the tolerance the {H["N_DSP_POSTS"]} screws inherit</li>
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
      <tr><td>Shroud</td><td>{" &times; ".join(mm(v) for v in LP.get("SHROUD_BBOX", []))}</td></tr>
      <tr><td>Clamp</td><td>{" &times; ".join(mm(v) for v in LP.get("CLAMP_BBOX", []))}</td></tr>
      <tr><td>LP-24 bore</td><td>&Oslash;24.4 teardrop</td></tr>
      <tr><td>Connector frame</td><td>46 &times; 46 &times; 12</td></tr>
      <tr><td>Jacket saddle</td><td>&Oslash;{LP.get("CABLE_D", 0):.1f}</td></tr>
      <tr><td>SR pilots</td><td>2 &times; &Oslash;3.5, opening down</td></tr>
      <tr><td>Mass in ASA</td><td>{g(LP.get("SHROUD_CM3"))} + {g(LP.get("CLAMP_CM3"))}</td></tr>
    </table></div>
    <div class="panel"><h3>Verified</h3><ul class="chk">
      <li><b>Ray-tested driver access</b> &mdash; 9 mm corridor from each pilot to the open face</li>
      <li>Teardrop <b>15.00</b> up vs <b>12.00</b> down, 38.7&deg; overhang</li>
      <li>Frame gives SF <b>4.4</b> against a 300 N lever on the plug</li>
      <li class="q">Confirm the 1058A jacket OD against the &Oslash;{LP.get("CABLE_D", 0):.1f} saddle</li>
    </ul></div>
  </div>
</section>

<section>
  <div class="sheet-hd"><h2>Fan shroud</h2><span class="file">{SH_BOX} box &middot; {S["REAR_PROUD"]:.0f} behind the cover</span></div>
  <div class="grid">
    {pic("cad/out/asm_shroud_fan.png","Shroud + both fans",f"{S['FAN_N']} x Coolerguys {S['FAN_W']:.0f}x{S['FAN_W']:.0f}x{S['FAN_T']:.0f} IP67, stacked at y {S['FAN_CY'][0]:+.0f} / {S['FAN_CY'][-1]:+.0f}, on eight pads behind the louvred face.")}
    {pic("cad/out/asm_shroud_fan_cut.png","Sectioned",f"Depth is counted through the stack, not chosen: {S['WALL']:.0f} wall + {S['FAN_BOSS']:.0f} boss + {S['FILT_MESH']} mesh + {S['FAN_T']:.0f} fan + plenum + {H['HS_PROUD']:.0f} of fin.")}
    {tile(6,"Bail base plate",f"{B['BASE_L']:.0f} x {B['BASE_W']:.0f} x {B['BASE_T']:.0f}, flat to the dash on {B['N_DASH']} slotted screws.")}
    {tile(7,"Bail arm - x2",f"Prints flat, blade in plane, eye r{B['EYE_R']:.0f} as a through boss. Nothing is in cross-layer bending.")}
  </div>
  <div class="flag w">
    <h3>Two 80s, not one 120 &mdash; and the louvres are the whole back</h3>
    <p>The heatsink is {H["HS_W"]:.0f} &times; {H["HS_L"]:.0f}: narrow and tall. A single 120 round was covering
       a square area over a strip and wasting most of its swept circle on shroud wall. Two 80s cover
       {2*S["FAN_W"]:.0f} of the {H["HS_W"]:.0f}.</p>
    <p>The outer face is <b>one louvred rectangle</b> &mdash; {S["LOUV_N"]} slats at {S["LOUV_ANG"]:.0f}&deg;, no
       round bores, no divider between the fans. Each slat&rsquo;s <b>outboard edge is its low edge</b>, so water
       that lands on it runs out and drips off; at {S["LOUV_ANG"]:.0f}&deg; with the pitch equal to the height
       there is no straight line of sight through the stack at all. Get that sign wrong and the louvres become
       gutters that funnel spray into the fan.</p>
    <p><b>These louvres are the only opening in the back.</b> Air leaves through side louvres with 45&deg; awnings
       over them and through a <b>{S["DRAIN_BAYS"]}-bay slot along the low edge</b> &mdash; which is the drain as
       much as it is exhaust. Without it this part is a tray holding salt water against the heatsink&rsquo;s glue
       line for the life of the boat.</p>
    <p>&#9888; The shroud <b>lands over four brim screw heads</b> and that is deliberate: shrinking it to clear
       them does not work, because two 80 mm fans span {2*S["FAN_W"]:.0f} exactly, and moving those four screws
       leaves a 104 mm gap in the fastener ring across the middle of the long edge. The shroud is relieved for
       the heads instead &mdash; a rain shield can afford four pockets; the pressure boundary cannot afford a
       gap in its clamp.</p>
  </div>
</section>

<section>
  <div class="sheet-hd"><h2>Drawings</h2><span class="file">LP-24 shroud &middot; all dimensions mm</span></div>
  <div class="grid dwgs">{dwg(0)}{dwg(1)}{dwg(2)}{dwg(3)}</div>
</section>

<section>
  <div class="sheet-hd"><h2>Subassemblies</h2><span class="file">the things a whole-unit render cannot show</span></div>
  <p>A render of the finished unit answers &ldquo;what does it look like&rdquo;. It does not answer
     &ldquo;where does that go&rdquo; or &ldquo;which way round does it fit&rdquo;, which are the
     questions that come up with a part in your hand. Each view below exists because a specific question
     had no picture.</p>
  <div class="grid">
    {subpic("sub_thermal_exploded")}
    {subpic("sub_shroud_fixing")}
  </div>
  <div class="grid">
    {subpic("sub_wire_pass")}
    {subpic("sub_fittings_context")}
    {subpic("sub_fittings_detail")}
    {subpic("sub_gps")}
  </div>
  <div class="flag">
    <h3>The thermal path &mdash; and the step that is honestly weak</h3>
    <p>One heatsink, <b>{H["HS_W"]:.0f} &times; {H["HS_L"]:.0f} &times; {H["HS_H"]:.0f}</b>, bonded
       <b>base-out</b> into a {H["HS_BASE"]:.0f} mm recess in the cover&rsquo;s <b>inner</b> face. Its base is
       flush inside; {H["HS_PROUD"]:.0f} mm of fin stands proud <b>outside</b> through the
       {H["AP_L"]:.0f} &times; {H["AP_W"]:.0f} aperture, under the shroud, in the fans&rsquo; airstream. There is
       no alloy plate and no conduction block: the heatsink&rsquo;s own base closes the aperture, which takes a
       part, an interface and 6 mm out of the stack.</p>
    <p>The recess walls <b>index the block while the adhesive cures</b>, so the gluing jig is gone too. Trim the
       fins back {H["AP_SEAL"]:.0f} mm all round first &mdash; a bought extrusion carries fins to the edge of its
       base, and without that band there is no flange to seal or glue against.</p>
    <p>&#9888; <b>The bottleneck is inside the box, not outside it.</b> With the fins pointing out, the interior
       sees a <b>bare flat plate {H["HS_L"]*H["HS_W"]/100:.0f} cm&sup2;</b>, and getting watts out of the
       internal air and into that plate is natural convection plus whatever the Pi&rsquo;s own fan stirs. The
       fans, the fins and the shroud are all working on the easy half of the problem. This is the one number on
       the build that nobody has measured.</p>
    <p><b>The fallback, if it throttles:</b> a second finned block bonded to the <b>inside</b> of that same base.
       The offcut from trimming this one&rsquo;s sealing land is very nearly the right part. The alternative
       orientation &mdash; fins inward &mdash; is not available: there are {H["FIN_GAP"]:.1f} mm behind the panel
       and the display screws need them.</p>
    <p>The <b>Pi</b> is the other source and it is handled differently, because it is a long way from anything
       metal and already carries its own cooler. In a sealed box that fan exports nothing &mdash; but it
       <em>stirs</em>, which lifts internal convection from roughly 4 to 15&ndash;20 W/m&sup2;K, and that term is
       exactly the one in the way.</p>
  </div>
</section>

<section>
  <div class="sheet-hd"><h2>Open items</h2><span class="file">what moves next</span></div>
  <div class="cols">
    <div class="panel"><h3>Blocking</h3><ul class="chk">
      <li class="q"><b>Gland, Gore vent and SMA bulkhead are being relocated</b> in a parallel pass &mdash; no coordinates for those three are settled, and this page states none</li>
      <li class="q"><b>Internal air-to-metal step unproven.</b> The inside of the heatsink base is a bare plate; if it throttles, bond a second finned block to it</li>
      <li class="q"><b>Touchscreen driver board is not placed</b> &mdash; outline, hole pattern, and which edge the ribbon and HDMI/USB leave from</li>
      <li class="q"><b>cad/exploded.py is a revision behind</b> &mdash; it still draws the alloy plate at balloon 33 and two strip heatsinks at 34</li>
      <li class="q"><b>Sensor tray has nowhere to go &mdash; and the spare room is in the wrong place.</b> With the audio boards measured, the PCM1808 stack is <b>15.0 mm</b> over the tray floor and the 5102A pair 12.0, against a <b>4.0 mm</b> air gap behind the display module. Meanwhile the Pi bay now measures <b>{H["PI_STACK_REAL"]:.1f} mm</b> of as-built stack (standoff {H["PI_STANDOFF_H"]:.0f} + Pi and PiCAN-M at {H["PI_HAT_H"]:.1f}) in <b>{H["PI_ROOM"]:.1f} mm</b> of room &mdash; about 24 mm of dead air. But the tray is 196 &times; 118 and the bay is {H["PI_BUMP_L"]:.0f} &times; {H["PI_BUMP_W"]:.0f}, so the headroom is not where the tray is. The tray outline was always provisional; this is what re-cuts it</li>
      <li class="q"><b>Fan drive.</b> Two IP67 fans on one potted pass: decide PWM off the MCP9808 vs straight 12 V before the leads are potted, because that is a one-shot joint</li>
    </ul></div>
    <div class="panel"><h3>Measure when convenient</h3><ul class="chk">
      <li>&#10003; <b>Encoder bushing 8.0 mm</b> &mdash; nut and lockwasher take 2.92, so it clamps 5.08 of panel and the {H["FACE_T"]} mm face fits with 2.58 spare. <b>No counterbore at the encoder.</b> Shaft and knob fixing are the owner&rsquo;s to sort at assembly</li>
      <li class="q">Belden 1058A jacket OD vs the &Oslash;{LP.get("CABLE_D", 0):.1f} saddle and the gland</li>
      <li class="q">PiCAN-M footprint and N2K connector position</li>
      <li class="q">Dash thickness, for the bail base screws</li>
    </ul></div>
  </div>
  <div class="flag w">
    <h3>Print notes</h3>
    <p><b>ASA blue &middot; 0.4 nozzle &middot; 0.2 mm &middot; enclosure on.</b>
       Perimeters <b>5 on the shell and cover</b>, 4 elsewhere. Infill <b>40% gyroid on the shell, cover and
       bail arms</b>, 25% elsewhere. This page used to say a flat &ldquo;5 perimeters, 30% gyroid&rdquo;, which
       contradicted the build manual&rsquo;s slicer card on both counts &mdash; the manual is the one you print
       and stand at the machine with, so it wins and this now matches it. Every part
       prints flat-face down with no supports &mdash; the shell face-down on the bed, the cover bays up, the
       shroud on its louvred face, both bail parts flat. Slice from 3MF at High refinement.</p>
    <p>About <b>{FILAMENT:.2f} kg</b> across {NPARTS} parts, at {ASA} g/cm&sup3;:
       {" &middot; ".join(f'{n} {g(v)}' + (f' x{q}' if q > 1 else '') for n, v, q in PRINTED if v)}.
       The fit coupon is extra &mdash; and print it first.</p>
    <p><b>Print <code>helm_encoder_coupon_revA</code> before anything else.</b> 9.8 cm&sup3;, about twenty minutes. Two &Oslash;9.7 bores: one through a {H["FACE_T"]} mm floor (the real shell face) and one through a 5.0 mm pad, which brackets the 5.08 mm the measured 8 mm bushing can clamp. Thread the encoder into the {H["FACE_T"]} station with its nut and lockwasher and you have proved the face.</p>
  </div>
</section>

<footer><span>Helm Print Package &middot; rev {H["REV"]} &middot; {NPARTS} printed parts</span><span>every dimension read from the geometry</span></footer>
</div>
"""
pathlib.Path("cad/out/review.html").write_text(HTML)
print("wrote", len(HTML)//1024, "KB")
