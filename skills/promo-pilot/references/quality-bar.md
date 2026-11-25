# Quality bar

The target: a viewer can't tell whether a brand's own studio made this. "It renders and the checks pass" is the floor, not the goal.

HyperFrames already holds the professional craft, measured on shipped films. This file doesn't replace it; it points at it and adds the few rules that matter most for promos. Read these before planning:
- hyperframes `references/types/launch.md` (real UI never a mockup, the product on screen, the end card, tells)
- hyperframes `references/types/vertical.md` for 9:16 (safe area, the first second, layout, pacing)
- hyperframes `references/motion.md` (eases, *Transitions with a cause*, *Defaults that look generated*)
- hyperframes `references/look.md` (the look line, palette, type)
- hyperframes `references/review.md` (the director's review, in step 4)

## The five rules that decide whether it looks professional

1. **Real material is the hero.** Every beat shows something real: a brand photo, a product shot or cutout, footage, the real UI, the real logo, or (typography-led films only) the brand's own words set large. A real photo with simple, confident motion beats any amount of animated drawing.
2. **Nothing is drawn that exists in the world.** Bottles, cans, food, phones, laptops, people, buildings and logos are never built from CSS or SVG shapes. If there's no image of it, change the beat. A drawn product reads as clip-art and loses the viewer at once.
3. **The brand's own system.** Its fonts (the captured files with their `@font-face` rules), its exact colours, its real lines. A real brand is never given invented taglines, made-up "moments" or generic ad copy.
4. **Motion with a cause, never decoration.** Use 3–5 kinds of transition, each caused by something on screen (motion.md). No breathing, floating or pulsing loops, no slow creeping zooms on titles, no every-element-fades-up, no bounce on UI. Those are the *Defaults that look generated*. A hold is a hold: the image does the work.
5. **Vertical is designed for the phone.** Frame 0 is the hook and the thumbnail: a face, the product or one bold line, never black and never a logo. Shots of 1–2 seconds, a new beat every 2–4 seconds, one subject per frame, everything readable inside the safe band, and the payoff before the swipe.

## Type and colour

- The brand's display and text faces (an icon font is never one of them), only in the weights the brand ships.
- Vertical: nothing meant to be read under 28px, and titles about ×1.35 of their landscape size. About 5 words per line for claims: cut words, never shrink.
- Reading time: about 0.3s per word once the line has settled, at least 1.2s; the closing line at least 2s.
- On-screen text adds to the voice and captions, never repeats them word for word.
- The accent is the colour the brand uses most across roles, never link blue or a status colour.

## Sound

- The final mix is about **−14 LUFS** (−16 to −12 is fine) with a **true peak of −1 dBTP or lower**. `check_video.py --loudness` checks both.
- The voice sits 12–18 dB above the music while speaking; the music is ducked under it, lifted for the end card, and faded out.
- Sound effects only on visible actions, below the voice, never harsh.

## Captions

Styled for the brand (never default white-on-black boxes), grouped and placed by hyperframes `references/captions.md`, with text from the script and timing from the voice.

## Hard stops: a version with any of these never reaches the user

- A drawn real-world object, or a redrawn or substituted logo.
- An invented tagline or claim for a real brand.
- A beat with no real material that isn't deliberately typography-led.
- Frame 0 that is empty, black or just a logo.
- Any P0 still open from the director's review (review.md).
- `<hf> check` errors, or unexplained warnings about safe zones, contrast, the first frame, unread lines or dead stretches.
- A failing `check_video.py` (duration, frames, loudness, true peak).

Don't score the film out of 10. A score finds nothing to fix; the P0/P1 notes from review.md do.
