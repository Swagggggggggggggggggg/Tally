#!/bin/bash
# v6 (main): ChatGPT's low-poly gorilla vs the real Claude monke, one continuous treehouse scene split at the divider.
# (v5: preset treehouse2 + cfg_treehouse2_final.json, v4: treehouse + cfg_treehouse_final.json)
# Run from this folder. Needs Blender 4.5 (BLENDER=...), the NachoEngine rig at rig/GorillaTag_IK_Rig.blend
# (or GT_RIG=...), and Inter.ttf from Google Fonts in assets/.
set -e
python3 ph_get.py                              # CC0 Poly Haven HDRI, fir, fern, rocks, wood textures -> ph/
JOBS=1 python3 concepts.py unified --hi        # one at a time: the fir-tree scene needs ~5 GB RAM
python3 compose.py cfg_unified_final.json      # golden-hour post + labels -> final2/thumbnail_*
