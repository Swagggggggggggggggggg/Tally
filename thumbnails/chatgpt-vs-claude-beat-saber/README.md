# Thumbnail: "ChatGPT vs Claude Make Beat Saber From Scratch"

**Upload this file:** `thumbnail_1280x720.jpg` (1280×720, sRGB, 281 KB).
The full-resolution master is `thumbnail_2560x1440.png`.

---

## Concept: "one tunnel, two builds"

This uses the same rules as the Gorilla Tag thumbnail:
- the genre's split template, with the brand labels as the only text
- the same moment on both sides
- **one continuous scene rendered from a single camera**, so the two halves meet exactly at the divider

The view is first person down the Beat Saber track. The neon arches run to a vanishing point in the dead centre, and the straight divider splits the tunnel there.

**ChatGPT (left): decent, but flat**
- Recognizably Beat Saber: a red note with a down arrow, a red saber, the track and arches.
- Built like a quick Unity prototype: a default skybox, matte grey arches, a flat-shaded cube and an unlit saber stick.
- The saber **clips straight through the cube** with no cut and no effects.

**Claude (right): the real thing**
- A dark neon tunnel: alternating blue and pink lit arches, a glossy reflective track, lane lines and bloom.
- The blue note is **sliced in two** along the saber, with the arrow split across the halves, a glowing cut face and spark bursts.
- A white-hot saber core with a blue glow and a motion trail.

The saber colours follow the game: red is the left hand and blue is the right hand. That matches ChatGPT on the left and Claude on the right, so the layout reads as natural Beat Saber.

**Divider:** a straight white line, unlike the Gorilla Tag one. It runs through the tunnel's vanishing point, which makes the "same tunnel" read instantly.

> The thumbnail shows Claude winning. If ChatGPT wins in the video, swap the builds before uploading.

---

## Research

- There's no existing "ChatGPT vs Claude make Beat Saber" video. The nearest are:
  - Valem, "Can AI code Beat Saber? Watch ChatGPT try" (118K)
  - Alexs Stuff, "I Made a Beat Saber in 24 Hours" (82K)
  - BrawlDev's same-format "ChatGPT vs Claude Make Rivals" (409K)
- The top Beat Saber thumbnails (5–32M views) share one language: dark backgrounds, neon red and blue, big glowing notes with arrows, and sabers as bold diagonals (`research/reference_thumbnails.jpg`). The Claude half speaks it.
- **Brightness:** luma is about 114, darker than the AI-genre median of 138. That's normal for Beat Saber, and the bright ChatGPT half is what makes it stand out in a Beat Saber feed (`qa/mock_home.png`).

---

## QA

| Check | Result |
|---|---|
| 160×90 / 240 / 360 | Intact red cube vs sliced blue cube, plus both labels, read at every size |
| Grayscale | Both cubes separate from their backgrounds |
| Safe zones | Labels sit inside the 5% margin. The timestamp covers only the blue saber's hilt. |
| Feed mock | Next to the top Beat Saber and AI-genre thumbnails (`qa/mock_*.png`) |
| Seam | The arches meet at the divider. Coplanar arch faces that z-fought (black notches) were fixed before the final render. |
| Crops | No noise or fireflies, and label edges are clean (`qa/crops_fullres.jpg`) |

---

## Files

| Path | What |
|---|---|
| `blender/ChatGPT_crude.blend`, `blender/Claude_neon.blend` | Both scenes as rendered, fully procedural with nothing external |
| `pipeline/bs_scene.py` | Builds the scene. `mode: crude` or `mode: real` share one layout and camera. |
| `pipeline/bs_run.py` | Renders both. `python3 bs_run.py v2 --hi` gives 2560×1440. Set `BLENDER=` to your Blender 4.5. |
| `pipeline/proj.py` | Camera projection helper used to place the cubes and sabers in screen space |
| `pipeline/compose.py` + `cfg_final.json` | Labels and divider. Put Inter.ttf from Google Fonts in `pipeline/assets/`. |
