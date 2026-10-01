"""Pinhole projection matching bs_scene's camera, to place things in screen space (fx, fy in 0..1)."""
import numpy as np
def basis(loc, target):
    loc, target = np.array(loc, float), np.array(target, float)
    f = target - loc; f /= np.linalg.norm(f)
    r = np.cross(f, [0, 0, 1]); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return loc, f, r, u
def project(p, loc=(0, -1.7, 1.55), target=(0, 6, 1.2), lens=24, sw=36, aspect=16 / 9):
    loc, f, r, u = basis(loc, target)
    d = np.array(p, float) - loc
    z = d @ f
    x = (d @ r) / z * lens / sw
    y = (d @ u) / z * lens / (sw / aspect)
    return 0.5 + x, 0.5 - y
def unproject(fx, fy, depth, loc=(0, -1.7, 1.55), target=(0, 6, 1.2), lens=24, sw=36, aspect=16 / 9):
    loc, f, r, u = basis(loc, target)
    x = (fx - 0.5) * sw / lens
    y = (0.5 - fy) * (sw / aspect) / lens
    return loc + depth * (f + x * r + y * u)
