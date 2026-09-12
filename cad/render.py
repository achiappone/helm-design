"""Self-contained STEP -> PNG renderer: tessellate, z-buffer rasterize, shade.
No external deps beyond numpy + zlib (PNG written by hand)."""
import numpy as np, zlib, struct, math
from build123d import import_step

def png(path, rgb):
    h, w, ch = rgb.shape
    raw = b''.join(b'\x00' + rgb[y].tobytes() for y in range(h))
    def chunk(t, d):
        c = struct.pack('>I', len(d)) + t + d
        return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    hdr = struct.pack('>IIBBBBB', w, h, 8, 6 if ch == 4 else 2, 0, 0, 0)
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', hdr)
                           + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))

def safe_tessellate(shape, tol):
    """build123d's own tessellate() is all-or-nothing: it walks every face and
    reads its triangulation, so ONE face that failed to mesh returns None and
    raises, losing the entire solid. Third-party STEP is full of those - Noctua's
    NF-F12 frame is 583 faces and a handful never mesh, which silently dropped
    the whole 55 cm3 frame from every assembly render and left the fan showing as
    blades and corner bumpers floating in mid air.

    So: mesh explicitly, then skip the faces that did not take, instead of
    throwing away the 570 that did. A few missing facets on a bought part shown
    for context is a far better answer than no part at all.
    """
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.BRep import BRep_Tool
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopAbs import TopAbs_REVERSED
    BRepMesh_IncrementalMesh(shape.wrapped, tol, False, 0.3, True)
    verts, tris, skipped = [], [], 0
    for f in shape.faces():
        loc = TopLoc_Location()
        poly = BRep_Tool.Triangulation_s(f.wrapped, loc)
        if poly is None:
            skipped += 1
            continue
        trsf = loc.Transformation()
        off = len(verts)
        for i in range(1, poly.NbNodes() + 1):
            pt = poly.Node(i).Transformed(trsf)
            verts.append((pt.X(), pt.Y(), pt.Z()))
        rev = f.wrapped.Orientation() == TopAbs_REVERSED
        for i in range(1, poly.NbTriangles() + 1):
            t = poly.Triangle(i)
            a, b, c = t.Value(1), t.Value(2), t.Value(3)
            if rev:
                b, c = c, b
            tris.append((off + a - 1, off + b - 1, off + c - 1))
    return verts, tris, skipped


def _mesh(shape, tol):
    """Fast path first, tolerant path only when the fast one dies."""
    try:
        v, t = shape.tessellate(tol)
        return [(q.X, q.Y, q.Z) for q in v], t
    except Exception:
        v, t, skipped = safe_tessellate(shape, tol)
        if skipped:
            print(f"  ~ tessellate: recovered {len(t)} tris, skipped {skipped} bad face(s)")
        return v, t


def rot(az, el):
    a, e = math.radians(az), math.radians(el)
    Rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, math.cos(e), -math.sin(e)], [0, math.sin(e), math.cos(e)]])
    return Rx @ Rz

