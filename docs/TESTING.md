# Testing promo-pilot

Test in three layers, from fastest to slowest.

## 1. Scripts (seconds, free)

```bash
python3 skills/promo-pilot/scripts/doctor.py --voice
```
Expected: a checklist of what's installed. If anything is missing, a list of what to install with the total size, and the one command that installs it.

**Site understanding** (about 10–20 seconds, needs internet):
```bash
python3 skills/promo-pilot/scripts/site_map.py https://linear.app -o /tmp/site --pages 5 --browser "$(node ~/.claude/skills/hyperframes/scripts/plugin-cli.mjs browser path)"
```
Expected: `/tmp/site/site-map.json` with 5 pages from the same site section, logo files in `/tmp/site/logo-candidates/`, and `/tmp/site/logo-check.png` showing the real logo on light and dark backgrounds.

**Test a brand-new computer** without touching your own setup: a pretend home folder with only promo-pilot in it.
```bash
mkdir -p /tmp/newuser/.claude/skills && cp -R skills/promo-pilot /tmp/newuser/.claude/skills/
```
```bash
HOME=/tmp/newuser python3 /tmp/newuser/.claude/skills/promo-pilot/scripts/doctor.py
```
```bash
HOME=/tmp/newuser python3 /tmp/newuser/.claude/skills/promo-pilot/scripts/setup.py --all
```
Expected: the check lists brag, the 4 HyperFrames skills and the render browser. Setup installs them all in one run and ends with `SETUP DONE`. (It downloads the ~410 MB browser into the pretend home; `rm -rf /tmp/newuser` afterwards.)

```bash
ffmpeg -y -f lavfi -i testsrc=size=1080x1920:rate=30 -f lavfi -i sine=frequency=440 -t 20 -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest /tmp/test.mp4
```
```bash
python3 skills/promo-pilot/scripts/check_video.py /tmp/test.mp4 --expect-duration 20 --fps 30 --format vertical --expect-audio --stills /tmp/stills
```
Expected: `ALL CHECKS PASSED`, plus 8 stills and a contact sheet. (A test tone is too loud for `--loudness`, so leave that flag off here.)

```bash
python3 skills/promo-pilot/scripts/feedback.py --message "test note" --rating 5 --tier mid
```
Expected: saved to `~/.promo-pilot/feedback.jsonl`.

## 2. Real videos (10–30 min each)

Open Claude Code in an empty folder and try these. Check each item listed:

| Try | Check |
|---|---|
| `/promo-pilot` + a 2-sentence business description | at most one short question · storyboard with a settings line · no invented facts · v1 has no empty frames or repeated text |
| Same + "Hindi voiceover" (voice tools not installed) | **one** install question at the start, with the total size · nothing asked mid-build · voice matches the scenes · Hindi captions with no □ boxes |
| `/promo-pilot setup` on a computer missing brag or HyperFrames | one question listing every missing piece · one install · `SETUP DONE` · the next video doesn't stop for anything |
| "voiceover please", no language | asks the language and doesn't use English by default |
| `quick:` + a description | no stops until v1 |
| `auto:` + a description | no stops at all · final files delivered |
| A URL that isn't yours | asks about permission once |
| "switch to max" mid-way | switches from the next step |
| Review: "scene 2 too slow" | only scene 2 changes · v1 kept |
| "this is final" | final.mp4, final.jpg, captions.srt, share-copy.txt, studio-notes.md |

Try at least one run on Haiku (min) and one on Sonnet or Opus.

## 3. Automatic tests (Claude Code v2.1.269+; real, billed model runs)

`skills/promo-pilot/evals/` has 6 cases:
- `few-questions-for-clear-request`: a clear request gets no or very few questions; defaults appear in the settings line
- `quick-mode-no-stops`: quick mode builds v1 before asking anything
- `voiceover-without-language`: asks for the language, never assumes English
- `url-permission-and-no-default-voice`: asks about website permission; voice stays off
- `text-input-hindi-voiceover`: a text source, provider chosen automatically, no invented facts
- `url-uses-real-site-assets`: your Coca-Cola prompt; must capture the site and build from its real images, logo, fonts and copy

```bash
cd skills/promo-pilot && claude plugin eval . --allow-tools Write,Edit,Bash
```
These check *behaviour*. Judge video quality with layer 2.
