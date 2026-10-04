# Thumbnail: "ChatGPT vs Claude Make Beat Saber From Scratch"

**Upload this file:** `thumbnail_1280x720.jpg` (1280×720, sRGB, 291 KB).
The full-resolution master is `thumbnail_2560x1440.png`.

---

## Concept: "one tunnel, two builds"

This uses the same rules as the Gorilla Tag thumbnail:
- the genre's split template, with the brand labels as the only text
- the same moment on both sides
- **one continuous scene rendered from a single camera**, so the two halves meet exactly at the divider

The view is first person down the Beat Saber track. The arches run to a vanishing point in the dead centre, and the straight divider splits the tunnel there.

**Both sides show the same swing at the same note.** Each note is a diagonal note, its arrow rolled to point along its own blade, so it's the same move mirrored.

**ChatGPT (left): decent, but flat**
- Recognizably Beat Saber, built like a quick Unity prototype: a default skybox, matte grey arches, a flat-shaded cube and an unlit saber stick.
- The saber **clips straight through the cube along the arrow** and nothing happens.

**Claude (right): the real thing**
- **A perfect cut.** The blue note is sliced exactly down the arrow's axis. The halves fly apart and the white-hot blade is visible running the full length of the gap.
  - The cut plane was solved to contain the camera ray, so on screen the cut and the blade are the same line.
  - Glowing rims trace the cut edges, with a spark burst and glowing debris at the exit.
- **A realistic saber:**
  - a thin white-hot core inside a saturated blue sheath
  - a volumetric glow that falls off into the air around it
  - real light it casts onto the halves and the track
  - a machined metal hilt with grip rings and a lit emitter
- **The world:** alternating blue and pink lit arches, a laser fan streaking under the label, a glossy reflective track, and bloom.

The saber colours follow the game: red is the left hand and blue is the right hand. That matches ChatGPT on the left and Claude on the right.

**Divider:** a straight white line through the tunnel's vanishing point. A gentle per-panel vignette darkens each half toward its outer corners, never toward the shared centre.

> The thumbnail shows Claude winning. If ChatGPT wins in the video, swap the builds before uploading.

### What changed in the polish pass (and why)

| Change | Why |
|---|---|
| Down notes → diagonal notes, cut exactly through the arrow axis | A centred cut splits the chevron into mirrored halves, which is the "perfect cut" players recognise |
| Halves pushed well apart | At 160×90, a blade running through an intact-looking cube reads like ChatGPT's clipping stick. A visible gap reads as **sliced**. |
| Saber rebuilt (core, sheath, volumetric halo, light spill, metal hilt) | The old blade was a flat glowing tube |
| Cut faces dimmed to deep blue, plus emissive rim lines | Bright cut faces read as a pale lavender smear |
| Motion trail removed | A thin glowing arc behind the blade added clutter without adding speed. A zero-strength ribbon also darkened the vanishing point, so it is now skipped entirely. |
| Low laser fan, angles solved to stay clear of the Claude wordmark | Adds energy on the right without crossing the label |
| Cube scaled 1.12× and the hilt brought into frame | Larger slice, and the blade now has a visible source |

---

## Research

- There's no existing "ChatGPT vs Claude make Beat Saber" video. The nearest are:
  - Valem, "Can AI code Beat Saber? Watch ChatGPT try" (118K)
  - Alexs Stuff, "I Made a Beat Saber in 24 Hours" (82K)
  - BrawlDev's same-format "ChatGPT vs Claude Make Rivals" (409K)
- The top Beat Saber thumbnails (5–32M views) share one language: dark backgrounds, neon red and blue, big glowing notes with arrows, and sabers as bold diagonals (`research/reference_thumbnails.jpg`). The Claude half speaks it.
- **Brightness:** luma is about 120, darker than the AI-genre median of 138. That's normal for Beat Saber, and the bright ChatGPT half is what makes it stand out in a Beat Saber feed (`qa/mock_home.png`).

---

## QA

| Check | Result |
|---|---|
| 160×90 / 240 / 360 | Intact red cube vs two separated blue halves with the blade between them, plus both labels, read at every size |
| Grayscale | Both cubes separate from their backgrounds |
| Safe zones | Labels sit inside the 5% margin. The timestamp covers only the end of the blue saber's hilt. |
| Feed mock | Next to the top Beat Saber and AI-genre thumbnails (`qa/mock_*.png`) |
| Seam | The arches meet at the divider. Coplanar arch faces that z-fought (black notches) were fixed before the final render. |
| Artifacts | Two were found and fixed in full-res crops: a zero-strength trail ribbon darkening the vanishing point, and specular "beads" burned into the blade by the light-spill lamps. The blade materials are now matte emitters. |
| Crops | No noise or fireflies, and label edges are clean (`qa/crops_fullres.jpg`) |

---

## Files

| Path | What |
|---|---|
| `blender/ChatGPT_crude.blend`, `blender/Claude_neon.blend` | Both scenes as rendered, fully procedural with nothing external |
| `alt_v1_down-notes/` | The first version, with down notes and the cube cut off-centre, kept for A/B comparison |
| `pipeline/bs_scene.py` | Builds the scene. `mode: crude` or `mode: real` share one layout and camera. |
| `pipeline/bs_run.py` | Renders both. `python3 bs_run.py final --hi` gives 2560×1440, and `MID=1` gives a 1080p preview. Set `BLENDER=` to your Blender 4.5. |
| `pipeline/proj.py` | Camera projection helper used to place the cubes and sabers in screen space |
| `pipeline/compose.py` + `cfg_final.json` | Labels, divider and per-panel vignette. Put Inter.ttf from Google Fonts in `pipeline/assets/`. |