def render(step, az, el, W=1000, H=750, ss=2, base=(0.16, 0.42, 0.78), bg=None):
    shape = import_step(step)
    verts, tris = _mesh(shape, 0.06)
    V = np.array(verts, dtype=np.float64)
    T = np.array(tris, dtype=np.int32)
    cen = (V.min(0) + V.max(0)) / 2
    V = V - cen
    R = rot(az, el)
    P = V @ R.T                       # camera space: x right, y depth, z up

    w, h = W * ss, H * ss
    sx, sz = P[:, 0], P[:, 2]
    scale = 0.86 * min(w / (sx.max() - sx.min()), h / (sz.max() - sz.min()))
    px = (sx * scale + w / 2)
    py = (h / 2 - sz * scale)
    depth = P[:, 1]

    A, B, C = T[:, 0], T[:, 1], T[:, 2]
    n = np.cross(P[B] - P[A], P[C] - P[A])
    ln = np.linalg.norm(n, axis=1); ln[ln == 0] = 1
    n = n / ln[:, None]
    n *= np.where(n[:, 1] > 0, -1.0, 1.0)[:, None]   # force normals toward camera
    L = np.array([-0.40, -0.72, 0.57]); L = L / np.linalg.norm(L)
    lam = np.clip(n @ L, 0, 1)
    L2 = np.array([0.55, -0.45, 0.20]); L2 = L2 / np.linalg.norm(L2)   # fill
    face = np.clip(0.30 + 0.62 * lam + 0.20 * np.clip(n @ L2, 0, 1), 0, 1.15)
    spec = np.clip(n @ L, 0, 1) ** 30 * 0.35

    zbuf = np.full((h, w), np.inf)
    img = np.zeros((h, w, 3), dtype=np.float32)
    img[:] = np.array(base) * 0.55 if bg is None else bg

    order = np.argsort(-((depth[A] + depth[B] + depth[C]) / 3))
    for i in order:
        a, b, c = A[i], B[i], C[i]
        x0, x1 = px[[a, b, c]].min(), px[[a, b, c]].max()
        y0, y1 = py[[a, b, c]].min(), py[[a, b, c]].max()
        ix0, ix1 = max(int(x0), 0), min(int(x1) + 2, w)
        iy0, iy1 = max(int(y0), 0), min(int(y1) + 2, h)
        if ix1 <= ix0 or iy1 <= iy0: continue
        xs = np.arange(ix0, ix1) + 0.5
        ys = np.arange(iy0, iy1) + 0.5
        gx, gy = np.meshgrid(xs, ys)
        x_a, y_a = px[a], py[a]; x_b, y_b = px[b], py[b]; x_c, y_c = px[c], py[c]
        d = (y_b - y_c) * (x_a - x_c) + (x_c - x_b) * (y_a - y_c)
        if abs(d) < 1e-12: continue
        l1 = ((y_b - y_c) * (gx - x_c) + (x_c - x_b) * (gy - y_c)) / d
        l2 = ((y_c - y_a) * (gx - x_c) + (x_a - x_c) * (gy - y_c)) / d
        l3 = 1 - l1 - l2
        m = (l1 >= -1e-9) & (l2 >= -1e-9) & (l3 >= -1e-9)
        if not m.any(): continue
        z = l1 * depth[a] + l2 * depth[b] + l3 * depth[c]
        sub = zbuf[iy0:iy1, ix0:ix1]
        upd = m & (z < sub)
        if not upd.any(): continue
        sub[upd] = z[upd]
        col = np.array(base) * face[i] + spec[i]
        img[iy0:iy1, ix0:ix1][upd] = np.clip(col, 0, 1)

    # crease / silhouette lines from depth discontinuities - CAD legibility
    z = np.where(np.isinf(zbuf), np.nan, zbuf)
    span = np.nanmax(z) - np.nanmin(z) if np.isfinite(z).any() else 1.0
    zf = np.nan_to_num(z, nan=np.nanmax(z) + span)
    gx_ = np.abs(np.diff(zf, axis=1, prepend=zf[:, :1]))
    gy_ = np.abs(np.diff(zf, axis=0, prepend=zf[:1, :]))
    edge = np.clip((np.maximum(gx_, gy_) / (span * 0.012)), 0, 1) ** 0.8
    img *= (1 - 0.85 * edge)[:, :, None]

    alpha = np.isfinite(zbuf).astype(np.float32)
    img = img.reshape(H, ss, W, ss, 3).mean(axis=(1, 3))     # downsample = AA
    alpha = alpha.reshape(H, ss, W, ss).mean(axis=(1, 3))
    rgba = np.concatenate([np.clip(img, 0, 1), alpha[:, :, None]], axis=2)

    ctr = (V.min(0) + V.max(0)) / 2 if False else None
    def proj(pt):
        q = (np.array(pt, dtype=float) - cen) @ R.T
        return (float(q[0]*scale + w/2)/ss, float(h/2 - q[2]*scale)/ss)
    return (rgba * 255).astype(np.uint8), proj

