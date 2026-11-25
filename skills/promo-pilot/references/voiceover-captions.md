# Voiceover and captions

promo-pilot plans the voice and captions itself, and uses the `media-use` skill (TTS, transcription) and the `hyperframes` skill (`references/captions.md`) to make them. Load those skills' instructions when you reach this step, and follow their exact commands and flags. Commands change between versions, so the ones shown here are only examples.

## 1. Write the narration script

Write it per scene, in the storyboard, before any audio exists.

- **Fit the time.** Budget about **2.3 words per second** of scene time for English. Use roughly 2.0 for Spanish, Hindi or Portuguese, which have longer words. For Japanese and Chinese, count characters instead (about 6–7 per second). Leave roughly 0.3s of air at scene cuts. If a line doesn't fit, cut the line, don't speed up the voice.
- **Complement the picture, don't read it.** If the screen says "Export in one click", the voice says why that matters. (brag's narration guidance says the same.)
- **Hook in the first line.** The first 2 seconds of voice matter as much as the first 2 seconds of picture.
- **Write in the target language from the start,** not as an English draft translated afterwards. Keep product names, the call to action and the URL as the user wrote them.
- Numbers and names: write them the way they should be **spoken** in the script ("twenty-four seven"), and the way they should be **shown** in the captions ("24/7"). Keep both versions.

The user sees and approves the script in the storyboard (guided mode).

## 2. Generate the voice

Setup is already done by now (SKILL.md step 0 and setup.md): the provider is chosen, and anything that needed installing was installed at the start. Never stop here to ask about tools or installs.

1. **Use the provider from setup:** `default_voice_provider` in the doctor report. Follow media-use's TTS instructions for its exact commands. For local Kokoro, run every TTS command with `HYPERFRAMES_PYTHON=~/.promo-pilot/kokoro-venv/bin/python`.
2. **Pick a voice** that matches the language and the requested style. For Kokoro, the first letter of the voice ID sets the language (see media-use `tts.md` → Multilingual).
3. Generate **per scene** (one file per line). This makes timing and later fixes easy: changing scene 3's line regenerates one file, not the whole track.
4. **Get word timings.** HeyGen returns them directly. For other providers, transcribe with media-use / `hyperframes transcribe`, **using a model that matches the language.** The default English model *translates* other languages into English, which would ruin the captions.

## 3. Fit the picture to the voice

- Set each scene to at least: voice length + about 0.4s of air. If the total goes more than 2s over the agreed duration, trim narration first, then scenes, and tell the user what you cut.
- Put the cuts and the key visual moments on words. For example, the product name appears as it's spoken.
- **Give every voice line and sound effect its real length.** In the composition, set each `<audio>` clip's `data-duration` to its file's length (measure with `ffprobe`). Without it, HyperFrames treats the clip as running to the end of the video, and `check` reports every voice line as overlapping the others. Music is the exception: it spans the video on purpose.
- **Mix.** The voice is on top. Duck the music under the speech (about −8 to −12 dB while the voice plays), and keep sound effects under the voice. Follow media-use's mixing guide.

## 4. Captions

Follow hyperframes `references/captions.md` for structure, grouping, fitting, and placement. promo-pilot adds:

- **Source of truth.** Caption text comes from the **script** (the display version), and timing comes from the **word timings**. Match words by position, never by text. If the transcription disagrees with the script (a name heard wrong), keep the script's wording.
- **Don't say it twice on screen.** When captions are on, the scene's own text should **add to** the caption, not repeat it: a price tag, a place name, a short label, the brand. If a storyboard line puts the narration's sentence on screen as big text, keep only one of the two. Usually that's the caption, with the big text reduced to a key word or a visual. Repeating the line looks cluttered and splits the viewer's attention. If you change an approved storyboard this way, mention it in one line when you present the video.
- **Group size.** 2–3 words for chaotic or energetic tones, 3–5 for most, 4–6 for polished or deadpan.
- **Safe areas.** For vertical video, keep captions inside the zone the platforms leave free (hyperframes captions.md gives the numbers). Captions must never cover the product's key visual or brag's on-screen text. If they would, move the caption or the text, and check the still.
- **Captions without a voice** (on-screen subtitles): time them from the storyboard, with each line on screen for its reading time (about 0.3s per word, minimum 1.2s).
- **Scripts.** Use a font that has the glyphs: Devanagari for Hindi, CJK fonts for Japanese and Chinese, Arabic with right-to-left layout. Check a still of every caption group for missing-glyph boxes (□).
- **Sidecar.** Also write `captions.srt` from the same groups.

## 5. Languages

Before you promise a language, check the provider. Kokoro covers about nine: English (US/UK), Spanish, French, Hindi, Italian, Brazilian Portuguese, Japanese and Mandarin Chinese (see media-use `tts.md` for the current list). HeyGen and ElevenLabs cover many more. If the requested language needs a provider the user hasn't set up, tell them the options. Never fall back to another language silently.

**`hyperframes tts --list` shows only 12 of Kokoro's 54 voices.** A missing language isn't necessarily unsupported. The CLI accepts any Kokoro voice ID: the first letter is the language, the second is f (female) or m (male). Always pass the language with `-l` for voices that aren't in the short list:

| Language | Voice IDs | Flag |
|---|---|---|
| Hindi | `hf_alpha`, `hf_beta` (female), `hm_omega`, `hm_psi` (male) | `-l hi` |
| Italian | `if_sara` (female), `im_nicola` (male) | `-l it` |
| Brazilian Portuguese | `pf_dora` (female), `pm_alex`, `pm_santa` (male) | `-l pt-br` |

The full list is on the kokoro-onnx project page linked in the `--list` output. If an ID is rejected, use another voice of the same language and say so in one line.
