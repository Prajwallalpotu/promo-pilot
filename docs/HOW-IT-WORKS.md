# How promo-pilot works

## The idea

A skill is a set of instructions Claude follows, not a program. brag makes great videos from **real material**, but it needs a project. promo-pilot's core job is to **build brag a real project from anything**: it captures a website, gathers the user's photos, or finds stock photos for a description. Then it lets brag do its craft, adds voice and captions, and runs HyperFrames' professional director's review before anyone sees the film.

```
 you ─► 0 setup check (doctor.py) ─► one install question, only if a voice needs it
        1 understand: defaults + at most one short question
        2 source kit: map the site (site_map.py: best pages, real logo, brand facts) + capture those pages /
          the project / photos + stock → real images, logo, fonts, copy, BRAND.md (gate)
        3 brag plans on the kit → storyboard ✋ (guided mode only)
        4 voice first → build → director's review (hyperframes review.md: P0/P1, fresh eyes)
        5 render vN.mp4 → verify (check_video.py, transcript, loudness)
        6 "happy, or what should change?" ✋ ↺  (guided + quick)
        7 deliver final.mp4 + poster + captions.srt + share copy
                                    ✋ = waits for you
```

## Files

```
skills/promo-pilot/
├── SKILL.md                    the workflow (always loaded)
├── feedback_config.json        version + GitHub repo for feedback links
├── references/                 read only when a step needs them
│   ├── setup.md                setup check, the one install question, voice provider choice
│   ├── intake.md               defaults, and the only 3 questions it may ask
│   ├── tiers.md                min / mid / max
│   ├── source-kit.md           turning a URL, description or photos into a real project for brag
│   ├── quality-bar.md          the 5 rules + hard stops, pointing at HyperFrames' craft guides
│   ├── voiceover-captions.md   narration script, voice timing, mixing, captions, languages
│   ├── review-loop.md          verify checklist + the review loop
│   ├── state.md                studio.json (resume + version history)
│   └── feedback.md             feedback on the skill itself
├── scripts/
│   ├── doctor.py               setup check: looks, never installs
│   ├── setup.py                one-step install of everything missing
│   ├── site_map.py             reads a website politely: best pages, real logo (checked on light/dark), brand facts
│   ├── check_video.py          duration, frames, size, audio, loudness, stills
│   └── feedback.py             saves feedback locally, prints a GitHub issue link
└── evals/                      6 test cases (see TESTING.md)
```

## Design choices

- **Ask little, show everything.** Defaults go in the storyboard's settings line, where one reply changes any of them. Only the topic, the voice language and website permission are ever asked.
- **All setup up front.** `doctor.py` finds everything a run could need in about 3 seconds, without downloading. If a voice needs tools, there's one question with the total size, then one install (`setup.py`). Nothing is asked mid-build.
- **The voice drives the timing.** The narration is written per scene and generated first; scenes are then fitted to the real audio, so the speech matches the picture.
- **Real material, never drawings.** The source kit has a gate: every beat must have a real asset (photo, footage, UI, logo) or be deliberately typography-led. Real-world objects are never drawn with CSS.
- **A director's review before the user.** HyperFrames' review.md (snapshot sheets, P0/P1 notes, a fresh-eyes sub-agent on mid and max) runs before rendering; then the render is verified (frames, loudness, transcript). You only review videos that already pass.
- **Wrap, don't fork.** brag is called, not copied, so its improvements reach promo-pilot automatically. Where they disagree (duration, voice, delivery), SKILL.md says promo-pilot wins.
- **State on disk.** `studio.json` and every `vN.mp4` are kept, so a run can resume and any change can be undone.
