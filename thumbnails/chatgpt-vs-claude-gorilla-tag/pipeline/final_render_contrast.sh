#!/bin/bash
# Contrast version: crude "AI build" ChatGPT panel (Claude panel reuses final/R.png). Run from blender/.
B=/opt/blender/blender-4.5.14-linux-x64/blender
CFG='"face_col":"#7C7C7C","sun":2.6,"arm_deg":86,"shoulder_z":0.32,"missing_arm":true,"missing_scale":14,"sky":[[0.0,"#5E5E5E"],[0.495,"#7D8287"],[0.505,"#DCE3EA"],[0.56,"#B9CFE9"],[0.75,"#7FA6DA"],[1.0,"#4D7EC6"]],"render":{"w":2560,"h":1440,"samples":64}'
mkdir -p final
$B -b -P crude.py -- "{$CFG,\"out\":\"final/L_crude.png\",\"mask_out\":\"final/L_crude_mask.png\",\"save_blend\":\"final/ChatGPT_crude_panel.blend\"}" > final/L_crude.log 2>&1
grep -h -E "DONE|MASK|Error|Traceback" final/L_crude.log
echo CRUDE_DONE
