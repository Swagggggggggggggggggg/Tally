#!/bin/bash
# v5 (main): teal crude ChatGPT build vs real golden-hour Claude scene, 2560x1440. (v4: preset treehouse + cfg_treehouse_final.json)
# Run from this folder. Needs Blender 4.5 (set B in concepts.py), the NachoEngine rig at rig/GorillaTag_IK_Rig.blend
# (or GT_RIG=...), and Inter.ttf from Google Fonts in assets/.
set -e
python3 ph_get.py                              # CC0 Poly Haven HDRI, fir, fern, rocks, wood textures -> ph/
JOBS=1 python3 concepts.py treehouse2 --hi     # one at a time: the fir-tree scene needs ~5 GB RAM
python3 compose.py cfg_treehouse2_final.json   # golden-hour post + labels -> final2/thumbnail_*
