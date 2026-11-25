# Verify, then review with the user

## Verify (before the user sees anything)

The user should only ever review a video that already passes these checks. Fix failures yourself.

1. **File check.** Run:
   ```bash
   python3 <skill-dir>/scripts/check_video.py <video> --expect-duration <s> --fps 30 --format <landscape|vertical|square> --stills <out>/work/stills --expect-audio --loudness
   ```
   It reports duration, fps, frame count, resolution, whether there's an audio stream, writes evenly spaced stills plus a contact sheet, and with `--loudness` measures integrated loudness and true peak against the quality bar (-16 to -12 LUFS, at most -1 dBTP). A non-zero exit means something failed; the output says what. If ffmpeg/ffprobe are missing, ask before fetching them (brag-slim's guidance: prefer `uv run --with imageio-ffmpeg`).
2. **Picture check.** Look at the contact sheet and stills. Each scene should match its storyboard line. Look for: text cut off or overlapping, unreadably small or low-contrast text, blank or half-loaded frames, missing-glyph boxes, captions over key visuals, and (vertical) text inside the platform UI zones.
3. **Voice check** (if voice is on). Transcribe the **final mix** with a model that matches the language and compare it to the script. Missing or garbled lines, or music drowning the voice, mean a fix. On max, also confirm the voice sits 12-18 dB above the music (measure the voice files and the music at its mixed volume with ffmpeg's `ebur128`).
4. **Caption check** (if on). Caption text equals the script's display text, groups appear while their words are spoken (spot-check 3 stills against the word timings), and nothing stays on screen after it should be gone.
5. **Quality bar.** No hard stop from quality-bar.md is present, and the director's review (SKILL.md step 4) has no P0 left open. If one slipped through to the render, fix it and render again before the user sees anything.
6. **Rules check.** No invented claims, no real personal data, credits present in `share-copy.txt`.

Record the result in `studio.json` → `versions[n].checks`.

## Review (with the user)

### Present each version like this

```
v2 is ready: promo-output/v2.mp4 (21s, vertical, Hindi voiceover, captions)
Poster: promo-output/v2.jpg
Changed since v1: shorter hook, captions moved up, calmer voice.
```

If a file-sending tool (e.g. SendUserFile) is available, send the video and poster so the user can watch them. Otherwise give the paths.

### Then ask one question

"Happy with it, or what should change?" Offer the most likely answers as options. With AskUserQuestion, you might offer: **This is final** · **Change specific scenes** · **Change voice or captions** · **Try a different tone**. The user can always type their own answer.

### Turn feedback into changes

- Restate vague feedback as concrete edits and confirm them in one line: "'Feels slow' → I'll cut scenes 3 and 4 by 1s each and use harder cuts. OK?" Skip the confirmation for clear, small requests.
- Change only what was asked. Keep everything else identical, because users notice unexpected changes and lose trust.
- Rebuild only what's needed: one regenerated voice line, one restyled scene. Then re-render the whole video and **verify again**.
- Log each round in `studio.json` → `versions` (what was asked, what changed).

### When to stop

- The tier's round count (tiers.md) is how many rounds you run without asking. After that, ask "Another round, or is this the one?" The user can always keep going.
- If two rounds pull in opposite directions ("faster" then "slower"), show both versions side by side (paths or stills) and let the user pick.
- Done = the user says it's final. Then go to *Deliver* in SKILL.md.
