# Thumbnail: "ChatGPT vs Claude Make Gorilla Tag From Scratch"

**Upload this file:** `thumbnail_1280x720.jpg` (1280×720, sRGB, 369 KB).
The full-resolution master is `thumbnail_2560x1440.png`.

---

## Main concept (v4): "same treehouse, different quality"

This follows the genre's biggest hits, Crazy Cat's ChatGPT vs Gemini Roblox (4.1M) and tef's Fortnite: the same subject in the same framing, staring at the camera, with only the quality changing. v4 adds the environment that hit thumbnails use. Both monkes stand in front of the **same Gorilla Tag treehouse**, built to two levels of quality.

**ChatGPT (left): a janky build "from scratch"**
- A primitive capsule monke with googly eyes and a stiff missing-texture arm.
- A grey-box treehouse with an open roof, cone trees and a Unity-default sky and grid.

**Claude (right): the real thing**
- The NachoEngine Gorilla Tag model in Claude orange, with the **default in-game face**, a peace sign and the in-game CLAUDE name tag.
- A plank-by-plank PBR treehouse: posts, braces, closed gables, railings, a slide, a ladder, a rope bridge and a ring platform.
- A real fir forest with ferns and mossy rocks (Poly Haven, CC0).
- **Golden-hour backlight:**
  - a low sun glinting between the peace-sign fingers
  - depth haze and light rays through the trunks
  - rim light on the monke

The gap is now in three places: the model, the build and the lighting.

**Divider:** a slight diagonal white split, as in v3.

> The thumbnail shows Claude winning. If ChatGPT wins in the video, swap which side gets the crude build before uploading. Test & Compare scores on watch time, so a thumbnail that promises the opposite of the video will show up there.

---

## QA

| Check | Result |
|---|---|
| 160×90 / 240 / 360 | Both faces and the quality gap read at every size. See `qa/qa_sizes_grayscale.png`. |
| Grayscale | Claude's monke reads as a dark silhouette on the glow, which separates better than v3. |
| Safe zones | Labels sit inside the 5% margin. The timestamp covers only Claude's arm. See `qa/qa_safezones.png`. |
| Feed mocks | Home, small and search layouts next to the real competitors, including DynamicGaming's same-title video. Ours is the only warm, glowing thumbnail in the grid. See `qa/mock_*.png`. |
| Full-resolution crops | No noise or fireflies. Label edges are crisp and the hut planks hold up. See `qa/crops_fullres.jpg`. |
| Brightness | Luma 128 (v3: 124). True white clipping is 2.1% on Claude's side, all of it the label. |
| .blend files | Both open and render standalone, with nothing missing. |

---

## Alternates

| Folder | What | Notes |
|---|---|---|
| `alt_v3_portrait-forest/` | v3: same monkes in a stylised daytime forest | Claude has the smiling face edit |
| `alt_v2_contrast-tpose/` | First contrast version | Claude's face is angry, so this version is superseded |
| `alt_v1_stare-down/` | Both monkes polished, brand-coloured stare-down | Use if the results end up close |

---

## Files

| Path | What |
|---|---|
| `blender/ChatGPT_crude_treehouse.blend` | The ChatGPT panel scene, exactly as rendered. |
| `blender/Claude_treehouse_lite.blend` | The Claude panel scene, with everything packed. The full scene is 408 MB because of the fir-tree meshes. This lite copy has decimated firs and 1K textures to fit GitHub, and renders almost the same. Rebuild the exact scene with the pipeline. |
| `blender/old/` | Scenes from v1 to v3 |
| `pipeline/` | Rebuild scripts. `final_render_treehouse.sh` runs everything. See the breakdown below. |
| `qa/` | v4 checks. Earlier versions are in `qa/v3/`, `qa/v2/` and `qa/stare-down/`. |
| `research/` | `RESEARCH.md`, the viral-thumbnail study, Higgsfield environment roughs, and the golden-post variants |

**Pipeline breakdown:**
- `ph_get.py` fetches the Poly Haven assets.
- `concepts.py treehouse --hi` renders both panels.
- `env.py` builds the treehouse (real and crude), the forest and the golden sun.
- `panel.py`, `gt.py` and `crude.py` build the monkes.
- `compose.py` with `golden.py` and `cfg_treehouse_final.json` does the golden-hour post and the labels.
- `blend_lite.py` makes the GitHub-sized scene.
- Put the NachoEngine rig in `rig/` (or set `GT_RIG`), and Inter.ttf from Google Fonts in `assets/`.
