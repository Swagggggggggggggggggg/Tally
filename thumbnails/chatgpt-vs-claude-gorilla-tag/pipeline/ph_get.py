"""Download Poly Haven assets: python3 ph_get.py"""
import json, os, subprocess
UA = ["-A", "Mozilla/5.0"]
def files(aid):
    out = subprocess.run(["curl", "-sS"] + UA + [f"https://api.polyhaven.com/files/{aid}"], capture_output=True, text=True).stdout
    return json.loads(out)
def dl(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        subprocess.run(["curl", "-sS"] + UA + ["-o", path, url], check=True)
    return path
# HDRI
for h in ["misty_pines", "sunset_forest"]:
    f = files(h)
    dl(f["hdri"]["4k"]["hdr"]["url"], f"ph/hdri/{h}_4k.hdr")
    print("hdri", h)
# textures (2k, diffuse/rough/normal-gl)
for t in ["weathered_planks", "pine_bark", "forest_leaves_02", "forest_ground_04", "brown_planks_05", "roof_planks"]:
    f = files(t)
    for key, alts in (("Diffuse", ["Diffuse"]), ("Rough", ["Rough", "rough"]), ("nor_gl", ["nor_gl"])):
        for a in alts:
            if a in f:
                dl(f[a]["2k"]["jpg"]["url"], f"ph/tex/{t}/{key}.jpg")
                break
    print("tex", t, os.listdir(f"ph/tex/{t}"))
# models (gltf 2k incl. textures)
for m in ["pine_tree_01", "fir_tree_01", "fern_02", "rock_moss_set_01", "moss_01", "tree_stump_01", "pine_roots"]:
    f = files(m)
    g = f["gltf"]["2k"]["gltf"]
    base = f"ph/models/{m}"
    dl(g["url"], f"{base}/{m}.gltf")
    for rel, inc in g.get("include", {}).items():
        dl(inc["url"], f"{base}/{rel}")
    print("model", m, sum(os.path.getsize(os.path.join(dp, fn)) for dp, _, fns in os.walk(base) for fn in fns) // 1024, "KB")
