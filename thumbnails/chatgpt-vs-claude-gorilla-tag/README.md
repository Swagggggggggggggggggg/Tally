# Thumbnail: "ChatGPT vs Claude Make Gorilla Tag From Scratch"

**Upload this file:** `thumbnail_1280x720.jpg` (1280×720, sRGB, 362 KB).
The full-resolution master is `thumbnail_2560x1440.png`.

---

## Main concept (v5): "same treehouse, same peace sign, different quality"

This follows the genre's biggest hits, Crazy Cat's ChatGPT vs Gemini Roblox (4.1M) and tef's Fortnite: the same subject in the same pose and framing, with only the quality changing. Both monkes throw a **peace sign** in front of the **same Gorilla Tag treehouse**.

**ChatGPT (left): the janky "from scratch" build**
- A primitive capsule monke in **ChatGPT teal**. Teal against Claude's orange is a near-complementary pair, and it's brand-coded, which nobody else in the genre does.
- Googly eyes, and a **peace sign made of primitives**: a box palm with two mismatched stick fingers.
- A grey-box treehouse, cone trees and a prototype grid.
- A touch more real than v4: filmic tone mapping, a soft sun, a subtle vinyl-toy surface and slight depth of field. It still reads as cheap.

**Claude (right): the real thing**
- The NachoEngine Gorilla Tag model in Claude orange, with the default in-game face, a real peace sign and the CLAUDE name tag.
- A plank-built treehouse in a real fir forest (Poly Haven, CC0).
- **Lit as a backlit golden-hour portrait:**
  - a warm soft key from front-left
  - a warm low fill
  - a strong rim on the sun side
  - the sun glinting between the fingers
- The haze and light rays are graded so the fur keeps its own colour.

**Divider:** a slight diagonal white split.

> The thumbnail shows Claude winning. If ChatGPT wins in the video, swap which side gets the crude build before uploading. Test & Compare scores on watch time, so a thumbnail that promises the opposite of the video will show up there.

---

## QA

| Check | Result |
|---|---|
| 160×90 / 240 / 360 | Both faces, both peace signs and the quality gap read at every size. See `qa/qa_sizes_grayscale.png`. |
| Grayscale | Both faces separate from the background. Claude's monke reads as a dark silhouette on the glow. |
| Safe zones | Labels sit inside the 5% margin. The timestamp covers only Claude's arm. See `qa/qa_safezones.png`. |
| Feed mocks | Home, small and search layouts next to the real competitors, including DynamicGaming's same-title video. Ours is the only warm, glowing thumbnail in the grid. See `qa/mock_*.png`. |
| Full-resolution crops | No noise or fireflies. Label edges are crisp and the hut planks hold up. See `qa/crops_fullres.jpg`. |
| Brightness | Luma 125. True white clipping is limited to the labels. |
| .blend files | Both open and render standalone, with nothing missing. |

---

## Alternates

| Folder | What | Notes |
|---|---|---|
| `alt_v4_treehouse-grey/` | v4: same treehouse concept with a grey ChatGPT monke and a missing-texture arm | Superseded by v5's relight and teal |
| `alt_v3_portrait-forest/` | v3: same monkes in a stylised daytime forest | Claude has the smiling face edit |
| `alt_v2_contrast-tpose/` | First contrast version | Claude's face is angry, so this version is superseded |
| `alt_v1_stare-down/` | Both monkes polished, brand-coloured stare-down | Use if the results end up close |

---

## Files

| Path | What |
|---|---|
| `blender/ChatGPT_crude_treehouse.blend` | The v5 ChatGPT panel scene, exactly as rendered. |
| `blender/Claude_treehouse_lite.blend` | The Claude panel scene, with everything packed. The full scene is 408 MB because of the fir-tree meshes. This lite copy has decimated firs and 1K textures to fit GitHub, and renders almost the same. Rebuild the exact scene with the pipeline. |
| `blender/old/` | Scenes from v1 to v4 |
| `pipeline/` | Rebuild scripts. `final_render_treehouse.sh` runs everything. See the breakdown below. |
| `qa/` | v5 checks. Earlier versions are in `qa/v4/`, `qa/v3/`, `qa/v2/` and `qa/stare-down/`. |
| `research/` | `RESEARCH.md`, the viral-thumbnail study, Higgsfield environment roughs, golden-post and teal variants, and `brainstorm/` (next-idea roughs) |

**Pipeline breakdown:**
- `ph_get.py` fetches the Poly Haven assets.
- `concepts.py treehouse2 --hi` renders both panels.
- `env.py` builds the treehouse (real and crude), the forest and the golden sun.
- `panel.py`, `gt.py` and `crude.py` build the monkes.
- `compose.py` with `golden.py` and `cfg_treehouse2_final.json` does the golden-hour post and the labels.
- `blend_lite.py` makes the GitHub-sized scene.
- Put the NachoEngine rig in `rig/` (or set `GT_RIG`), and Inter.ttf from Google Fonts in `assets/`.