if __name__ == "__main__":
    import sys, time, base64, json
    jobs = [
        # rev C: display centred, controls in a row below, one-piece shell
        # Camera notes, both of which bit once:
        #  - at +el the camera sees the largest z first, i.e. the REAR brim.
        #    The front A-surface is at z=0, so it needs NEGATIVE el.
        #  - az=180 with -el puts model +y up and model -x on screen right.
        #    Viewer's right IS model -x, so this is the as-installed view;
        #    at az=0 the render comes out upside down AND mirrored.
        ("helm_shell_revC",  "rev C front face - straight on", 180,-90),
        ("helm_shell_revC",  "rev C front face - raking",      180,-62),
        ("helm_shell_revC",  "rev C - three-quarter",          150,-38),
        ("helm_shell_revC",  "rev C - rear / inside",           26, 52),
        ("helm_cover_revC",  "rev C rear cover",            30, 44),
        
        # still on rev B pivots - these need rebuilding for rev C
        ("helm_visor_revC",  "Visor - hinged, 16-tooth detent", 28, 30),
        ("tilt_bracket_revC","Dash tilt bracket",           200,-25),
        ("lp24_shroud_revD", "LP-24 shroud",                 35, 22),
        ("lp24_clamp_revD",  "Strain relief clamp",          32, 34),
        ("heatsink_shroud_revD", "Fan shroud - NF-F12",     200, 28),
    ]
    # ── detail crops ──────────────────────────────────────────────────────
    # The antenna knockout is 22 x 19 x 4 and does not read at whole-part
    # scale. Cut a chunk out and render that. The two lead-in details that used
    # to sit beside it are gone with the recesses they existed to show.
    from build123d import import_step as _imp, Pos, Box, Align, export_step
    import json as _json
    _H = _json.load(open("cad/out/housing.json"))
    _shell = _imp("cad/out/helm_shell_revC.stp")
    _cover = _imp("cad/out/helm_cover_revC.stp")
    _crop = _cover & (Pos(_H["ANT_X"], -_H["ANT_Y"], 0) * Box(70, 70, 40, align=(Align.CENTER,)*3))
    export_step(_crop, "cad/out/detail_antenna.stp")
    # Shallow elevation on purpose: the pocket is 4 deep, so a raking light is
    # the only thing that makes it read as depth.
    jobs += [("detail_antenna", "DETAIL - antenna bulkhead on the cover", 20, 40)]

    out = []
    for i, (f, title, az, el) in enumerate(jobs):
        t = time.time()
        rgb, _ = render(f"cad/out/{f}.stp", az, el)
        p = f"cad/out/render_{i}.png"
        png(p, rgb)
        out.append({"file": p, "title": title, "part": f})
        print(f"  {title:32s} {time.time()-t:5.1f}s  {len(open(p,'rb').read())//1024} KB")
    json.dump(out, open("cad/out/renders.json", "w"), indent=1)


