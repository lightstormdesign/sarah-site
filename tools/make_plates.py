"""Hero plates for the Hall of Records preview.

Input  source/giza-original-crop.png  Sarah's real Giza photo (Instagram crop)
       source/giza-empty-crop.png     the same photo with her removed (tools/remove_sarah.py)
Output plates/giza-{mobile,desktop}-{sarah,empty}.jpg

The area added around the photo is environment only, built from the photo's own pixels:
the sky continues its own gradient, and pyramid stone and ground are copied from the photo's
own rows (so the courses stay level). Sarah is only ever her real photo, pasted back unchanged.
"""
import cv2, numpy as np
rng = np.random.default_rng(7)
orig = cv2.imread('source/giza-original-crop.png'); emp = cv2.imread('source/giza-empty-crop.png')
H, W = orig.shape[:2]
ef = emp.astype(np.float32)
g = cv2.cvtColor(emp, cv2.COLOR_BGR2GRAY).astype(int)

# the pyramid's two flanks, as lines x(y), and the row its base meets the ground
L = [(y, np.where(g[y] < 150)[0].min()) for y in range(90, 560, 10)]
R = [(y, np.where(g[y] < 150)[0].max()) for y in range(90, 650, 10)]
fl = np.polyfit(*zip(*L), 1); fr = np.polyfit(*zip(*R), 1)
xl = lambda y: np.polyval(fl, y); xr = lambda y: np.polyval(fr, y)
BASE = 1004

def edge_profile(cols):
    """Sky colour per row along one edge of the photo, carried on past the last sky row."""
    prof = np.zeros((H, 3), np.float32); last = 0
    for y in range(H):
        px = ef[y, cols]; sky = g[y, cols] > 175
        if sky.mean() > 0.9 and y < 700: prof[y] = px[sky].mean(0); last = y
    fit = [np.polyfit(np.arange(last - 120, last), prof[last - 120:last, c], 1) for c in range(3)]
    for y in range(last + 1, H):
        prof[y] = [np.clip(np.polyval(fit[c], min(y, last + 250)), 0, 255) for c in range(3)]
    return cv2.GaussianBlur(prof[:, None, :], (1, 31), 0)[:, 0]

def up_profile(rows):
    """Sky colour per column along the top edge, and how it changes going up."""
    top = ef[rows].mean(0)
    slope = (ef[0:20].mean(0) - ef[60:80].mean(0)) / 60.0
    return cv2.GaussianBlur(top[None], (61, 1), 0)[0], cv2.GaussianBlur(slope[None], (151, 1), 0)[0]

profL, profR = edge_profile(np.arange(0, 14)), edge_profile(np.arange(W - 14, W))
topC, topS = up_profile(slice(0, 8))

def quilt_rows(px, py, region, canvas):
    """Ground beyond the photo: blocks copied from random spots of the same rows, cross-faded."""
    ys, xs = np.where(region)
    if not len(ys): return
    B = 220
    blk = np.floor(px[ys, xs] / B).astype(int)
    u = (px[ys, xs] / B) - blk
    def src(b):
        r = np.random.default_rng(abs(int(b)) * 31 + 5)
        return r.integers(40, W - B - 40)
    off = {b: src(b) for b in range(blk.min(), blk.max() + 2)}
    s0 = np.array([off[b] for b in blk]) + (u * B).astype(int)
    s1 = np.array([off[b + 1] for b in blk]) + (u * B).astype(int) - B
    s1 = np.clip(s1, 0, W - 1)
    sy = np.clip(py[ys, xs], 0, H - 1)
    w = np.clip((u - 0.8) / 0.2, 0, 1)[:, None]          # fade into the next block over its last fifth
    canvas[ys, xs] = ef[sy, np.clip(s0, 0, W - 1)] * (1 - w) + ef[sy, s1] * w

