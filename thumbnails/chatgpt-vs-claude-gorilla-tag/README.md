# Thumbnail: "ChatGPT vs Claude Make Gorilla Tag From Scratch"

**Upload this file:** `thumbnail_1280x720.jpg` (1280×720, sRGB, under 2 MB).
The full-resolution master is `thumbnail_2560x1440.png`.

---

## The concept

The thumbnail uses the format's standard split screen with each AI's logo and name as the panel header. Each side has a Gorilla Tag monke rendered from the real model and coloured to match its AI. The two monkes face off in a stare-down.

- **Viewer sees:** ChatGPT's monke vs Claude's monke, in Gorilla Tag.
- **Viewer doesn't know:** whose Gorilla Tag is better. That question is the click.

---

## Why it looks like this

- **Genre template:** split panel, ChatGPT on the left, white knot plus "ChatGPT", orange spark plus the serif "Claude". This is what 58 of the 64 top ChatGPT-vs-Claude thumbnails do, so the video reads as part of that series in Suggested.
- **Monkes coloured by brand:**
  - ChatGPT is charcoal, matching its current app icon.
  - Claude is orange; the lit fur measures #D0764D against the brand #D97757.
  - None of the competitors do this.
- **Real Gorilla Tag model:** the NachoEngine rig, with in-game pixel fur, the face plate, and the chest name tags (CHATGPT / CLAUDE).
- **Angry eyelids and closed mouths:** the expression is pixel-edited into the original 64px face texture. It also avoids the saturated shocked-face trope.
- **Bright daylight forest:** this separates it from the dark, muted thumbnail on DynamicGaming's same-title video, and from the horror-heavy Gorilla Tag feed.
- **Outer glow on each monke and pale sky behind the heads:** both monkes hold up in grayscale and at 160×90.
- **Bottom-right timestamp area:** nothing important sits there.

---

## Files

| Path | What |
|---|---|
| `thumbnail_1280x720.jpg` / `.png` | Upload-ready |
| `thumbnail_2560x1440.png` | Master |
| `blender/ChatGPT_panel.blend`, `blender/Claude_panel.blend` | Editable Blender 4.5 scenes with textures packed |
| `pipeline/` | Scripts that rebuild it: `final_render.sh` produces the panels and `compose.py` builds the composite. They need the NachoEngine rig; set `RIG_BLEND` in `gt.py` to wherever it lives on your machine. |
| `qa/` | Feed-size and grayscale checks |
| `research/RESEARCH.md` | Research summary, competitor data and rejected concepts |

---

## A/B idea for later

The genre's biggest outliers show a visible quality gap between the two builds. Once you know which AI won, a Test & Compare variant could show each panel's monke as that AI's actual build. Test it against this one.
