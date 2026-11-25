# studio.json

Keep a small state file in the output folder and update it after every step. It lets a later session (or the same one after the context was summarized) pick up exactly where things stand, and it records what changed between versions.

```json
{
  "skill": "promo-pilot",
  "skill_version": "3.0.1",
  "created": "2026-11-26T10:00:00Z",
  "mode": "guided | quick | auto",
  "source": { "type": "url | project | text | mixed", "value": "https://... or path or work/source-text.md" },
  "permission_confirmed": true,
  "goal": "launch",
  "audience": "indie developers",
  "format": "vertical",
  "duration_s": 20,
  "tone": "polished",
  "voice": { "enabled": true, "language": "hi", "provider": "heygen | kokoro | elevenlabs | gemini", "voice_id": "...", "style": "calm female" },
  "captions": { "enabled": true, "mode": "voice | subtitles", "language": "hi", "style": "..." },
  "tier": "mid",
  "tier_history": [{ "tier": "mid", "reason": "default for Sonnet", "at": "..." }],
  "engine": "brag-slim",
  "hyperframes_cli": "the <hf> command from doctor.py",
  "setup": { "installed": ["kokoro", "whisper"], "declined": [] },
  "step": "setup | understand | gather | plan | storyboard | voice | build | self-review | render | verify | review | delivered",
  "versions": [
    { "n": 1, "file": "v1.mp4", "requested": null, "changed": "first cut", "checks": { "file": "pass", "loudness": "-14.1 LUFS, -1.6 dBTP", "picture": "pass", "voice": "pass", "captions": "pass", "director_review": "0 P0 open, 2 P1 fixed" } }
  ],
  "final": null
}
```

Keep the user's own words for anything they specified (tone, language, requests), not a paraphrase. Never store secrets in this file: no API keys, tokens or credentials.
