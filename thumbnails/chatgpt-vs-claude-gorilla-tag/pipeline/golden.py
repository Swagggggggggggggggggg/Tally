"""Golden-hour post for a render: depth haze, sun bloom, crepuscular rays, light wrap, split-tone grade.
Driven by the render's mist pass (0 = near, 1 = far/sky) and the subject's silhouette mask.
"""
import numpy as np
import cv2
from PIL import Image


def hexcol(h):
    return np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)], dtype=np.float32)


def to_lin(a):
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def to_srgb(a):
    a = np.clip(a, 0, None)
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - 0.055)


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def shoulder(x, knee=0.8):
    """Soft highlight roll-off so additive light never hard-clips."""
    over = np.maximum(x - knee, 0)
    return np.where(x < knee, x, knee + (1 - knee) * (1 - np.exp(-over / (1 - knee))))


def gray(path, W, H, alpha=False):
    im = Image.open(path)
    if alpha:
        a = np.asarray(im.split()[3], dtype=np.float32) / 255.0
    elif im.mode.startswith("I"):
        a = np.asarray(im).astype(np.float32) / 65535.0
    else:
        a = np.asarray(im.convert("L"), dtype=np.float32) / 255.0
    return cv2.resize(a, (W, H), interpolation=cv2.INTER_LINEAR)


def blur(a, sigma):
    return cv2.GaussianBlur(a, (0, 0), sigma) if sigma > 0 else a


def radial_blur(src, cx, cy, length, steps, decay):
    """Zoom-blur towards (cx, cy): screen-space volumetric light scattering."""
    H, W = src.shape[:2]
    acc = np.zeros_like(src)
    wsum = 0.0
    for i in range(steps):
        s = 1.0 - length * i / steps
        M = np.float32([[s, 0, cx * (1 - s)], [0, s, cy * (1 - s)]])
        w = decay ** i
        acc += w * cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        wsum += w
    return acc / wsum


def apply(img, G):
    """img: PIL RGB. G: golden config. Returns PIL RGB."""
    W, H = img.size
    rgb = to_lin(np.asarray(img, dtype=np.float32) / 255.0)
    mist = gray(G["mist"], W, H)
    a = gray(G["mask"], W, H, alpha=True)
    sx, sy = G["sun"][0] * W, G["sun"][1] * H
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.hypot(xx - sx, yy - sy) / W  # distance to sun in widths

    # 1) depth haze: far geometry dissolves into warm backlit air, brighter towards the sun
    Z = G.get("haze", {})
    if Z:
        near_sun = np.exp(-(d / Z.get("sun_r", 0.45)) ** 2)[..., None]
        col = to_lin(hexcol(Z.get("far_col", "#E9B98A"))) * (1 - near_sun) + to_lin(hexcol(Z.get("sun_col", "#FFD58F"))) * near_sun
        col = col * Z.get("intensity", 1.0)
        h = (Z.get("max", 0.5) * smooth(Z.get("start", 0.15), Z.get("end", 0.9), mist) * (1 - a))[..., None]
        h = h * (Z.get("floor", 0.55) + (1 - Z.get("floor", 0.55)) * near_sun)  # thicker glow in the sun's direction
        top = Z.get("top", 1.0)  # thinner air up in the canopy keeps the label zone dark
        h = h * (top + (1 - top) * smooth(Z.get("top_y0", 0.05), Z.get("top_y1", 0.45), yy / H))[..., None]
        rgb = rgb * (1 - h) + col * h

    # 2) rays: bright far pixels (sky gaps between trunks) smeared towards the sun
    R = G.get("rays", {})
    if R:
        lum = rgb @ np.float32([0.2126, 0.7152, 0.0722])
        src = smooth(R.get("depth", 0.8), 1.0, mist) * (1 - a)  # open air between trunks lets the sun through
        if R.get("lum1"):
            src = src * smooth(R.get("lum0", 0.0), R["lum1"], lum)
        src *= np.exp(-(d / R.get("reach", 0.6)) ** 2)
        rays = radial_blur(src.astype(np.float32), sx, sy, R.get("length", 0.55), R.get("steps", 48), R.get("decay", 0.985))
        rays = rays * R.get("strength", 1.2) * (1 - R.get("over_subject", 0.8) * a)
        rgb = rgb + rays[..., None] * to_lin(hexcol(R.get("color", "#FFC77A")))

    # 2b) background-only exposure lift (keeps the subject's grade untouched)
    if G.get("bg_lift"):
        rgb = rgb * (1 + (G["bg_lift"] - 1) * (1 - a))[..., None]

    # 3) sun bloom, occluded by the subject
    B = G.get("bloom", {})
    if B:
        g = B.get("core", 2.5) * np.exp(-(d / B.get("core_r", 0.035)) ** 2) + B.get("broad", 0.6) * np.exp(-(d / B.get("broad_r", 0.3)) ** 2)
        occl = np.clip(a * 1.0, 0, 1)
        rgb = rgb + (g * (1 - occl))[..., None] * to_lin(hexcol(B.get("color", "#FFC062")))

    # 4) light wrap: blurred background light bleeds onto the subject's silhouette edges
    L = G.get("wrap", {})
    if L:
        bg = rgb * (1 - a)[..., None]
        sig = L.get("radius", 0.008) * W
        wrap = blur(bg, sig) / np.maximum(blur(1 - a, sig), 1e-3)[..., None]
        edge = a * (1 - blur(a, sig) ** L.get("tightness", 2.0))
        rgb = rgb + wrap * (edge * L.get("strength", 0.8))[..., None]

    # 5) exposure + split tone (teal shadows, amber highlights), then soft shoulder
    T = G.get("grade", {})
    rgb = rgb * T.get("exposure", 1.0)
    if T:
        lum = rgb @ np.float32([0.2126, 0.7152, 0.0722])
        t = smooth(T.get("lo", 0.02), T.get("hi", 0.5), lum)[..., None]
        sh, hi = to_lin(hexcol(T.get("shadow", "#5E8A9A"))), to_lin(hexcol(T.get("high", "#FFC98C")))
        sh, hi = sh / (sh @ np.float32([0.2126, 0.7152, 0.0722])), hi / (hi @ np.float32([0.2126, 0.7152, 0.0722]))
        tint = sh * (1 - t) + hi * t
        amt = T.get("amount", 0.25)
        rgb = rgb * (1 - amt + amt * tint)
    rgb = shoulder(rgb, T.get("knee", 0.82))
    out = np.clip(to_srgb(rgb) * 255 + 0.5, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGB")
