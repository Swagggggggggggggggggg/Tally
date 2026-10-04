"""Render the Beat Saber pair (crude left / real right) from one shared config.
python3 bs_run.py final [--hi]   (MID=1 for a 1920x1080 preview)
"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
B = os.environ.get("BLENDER", "/opt/blender/blender-4.5.14-linux-x64/blender")
HERE = os.path.dirname(os.path.abspath(__file__))
HI = "--hi" in sys.argv
RES = {"w": 2560, "h": 1440, "samples": 96} if HI else ({"w": 1920, "h": 1080, "samples": 24} if os.environ.get("MID") else {"w": 960, "h": 540, "samples": 16})
OUT = "final" if HI else "out"
BASE = {
    "cam": {"loc": [0, -1.7, 1.55], "target": [0, 6, 1.2], "lens": 24},
    "hero": {"left_note": [-0.661, -0.029, 1.333], "left_hilt": [-0.881, -0.479, 0.882], "left_dir": [0.327, 0.668, 0.669], "left_len": 1.73, "right_note": [0.661, -0.029, 1.333], "right_hilt": [0.881, -0.479, 0.882], "right_dir": [-0.327, 0.668, 0.669], "right_len": 1.73, "cut_normal": [-0.906, -0.019, -0.423], "swing_dir": [-0.27, -0.744, 0.611], "trail_axis": [0, 0.999, -0.045]},
}
# final: the published thumbnail. Hero placement (notes, sabers, cut plane) was solved in screen space with proj.py:
# each note sits on its blade line, the cut plane contains the camera ray, arrows are rolled to point along the swing.
PRESETS = {"final": {
        "hero": {
            "open": 14,
            "cut_gap": 0.36,
            "sparks": 20,
            "trail_deg": 45,
            "trail_in": 0.5,
            "saber_light": 14,
            "shards": 6,
            "right_hilt": [
                0.893,
                -0.327,
                0.914
            ],
            "right_dir": [
                -0.269,
                0.733,
                0.624
            ],
            "right_len": 1.99,
            "cut_normal": [
                -0.7708,
                0.2247,
                -0.5962
            ],
            "swing_dir": [
                -0.267,
                -0.68,
                0.683
            ],
            "trail_axis": [
                0,
                0.999,
                -0.045
            ],
            "right_note": [
                0.722,
                0.135,
                1.308
            ],
            "right_scale": 1.12,
            "spark_ends": [
                -1
            ],
            "left_note_shift": [
                0.0506,
                0.0149,
                -0.0396
            ],
            "left_arrow": -31.6,
            "right_note_shift": [
                -0.0562,
                0.0164,
                -0.0434
            ],
            "right_arrow": 31.3
        },
        "trail": 0,
        "trail_op": 0.14,
        "saber_fx": {
            "halo": 110,
            "halo_r": 0.08,
            "sheath": 1.6,
            "core": 70,
            "core_r": 0.0068,
            "sheath_r": 0.012
        },
        "layout": {
            "fan": [
                [
                    -6,
                    "blue"
                ],
                [
                    -2,
                    "pink"
                ],
                [
                    2,
                    "blue"
                ],
                [
                    6,
                    "pink"
                ],
                [
                    10,
                    "blue"
                ],
                [
                    14,
                    "pink"
                ]
            ]
        },
        "cut": 2.2,
        "cut_col": "#0A3DFF"
    }}


def merge(a, b):
    out = json.loads(json.dumps(a))
    for k, v in b.items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def job(name, mode):
    cfg = merge(merge(BASE, PRESETS[name]), PRESETS[name].get(mode, {}))
    side = "L" if mode == "crude" else "R"
    cfg.update(mode=mode, render=RES, out=f"{OUT}/{name}_{side}.png")
    cfg.update(cfg.pop(mode, {}) if False else {})
    if HI:
        cfg["save_blend"] = f"{OUT}/{name}_{side}.blend"
    r = subprocess.run([B, "-b", "-P", "bs_scene.py", "--", json.dumps(cfg)], cwd=HERE, capture_output=True, text=True)
    bad = [l for l in (r.stdout + r.stderr).splitlines() if "Error" in l or "Traceback" in l]
    ok = os.path.exists(os.path.join(HERE, cfg["out"])) and not bad
    return f"{name}_{side}: {'OK' if ok else 'FAIL ' + ' | '.join(bad[:4])}"


if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    os.makedirs(os.path.join(HERE, OUT), exist_ok=True)
    with ThreadPoolExecutor(max_workers=int(os.environ.get("JOBS", "2"))) as ex:
        for res in ex.map(lambda t: job(*t), [(n, m) for n in names for m in os.environ.get("MODES", "crude,real").split(",")]):
            print(res)
