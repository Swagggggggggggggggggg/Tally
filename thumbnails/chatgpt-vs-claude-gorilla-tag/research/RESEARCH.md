# Research behind the thumbnail: "ChatGPT vs Claude Make Gorilla Tag From Scratch"

Collected 2026-10-01. View counts are YouTube search or flat-playlist figures. They are rounded and have no controls. Treat them as order of magnitude only.

---

## Sources used

- **Spencer's Drive library:**
  - `2026-09-15_packaging-examples_claude.md`
  - `thumbnail-composition_claude.md`
  - `curiosity-gap-packaging_claude.md`
  - `ab-evidence-outliers_claude.md`
  - `vr-gorilla-tag-niche_claude.md`
  - `packaging-by-surface_grok.md`
  - `thumbnails-official_grok.md`
  - `pack-checklist_grok.md`
  - `CONT-02-faces_grok.md`
  - the Deanster idea database
- **YouTube scrape:**
  - 44 genre searches and 31 Gorilla Tag searches
  - 775 genre rows, with uploads from 81 channels to compute medians
  - 393 Gorilla Tag niche rows
  - 900+ thumbnails downloaded; 95 viewed one by one
- **Brand checks:** current App Store icons for ChatGPT and Claude, and the claude.ai and OpenAI CDN favicons, all as of 2026-09-30.
- **Model:** NachoEngine `Gorilla_IK_Rig` (github.com/NachoEngine/Gorilla_IK_Rig). This is the real Gorilla Tag player mesh, with its textures and an IK rig.

---

## The direct competitor (the most important finding)

DynamicGaming has already posted **"ChatGPT vs Claude make Gorilla Tag from Scratch"** (`EewMLtgQ3Ks`).
- 34.7K views in about 60 days, which is about 43x the channel's median of 800.
- Their thumbnail is split: a photoreal gorilla on the ChatGPT side and a flat pixel black monke on the Claude side.
- The palette is dark and muted, with no red and no text.
- It will appear next to ours in search and Suggested.
- Their sequel, the Mod Menu video (`Bn581LktcX4`), got 14.3K.

This tells us two things. The topic works for a small Gorilla Tag channel. And our package has to look clearly different from theirs.

---

## The genre template (ChatGPT vs Claude "make X")

- **Split screen:** 58 of the 64 most-viewed thumbnails use one, with a thin white divider.
- **Header on each panel:** the official logo plus the name in white with a dark glow.
  - ChatGPT: the white knot plus a sans-serif "ChatGPT".
  - Claude: the orange spark plus the serif "Claude".
- **ChatGPT is on the left in 49 of 64.** 86% of titles name ChatGPT first.
- **Same subject in each panel, at two quality levels.** The outlier lever is a large, funny gap between the two builds:
  - Crazy Cat, Roblox: 40x
  - Tikoco, FIFA 27: 35.5x
  - quisshy, "bean ghost": 35.9x
  - Wxter, "1341 FPS vs 67 FPS": 138x
- **Niche crossovers produce the biggest relative outliers.** This is when a creator makes the AI video about their own game: Wxter (Minecraft clients), DynamicGaming (Gorilla Tag), W4ddles (FL Studio).
- **Nobody colour-codes the characters to the brand.** That is an open lane.
- **Brightness:** median 138/255 across the genre, and 152 for the top 50.

---

## The Gorilla Tag feed (last ~90 days)

- Most thumbnails are 3D Blender renders of the real monke model. Red is the most common colour, then blue and green.
- About a third are dark horror (Be Prepared at 1.5–1.9M) and about a quarter are bright cyan sky over pixel grass (BlizzardGT).
- About half use no text.
- Faces are monke faces, with emotion added by repainting the face texture.
- "I recreated Gorilla Tag" videos get 0.5–1.1M views. That shows demand for the "built it" angle.

---

## Packaging rules applied (from Spencer's library)

- **Anchor one concrete thing and withhold one specific thing.**
  - Anchored: ChatGPT's monke vs Claude's monke, in Gorilla Tag.
  - Withheld: whose build wins.
- **The title and thumbnail split the work.** The thumbnail adds no extra words beyond the genre's brand labels and the in-game name tags.
- **One focal pair**, readable at 160×90, with the bottom-right timestamp zone kept clear of anything that matters.
- **Mouths are closed.** This follows the MrBeast closed-mouth A/B result: the shocked open-mouth monke is the saturated local default.
- **Colours are complementary** (orange against blue sky; charcoal against pale sky), and the image passes a grayscale check.
- **Honest promise.** The thumbnail does not claim a winner, because the outcome was not known when it was made. The rivalry is the promise, and the video delivers it.

---

## Concepts explored (17 Higgsfield roughs, then Blender tests)

1. **Rejected:** a single monke split down the middle. It is iconic, but it loses the genre template.
2. **Rejected:** the stare-down with foreheads touching. It looked like a realistic gorilla, not Gorilla Tag.
3. **Rejected:** the lava monke tagging the ChatGPT monke. It implies Claude wins.
4. **Rejected:** Claude's arm reaching across the divider to tag. Same problem: it implies an outcome.
5. **Rejected:** a Creation-of-Adam reach. It reads as cooperation, not "vs".
6. **Rejected:** half-wireframe "being built" monkes. Too cluttered at small size.
7. **Rejected:** boxing stance. Gorilla Tag's long arms make a guard look wrong in 3D.
8. **Rejected:** a crown at the divider. It is a tiny dull blob at feed size and fights the labels.
9. **Chosen:** the genre-native panel stare-down, with brand-colour-coded real Gorilla Tag monkes, angry lids, closed mouths, in-game chest name tags, and bright daylight Gorilla Tag forest.

---

## Update: contrast version is now the main thumbnail

Spencer chose to lean into the quality-gap lever. Claude stays on the right as the polished real model. ChatGPT's side becomes a deliberately janky primitive-shape build:
- googly mismatched eyes
- T-pose arms, one with a missing-texture checker
- a name tag in the default font
- a Unity-default sky and primitive trees

The stare-down hero stays as the alternate for Test & Compare. If the video's actual result flips, swap which side gets the crude build so the thumbnail's promise matches the footage.
