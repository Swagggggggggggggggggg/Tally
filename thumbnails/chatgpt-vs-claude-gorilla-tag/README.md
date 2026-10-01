# Thumbnail: "ChatGPT vs Claude Make Gorilla Tag From Scratch"

**Upload this file:** `thumbnail_1280x720.jpg` (1280×720, sRGB, 346 KB).
The full-resolution master is `thumbnail_2560x1440.png`.

---

## Main concept (v3): "same monke, different quality"

This is the same structure as the genre's biggest hits, such as Crazy Cat's ChatGPT vs Gemini Roblox (4.1M, 40x the channel median) and tef's 6-AI Fortnite (917K). Both sides show the same subject in the same framing, staring at the camera. Only the quality is different.

**ChatGPT (left):** a janky "AI built it from scratch" monke.
- Primitive capsule body and a low-poly ball head.
- A flat grey face disc with googly eyes pointing different ways and a flat-line mouth.
- It tries to copy Claude's raised hand, but its arm is a stiff cylinder sticking straight up with the magenta and black missing-texture checker.
- The background is a Unity-default sky, a grey grid floor and flat cone trees.

**Claude (right):** the real Gorilla Tag model (NachoEngine rig).
- Pixel fur in Claude orange.
- A **friendly smile** (pixel-edited into the original 64px face texture) and a **peace sign** next to its face.
- The in-game CLAUDE name tag, and a lush forest behind.

**Divider:** a slight diagonal white split. It's the genre's recognizable two-panel format, with a bit of motion. I also tested straight, thick, zigzag and pixel-step lines, a VS badge, and the monke gripping the divider like a climbing pole. At feed size the divider style barely registers. The faces and the quality gap do the work. See `research/concepts/divider_styles.jpg`.

> The thumbnail shows Claude winning. If ChatGPT ends up winning in the video, swap which side gets the crude build before uploading. Test & Compare scores on watch time, so a thumbnail that promises the opposite of the video will show up there.

---

## QA

| Check | Result |
|---|---|
| 160×90 | Both faces read clearly. |
| Grayscale | Both faces still separate from the background. |
| Safe zones | Labels sit inside the 5% margin. The timestamp badge only covers Claude's lower arm. |
| Feed mock | Checked next to the real competitors, including DynamicGaming's same-title video: `qa/mock_home.png`. |
| Full-resolution crops | No render artifacts: `qa/faces_fullres.png`. |

---

## Alternates

| Folder | What | Notes |
|---|---|---|
| `alt_v2_contrast-tpose/` | Earlier contrast version | Its Claude has an angry face, so it's superseded. |
| `alt_v1_stare-down/` | Both monkes polished, brand-coloured stare-down | Use it if the results end up close. |

---

## Files

| Path | What |
|---|---|
| `blender/ChatGPT_crude_portrait.blend`, `blender/Claude_portrait.blend` | Editable Blender 4.5 scenes for v3, with textures packed. Older scenes are in `blender/old/`. |
| `pipeline/` | Rebuild scripts. `concepts.py` defines every concept preset (`python3 concepts.py portrait --hi` renders the final panels). `crude.py` builds the janky monke, `panel.py` and `gt.py` handle the real rig, and `compose.py` with `cfg_portrait_final.json` builds the composite. Set `RIG_BLEND` in `gt.py` to wherever the NachoEngine rig lives on your machine. |
| `qa/` | v3 checks; earlier versions are in subfolders |
| `research/RESEARCH.md`, `research/concepts/` | Research notes, the top-viral thumbnail study sheets, Higgsfield roughs, Blender concept tests and divider tests |