def build(CW, CH, ox, oy):
    yy, xx = np.mgrid[0:CH, 0:CW]; py = yy - oy; px = xx - ox
    inside = (px >= 0) & (px < W) & (py >= 0) & (py < H)
    jit = cv2.GaussianBlur(rng.normal(0, 5, (CH, 1)), (1, 7), 0)[:, 0][:, None]
    stone = (py < BASE) & (py > 0) & (px > xl(py) + jit) & (px < xr(py) - jit)
    ground = py >= BASE
    sky = ~stone & ~ground
    out = np.zeros((CH, CW, 3), np.float32)
    # sky: left of the photo follows its left edge, right its right edge, above it its top edge
    pyc = np.clip(py, 0, H - 1)
    left = profL[pyc]; right = profR[pyc]
    t = np.clip(px / (W - 1), 0, 1)[..., None]
    side = left * (1 - t) + right * t
    above = np.clip(py, None, 0)                      # rows above the photo (negative)
    pxc = np.clip(px, 0, W - 1)
    climb = (-above)[..., None].astype(np.float32)
    damp = 60 * (1 - np.exp(-climb / 60))             # the change going up slows, as a real sky's does
    edge0 = np.where((px < 0)[..., None], profL[0], np.where((px >= W)[..., None], profR[0], topC[pxc]))
    skyv = np.where((py < 0)[..., None], edge0 + topS[pxc] * damp, side)
    skyv = cv2.GaussianBlur(skyv, (0, 0), 6)
    skyv += rng.normal(0, 1.5, (CH, CW, 1)).astype(np.float32)
    out[sky] = skyv[sky]
    # stone beyond the photo: same row, taken from the middle of the face at that height
    ys, xs = np.where(stone & ~inside)
    p = py[ys, xs]; mid = (xl(p) + xr(p)) / 2
    span = np.minimum((xr(p) - xl(p)) * 0.7, 520)
    sx = np.clip(mid - span / 2 + np.mod(px[ys, xs] - mid, span), 0, W - 1).astype(int)
    out[ys, xs] = ef[np.clip(p, 0, H - 1), sx]
    quilt_rows(px, py, ground & ~inside, out)
    # match the copied stone and ground to the photo's own tone at its edges, row by row:
    # keep their detail, replace their low frequencies with the photo's edge colour for that row
    def rowtarget(y, kind, side):
        y = min(max(y, 0), H - 1)
        if kind == 'ground':
            band = ef[y, :40] if side < 0 else ef[y, W - 40:]
        else:
            a = int(max(0, xl(y))) if side < 0 else int(min(W, xr(y))) - 60
            band = ef[y, max(0, a):max(0, a) + 60]
        return band.mean(0)
    for kind, M in (('stone', stone & ~inside), ('ground', ground & ~inside)):
        if not M.any(): continue
        Mf = M.astype(np.float32)
        lf = cv2.GaussianBlur(out * Mf[..., None], (0, 0), 30) / np.maximum(cv2.GaussianBlur(Mf, (0, 0), 30), 1e-3)[..., None]
        tl = np.array([rowtarget(y - oy, kind, -1) for y in range(CH)], np.float32)
        tr = np.array([rowtarget(y - oy, kind, 1) for y in range(CH)], np.float32)
        tl = cv2.GaussianBlur(tl[:, None], (1, 41), 0)[:, 0]; tr = cv2.GaussianBlur(tr[:, None], (1, 41), 0)[:, 0]
        tgt = np.where((px < W / 2)[..., None], tl[yy], tr[yy])
        out[M] = (out - lf + tgt)[M]
    # the far ground melts into a little haze where it meets the sky
    haze = ground & ~stone & ~inside
    hz = np.clip(1 - (py - BASE) / 26.0, 0, 1)[..., None] * 0.55
    hazec = np.where((px < 0)[..., None], profL[np.minimum(BASE, H - 1)], profR[np.minimum(BASE, H - 1)])
    out = np.where(haze[..., None], out * (1 - hz) + hazec * hz, out)
    # soften the new stone edges against the sky
    se = (stone & ~inside).astype(np.uint8)
    edge = cv2.dilate(se, np.ones((3, 3))) - cv2.erode(se, np.ones((3, 3)))
    bl = cv2.GaussianBlur(out, (3, 3), 0); out[edge > 0] = bl[edge > 0]
    # feather the new sky into the photo's own sky across the seam
    a = np.zeros((CH, CW), np.float32); a[inside] = 1
    a = cv2.GaussianBlur(a, (0, 0), 14)
    res = {}
    for tag, src in (('empty', emp), ('sarah', orig)):
        c = out.copy(); c[oy:oy + H, ox:ox + W][:] = 0
        full = out.copy(); full[inside] = src.astype(np.float32)[py[inside], px[inside]]
        fe = sky & (a < 1) & inside                     # photo sky pixels near the seam
        w = a[..., None]
        blend = np.where(fe[..., None], full * w + out * (1 - w), full)
        res[tag] = np.clip(blend, 0, 255).astype(np.uint8)
    return res

