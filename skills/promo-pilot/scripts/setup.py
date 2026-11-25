#!/usr/bin/env python3
"""promo-pilot one-step setup. Run it only after the user said yes.

It asks doctor.py what's missing and installs all of it, in this order:
  1. tools      node / ffmpeg via Homebrew (macOS). Elsewhere it prints the command
                for the user, because those need admin rights.
  2. skills     brag + brag-slim (latent-spaces/brag) and hyperframes, hyperframes-cli,
                hyperframes-registry, media-use (heygen-com/hyperframes), installed for
                Claude Code in ~/.claude/skills with the `skills` CLI.
  3. browser    the headless Chrome HyperFrames renders with (~410 MB), so the first
                render doesn't stop to download it.
  4. voice      (with --voice) local Kokoro voice in its own venv, ~/.promo-pilot/kokoro-venv
                (system Python untouched), and Whisper speech-to-text for captions.

  python3 setup.py --all              # everything needed to make videos
  python3 setup.py --all --voice      # ... plus voiceover and captions
  python3 setup.py --kokoro --whisper # only the voice parts

Ends with SETUP DONE or SETUP INCOMPLETE and a fresh doctor report.
Remove later: rm -rf ~/.promo-pilot/kokoro-venv; skills live in ~/.claude/skills; models in ~/.cache/hyperframes.
"""
import argparse
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import doctor  # noqa: E402

VENV = Path.home() / ".promo-pilot" / "kokoro-venv"


def step(msg):
    print(f"\n==> {msg}", flush=True)


def run(cmd, env=None):
    print("    $ " + " ".join(shlex.quote(str(c)) for c in cmd), flush=True)
    try:
        return subprocess.run([str(c) for c in cmd], env=env).returncode
    except OSError as e:
        print(f"    failed: {e}")
        return 1


def hf_command(rep):
    c = (rep.get("hyperframes_cli") or {}).get("command")
    return shlex.split(c) if c else None


def install_kokoro(hf):
    step("Voice: Kokoro in its own Python environment (~490 MB)")
    if not (VENV / "bin" / "python").is_file() and run([sys.executable, "-m", "venv", str(VENV)]) != 0:
        return False
    if run([str(VENV / "bin" / "pip"), "install", "-q", "kokoro-onnx", "soundfile"]) != 0:
        return False
    env = dict(os.environ, HYPERFRAMES_PYTHON=str(VENV / "bin" / "python"))
    tmp = Path(tempfile.mkdtemp(prefix="promo-pilot-setup-"))
    return run(hf + ["tts", "hello", "-v", "af_heart", "-o", tmp / "probe.wav"], env=env) == 0


def install_whisper(hf, model):
    step(f"Captions: Whisper runtime + '{model}' speech model (~470 MB)")
    tmp = Path(tempfile.mkdtemp(prefix="promo-pilot-setup-"))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=300:duration=1", str(tmp / "tone.wav")])
    return run(hf + ["transcribe", tmp / "tone.wav", "-m", model, "--json", "-d", tmp]) == 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true", help="install everything doctor.py reports missing")
    ap.add_argument("--voice", action="store_true", help="with --all: include the voice and caption tools")
    ap.add_argument("--kokoro", action="store_true", help="install only the local Kokoro voice")
    ap.add_argument("--whisper", action="store_true", help="install only Whisper speech-to-text")
    ap.add_argument("--whisper-model", default="small", help="small (any language, default) or small.en")
    a = ap.parse_args()
    if not (a.all or a.kokoro or a.whisper):
        ap.error("nothing to do: pass --all [--voice], --kokoro or --whisper")

    failed, manual, installed_skills = [], [], False
    rep = doctor.check(want_voice=a.voice or a.kokoro or a.whisper, network=False)
    plan = rep["install_plan"]

    if a.all:
        # 1. tools
        for t in plan["tools"]:
            step(f"Tool: {t['item']}")
            if run(t["command"]) != 0:
                failed.append(t["item"])
        manual += plan["manual"]
        # 2. skills (the skills CLI needs node/npx, which step 1 may have just installed)
        for s in plan["skills"]:
            step(f"Skills: {', '.join(s['skills'])} ({s['why']})")
            cmd = ["npx", "-y", "skills", "add", s["repo"]]
            for name in s["skills"]:
                cmd += ["-s", name]
            cmd += ["-g", "-a", "claude-code", "-y"]
            if run(cmd) != 0:
                failed.append(f"skills from {s['repo']}")
            else:
                installed_skills = True
        rep = doctor.check(want_voice=a.voice, network=False)  # re-check: the HyperFrames CLI comes with its skill
        plan = rep["install_plan"]

    hf = hf_command(rep)
    if a.all and plan["browser"]:
        step("Render browser: headless Chrome for HyperFrames (~410 MB)")
        if not hf or run(hf + ["browser", "ensure"]) != 0:
            failed.append("render browser")

    want_kokoro = a.kokoro or (a.all and a.voice and any(v["item"] == "kokoro" for v in plan["voice"]))
    want_whisper = a.whisper or (a.all and a.voice and any(v["item"] == "whisper" for v in plan["voice"]))
    if (want_kokoro or want_whisper) and not hf:
        failed.append("voice tools (HyperFrames CLI not available)")
    else:
        if want_kokoro and not install_kokoro(hf):
            failed.append("kokoro voice")
        if want_whisper and not install_whisper(hf, a.whisper_model):
            failed.append("whisper")

    print()
    final = doctor.check(want_voice=a.voice or a.kokoro or a.whisper, network=False)
    for m in manual:
        print(f"ACTION NEEDED: install {m['item']} yourself: {m['how']}")
    if failed or not final["summary"]["can_make_video"]:
        print("SETUP INCOMPLETE." + (" Failed: " + ", ".join(failed) if failed else ""))
        print("Run `python3 doctor.py` to see what is still missing.")
        return 1
    print("SETUP DONE. promo-pilot can make videos" +
          (" with voiceover and captions." if final["summary"]["voice_and_captions_ready"] and (a.voice or a.kokoro) else "."))
    if final["voice"]["kokoro_ready"]:
        print(f"Local voice runs with HYPERFRAMES_PYTHON={VENV / 'bin' / 'python'}")
    if installed_skills:
        print("If this Claude Code session can't see newly installed skills, they load in the next session; "
              "promo-pilot can also read them from ~/.claude/skills/<name>/SKILL.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
