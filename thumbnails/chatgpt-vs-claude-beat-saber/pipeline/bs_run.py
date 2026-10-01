"""Render the Beat Saber pair (crude left / real right) from one shared config.
python3 bs_run.py NAME [--hi]   (presets in PRESETS)
"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
B = os.environ.get("BLENDER", "/opt/blender/blender-4.5.14-linux-x64/blender")
HERE = os.path.dirname(os.path.abspath(__file__))
HI = "--hi" in sys.argv
RES = {"w": 2560, "h": 1440, "samples": 96} if HI else {"w": 960, "h": 540, "samples": 16}
OUT = "final" if HI else "out"
BASE = {
    "cam": {"loc": [0, -1.7, 1.55], "target": [0, 6, 1.2], "lens": 24},
    "hero": {"left_note": [-0.661, -0.029, 1.333], "left_hilt": [-0.881, -0.479, 0.882], "left_dir": [0.327, 0.668, 0.669], "left_len": 1.73, "right_note": [0.661, -0.029, 1.333], "right_hilt": [0.881, -0.479, 0.882], "right_dir": [-0.327, 0.668, 0.669], "right_len": 1.73, "cut_normal": [-0.906, -0.019, -0.423], "swing_dir": [-0.27, -0.744, 0.611], "trail_axis": [0, 0.999, -0.045]},
}
# v2 = the final thumbnail. Add "fog": 0.012 for volumetric haze on the neon side (tested: softer, less contrast at feed size)
PRESETS = {"v2": {"hero": {"open": 6, "cut_gap": 0.20}}}


def merge(a, b):
    out = json.loads(json.dumps(a))
    for k, v in b.items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def job(name, mode):
    cfg = merge(merge(BASE, PRESETS[name]), PRESETS[name].get(mode, {}))
    side = "L" if mode == "crude" else "R"
    cfg.update(mode=mode, render=RES, out=f"{OUT}/{name}_{side}.png")
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
