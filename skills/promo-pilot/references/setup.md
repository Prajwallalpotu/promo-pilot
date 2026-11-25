# Setup

The rule: **all setup happens once, at the start, in one question and one command.** A user who is asked to install one thing, watches it fail, and is then asked for something else loses trust in the tool. The doctor report lists everything up front, so there's never a reason for a second ask.

## What the doctor checks

`python3 <skill-dir>/scripts/doctor.py --json [--voice]` only looks; it never installs or downloads anything. It reports:

| Section | Meaning |
|---|---|
| `skills` | Where each skill promo-pilot builds on is installed (or `null`): brag, brag-slim (from `latent-spaces/brag`), and hyperframes, hyperframes-cli, hyperframes-registry, media-use (from `heygen-com/hyperframes`) |
| `tools` | node, npx, ffmpeg, ffprobe, python3, brew |
| `hyperframes_cli.command` | How to run HyperFrames: the hyperframes skill's own launcher, or `npx` as a fallback. This is `<hf>`. |
| `browser` | The headless Chrome HyperFrames renders with. Without it, the first render would stop to download about 410 MB. |
| `voice` | HeyGen sign-in, local Kokoro (`~/.promo-pilot/kokoro-venv` plus its model), ElevenLabs key |
| `captions` | The Whisper runtime and models, for word-timed captions and the voice check |
| `install_plan` | Everything missing: `tools`, `skills`, `browser`, `voice` (only with `--voice`), and `manual` (things only the user can install) |
| `summary` | `can_make_video`, `nothing_to_install`, `install_total_mb`, `voice_and_captions_ready`, `default_voice_provider` |

## The one install question

Ask it only when `install_plan` isn't empty. Put **everything** in it, in plain words, with the total size from `install_total_mb`. If AskUserQuestion is available, use it; otherwise send one short message, for example:

> To make videos, promo-pilot needs a one-time setup on this computer (about 1.4 GB, free, and you only do it once):
> - the brag and HyperFrames skills, which design and render the video (~20 MB)
> - the render browser HyperFrames uses (~410 MB)
> - for your voiceover: a local voice (~490 MB) and speech-to-text for captions (~470 MB)
>
> **Install everything now** (recommended) · **Not now**

Leave out what isn't missing. For a voiceover, also offer **"Use HeyGen voices instead"** (`! <hf> auth login`) if the hyperframes skill is installed. That option replaces the local voice and speech-to-text, because HeyGen returns word timings itself.

On yes, run **one** command:

```bash
python3 <skill-dir>/scripts/setup.py --all [--voice]
```

It installs in this order:
1. Tools: node and ffmpeg via Homebrew on macOS.
2. The skills, with `npx skills add … -g -a claude-code -y` (for Claude Code, in `~/.claude/skills`).
3. The render browser.
4. With `--voice`: Kokoro in its own venv (system Python untouched) and Whisper.

It re-checks at the end and prints `SETUP DONE` or `SETUP INCOMPLETE` with what failed. It can take several minutes, so tell the user once ("Installing, about 3–8 minutes…") and don't interrupt it.

- **`manual` items** (for example ffmpeg or Node on Linux, or anything without Homebrew) need admin rights. Give the user the exact command from the plan, wait until they say it's done, then run doctor again.
- **`SETUP INCOMPLETE`:** tell the user plainly what failed and what to do (the output names it). If `can_make_video` is still false, stop there. If only the voice tools failed, offer the video without voice.
- **"Not now":** if `can_make_video` is false, stop politely and say they can run `/promo-pilot setup` any time. If only the voice tools were declined, make the video without voice.
- **Newly installed skills:** the Skill tool may not list them until the next session. Read them directly from `~/.claude/skills/<name>/SKILL.md` instead.
- **Kokoro:** run every TTS command with `HYPERFRAMES_PYTHON=~/.promo-pilot/kokoro-venv/bin/python`.

## The voice provider

It's chosen automatically from the report: HeyGen if signed in (best quality, many languages, word timings included), otherwise Kokoro, otherwise ElevenLabs. Say which one in the storyboard's settings line. Switch only if the user asks, or if the language needs a provider that can do it (voiceover-captions.md → *Languages*). In that case, say so in one line.

## Pinning a version (fallback only)

If HyperFrames can't run through the skill's launcher and `npx -y hyperframes` fails with `ETARGET` / "No matching version", a brand-new release is listed on npm but can't be downloaded yet. Pin a version that works:
1. The newest version in the npx cache: read `version` from each `~/.npm/_npx/*/node_modules/hyperframes/package.json`.
2. Otherwise the previous release from `npm view hyperframes versions --json`.

Check it with `npx -y hyperframes@<version> --version`, then use `npx -y hyperframes@<version>` as `<hf>`. Tell the user in one line.