def frame(fx, fy, FW, FH):
    x0 = min(0, fx); y0 = min(0, fy); x1 = max(W, fx + FW); y1 = max(H, fy + FH)
    imgs = build(x1 - x0, y1 - y0, -x0, -y0)
    return {k: v[fy - y0:fy - y0 + FH, fx - x0:fx - x0 + FW] for k, v in imgs.items()}

def save(imgs, size, base):
    for tag, c in imgs.items():
        r = cv2.resize(c, size, interpolation=cv2.INTER_AREA)
        cv2.imwrite(f'plates/{base}-{tag}.jpg', r, [cv2.IMWRITE_JPEG_QUALITY, 86, cv2.IMWRITE_JPEG_PROGRESSIVE, 1])

FRAMES = {}
_FH = H + 420; _FW = round(_FH * 9 / 16)             # phone 9:16: sky above the pyramid for the title
FRAMES['mobile'] = ((W - _FW) // 2 + 10, -420, _FW, _FH, (1080, 1920))
_FH = H + 150; _FW = round(_FH * 16 / 9)             # desktop 16:9: the whole pyramid, Sarah right of centre
FRAMES['desktop'] = (830 - int(_FW * 0.64), -150, _FW, _FH, (1920, 1080))

def cutouts():
    """Sarah's real photo as a cutout (her pixels unchanged, soft edge) for each frame, so the site can
    dissolve her out in code over the empty plate. Writes plates/giza-{mobile,desktop}-cutout.webp and
    their position in the frame to plates/cutouts.json."""
    import json
    from PIL import Image
    m = cv2.imread('source/sarah-mask.png', 0).astype(np.float32) / 255
    m = cv2.GaussianBlur(m, (0, 0), 6)
    info = {}
    for name, (fx, fy, FW, FH, size) in FRAMES.items():
        k = size[0] / FW
        rgba = np.dstack([orig, (m * 255).astype(np.uint8)])
        ys, xs = np.where(m > 0.01)
        x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, min(ys.max() + 1, H)
        crop = rgba[y0:y1, x0:x1]
        # position in the output frame (px of a size[0] x size[1] image)
        X, Y = (x0 - fx) * k, (y0 - fy) * k
        w, h = round((x1 - x0) * k), round((y1 - y0) * k)
        crop = cv2.resize(crop, (w, h), interpolation=cv2.INTER_AREA)
        # keep only what lands inside the frame
        cx0, cy0 = max(0, -round(X)), max(0, -round(Y))
        cx1, cy1 = min(w, size[0] - round(X)), min(h, size[1] - round(Y))
        crop = crop[cy0:cy1, cx0:cx1]
        Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGRA2RGBA)).save(f'plates/giza-{name}-cutout.webp', quality=86, method=6)
        info[name] = {'frame': list(size), 'x': round(X) + cx0, 'y': round(Y) + cy0, 'w': int(crop.shape[1]), 'h': int(crop.shape[0])}
    json.dump(info, open('plates/cutouts.json', 'w'), indent=2)
    print(info)


if __name__ == '__main__':
    for name, (fx, fy, FW, FH, size) in FRAMES.items():
        save(frame(fx, fy, FW, FH), size, f'giza-{name}')
    cutouts()
