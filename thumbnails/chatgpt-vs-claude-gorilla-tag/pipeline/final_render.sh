#!/bin/bash
# Final hero renders (2560x1440). Run from the blender/ folder.
B=/opt/blender/blender-4.5.14-linux-x64/blender
BASE='"face":"tex/face_angry.png","treehouse":false,"turn":30,"trees":44,"tree_ymin":5,"tree_clear_x":1.3,"clear_ray":true,"cliffs":0,"fur_emission":0.0,"subsurface":0.0,"leaf1":"#1F6A24","leaf2":"#57B23A","grass1":"#3E8A22","grass2":"#86C83A","render":{"w":2560,"h":1440,"samples":96},"cam":{"loc":[0.32,-1.40,0.13],"target":[0.32,0,0.49],"lens":34,"fstop":2.0},"pose":{"torso":[20,0,0],"head":[7,0,0],"lead_world":[0.30,-0.30,-0.20],"lead_elbow":[0.7,0.3,-0.6]}'
LEFT='"side":"left","fur":"#2E3238","glossy":0.12,"glossy_color":"#DDF6FF","name":"CHATGPT","ambient":"#CFE2FF","ambient_strength":1.0,"lights":{"key":320,"rim":340,"rim2":160,"fill":80,"sun":4.2,"sun_rot":[55,0,-35],"rim_col":"#9EE8FF"},"sky":[[0,"#DFF6FF"],[0.5,"#C2ECFF"],[0.7,"#6CC0FF"],[0.88,"#2F86F0"],[1,"#1A55D0"]],"fog":{"near":9,"far":30,"max":0.18,"color":"#C4ECFF"},"mask_out":"final/L_mask.png","save_blend":"final/ChatGPT_panel.blend"'
RIGHT='"side":"right","fur":"#F0784A","glossy":0.12,"glossy_color":"#FFE2B8","name":"CLAUDE","ambient":"#FFF0DC","ambient_strength":1.0,"lights":{"key":320,"key_col":"#FFF0DC","rim":340,"rim2":160,"fill":80,"sun":4.6,"sun_rot":[55,0,35],"sun_col":"#FFD9A8","rim_col":"#FFC27A","fill_col":"#FFE9D6"},"sky":[[0,"#FFF0DA"],[0.45,"#FFE8CC"],[0.62,"#CFE6F7"],[0.8,"#5C9DEB"],[1,"#1E52C8"]],"fog":{"near":9,"far":30,"max":0.18,"color":"#F7E6CF"},"mask_out":"final/R_mask.png","save_blend":"final/Claude_panel.blend"'
mkdir -p final
$B -b -P panel.py -- "{$LEFT,$BASE,\"out\":\"final/L.png\"}" > final/L.log 2>&1 &
$B -b -P panel.py -- "{$RIGHT,$BASE,\"out\":\"final/R.png\"}" > final/R.log 2>&1 &
wait
grep -h -E "DONE|MASK|Error|Traceback" final/L.log final/R.log
echo FINAL_DONE
