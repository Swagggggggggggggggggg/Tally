"""Render paired concept panels (crude ChatGPT left / real Claude right) from named presets.
python3 concepts.py NAME [NAME...] [--hi]
"""
import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor

B = os.environ.get("BLENDER", "/opt/blender/blender-4.5.14-linux-x64/blender")
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
    # D+E: same Gorilla Tag treehouse at two qualities, golden-hour backlight on the Claude side
    "treehouse": dict(
        L=dict(arm_deg=14, arm_deg_side={"-1": 177}, offset=[0, 0, 0.17], env="gt_crude",
               layout={"th_x": 1.5, "th_y": 5.4, "deck_z": 0.32},
               cam=cam([0, -1.05, 0.70], [0, 0, 0.70], 30, "L")),
        R=dict(pose=PEACE, face=None, env="gt_real", trees=0, cliffs=0, treehouse=False, no_env_bounce=False, sun_frame=[0.86, 0.42],
               layout={"th_x": 1.5, "th_y": 5.4, "deck_z": 0.32},
               hdri={"name": "sunset_forest", "rot": 0, "tint": "#FFF1DE", "strength": 1.0},
               sun={"energy": 8.0, "color": "#FFA84F", "angle": 3},
               haze=None, ferns=160, rocks=6,
               lights={"key": 200, "key_col": "#FFE9D2", "rim": 700, "rim_col": "#FFB561", "rim2": 500, "rim2_col": "#FFC780",
                       "fill": 60, "fill_col": "#D9E6FF", "sun": 0},
               cam=cam([0, -1.05, 0.70], [0, 0, 0.70], 30, "R", fstop=4.5))),
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


# v5 (main): teal ChatGPT build doing a primitive peace sign, a touch more real (AgX, soft sun, vinyl breakup, mild DOF);
# Claude relit as a backlit portrait (warm key front-left, warm low fill, strong rim on the sun side)
import copy as _copy
PRESETS["treehouse2"] = _copy.deepcopy(PRESETS["treehouse"])
PRESETS["treehouse2"]["L"].update(
    body="#0E8F6E", face_col="#A7ADB2", missing_arm=False, view="AgX", look="AgX - Punchy",
    arm_deg_side={"-1": 186, "1": 14}, arm_len_side={"-1": 0.19}, peace_side=["-1"],
    mat_detail={"scale": 40, "rough_var": 0.15, "bump": 0.06}, sun=3.4, sun_angle=4.0, sun_col="#FFF6EA",
    fill=90, fill_col="#E8F0FF", cam=cam([0, -1.05, 0.70], [0, 0, 0.70], 30, "L", fstop=5.6))
PRESETS["treehouse2"]["R"].update(
    sun={"energy": 10.0, "color": "#FFA84F", "angle": 3},
    lights={"key": 170, "key_pos": [-1.1, -2.0, 1.2], "key_size": 2.5, "key_col": "#FFE2C6",
            "fill": 35, "fill_pos": [0.3, -1.6, -0.4], "fill_size": 2.0, "fill_col": "#FFC7A0",
            "rim": 450, "rim_col": "#FFB868", "rim2": 1000, "rim2_col": "#FFB050", "sun": 0})


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
        if cfg.get('env') == 'gt_real':
            cfg['mist_out'] = f"{OUT}/{name}_R_mist.png"
        script = "panel.py"
    if HI:
        cfg["save_blend"] = f"{OUT}/{name}_{side}.blend"
    r = subprocess.run([B, "-b", "-P", script, "--", json.dumps(cfg)], cwd=HERE, capture_output=True, text=True)
    bad = [l for l in r.stdout.splitlines() + r.stderr.splitlines() if "Error" in l or "Traceback" in l]
    return f"{name}_{side}: {'OK' if os.path.exists(os.path.join(HERE, cfg['out'])) and not bad else 'FAIL ' + ' | '.join(bad[:3])}"


if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    sides = os.environ.get("SIDES", "LR")
    os.makedirs(os.path.join(HERE, OUT), exist_ok=True)
    with ThreadPoolExecutor(max_workers=int(os.environ.get("JOBS", "3"))) as ex:
        for res in ex.map(lambda t: job(*t), [(n, s) for n in names for s in sides]):
            print(res)
