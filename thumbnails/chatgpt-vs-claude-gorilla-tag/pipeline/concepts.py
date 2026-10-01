"""Render paired concept panels (crude ChatGPT left / real Claude right) from named presets.
python3 concepts.py NAME [NAME...] [--hi]
"""
import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor

B = "/opt/blender/blender-4.5.14-linux-x64/blender"
HERE = os.path.dirname(os.path.abspath(__file__))
HI = "--hi" in sys.argv
RES = {"w": 2560, "h": 1440, "samples": 64} if HI else {"w": 960, "h": 540, "samples": 12}
OUT = "final2" if HI else "out"

REAL_ENV = {
    "side": "right", "fur": "#F0784A", "glossy": 0.12, "glossy_color": "#FFE2B8", "name": "CLAUDE",
    "face": "tex/face_happy.png", "turn": 0, "root": [0, 0, 0.22], "aim_z": 0.7, "treehouse": False,
    "trees": 44, "tree_ymin": 5, "tree_clear_x": 1.3, "clear_ray": True, "cliffs": 0, "fur_emission": 0.0,
    "subsurface": 0.0, "leaf1": "#1F6A24", "leaf2": "#57B23A", "grass1": "#3E8A22", "grass2": "#86C83A",
    "ambient": "#FFF0DC", "ambient_strength": 1.0,
    "lights": {"key": 320, "key_col": "#FFF0DC", "rim": 340, "rim2": 160, "fill": 80, "sun": 4.6,
               "sun_rot": [35, 0, 25], "sun_col": "#FFE2B8", "rim_col": "#FFC27A", "fill_col": "#FFE9D6"},
    "sky": [[0, "#FFF0DA"], [0.45, "#E8F4FF"], [0.62, "#B5DAFA"], [0.8, "#5C9DEB"], [1, "#1E52C8"]],
    "fog": {"near": 9, "far": 30, "max": 0.18, "color": "#E6F1FA"},
}
CRUDE_ENV = {
    "face_col": "#7C7C7C", "sun": 2.6, "shoulder_z": 0.32, "missing_arm": True, "missing_scale": 14,
    "scale": 1.0, "offset": [0, 0, 0.21], "sun_rot": [25, 0, -20], "cube": False,
    "sky": [[0.0, "#5E5E5E"], [0.495, "#7D8287"], [0.505, "#DCE3EA"], [0.56, "#B9CFE9"], [0.75, "#7FA6DA"],
            [1.0, "#4D7EC6"]],
}
IDLE = {"torso": [2, 0, 0], "head": [-3, 0, 4],
        "hands_world": {"L": [0.36, -0.12, -0.34], "R": [-0.36, -0.12, -0.34]},
        "elbows_world": {"L": [1, 0.3, -0.2], "R": [-1, 0.3, -0.2]},
        "curls": {"L": [25, 25, 15], "R": [25, 25, 15]}}
V_POSE = {"torso": [-6, 0, 0], "head": [-4, 0, 6],
          "hands_world": {"L": [0.55, -0.15, 0.92], "R": [-0.55, -0.15, 0.92]},
          "elbows_world": {"L": [1, 0.2, -0.3], "R": [-1, 0.2, -0.3]},
          "curls": {"L": [0, 0, 0], "R": [0, 0, 0]}}
REACH = {"torso": [24, 0, 0], "head": [10, 0, 0],   # third person: arms reaching forward into the world
         "hands_world": {"L": [0.42, 0.55, 0.55], "R": [-0.42, 0.55, 0.40]},
         "elbows_world": {"L": [1, 0, -0.5], "R": [-1, 0, -0.5]},
         "curls": {"L": [10, 10, 0], "R": [10, 10, 0]}}


def cam(loc, target, lens, side, fstop=2.8):
    return {"loc": loc, "target": target, "lens": lens, "fstop": fstop, "shift_x": 0.25 if side == "L" else -0.25}


PEACE = {"torso": [2, 0, 0], "head": [-3, 0, 6],
         "hands_world": {"L": [0.13, -0.22, 0.44], "R": [-0.36, -0.12, -0.34]},
         "hand_rot": {"L": [-120, 0, 0]},
         "elbows_world": {"L": [1, 0, -1], "R": [-1, 0.3, -0.2]},
         "curls": {"L": [0, 0, 70], "R": [25, 25, 15]}}
IDLE_WIDE = {"torso": [2, 0, 0], "head": [-3, 0, 4],
             "hands_world": {"L": [0.42, -0.10, -0.40], "R": [-0.42, -0.10, -0.40]},
             "elbows_world": {"L": [1, 0.3, -0.2], "R": [-1, 0.3, -0.2]},
             "curls": {"L": [25, 25, 15], "R": [25, 25, 15]}}

