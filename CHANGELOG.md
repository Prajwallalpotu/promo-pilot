# Changelog

## 3.0.1 (2026-11-26): understands the whole website, finds the real logo
- **New `site_map.py`:** before capturing, it reads the site politely (robots.txt respected, a pause between requests, an honest identity, nothing downloaded is ever run): the menu, footer and sitemap. It picks the best 2–5 pages for a promo (products, features, pricing, about, campaigns), staying inside the section the user linked (for example `/in/en/`).
- **Real logo, checked by eye:** it collects every logo candidate (header logo linked to home, structured-data logo, press or brand page downloads, app and manifest icons), downloads them and draws them on light and dark backgrounds in `logo-check.png`, so Claude picks the brand's own mark visually. It's never redrawn.
- **Brand brief:** `BRAND.md` (products, real taglines with their pages, voice, colours, fonts, logo) feeds brag's plan.
- Captures each chosen page (2 on min, 3 on mid, 5 on max).
- Tested on coca-cola.com/in/en, linear.app and apple.com/in: right pages, right logos. Fixed two parser bugs found in testing (customer logos mistaken for the brand's; broken inline SVGs).

## 3.0.0 (2026-11-26): real material, brag on a real project, a director's review
Found in a real test: a 25s Coca-Cola reel on Opus came out as CSS-drawn clip-art (bottles, cans, cards) with invented taglines, although audio and captions were good.
- **Source kit (new step):** promo-pilot now builds brag a real project from any input: `hyperframes capture` for a URL (real photos, logo SVG, fonts, colour tokens, copy, site videos), the user's files and HeyGen stock or generated images for a description, and cutouts to animate real objects. It has a gate: no planning until every beat has real material.
- **brag works on the kit as its project,** so its "show the real thing" craft finally has real things; HyperFrames' launch.md, vertical.md and motion.md are read for craft.
- **Director's review** from HyperFrames review.md replaces the self-score out of 10: snapshot sheets, P0/P1 notes, a fresh-eyes sub-agent on mid and max.
- **Quality bar rewritten** to follow HyperFrames: removed advice that HyperFrames lists as "defaults that look generated" (slow push-ins, breathing glows); added hard stops (drawn real-world objects, redrawn logos, invented brand taglines).
- Text-only input recommends the free HeyGen sign-in for real stock photos. Someone else's brand gets a visible "spec ad" label.
- New test case `url-uses-real-site-assets`, built from that prompt. `text-input.md` is merged into `source-kit.md`.

## 2.1.0 (2026-11-26): one-step setup installs everything
- `doctor.py` now checks **everything** promo-pilot needs: the brag skills (latent-spaces/brag), the 4 HyperFrames skills (heygen-com/hyperframes), node/ffmpeg, the render browser and (with `--voice`) the voice and caption tools. It builds one install plan with the total size.
- `setup.py --all [--voice]` installs the whole plan in one run: skills via `npx skills add … -g -a claude-code -y`, node/ffmpeg via Homebrew on macOS (otherwise the exact command for the user), the render browser up front, and the voice tools.
- SKILL.md asks one question for all of it at the start; skills installed mid-session are read from `~/.claude/skills/<name>/SKILL.md`.
- README: a 2-step install (add promo-pilot, run `/promo-pilot setup`).
- Tested on a pretend brand-new home: all 6 skills installed in one run.

## 2.0.0 (2026-11-26): renamed to promo-pilot
- **New name:** brag-studio is now promo-pilot (`/promo-pilot`, `~/.promo-pilot/`, output in `promo-output/`).
- **Fewer questions:** smart defaults are shown in the storyboard's settings line; only the topic, the voice language and website permission are ever asked (one message, at most 3).
- **Setup up front:** the new `doctor.py` checks everything in about 3 seconds without downloading; if a voice needs tools, there's one question with the total size, then a one-step `setup.py` install. No more mid-build install prompts, and the voice provider is chosen automatically.
- **Modes:** guided (default), quick (no stops until v1), auto (hands-off).
- **Quality bar:** a new professional standard and a 10-point self-review that Claude runs before any user sees a frame; `check_video.py --loudness` checks -14 LUFS and the true peak.
- 2 new test cases (few questions, quick mode); the provider test updated.

## 1.0.2 (2026-11-26)
Fixes from the first full test run (a Hindi voiceover reel, delivered):
- Preflight runs HyperFrames through the hyperframes skill's own launcher (plugin-cli.mjs); a pinned npx version is now only the fallback.
- The provider check also tests speech-to-text (Whisper) when captions or the voice check need it, and asks for every needed install in one question with the total size.
- Captions and on-screen text no longer repeat the same line; on-screen text adds to the caption.
- Every voice line and sound effect gets its real length (data-duration), so HyperFrames doesn't count them as running to the end.

## 1.0.1 (2026-11-26)
Fixes from the first real test run:
- Preflight pins a working HyperFrames CLI version when the newest npm release can't be downloaded (ETARGET), and uses it for every command in the run.
- Voice providers are tested before they're offered; each option says what it needs (sign-in, or a one-time Kokoro install of ~300 MB). Kokoro can be installed into a separate venv.
- Documented Kokoro voices that the CLI's short list hides (Hindi hf_alpha/hf_beta/hm_omega/hm_psi, Italian, Brazilian Portuguese) and their -l flags.

## 1.0.0 (2026-11-26)
- First release: URL, project and text input; voiceover in the user's language; synced captions + .srt; min/mid/max tiers chosen from the model; storyboard and preview checkpoints; verify-before-review; review loop with kept versions; local feedback with optional GitHub issue link.
