#!/usr/bin/env python3
"""promo-pilot setup check. Looks, never installs or downloads anything.

Finds everything promo-pilot needs (skills, tools, the render browser, and the
voice / caption tools) and builds ONE install plan with sizes, so the user is
asked once, at the start, and setup.py can install it all in one go.

  python3 doctor.py                 # readable report
  python3 doctor.py --json          # for Claude to read
  python3 doctor.py --voice --json  # also plan the voice + caption tools
Exit code: 0 = ready to make videos, 1 = something is missing (see the plan).
"""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
VENV_PY = HOME / ".promo-pilot" / "kokoro-venv" / "bin" / "python"
HF_CACHE = HOME / ".cache" / "hyperframes"
KOKORO_MODEL = HF_CACHE / "tts" / "models" / "kokoro-v1.0.onnx"
KOKORO_VOICES = HF_CACHE / "tts" / "voices" / "voices-v1.0.bin"
WHISPER_MODELS = HF_CACHE / "whisper" / "models"

# Skills promo-pilot builds on, where they're published, and how big they are.
SKILL_SOURCES = [
    {"id": "brag", "repo": "https://github.com/latent-spaces/brag",
     "skills": ["brag", "brag-slim"], "size_mb": 16, "why": "designs the video"},
    {"id": "hyperframes", "repo": "https://github.com/heygen-com/hyperframes",
     "skills": ["hyperframes", "hyperframes-cli", "hyperframes-registry", "media-use"], "size_mb": 4,
     "why": "builds and renders the video, music, voice and captions"},
]
REQUIRED_SKILLS = ["hyperframes", "media-use"]   # plus brag OR brag-slim
SIZES_MB = {"chrome": 410, "kokoro": 490, "whisper": 470, "node": 80, "ffmpeg": 120}


def find_skill(name):
    for root in (Path.cwd() / ".claude" / "skills", HOME / ".claude" / "skills"):
        p = root / name / "SKILL.md"
        if p.is_file():
            return str(p.parent.resolve())
    plugins = HOME / ".claude" / "plugins"
    if plugins.is_dir():
        for p in plugins.glob(f"**/skills/{name}/SKILL.md"):
            return str(p.parent.resolve())
    return None


def run(cmd, timeout=60, env=None):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, str(e)


def tool_install_cmd(tool):
    """How to install a system tool on this OS, or None if it needs the user."""
    pkg = {"node": "node", "ffmpeg": "ffmpeg", "ffprobe": "ffmpeg"}.get(tool)
    if not pkg:
        return None
    if platform.system() == "Darwin" and shutil.which("brew"):
        return ["brew", "install", pkg]
    return None  # Linux/Windows or no Homebrew: the user installs it (needs admin rights)


def manual_tool_hint(tool):
    pkg = {"node": "Node.js (https://nodejs.org)", "ffmpeg": "ffmpeg", "ffprobe": "ffmpeg"}.get(tool, tool)
    if platform.system() == "Darwin":
        return f"Install Homebrew (https://brew.sh), then: brew install {'node' if tool == 'node' else 'ffmpeg'}"
    if platform.system() == "Linux":
        return f"sudo apt install {'nodejs npm' if tool == 'node' else 'ffmpeg'}  (or your distro's package manager)"
    return f"Install {pkg} and make sure it is on PATH"