# ─────────────────────────────────────────────────────── multi-part assembly
def render_multi(parts, az, el, W=1200, H=850, ss=2, bgtint=0.55, style="solid"):
    """parts = [(build123d shape, (r,g,b)), ...] rendered with one shared camera."""
    import numpy as _np
    Vs, Ts, Cs, off = [], [], [], 0
    for shape, col in parts:
        v, t = _mesh(shape, 0.12)
        Vs.append(_np.array(v))
        Ts.append(_np.array(t, dtype=_np.int32) + off)
        Cs.append(_np.tile(_np.array(col, dtype=float), (len(t), 1)))
        off += len(v)
    V = _np.vstack(Vs); T = _np.vstack(Ts); C = _np.vstack(Cs)

    cen = (V.min(0) + V.max(0)) / 2
    V = V - cen
    R = rot(az, el)
    P = V @ R.T
    w, h = W * ss, H * ss
    sx, sz = P[:, 0], P[:, 2]
    scale = 0.88 * min(w / (sx.max() - sx.min()), h / (sz.max() - sz.min()))
    px = sx * scale + w / 2
    py = h / 2 - sz * scale
    depth = P[:, 1]

    A, B, Cc = T[:, 0], T[:, 1], T[:, 2]
    n = _np.cross(P[B] - P[A], P[Cc] - P[A])
    ln = _np.linalg.norm(n, axis=1); ln[ln == 0] = 1
    n = n / ln[:, None]
    n *= _np.where(n[:, 1] > 0, -1.0, 1.0)[:, None]
    L = _np.array([-0.40, -0.72, 0.57]); L = L / _np.linalg.norm(L)
    L2 = _np.array([0.55, -0.45, 0.20]); L2 = L2 / _np.linalg.norm(L2)
    shade = _np.clip(0.34 + 0.60 * _np.clip(n @ L, 0, 1)
                     + 0.20 * _np.clip(n @ L2, 0, 1), 0, 1.2)

    line = (style == "line")
    if line:
        C = _np.ones_like(C) * 0.93
        shade = _np.clip(0.86 + 0.14 * shade, 0, 1)
    zbuf = _np.full((h, w), _np.inf)
    img = _np.zeros((h, w, 3), dtype=_np.float32)
    img[:] = 0.93 if line else 0.30
    order = _np.argsort(-((depth[A] + depth[B] + depth[Cc]) / 3))
    for i in order:
        a, b, c = A[i], B[i], Cc[i]
        ix0, ix1 = max(int(px[[a, b, c]].min()), 0), min(int(px[[a, b, c]].max()) + 2, w)
        iy0, iy1 = max(int(py[[a, b, c]].min()), 0), min(int(py[[a, b, c]].max()) + 2, h)
        if ix1 <= ix0 or iy1 <= iy0: continue
        gx, gy = _np.meshgrid(_np.arange(ix0, ix1) + 0.5, _np.arange(iy0, iy1) + 0.5)
        xa, ya, xb, yb, xc, yc = px[a], py[a], px[b], py[b], px[c], py[c]
        d = (yb - yc) * (xa - xc) + (xc - xb) * (ya - yc)
        if abs(d) < 1e-12: continue
        l1 = ((yb - yc) * (gx - xc) + (xc - xb) * (gy - yc)) / d
        l2 = ((yc - ya) * (gx - xc) + (xa - xc) * (gy - yc)) / d
        l3 = 1 - l1 - l2
        m = (l1 >= -1e-9) & (l2 >= -1e-9) & (l3 >= -1e-9)
        if not m.any(): continue
        z = l1 * depth[a] + l2 * depth[b] + l3 * depth[c]
        sub = zbuf[iy0:iy1, ix0:ix1]
        upd = m & (z < sub)
        if not upd.any(): continue
        sub[upd] = z[upd]
        img[iy0:iy1, ix0:ix1][upd] = _np.clip(C[i] * shade[i], 0, 1)

    zf = _np.where(_np.isinf(zbuf), _np.nan, zbuf)
    span = (_np.nanmax(zf) - _np.nanmin(zf)) if _np.isfinite(zf).any() else 1.0
    zf = _np.nan_to_num(zf, nan=_np.nanmax(zf) + span)
    thr = span * (0.0035 if line else 0.010)
    e = _np.clip(_np.maximum(_np.abs(_np.diff(zf, axis=1, prepend=zf[:, :1])),
                             _np.abs(_np.diff(zf, axis=0, prepend=zf[:1, :]))) / thr, 0, 1)
    img *= (1 - (0.97 if line else 0.85) * e)[:, :, None]
    alpha = _np.isfinite(zbuf).astype(_np.float32)
    img = img.reshape(H, ss, W, ss, 3).mean(axis=(1, 3))
    alpha = alpha.reshape(H, ss, W, ss).mean(axis=(1, 3))
    def proj(pt):
        q = (_np.array(pt, dtype=float) - cen) @ R.T
        return (float(q[0]*scale + w/2)/ss, float(h/2 - q[2]*scale)/ss)
    rgba = (_np.concatenate([_np.clip(img, 0, 1), alpha[:, :, None]], axis=2) * 255).astype(_np.uint8)
    return rgba, proj