PRESETS = {
    # chest-up portrait, staring at camera; Claude peace sign, crude copy raises a stiff arm
    "portrait": dict(
        L=dict(arm_deg=14, arm_deg_side={"-1": 177}, offset=[0, 0, 0.17], cam=cam([0, -1.05, 0.70], [0, 0, 0.70], 30, "L")),
        R=dict(pose=PEACE, cam=cam([0, -1.05, 0.70], [0, 0, 0.70], 30, "R"))),
    # same, but Claude's monke grips the divider bar like a climbing pole
    "grip": dict(
        L=dict(arm_deg=14, arm_deg_side={"-1": 177}, offset=[0, 0, 0.17], cam=cam([0, -1.05, 0.70], [0, 0, 0.70], 30, "L")),
        R=dict(pose=PEACE, pole={"dist": 0.78, "frac": 0.011, "grip": True, "grip_fy": 0.70, "grip_side": "R",
                                 "grip_offset": [0.075, 0.03, 0.0], "grip_rot": [0, 0, 90], "grip_elbow": [-1, 0.2, -0.6],
                                 "grip_curl": [80, 80, 60]},
               cam=cam([0, -1.05, 0.70], [0, 0, 0.70], 30, "R"))),
    # full body, Crazy Cat structure: crude T-pose vs real idle
    "fullbody": dict(
        L=dict(arm_deg=88, cam=cam([0, -1.85, 0.42], [0, 0, 0.48], 30, "L")),
        R=dict(pose=IDLE_WIDE, cam=cam([0, -1.85, 0.42], [0, 0, 0.48], 30, "R"))),
    # both idle, staring at camera, waist-up (Crazy Cat structure)
    "stare": dict(
        L=dict(arm_deg=14, cam=cam([0, -1.40, 0.62], [0, 0, 0.62], 24, "L")),
        R=dict(pose=IDLE, cam=cam([0, -1.40, 0.62], [0, 0, 0.62], 24, "R"))),
    # close-up faces staring at camera
    "faces": dict(
        L=dict(arm_deg=14, cam=cam([0, -0.78, 0.70], [0, 0, 0.68], 30, "L")),
        R=dict(pose=IDLE, cam=cam([0, -0.78, 0.70], [0, 0, 0.68], 30, "R"))),
    # T-pose (unfinished) vs celebrating
    "tpose": dict(
        L=dict(arm_deg=88, cam=cam([0, -1.70, 0.55], [0, 0, 0.62], 24, "L")),
        R=dict(pose=V_POSE, cam=cam([0, -1.70, 0.55], [0, 0, 0.62], 24, "R"))),
    # third person from behind, looking into the world each AI built
    "third": dict(
        L=dict(arm_deg=40, turn=180, cam=cam([0.0, -1.25, 1.05], [0, 3.0, 0.55], 24, "L")),
        R=dict(pose=REACH, turn=180, treehouse=True, treehouse_x=-0.6, treehouse_y=7.0, treehouse_z=1.8,
               tree_clear_x=0.6, cam=cam([0.0, -1.25, 1.05], [0, 3.0, 0.55], 24, "R"))),
}


def job(name, side):
    p = PRESETS[name][side]
    if side == "L":
        cfg = dict(CRUDE_ENV)
        cfg.update({k: v for k, v in p.items()})
        cfg.update(render=RES, out=f"{OUT}/{name}_L.png", mask_out=f"{OUT}/{name}_L_mask.png")
        script = "crude.py"
    else:
        cfg = dict(REAL_ENV)
        cfg.update({k: v for k, v in p.items()})
        cfg.update(render=RES, out=f"{OUT}/{name}_R.png", mask_out=f"{OUT}/{name}_R_mask.png")
        script = "panel.py"
    if HI:
        cfg["save_blend"] = f"{OUT}/{name}_{side}.blend"
    r = subprocess.run([B, "-b", "-P", script, "--", json.dumps(cfg)], cwd=HERE, capture_output=True, text=True)
    bad = [l for l in r.stdout.splitlines() + r.stderr.splitlines() if "Error" in l or "Traceback" in l]
    return f"{name}_{side}: {'OK' if os.path.exists(os.path.join(HERE, cfg['out'])) and not bad else 'FAIL ' + ' | '.join(bad[:3])}"


if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    os.makedirs(os.path.join(HERE, OUT), exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as ex:
        for res in ex.map(lambda t: job(*t), [(n, s) for n in names for s in ("L", "R")]):
            print(res)
