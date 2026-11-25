# promo-pilot

**Professional short promo videos from a link, a project, or a few sentences, with voiceover in your language, synced captions, and revisions until you're happy.** A skill for Claude Code, built on the `brag` video skills, HyperFrames and media-use.

```
/promo-pilot https://myapp.com 20s reel, Hindi voiceover
```

## What you can make with it

| You have | You say | You get |
|---|---|---|
| A website | `/promo-pilot https://mysite.com` | It reads the site (the best 2–5 pages, the real logo, the brand's story) and makes a promo from its real photos, copy, fonts and colours |
| A code project | `/promo-pilot` inside the project folder | A launch video showing the actual app |
| Just an idea or business | `/promo-pilot` + a few sentences about it | A video built from your words, with no invented facts |
| A new feature | "video for our new dark mode" | A video focused on that one thing |

**Add any of these:** `voiceover in Spanish` · `captions` · `vertical` / `landscape` / `square` · `30s` · `cinematic` / `playful` / `polished` · a logo or screenshots.

## Modes: how much it checks in with you

| Mode | Say | It stops for you | Best for |
|---|---|---|---|
| **Guided** (default) | anything | once at the storyboard, then for your review | most videos |
| **Quick** | `quick` | only to review the finished video | when you trust the defaults |
| **Auto** | `auto` | never: delivers the final video | batches, scripts, overnight runs |

It never guesses two things in any mode: **what the video is about**, and **the voiceover language**.

## Quality levels: picked from your model, change any time

| Level | Default for | What you get |
|---|---|---|
| **min** | Haiku | Fast: ~15s, 3–4 scenes, clean and correct |
| **mid** | Sonnet | Balanced: ~20s, beat-synced cuts, registry transitions, voice checked against the script |
| **max** | Opus / Fable | Best: full brag workflow, richer visuals, loudness check, extra review rounds |

Say "max" or "min" at any point to switch. Every level meets the same [quality bar](skills/promo-pilot/references/quality-bar.md): real material on screen (never drawn clip-art), the brand's own fonts, colours and lines, motion with a cause, phone-first vertical layout, a pro audio mix (−14 LUFS) and a real poster as the thumbnail.

## How a run goes

1. **Setup check** (a few seconds). If anything is missing, you get **one** question with the total size, and that's the only time.
2. **One short question at most,** usually none. Everything else gets a sensible default.
3. **Source kit:** it gathers **real material**: the website's own photos, logo, fonts and copy (captured automatically), your photos, or stock photos for a description. Nothing is drawn as clip-art.
4. **Storyboard** (guided mode): one message with the scenes, the real asset each one shows, the voice lines and a settings line. Reply "build it", or change anything.
5. **Build and director's review.** brag builds the film; then a harsh HyperFrames-style review (and a fresh-eyes reviewer on mid and max) fixes every problem before you see anything.
6. **v1:** checked for length, frames, loudness, the voice matching the script, and captions matching the voice.
7. **"Happy, or what should change?"** It makes v2, v3, … until you say it's final.
8. **Delivery:** `final.mp4` (poster as the thumbnail), `final.jpg`, `captions.srt`, `share-copy.txt` (with any required credits) and `studio-notes.md`.

## Install (2 steps)

**1. Add promo-pilot to Claude Code**, either way:
```
/plugin marketplace add Prajwallalpotu/promo-pilot
/plugin install promo-pilot@promo-pilot
```
```bash
npx skills add https://github.com/Prajwallalpotu/promo-pilot -s promo-pilot -g -a claude-code -y
```

**2. Run the setup once** in Claude Code:
```
/promo-pilot setup
```
It checks your computer and asks **one** question that lists everything missing, with the total size. Say yes, and it installs all of it in one go:
- the **brag** skills ([latent-spaces/brag](https://github.com/latent-spaces/brag)), which design the video
- the **HyperFrames** skills ([heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)): hyperframes, hyperframes-cli, hyperframes-registry and media-use, which render the video and handle music, voice and captions
- the render browser HyperFrames uses
- **Node.js** and **ffmpeg** if missing (automatically on a Mac with Homebrew; elsewhere it gives you the command)
- for voiceovers: a free local voice and speech-to-text, about 1 GB. Or sign in to HeyGen instead.

You can also skip step 2: your first `/promo-pilot` video asks the same single question before it starts. After that, no video ever stops for a missing piece.

> **Use a local Claude Code session**: the desktop app with a folder on your computer, `claude` in a terminal, or an IDE. Cloud sessions (claude.ai/code in a browser) run on a remote machine. They can't see skills installed on your computer, and they often block websites, so promo-pilot can't read the site there.

You need [Claude Code](https://claude.com/claude-code) and Python 3, which macOS already includes. Check your setup at any time:
```bash
python3 ~/.claude/skills/promo-pilot/scripts/doctor.py --voice
```

## Feedback

Say "feedback for promo-pilot: …". It's saved to `~/.promo-pilot/feedback.jsonl`, and you get a pre-filled GitHub issue link. **Nothing is sent unless you open the link and click Submit.**

## Good to know

- **Your content, your rights.** Only make promos of sites and brands you own or have permission to use. It asks.
- **Credits.** brag's bundled music is CC BY 4.0, and the credit is added to `share-copy.txt`. Keep it when you post.
- **Voices.** It clones only your own voice, and only if you ask. It never imitates real people.
- **No made-up claims.** Numbers, reviews and logos come only from you or your source.

More: [How it works](docs/HOW-IT-WORKS.md) · [Testing](docs/TESTING.md) · [Publishing](docs/PUBLISHING.md) · [Changelog](CHANGELOG.md)

## License

MIT, see [LICENSE](LICENSE). brag, HyperFrames and media-use are separate projects with their own licenses.
