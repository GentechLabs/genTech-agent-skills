---
name: reference-to-choreography-recipe
description: "When the user points at a reference fight clip and asks you to adapt its moves, this is the recipe: get the clip, sample frames, read the body mechanics with vision, map by role, translate into physics beats, and write the Seedance prompt."
---

# Reference-to-Choreography Recipe

Turn a collaborator's reference clip into a Seedance fight prompt, move by move.

## When to use

The user points at an external fight clip (X, Telegram, YouTube, a file) and says something like:

- *"I want them to use their legs like they do here"*
- *"the white-haired one does flips — I want Kiri to do that"*
- *"make it feel like this fight"*

Do not describe the moves from memory or from the caption. Pull frames and read them.

## Steps

### 1. Get the reference

- **Telegram file:** path is in the incoming message metadata, usually under
  `/root/.hermes/profiles/pixel/cache/videos/`. Use that path directly.
- **URL (X, YouTube, etc.):** download with `web_extract`, curl, or browser automation.
  X/Twitter hides the video behind syndication — use the platform's embed/syndication endpoint or
  `yt-dlp` for YouTube. If the download fails, tell the user you need the file.

### 2. Sample frames at the beats the user named

Find the timestamps the user cares about. If they didn't name them, sample across the action.

```bash
mkdir -p /tmp/ref-frames
cd /tmp/ref-frames
for t in 3.2 3.8 4.4 5.0 5.6 7.2; do
  ffmpeg -y -v error -ss $t -i ref.mp4 -frames:v 1 -vf scale=620:-1 lg_$t.png
done
```

Build a contact sheet for vision:

```bash
ffmpeg -y -i lg_3.2.png -i lg_3.8.png -i lg_4.4.png \
  -filter_complex "[0][1][2]hstack=inputs=3" set-A.png
```

### 3. Ask vision for the right thing

Use `vision_analyze` and ask specifically about the body parts the user named.

Example:

> Three frames of the reference fight (t=3.2, 3.8, 4.4s). I'm looking for LEG techniques — kicks,
> sweeps, knee strikes, aerial/flip kicks. Describe exactly what the two fighters are doing with
> their legs/feet in each frame: is anyone airborne, upside down, throwing a kick, sweeping? Which
> fighter (left or right, red jacket or silver hair) is doing the leg work?

Repeat for other body parts or camera moves if needed.

### 4. Map reference fighters to your characters by ROLE, not color

The user usually gives the mapping:

- *"Kage on the left, Kiri on the right"* → map reference's left fighter → Kage, right fighter → Kiri
- *"Kiri is the white-haired one"* → map reference's silver-haired fighter → Kiri

Write the mapping explicitly before writing the prompt, and check it against the user's words.

### 5. Translate into a Seedance timeline

Write each observed move as physics, not adjectives:

- Approach → contact → transfer of force → recovery
- Name the body part and the surface (heel, shin, knee, sole)
- Add the elemental/power lock if your characters have one (fire = embers/scorch, ice = frost/shards)
- Make clear which character is the initiator and which is reacting

Example from a real session:

> **Kiri** is the acrobatic leg fighter: he rises straight into an aerial flip kick, going
> upside-down in mid-air inside a spinning ring of frost, then whips a heel down at Kage. He follows
> with a descending axe kick stomping down with a burst of ice, a low sliding sweep along the wet
> cobbles that rimes the road, and a cartwheel hand-plant recovery that carries him back onto his
> feet. **Kage** is the grounded heavy: he eats the flip kick on his raised forearm, blocks the axe
> kick, hops the sweep, and answers with his own legs — a low sliding sweep that kicks up spray,
> a heavy body kick, a knee and a rising elbow, plus heavy flame-charged punches. Both land.

### 6. Adapt the reference framing when switching from 2D to 3D CGI

If the user wants a **3D CGI** result but the reference is **2D anime**, do not copy the reference's still framing. Rebuild the equivalent shot as an **impact frame**: camera lower or tracking, bodies in motion, contact already happening or about to happen, environmental objects reacting to the force. The Seedance prompt should describe the physics of the reference move, not the reference's composition. The keyframe must show depth cues (shadows under bodies, receding cobblestones, volumetric fog, kicked spray, splinters) rather than a flat character lineup.

### 7. Write the prompt

Use the standard 6-part Seedance fight-prompt structure:

1. **Style + setting**
2. **Characters with locked descriptions**
3. **Timeline of beats** (with the mapped moves)
4. **Camera**
5. **Atmosphere + effects**
6. **Constraints / negatives**

See `references/boss-fight-video-recipe.md` for the full prompt template.

## Verification

Before firing the render, re-read the prompt and confirm:

- [ ] Each observed move from the reference appears in the timeline
- [ ] The character mapping matches what the user said
- [ ] Both fighters are active if the reference shows both active
- [ ] No new moves were invented that the user didn't ask for
- [ ] The camera description matches the reference's shot flow
- [ ] For 3D CGI outputs, the keyframe is an impact/motion frame, not a flat stand-off

## Pitfalls

- **Sampling too few frames misses the move.** If the user says "they use their legs," sample at
  least 6-8 frames across the leg-heavy section.
- **Asking vision "what's happening" returns a story, not a move list.** Ask specifically about the
  body parts and the spatial relationships (airborne, upside-down, grounded).
- **Mapping by color instead of role swaps the characters.** The reference's red-jacket fighter may
  not be your red-themed fighter. Map by the user's explicit casting.
- **Describing a move in adjectives loses the physics.** "Dynamic kick" is weaker than "descending
  axe kick, heel strikes pavement, shockwave sprays wet cobbles."
- **Inventing extra moves the user didn't ask for wastes budget and gets rejected.** Stick to the
  reference moves plus any single change the user explicitly named.
- **Copying a 2D reference's composition into a 3D CGI request produces a flat-looking result.**
  Rebuild the scene as an impact frame with depth cues and a dynamic camera.
