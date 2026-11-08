"""Cinematic grade for the hero plates: a golden-hour-into-dusk sky (deep indigo at the top for the gold
title, amber at the horizon, a low sun glow) and a warm teal-and-gold grade on the stone and sand.
No AI: the sky is a gradient painted in code over the photo's own (plain) sky, keeping its grain.
The SAME grade goes on the plate with Sarah and the plate without her, so the dissolve stays seamless;
Sarah herself gets only a light touch of it, so her skin stays true.
Output: plates/giza-{mobile,desktop}-{sarah,empty}-graded.jpg and -cutout-graded.webp.
Run after tools/make_plates.py, from the repo root."""
import json, cv2, numpy as np
from PIL import Image
import importlib.util
spec = importlib.util.spec_from_file_location('mp', 'tools/make_plates.py'); mp = importlib.util.module_from_spec(spec); spec.loader.exec_module(mp)

def hexbgr(h): return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32) / 255

def her_mask(name, size):
    """Sarah's body (undilated) in frame pixels: only here is the grade softened."""
    fx, fy, FW, FH, _ = mp.FRAMES[name]; k = size[0] / FW
    raw = cv2.imread('source/sarah-mask-raw.png', 0)
    M = np.float32([[k, 0, -fx * k], [0, k, -fy * k]])
    m = cv2.warpAffine(raw, M, size, flags=cv2.INTER_LINEAR).astype(np.float32) / 255
    m = cv2.erode(m, np.ones((5, 5), np.uint8))
    return cv2.GaussianBlur(m, (0, 0), 3)

def sky_mask(img, base_y):
    """Soft sky matte: solid sky, plus a luminance matte across the pyramid's edge so no pale fringe stays."""
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    m = ((g > 165) & (np.arange(img.shape[0])[:, None] < base_y)).astype(np.uint8)
    n, l, s, _ = cv2.connectedComponentsWithStats(m)
    top = set(l[0][l[0] > 0])                                   # keep what touches the top edge
    core = np.isin(l, list(top)).astype(np.uint8)
    core = cv2.morphologyEx(core, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    band = cv2.dilate(core, np.ones((7, 7), np.uint8)) - cv2.erode(core, np.ones((3, 3), np.uint8))
    edge = np.clip((g.astype(np.float32) - 120) / (205 - 120), 0, 1) ** 1.4   # how much of the edge pixel is sky
    m = np.where(band > 0, edge, core.astype(np.float32))
    m[base_y:] = 0
    return cv2.GaussianBlur(m, (0, 0), 0.7)

def grade(img, sky, her, base_y, sun_x):
    f = img.astype(np.float32) / 255
    H, W = f.shape[:2]
    y = np.arange(H, dtype=np.float32)[:, None, None] / base_y   # 0 at top, 1 at the horizon
    x = np.arange(W, dtype=np.float32)[None, :, None] / W
    # --- the sky: indigo -> violet -> rose -> amber, with a low sun glow on the warm side
    stops = [(0.0, '0d0c26'), (0.28, '27234d'), (0.52, '5a3f6a'), (0.72, 'b0697a'), (0.86, 'e59a6e'), (1.0, 'f6c47f')]
    ys = np.clip(y[:, 0, 0], 0, 1); col = np.zeros((H, 3), np.float32)
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        t = np.clip((ys - a) / (b - a), 0, 1)[:, None]; sel = (ys >= a) & (ys <= b)
        col[sel] = (hexbgr(ca) * (1 - t) + hexbgr(cb) * t)[sel]
    newsky = np.broadcast_to(col[:, None, :], f.shape).copy()
    d = np.sqrt(((x - sun_x) * W / H) ** 2 + (y - 1.0) ** 2 * 0.35)
    glow = np.exp(-(d / 0.22) ** 2)
    newsky += glow * (hexbgr('ffd9a0') - newsky) * 0.75
    # keep the photo's own grain in it
    lum = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    grain = (lum - cv2.GaussianBlur(lum, (0, 0), 4))[..., None]
    newsky = np.clip(newsky + grain * 0.8, 0, 1)
    rs = np.random.default_rng(3); n = int(W * H / 9000)
    sx, sy = rs.integers(0, W, n), (rs.random(n) ** 2 * base_y * 0.45).astype(int)
    for a, b, v in zip(sx, sy, rs.random(n)):
        cv2.circle(newsky, (int(a), int(b)), 1, (1, 1, 1), -1, cv2.LINE_AA) if v > 0.85 else None
        newsky[b, a] = np.clip(newsky[b, a] + 0.25 + 0.4 * v * (1 - b / (base_y * 0.45)), 0, 1)
    # --- the land: lit by the low sun, warm amber highlights, plum-cool shadows, contrast
    land = 0.5 + (f - 0.5) * 1.15
    l = cv2.cvtColor(np.clip(land, 0, 1), cv2.COLOR_BGR2GRAY)[..., None]
    land = land * hexbgr('ffd29a')[None, None] * 1.06                        # golden light on everything
    land += np.array([-0.03, 0.03, 0.10], np.float32) * np.clip(l * 1.8 - 0.6, 0, 1)    # amber highlights
    land += np.array([0.06, -0.01, 0.01], np.float32) * np.clip(1 - l * 2.2, 0, 1)      # plum shadows
    side = np.clip(1 - np.abs(x - sun_x) * 0.9, 0.5, 1)                     # brighter toward the sun
    land *= (0.78 + 0.26 * side)
    gray = cv2.cvtColor(np.clip(land, 0, 1), cv2.COLOR_BGR2GRAY)[..., None]
    land = gray + (land - gray) * 1.15
    vig = 1 - 0.30 * np.clip(((y - 1) * base_y / H) * 2.2, 0, 1)             # the foreground settles into shadow
    land = np.clip(land * vig, 0, 1)
    # Sarah: a light touch only (her skin stays true)
    h = her[..., None] * 0.7
    land = land * (1 - h) + (f * 0.6 + land * 0.4) * h
    s = sky[..., None]
    return (np.clip(newsky * s + land * (1 - s), 0, 1) * 255).astype(np.uint8)

info = json.load(open('plates/cutouts.json'))
for name, (fx, fy, FW, FH, size) in mp.FRAMES.items():
    emp = cv2.imread(f'plates/giza-{name}-empty.jpg'); sar = cv2.imread(f'plates/giza-{name}-sarah.jpg')
    base_y = info[name]['base'][1]
    sky = sky_mask(emp, base_y)                    # from the EMPTY plate, used on both: identical backgrounds
    her = her_mask(name, size)
    sun_x = 0.12 if name == 'mobile' else 0.2      # the warm side of the original light (left)
    ge = grade(emp, sky, np.zeros_like(her), base_y, sun_x)
    gs = grade(sar, sky, her, base_y, sun_x)
    q = [cv2.IMWRITE_JPEG_QUALITY, 86, cv2.IMWRITE_JPEG_PROGRESSIVE, 1]
    cv2.imwrite(f'plates/giza-{name}-empty-graded.jpg', ge, q); cv2.imwrite(f'plates/giza-{name}-sarah-graded.jpg', gs, q)
    # the cutout, re-cut from the graded plate with Sarah (same alpha, same position)
    c = info[name]; old = np.array(Image.open(f'plates/giza-{name}-cutout.webp'))
    rgb = cv2.cvtColor(gs[c['y']:c['y'] + c['h'], c['x']:c['x'] + c['w']], cv2.COLOR_BGR2RGB)
    Image.fromarray(np.dstack([rgb, old[..., 3]])).save(f'plates/giza-{name}-cutout-graded.webp', quality=86, method=6)
    print(name, 'done')
