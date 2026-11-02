#!/usr/bin/env python3
"""Owner-only GitHub Issue to MoneyPrinterTurbo CLI runner."""
from __future__ import annotations
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "storage" / "chatgpt-bridge"


def issue_payload():
    event_file = os.environ.get("GITHUB_EVENT_PATH")
    if not event_file:
        raise ValueError("GITHUB_EVENT_PATH is missing")
    issue = json.loads(Path(event_file).read_text(encoding="utf-8"))["issue"]
    try:
        payload = json.loads((issue.get("body") or "").strip())
    except json.JSONDecodeError as exc:
        raise ValueError("Issue body must contain a plain JSON object") from exc
    if not isinstance(payload, dict):
        raise ValueError("Issue body must be a JSON object")
    title, script = payload.get("title"), payload.get("script")
    if not isinstance(title, str) or not 1 <= len(title.strip()) <= 120:
        raise ValueError("title must contain 1-120 characters")
    if not isinstance(script, str) or not 1 <= len(script.strip()) <= 2500:
        raise ValueError("script must contain 1-2500 characters")
    source = payload.get("source", "slides")
    aspect = payload.get("aspect", "9:16")
    lang = payload.get("language", "ar-SA")
    scenes = payload.get("scenes", [])
    terms = payload.get("terms", [])
    if source not in ("slides", "pexels"):
        raise ValueError("source must be slides or pexels (paid generation disabled)")
    if aspect not in ("9:16", "16:9", "1:1") or lang not in ("ar-SA", "en-US"):
        raise ValueError("invalid aspect or language")
    if not isinstance(scenes, list) or len(scenes) > 6 or any(
        not isinstance(s, str) or not 1 <= len(s.strip()) <= 100 for s in scenes
    ):
        raise ValueError("scenes must be a list of up to six short headings")
    if not isinstance(terms, list) or len(terms) > 8 or any(
        not isinstance(t, str) or not re.fullmatch(r"[A-Za-z0-9 -]{2,60}", t) for t in terms
    ):
        raise ValueError("terms must be up to eight English keyword phrases")
    if source == "pexels" and not terms:
        raise ValueError("pexels source requires English terms")
    return dict(title=title.strip(), script=script.strip(), source=source,
                aspect=aspect, language=lang, scenes=scenes, terms=terms)


def slide_images(data):
    from PIL import Image, ImageDraw, ImageFont
    folder = WORK / "media"
    folder.mkdir(parents=True, exist_ok=True)
    w, h = {"9:16": (720, 1280), "16:9": (1280, 720), "1:1": (900, 900)}[data["aspect"]]
    fonts = ["/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
             "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    font_file = next((p for p in fonts if Path(p).exists()), None)
    if not font_file:
        raise ValueError("Arabic font is not installed")
    main = ImageFont.truetype(font_file, 58 if w < 1000 else 72)
    small = ImageFont.truetype(font_file, 26)
    scenes = data["scenes"] or [data["title"], "الفكرة", "الخاتمة"]
    palette = [("#132F42", "#21A7AE"), ("#263B51", "#CC9575"),
               ("#1D3D40", "#6EAE86"), ("#303958", "#A79CE4")]
    direction = "rtl" if data["language"] == "ar-SA" else "ltr"
    paths = []
    for i, heading in enumerate(scenes):
        bg, accent = palette[i % len(palette)]
        im = Image.new("RGB", (w, h), bg)
        dr = ImageDraw.Draw(im)
        dr.rounded_rectangle((40, 50, w - 40, h - 50), radius=32,
                             outline=accent, width=5)
        dr.rounded_rectangle((70, int(h * .27), w - 70, int(h * .28)),
                             radius=4, fill=accent)
        lines, line = [], ""
        for word in heading.split():
            candidate = (line + " " + word).strip()
            bounds = dr.textbbox((0, 0), candidate, font=main, direction=direction)
            if line and bounds[2] - bounds[0] > w - 140:
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        lines = lines[:5]
        y = h // 2 - 53 * len(lines)
        for content in lines:
            dr.text((w // 2, y), content, font=main, fill="white",
                    anchor="mt", direction=direction)
            y += 106
        dr.text((w // 2, h - 110), f"{i + 1} / {len(scenes)}",
                font=small, fill="#B8DFE2", anchor="mm")
        path = folder / f"scene-{i + 1}.png"
        im.save(path)
        paths.append(str(path))
    return paths


def write_config(data):
    conf = (ROOT / "config.example.toml").read_text(encoding="utf-8")
    if data["source"] == "pexels":
        key = os.environ.get("PEXELS_API_KEY", "").strip()
        if not key:
            raise ValueError("Add a PEXELS_API_KEY repository Actions secret first")
        marker = "pexels_api_keys = []"
        if conf.count(marker) != 1:
            raise ValueError("Unexpected configuration template")
        conf = conf.replace(marker, "pexels_api_keys = [" + json.dumps(key) + "]", 1)
    target = ROOT / "config.toml"
    target.write_text(conf, encoding="utf-8")
    target.chmod(0o600)


def main():
    data = issue_payload()
    write_config(data)
    args = [sys.executable, "cli.py", "--video-subject", data["title"],
            "--video-script", data["script"], "--video-aspect", data["aspect"],
            "--video-language", data["language"], "--video-count", "1",
            "--voice-name", ("ar-SA-HamedNeural-Male" if data["language"] == "ar-SA"
                             else "en-US-GuyNeural-Male"),
            "--bgm-type", "none", "--no-subtitle-enabled"]
    if data["source"] == "slides":
        paths = slide_images(data)
        args.extend(["--video-source", "local", "--video-materials", ",".join(paths),
                     "--video-concat-mode", "sequential", "--image-motion", "zoom"])
    else:
        args.extend(["--video-source", "pexels", "--video-terms", ",".join(data["terms"])])
    print("Rendering video:", data["title"], flush=True)
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                            errors="replace", timeout=2400)
    if result.returncode:
        print(result.stderr[-3500:], file=sys.stderr)
        raise RuntimeError(f"MoneyPrinterTurbo CLI failed ({result.returncode})")
    videos = list((ROOT / "storage" / "tasks").rglob("final-*.mp4"))
    if not videos:
        raise RuntimeError("CLI returned success but no final-*.mp4 was found")
    latest = max(videos, key=lambda item: item.stat().st_mtime)
    out = WORK / "output"
    out.mkdir(parents=True, exist_ok=True)
    destination = out / "video.mp4"
    shutil.copyfile(latest, destination)
    if not destination.stat().st_size:
        raise RuntimeError("Output video is empty")
    print("VIDEO_OUTPUT=" + str(destination.relative_to(ROOT)), flush=True)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, subprocess.TimeoutExpired) as err:
        print("Video bridge error:", err, file=sys.stderr)
        sys.exit(1)
