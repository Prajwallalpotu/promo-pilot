# Feedback on promo-pilot itself

This is for feedback on **the skill** ("the voiceover timing was off", "I wish it asked fewer questions"), not on the user's video. Feedback on the video goes into the review loop.

## When

- At the end, offer it once, in one line.
- At any time, if the user says something like "feedback for the skill", "report a bug in promo-pilot", or "tell the makers…".
- Don't push it. If they skip it, never mention it again in that session.

## How

1. Ask what they'd like to say if they haven't already. Optionally ask for a rating from 1 to 5.
2. Show them exactly what will be saved, then run:
   ```bash
   python3 <skill-dir>/scripts/feedback.py --rating 4 --tier mid --model "<model name>" --message "<their words>"
   ```
   This appends the note to `~/.promo-pilot/feedback.jsonl` on their machine. It also prints a pre-filled GitHub "new issue" link for the promo-pilot repository (set in `<skill-dir>/feedback_config.json`).
3. Give them the link: "To send it to the authors, open this link and click Submit. Nothing is sent unless you do." Don't open or submit it for them.

## Privacy

- The note contains only what the user wrote, the rating, the tier, the model name, the skill version, and the date. Leave out their name, email, file paths, URLs of their private projects, and video content, unless they explicitly ask for something to be included.
- If the repository in `feedback_config.json` is still the placeholder, skip the link and say the note was saved locally.