def check(want_voice=False, network=True):
    rep = {"os": platform.system(), "skills": {}, "tools": {}, "hyperframes_cli": None,
           "browser": None, "voice": {}, "captions": {}}

    for src in SKILL_SOURCES:
        for name in src["skills"]:
            rep["skills"][name] = find_skill(name)
    for t in ("node", "npx", "ffmpeg", "ffprobe", "python3", "brew"):
        rep["tools"][t] = shutil.which(t)

    # HyperFrames: the skill's own launcher first, npx as fallback
    hf_cmd = None
    hf_dir = rep["skills"]["hyperframes"]
    launcher = Path(hf_dir) / "scripts" / "plugin-cli.mjs" if hf_dir else None
    if launcher and launcher.is_file() and rep["tools"]["node"]:
        code, out = run(["node", str(launcher), "--version"], timeout=180)
        if code == 0:
            hf_cmd = ["node", str(launcher)]
            rep["hyperframes_cli"] = {"command": f'node "{launcher}"', "version": out.strip().splitlines()[-1]}
    if hf_cmd is None and rep["tools"]["npx"] and hf_dir is None:
        rep["hyperframes_cli"] = {"command": None, "note": "comes with the hyperframes skill"}
    elif hf_cmd is None and rep["tools"]["npx"]:
        code, out = run(["npx", "-y", "hyperframes", "--version"], timeout=180)
        if code == 0:
            hf_cmd = ["npx", "-y", "hyperframes"]
            rep["hyperframes_cli"] = {"command": "npx -y hyperframes", "version": out.strip().splitlines()[-1]}
        else:
            rep["hyperframes_cli"] = {"command": None, "error": "npx hyperframes failed; see setup.md -> Pinning a version"}

    # Render browser (HyperFrames downloads headless Chrome on first render otherwise)
    if hf_cmd:
        code, out = run(hf_cmd + ["browser", "path"], timeout=60)
        rep["browser"] = out.strip().splitlines()[-1] if code == 0 and out.strip() else None

    # Voice options
    heygen = None
    if hf_cmd and network:
        code, out = run(hf_cmd + ["auth", "status"], timeout=60)
        heygen = code == 0 and "not signed in" not in out.lower()
    kokoro_pkg = False
    if VENV_PY.is_file():
        code, _ = run([str(VENV_PY), "-c", "import kokoro_onnx, soundfile"], timeout=60)
        kokoro_pkg = code == 0
    rep["voice"] = {
        "heygen_signed_in": heygen,
        "kokoro_package": kokoro_pkg,
        "kokoro_python": str(VENV_PY) if kokoro_pkg else None,
        "kokoro_model": KOKORO_MODEL.is_file() and KOKORO_VOICES.is_file(),
        "elevenlabs_key": bool(os.environ.get("ELEVENLABS_API_KEY")),
    }
    rep["voice"]["kokoro_ready"] = kokoro_pkg and rep["voice"]["kokoro_model"]
    whisper_bin = shutil.which("whisper-cli") or shutil.which("whisper-cpp")
    models = sorted(p.name for p in WHISPER_MODELS.glob("ggml-*.bin")) if WHISPER_MODELS.is_dir() else []
    rep["captions"] = {
        "whisper_runtime": whisper_bin,
        "whisper_models": models,
        "multilingual_ready": bool(whisper_bin and "ggml-small.bin" in models),
    }

    # ---- One install plan ----
    plan = {"tools": [], "skills": [], "browser": None, "voice": [], "manual": []}
    for t in ("node", "ffmpeg"):
        if not rep["tools"][t] or (t == "ffmpeg" and not rep["tools"]["ffprobe"]):
            cmd = tool_install_cmd(t)
            if cmd:
                plan["tools"].append({"item": t, "command": cmd, "size_mb": SIZES_MB[t]})
            else:
                plan["manual"].append({"item": t, "how": manual_tool_hint(t)})
    for src in SKILL_SOURCES:
        missing = [s for s in src["skills"] if not rep["skills"][s]]
        if missing:
            plan["skills"].append({"item": src["id"], "repo": src["repo"], "skills": missing,
                                   "size_mb": src["size_mb"], "why": src["why"]})
    if not rep["browser"]:
        plan["browser"] = {"item": "render browser (headless Chrome)", "size_mb": SIZES_MB["chrome"]}
    voice_ready = bool(heygen or rep["voice"]["kokoro_ready"] or rep["voice"]["elevenlabs_key"])
    if want_voice:
        if not voice_ready:
            plan["voice"].append({"item": "kokoro", "why": "local voice", "size_mb": SIZES_MB["kokoro"]})
        if not rep["captions"]["multilingual_ready"]:
            plan["voice"].append({"item": "whisper", "why": "speech-to-text for captions and the voice check",
                                  "size_mb": SIZES_MB["whisper"]})
    total = sum(x["size_mb"] for x in plan["tools"] + plan["skills"] + plan["voice"]) + \
        (plan["browser"]["size_mb"] if plan["browser"] else 0)

    engine_ok = bool(rep["skills"]["brag"] or rep["skills"]["brag-slim"])
    can_make = engine_ok and all(rep["skills"][s] for s in REQUIRED_SKILLS) and bool(hf_cmd) \
        and all(rep["tools"][t] for t in ("node", "ffmpeg", "ffprobe", "python3"))
    rep["install_plan"] = plan
    rep["summary"] = {
        "can_make_video": can_make,
        "render_browser_ready": bool(rep["browser"]),
        "voice_and_captions_ready": voice_ready and bool(heygen or rep["captions"]["multilingual_ready"]),
        "default_voice_provider": "heygen" if heygen else ("kokoro" if rep["voice"]["kokoro_ready"]
                                                            else ("elevenlabs" if rep["voice"]["elevenlabs_key"] else None)),
        "nothing_to_install": not (plan["tools"] or plan["skills"] or plan["browser"] or plan["voice"] or plan["manual"]),
        "needs_user_action": bool(plan["manual"]),
        "install_total_mb": total,
    }
    return rep


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--voice", action="store_true", help="also plan the voice and caption tools")
    ap.add_argument("--no-network", action="store_true", help="skip the HeyGen sign-in check")
    a = ap.parse_args()
    rep = check(want_voice=a.voice, network=not a.no_network)

    if a.json:
        print(json.dumps(rep, indent=2))
    else:
        s, plan = rep["summary"], rep["install_plan"]
        ok = lambda b: "OK " if b else "-- "
        print("promo-pilot setup check")
        print(f"  [{ok(rep['skills']['brag'] or rep['skills']['brag-slim'])}] brag (video design)")
        for n in ("hyperframes", "hyperframes-cli", "hyperframes-registry", "media-use"):
            print(f"  [{ok(rep['skills'][n])}] {n}")
        for t in ("node", "ffmpeg", "ffprobe", "python3"):
            print(f"  [{ok(rep['tools'][t])}] {t}")
        hv = rep["hyperframes_cli"] or {}
        print(f"  [{ok(hv.get('command'))}] HyperFrames CLI {hv.get('version', '')}")
        print(f"  [{ok(rep['browser'])}] render browser")
        print(f"  [{ok(rep['voice']['heygen_signed_in'])}] HeyGen voices (signed in)")
        print(f"  [{ok(rep['voice']['kokoro_ready'])}] local Kokoro voice")
        print(f"  [{ok(rep['captions']['multilingual_ready'])}] Whisper speech-to-text")
        print()
        if s["nothing_to_install"]:
            print("Everything needed is installed." + ("" if a.voice else " (Add --voice to also check voiceover tools.)"))
        else:
            print(f"To install (about {s['install_total_mb']} MB):")
            for x in plan["tools"]:
                print(f"  - {x['item']} ({' '.join(x['command'])})")
            for x in plan["skills"]:
                print(f"  - skills {', '.join(x['skills'])} from {x['repo']} ({x['why']})")
            if plan["browser"]:
                print(f"  - {plan['browser']['item']}")
            for x in plan["voice"]:
                print(f"  - {x['item']} ({x['why']})")
            for x in plan["manual"]:
                print(f"  ! {x['item']}: you need to install this yourself: {x['how']}")
            print("Install it all with:  python3 setup.py --all" + (" --voice" if a.voice else ""))
    return 0 if rep["summary"]["can_make_video"] else 1


if __name__ == "__main__":
    sys.exit(main())
