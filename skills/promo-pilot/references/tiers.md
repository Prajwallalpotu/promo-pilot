# Quality tiers: min, mid, max

A tier sets how much craft and checking goes into a video. It never changes the honesty rules, the quality bar's hard stops, or the user's own choices. Every tier uses real material from the source kit.

## Picking the tier

| Model | Default tier |
|---|---|
| Claude Haiku (any version) | **min** |
| Claude Sonnet (any version) | **mid** |
| Claude Opus or Claude Fable (any version) | **max** |
| Can't tell | **mid** (and say so) |

Show the tier in the storyboard's settings line. The user can switch at any time ("go max", "min is fine"). Apply the switch from the next step without redoing finished work, and record it in `studio.json` → `tier_history`. If a request is heavy for min (voice plus captions in a non-English language, longer than 30s, more than 6 scenes), say "This is a lot for min. Using mid instead (say 'min' to keep it)." Make it a statement, not a question.

## What each tier does

| | **min** | **mid** | **max** |
|---|---|---|---|
| Engine | brag-slim | brag-slim | `brag --full` if installed, otherwise brag-slim |
| Default length | ~15s | ~20s | ~20–25s |
| Scenes | 3–4 | 4–6 | 4–8 |
| Site pages mapped + captured (URL) | 2 (home + best page) | 3 | 5 |
| Source kit | capture or the user's files; the best 4–6 assets | + per-beat stock photos when signed in, cutouts for the hero product | + site videos, several cutouts, a second capture pass at 2x for push-ins |
| Visual craft | brand type and colour, clean cuts | + registry transitions and titles, beat-synced cuts, 3–5 transitions with a cause | + layered cutouts and parallax built from real photos, audio-reactive accents on brand elements |
| Director's review (review.md) | check + `snapshot --review`, fix P0s | + fix P1s, fresh-eyes sub-agent | + a second fresh-eyes pass after fixes, motion ranges around the hero move and the payoff |
| Voice check | durations fit | transcript of the final mix vs the script | + loudness and true peak (`--loudness`) |
| Review rounds before asking "another round?" | 1 | 2 | 3 |

The quality bar's hard stops apply on every tier. The tier only changes how much is built and reviewed on top of them.
