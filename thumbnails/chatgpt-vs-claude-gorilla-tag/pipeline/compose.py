"""Composite two panel renders into the final YouTube thumbnail.
python3 compose.py config.json
"""
import json, sys, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))


def load(p):
    return Image.open(p).convert("RGB")


def glow_layer(alpha, radius, opacity, color=(0, 0, 0)):
    """Soft shadow/glow from an alpha mask."""
    a = alpha.filter(ImageFilter.GaussianBlur(radius))
    a = a.point(lambda v: int(min(255, v * opacity)))
    lay = Image.new("RGBA", alpha.size, color + (0,))
    lay.putalpha(a)
    return lay


def stroke_layer(alpha, px, color=(0, 0, 0), opacity=1.0):
    a = alpha.filter(ImageFilter.MaxFilter(px * 2 + 1)).point(lambda v: int(v * opacity))
    lay = Image.new("RGBA", alpha.size, color + (0,))
    lay.putalpha(a)
    return lay


def text_img(text, font_path, size, weight=600, fill=(255, 255, 255), tracking=0):
    f = ImageFont.truetype(font_path, size)
    try:
        f.set_variation_by_axes([32, weight])
    except Exception:
        pass
    # measure
    tmp = Image.new("L", (10, 10))
    d = ImageDraw.Draw(tmp)
    w = 0
    boxes = []
    for ch in text:
        bb = d.textbbox((0, 0), ch, font=f)
        adv = f.getlength(ch)
        boxes.append(adv)
        w += adv + tracking
    asc, desc = f.getmetrics()
    im = Image.new("RGBA", (int(w + size * 0.2), asc + desc), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    x = 0
    for ch, adv in zip(text, boxes):
        dd.text((x, 0), ch, font=f, fill=fill + (255,))
        x += adv + tracking
    return im.crop(im.getbbox())


def label_left(cfg, W, H):
    """ChatGPT blossom + wordmark."""
    L = cfg["label_left"]
    h = int(L["height"] * H)
    logo = Image.open(L["logo"]).convert("RGBA")
    logo = logo.crop(logo.getbbox())
    logo = logo.resize((int(logo.width * h / logo.height), h), Image.LANCZOS)
    txt = text_img(L["text"], L["font"], int(h * L.get("text_scale", 1.0)), L.get("weight", 600),
                   tracking=L.get("tracking", 0))
    th = int(h * L.get("cap_ratio", 0.62))
    txt = txt.resize((int(txt.width * th / txt.height), th), Image.LANCZOS)
    gap = int(h * L.get("gap", 0.22))
    im = Image.new("RGBA", (logo.width + gap + txt.width, h), (0, 0, 0, 0))
    im.alpha_composite(logo, (0, 0))
    im.alpha_composite(txt, (logo.width + gap, int((h - th) / 2)))
    return im


def label_right(cfg, W, H):
    """Claude spark + serif wordmark (official artwork, text recoloured white)."""
    R = cfg["label_right"]
    h = int(R["height"] * H)
    wm = Image.open(R["wordmark"]).convert("RGBA")
    wm = wm.crop(wm.getbbox())
    wm = wm.resize((int(wm.width * h / wm.height), h), Image.LANCZOS)
    return wm


def place_label(base, lab, x, y, cfg):
    """Composite a label with dark glow + thin stroke for legibility on any sky."""
    pad = 60
    canvas = Image.new("RGBA", (lab.width + pad * 2, lab.height + pad * 2), (0, 0, 0, 0))
    canvas.alpha_composite(lab, (pad, pad))
    a = canvas.split()[3]
    S = cfg.get("label_style", {})
    out = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    out.alpha_composite(glow_layer(a, S.get("glow_r", 18), S.get("glow_op", 1.3)))
    if S.get("stroke", 0):
        out.alpha_composite(stroke_layer(a, S["stroke"], opacity=S.get("stroke_op", 0.85)))
    out.alpha_composite(canvas)
    base.alpha_composite(out, (int(x - pad), int(y - pad)))


def main(cfgp):
    cfg = json.load(open(cfgp))
    Lr, Rr = load(cfg["left"]), load(cfg["right"])
    W, H = Lr.size
    # per-panel grade
    for key, img in (("grade_left", Lr), ("grade_right", Rr)):
        g = cfg.get(key, {})
        if g:
            img2 = ImageEnhance.Color(img).enhance(g.get("sat", 1.0))
            img2 = ImageEnhance.Contrast(img2).enhance(g.get("con", 1.0))
            img2 = ImageEnhance.Brightness(img2).enhance(g.get("bri", 1.0))
            if key == "grade_left":
                Lr = img2
            else:
                Rr = img2
    D = cfg.get("divider", {})
    tx, bx = D.get("top", 0.53) * W, D.get("bottom", 0.47) * W
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon([(0, 0), (tx, 0), (bx, H), (0, H)], fill=255)
    base = Image.composite(Lr, Rr, mask).convert("RGBA")
    # optional outer glow around each monke (from silhouette masks), clipped to its own panel
    G = cfg.get("monke_glow")
    if G:
        for side, pm in (("left", mask), ("right", ImageChops.invert(mask))):
            mk = Image.open(G[side + "_mask"]).split()[3].resize((W, H))
            mk = ImageChops.multiply(mk, pm)
            dil = mk.filter(ImageFilter.MaxFilter(G.get("spread", 5) * 2 + 1))
            soft = dil.filter(ImageFilter.GaussianBlur(G.get("radius", 14)))
            outside = ImageChops.multiply(soft, ImageChops.invert(mk))
            op = G.get(side + "_opacity", G.get("opacity", 0.7))
            outside = ImageChops.multiply(outside, pm).point(lambda v, op=op: int(min(255, v * op)))
            col = tuple(int(G.get(side + "_color", "#FFFFFF")[i:i + 2], 16) for i in (1, 3, 5))
            lay = Image.new("RGBA", (W, H), col + (0,))
            lay.putalpha(outside)
            base.alpha_composite(lay)
    # divider: soft dark shadow then white line
    dw = int(D.get("width", 0.006) * W)
    line = Image.new("L", (W, H), 0)
    ImageDraw.Draw(line).line([(tx, -10), (bx, H + 10)], fill=255, width=dw)
    base.alpha_composite(glow_layer(line, D.get("shadow_r", 10), D.get("shadow_op", 0.6)))
    if D.get("glow_op", 0):
        base.alpha_composite(glow_layer(line, D.get("glow_r", 14), D["glow_op"], (255, 255, 255)))
    white = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    white.putalpha(line)
    base.alpha_composite(white)
    # labels
    ll = label_left(cfg, W, H)
    lr = label_right(cfg, W, H)
    m = cfg.get("label_margin", [0.035, 0.045])
    place_label(base, ll, m[0] * W, m[1] * H, cfg)
    place_label(base, lr, W - m[0] * W - lr.width, m[1] * H, cfg)
    # optional overlay (e.g. spark at the divider)
    for ov in cfg.get("overlays", []):
        o = Image.open(ov["path"]).convert("RGBA")
        if "size" in ov:
            o = o.resize((int(ov["size"][0] * W), int(ov["size"][1] * H)), Image.LANCZOS)
        base.alpha_composite(o, (int(ov["pos"][0] * W - o.width / 2), int(ov["pos"][1] * H - o.height / 2)))
    final = base.convert("RGB")
    g = cfg.get("grade_final", {})
    if g:
        final = ImageEnhance.Color(final).enhance(g.get("sat", 1.0))
        final = ImageEnhance.Contrast(final).enhance(g.get("con", 1.0))
    out = cfg["out"]
    final.save(out + "_full.png")
    small = final.resize((1280, 720), Image.LANCZOS)
    small = small.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
    small.save(out + "_1280.png")
    small.save(out + "_1280.jpg", quality=95, optimize=True, subsampling=0)
    # feed-size previews
    small.resize((320, 180), Image.LANCZOS).save(out + "_320.png")
    small.resize((160, 90), Image.LANCZOS).save(out + "_160.png")
    print("wrote", out, os.path.getsize(out + "_1280.jpg") // 1024, "KB jpg")


if __name__ == "__main__":
    main(sys.argv[1])
