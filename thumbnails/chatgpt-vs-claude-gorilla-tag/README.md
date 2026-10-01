# Thumbnail: "ChatGPT vs Claude Make Gorilla Tag From Scratch"

**Upload this file:** `thumbnail_1280x720.jpg` (1280×720, sRGB, 371 KB).
The full-resolution master is `thumbnail_2560x1440.png`.

---

## Main concept (v6): "one scene, two builds"

This follows the genre's biggest hits, Crazy Cat's ChatGPT vs Gemini Roblox (4.1M) and tef's Fortnite: the same subject in the same pose and framing, with only the quality changing. v6 makes that literal.
- **One continuous scene, split by the divider.** Both sides are rendered from the same camera, and one treehouse straddles the divider. The left half of the shed is ChatGPT's build and the right half is Claude's. The roof and walls meet exactly at the split.
- **Both monkes throw a peace sign**, at the same size and height, turned to face the camera.

**ChatGPT (left): decent, but clearly not Claude's**
- A from-scratch low-poly gorilla in **ChatGPT teal**: chunky long-armed body, a big round head, and a curved Gorilla Tag-style face plate.
- Clean cartoon eyes, a modelled peace-sign hand, and a CHATGPT chest tag in a default font.
- Its world is the prototype version of the same scene: a grey-box treehouse, lime cone trees and flat daylight.

**Claude (right): the real thing**
- The NachoEngine Gorilla Tag model in Claude orange, with the default in-game face, a real peace sign and the pixel CLAUDE tag.
- The plank-built treehouse in a real fir forest (Poly Haven, CC0).
- Lit as a backlit golden-hour portrait, with the sun glinting between the fingers.

**No stat text.** The brand labels are the only text on the thumbnail.

> The thumbnail shows Claude winning. If ChatGPT wins in the video, swap the builds before uploading. Test & Compare scores on watch time, so a thumbnail that promises the opposite of the video will show up there.

---

## QA

| Check | Result |
|---|---|
| 160×90 / 240 / 360 | Both faces, both peace signs, the split treehouse and the quality gap read at every size. See `qa/qa_sizes_grayscale.png`. |
| Grayscale | Both faces separate from the background. Claude's monke reads as a dark silhouette on the glow. |
| Safe zones | Labels sit inside the 5% margin. The timestamp covers only Claude's arm. See `qa/qa_safezones.png`. |
| Feed mocks | Home, small and search layouts next to the real competitors, including DynamicGaming's same-title video. Ours is the only warm, glowing thumbnail in the grid. See `qa/mock_*.png`. |
| Seam | The roof and walls line up across the divider, checked on the raw renders. See the top-left tile of `qa/crops_fullres.jpg`. |
| Full-resolution crops | No noise or fireflies. Label edges are crisp and the hut planks hold up. See `qa/crops_fullres.jpg`. |
| Brightness | Luma 128. True white clipping is limited to the labels. |
| .blend files | Both open and render standalone, with nothing missing. |

---

## Alternates

| Folder | What | Notes |
|---|---|---|
| `alt_v5_teal-primitive/` | v5: teal primitive monke with googly eyes, mirrored treehouses | Superseded by v6's gorilla and continuous scene |
| `alt_v4_treehouse-grey/` | v4: same treehouse concept with a grey ChatGPT monke and a missing-texture arm | Superseded by v5's relight and teal |
| `alt_v3_portrait-forest/` | v3: same monkes in a stylised daytime forest | Claude has the smiling face edit |
| `alt_v2_contrast-tpose/` | First contrast version | Claude's face is angry, so this version is superseded |
| `alt_v1_stare-down/` | Both monkes polished, brand-coloured stare-down | Use if the results end up close |

---

## Files

| Path | What |
|---|---|
| `blender/ChatGPT_gorilla_unified.blend` | The v6 ChatGPT panel scene, exactly as rendered. |
| `blender/Claude_treehouse_lite.blend` | The Claude panel scene, with everything packed. The full scene is 408 MB because of the fir-tree meshes. This lite copy has decimated firs and 1K textures to fit GitHub, and renders almost the same. Rebuild the exact scene with the pipeline. |
| `blender/old/` | Scenes from v1 to v5 |
| `pipeline/` | Rebuild scripts. `final_render_treehouse.sh` runs everything. See the breakdown below. |
| `qa/` | v6 checks. Earlier versions are in `qa/v5/`, `qa/v4/`, `qa/v3/`, `qa/v2/` and `qa/stare-down/`. |
| `research/` | `RESEARCH.md`, the viral-thumbnail study, Higgsfield environment roughs, golden-post and teal variants, and `brainstorm/` (next-idea roughs) |

**Pipeline breakdown:**
- `ph_get.py` fetches the Poly Haven assets.
- `concepts.py unified --hi` renders both panels from the shared camera.
- `env.py` builds the treehouse (real and crude), the forest and the golden sun.
- `panel.py` and `gt.py` build the real monke. `crude.py` with `gorilla.py` builds ChatGPT's gorilla and its world.
- `compose.py` with `golden.py` and `cfg_unified_final.json` does the golden-hour post and the labels.
- `blend_lite.py` makes the GitHub-sized scene.
- Put the NachoEngine rig in `rig/` (or set `GT_RIG`), and Inter.ttf from Google Fonts in `assets/`.
