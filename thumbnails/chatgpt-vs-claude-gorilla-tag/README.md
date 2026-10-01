# Thumbnail: "ChatGPT vs Claude Make Gorilla Tag From Scratch"

**Upload this file:** `thumbnail_1280x720.jpg` (1280×720, sRGB, under 2 MB).
The full-resolution master is `thumbnail_2560x1440.png`.

---

## Main concept: quality contrast

This uses the format's standard split screen with logo and name headers. Both sides show the same subject in the same spot. Only the quality is different.

**ChatGPT (left):** a janky "built from scratch" monke made of primitive shapes.
- Capsule body and a low-poly ball head.
- A crooked face plate with googly, mismatched eyes.
- Stiff T-pose arms, one with a magenta and black missing-texture checker.
- The name tag is in Blender's default font.
- The background is a Unity-default sky with flat primitive trees.

**Claude (right):** the real Gorilla Tag model (NachoEngine rig).
- Pixel fur in Claude orange (lit fur #D0764D against the brand's #D97757).
- Angry eyelids and the in-game CLAUDE name tag.
- A bright forest with a soft outer glow around the monke.

This is the genre's strongest outlier pattern, a big and funny quality gap between the two sides: Crazy Cat at 40x their median, Tikoco at 35.5x, quisshy's comedic-fail side at 35.9x.

> If ChatGPT ends up winning in the video, swap which side gets the crude build before uploading. Test & Compare scores on watch time, so a thumbnail that promises the opposite of the video will show up there.

---

## Alternate: stare-down (`alt_stare-down/`)

Both monkes are polished and colour-coded to their brand, glaring at each other. It shows no winner. Use it as a Test & Compare option, or as the thumbnail if the results are close.

---

## Files

| Path | What |
|---|---|
| `thumbnail_1280x720.jpg` / `.png`, `thumbnail_2560x1440.png` | Main (contrast) |
| `alt_stare-down/` | Alternate version |
| `blender/ChatGPT_crude_panel.blend`, `blender/Claude_panel.blend`, `blender/ChatGPT_panel.blend` | Editable Blender 4.5 scenes with textures packed |
| `pipeline/` | Rebuild scripts: `final_render_contrast.sh` / `crude.py` for the crude side, `final_render.sh` / `panel.py` for the rig sides, `compose.py` plus `cfg_contrast.json` for the composite. Set `RIG_BLEND` in `gt.py` to wherever the NachoEngine rig lives on your machine. |
| `qa/` | Feed-size, grayscale and safe-zone checks (stare-down checks in `qa/stare-down/`) |
| `research/RESEARCH.md` | Research summary, competitor data and rejected concepts |
