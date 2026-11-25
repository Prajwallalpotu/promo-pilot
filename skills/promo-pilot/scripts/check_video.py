#!/usr/bin/env python3
"""Check a rendered video before the user sees it.

Reports duration, fps, frame count, resolution and audio, and optionally writes
evenly spaced stills plus a contact sheet for visual review.

Exit code 0 = all checks passed, 1 = a check failed, 2 = tool/usage error.
Needs ffprobe and ffmpeg on PATH (standard library only otherwise).
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

FORMATS = {"landscape": (1920, 1080), "vertical": (1080, 1920), "square": (1080, 1080)}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    r = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)])
    if r.returncode != 0:
        raise RuntimeError(f"ffprobe could not read {path}: {r.stderr.strip()}")
    return json.loads(r.stdout)


def parse_rate(rate):
    num, _, den = rate.partition("/")
    return float(num) / float(den or 1) if float(den or 1) else 0.0


def count_frames(path):
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets",
             "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(path)])
    try:
        return int(r.stdout.strip().split(",")[0])
    except ValueError:
        return None


def loudness(path):
    """Integrated loudness (LUFS) and true peak (dBTP) via ffmpeg's ebur128."""
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"])
    lufs = peak = None
    summary = r.stderr[r.stderr.rfind("Summary:"):] if "Summary:" in r.stderr else ""
    for line in summary.splitlines():
        s = line.strip()
        if s.startswith("I:"):
            lufs = float(s.split()[1])
        elif s.startswith("Peak:"):
            peak = float(s.split()[1])
    return lufs, peak


def write_stills(path, duration, out_dir, count):
    out_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for i in range(count):
        t = duration * (i + 0.5) / count  # middle of each slice, avoids the black first/last frame
        f = out_dir / f"still-{i + 1:02d}-{t:05.2f}s.jpg"
        r = run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(path),
                 "-frames:v", "1", "-q:v", "3", str(f)])
        if r.returncode == 0:
            files.append(f)
    if files:
        cols = 4 if count > 6 else count
        rows = -(-count // cols)
        sheet = out_dir / "contact-sheet.jpg"
        step = duration / count
        run(["ffmpeg", "-y", "-v", "error", "-i", str(path), "-vf",
             f"fps=1/{step:.4f},scale=480:-2,tile={cols}x{rows}", "-frames:v", "1", str(sheet)])
        if sheet.exists():
            files.append(sheet)
    return files


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--expect-duration", type=float, help="expected seconds")
    ap.add_argument("--tolerance", type=float, default=1.0, help="allowed duration difference in seconds (default 1.0)")
    ap.add_argument("--fps", type=float, help="expected frames per second")
    ap.add_argument("--format", choices=FORMATS, help="expected frame size")
    ap.add_argument("--expect-audio", action="store_true", help="fail if there is no audio stream")
    ap.add_argument("--loudness", action="store_true", help="check integrated loudness (-16..-12 LUFS) and true peak (<= -1 dBTP)")
    ap.add_argument("--stills", help="folder to write stills and a contact sheet into")
    ap.add_argument("--count", type=int, default=8, help="number of stills (default 8)")
    ap.add_argument("--json", action="store_true", help="print the report as JSON")
    a = ap.parse_args()

    for tool in ("ffprobe", "ffmpeg"):
        if not shutil.which(tool):
            print(f"ERROR: {tool} not found on PATH. Ask the user before installing it.", file=sys.stderr)
            return 2
    path = Path(a.video)
    if not path.exists():
        print(f"ERROR: {path} does not exist", file=sys.stderr)
        return 2

    try:
        info = probe(path)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    v = next((s for s in info["streams"] if s.get("codec_type") == "video"), None)
    aud = [s for s in info["streams"] if s.get("codec_type") == "audio"]
    duration = float(info["format"].get("duration", 0))
    checks, report = [], {"file": str(path), "duration_s": round(duration, 3), "has_audio": bool(aud)}

    def check(name, ok, detail):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    if v is None:
        check("video stream", False, "no video stream")
    else:
        w, h = int(v["width"]), int(v["height"])
        fps = parse_rate(v.get("avg_frame_rate") or v.get("r_frame_rate", "0/1"))
        frames = count_frames(path)
        report.update(width=w, height=h, fps=round(fps, 3), frames=frames, codec=v.get("codec_name"))
        if a.format:
            ew, eh = FORMATS[a.format]
            check("resolution", (w, h) == (ew, eh), f"{w}x{h} (expected {ew}x{eh} for {a.format})")
        if a.fps:
            check("fps", abs(fps - a.fps) < 0.05, f"{fps:.3f} (expected {a.fps})")
            if frames is not None:
                expected = round(duration * a.fps)
                check("frame count", abs(frames - expected) <= 2,
                      f"{frames} frames (expected about {expected} = duration x fps; a gap means dropped frames)")
    if a.expect_duration is not None:
        check("duration", abs(duration - a.expect_duration) <= a.tolerance,
              f"{duration:.2f}s (expected {a.expect_duration}s +/- {a.tolerance}s)")
    if a.expect_audio:
        check("audio", bool(aud), "audio stream present" if aud else "no audio stream")

    if a.loudness and aud:
        lufs, peak = loudness(path)
        report.update(lufs=lufs, true_peak_dbtp=peak)
        check("loudness", lufs is not None and -16.0 <= lufs <= -12.0,
              f"{lufs} LUFS integrated (target about -14, range -16 to -12)")
        check("true peak", peak is not None and peak <= -1.0, f"{peak} dBTP (must be -1.0 or lower)")

    if a.stills and duration > 0:
        report["stills"] = [str(p) for p in write_stills(path, duration, Path(a.stills), a.count)]

    report["checks"] = checks
    ok = all(c["pass"] for c in checks)
    report["pass"] = ok
    if a.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"{path}  {duration:.2f}s  {report.get('width')}x{report.get('height')}  "
              f"{report.get('fps')}fps  {report.get('frames')} frames  audio={'yes' if aud else 'no'}")
        for c in checks:
            print(f"  [{'PASS' if c['pass'] else 'FAIL'}] {c['check']}: {c['detail']}")
        for s in report.get("stills", []):
            print(f"  still: {s}")
        print("ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
