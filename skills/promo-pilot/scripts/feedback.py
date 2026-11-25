#!/usr/bin/env python3
"""Save feedback about the promo-pilot skill on this machine, and print a
pre-filled GitHub "new issue" link the user can open and submit themselves.

Nothing is sent over the network by this script.

  python3 feedback.py --message "Captions were too small" --rating 3 --tier mid --model "Sonnet 5.5"
  python3 feedback.py --list        # show saved feedback
"""
import argparse
import json
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
STORE = Path.home() / ".promo-pilot" / "feedback.jsonl"
PLACEHOLDER = "YOUR-GITHUB-USER/promo-pilot"


def load_config():
    try:
        return json.loads((SKILL_DIR / "feedback_config.json").read_text())
    except (OSError, ValueError):
        return {}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--message", help="the user's feedback, in their words")
    ap.add_argument("--rating", type=int, choices=range(1, 6), help="1 (bad) to 5 (great)")
    ap.add_argument("--tier", choices=["min", "mid", "max"])
    ap.add_argument("--model", help="model name, e.g. 'Sonnet 5.5'")
    ap.add_argument("--list", action="store_true", help="print saved feedback and exit")
    a = ap.parse_args()

    if a.list:
        if not STORE.exists():
            print("No feedback saved yet.")
            return 0
        print(STORE.read_text(), end="")
        return 0
    if not a.message or not a.message.strip():
        ap.error("--message is required")

    cfg = load_config()
    entry = {
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "skill_version": cfg.get("skill_version", "unknown"),
        "tier": a.tier,
        "model": a.model,
        "rating": a.rating,
        "message": a.message.strip(),
    }
    STORE.parent.mkdir(parents=True, exist_ok=True)
    with STORE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"Saved to {STORE}")

    repo = cfg.get("github_repo", PLACEHOLDER)
    if not repo or repo == PLACEHOLDER:
        print("No public repository configured, so there is no link to send it. The note is saved locally.")
        return 0
    stars = f"{a.rating}/5" if a.rating else "not given"
    title = f"[feedback] {entry['message'][:60]}"
    body = (
        f"**Feedback**\n\n{entry['message']}\n\n"
        f"| | |\n|---|---|\n| Rating | {stars} |\n| Tier | {a.tier or '-'} |\n"
        f"| Model | {a.model or '-'} |\n| Skill version | {entry['skill_version']} |\n"
    )
    query = urllib.parse.urlencode({"title": title, "body": body, "labels": "feedback"})
    print("Open this link and click Submit to send it to the authors (nothing is sent until you do):")
    print(f"https://github.com/{repo}/issues/new?{query}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
