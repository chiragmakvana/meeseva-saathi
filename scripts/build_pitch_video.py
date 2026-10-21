"""Assemble the team pitch video: one still per segment (rendered slide PNG) held for its narration clip.

Usage: python -m scripts.build_pitch_video <segments.json> <audioDir> <slidesDir> <out.mp4>
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HOLD_AFTER = 0.6  # seconds of silence after each clip before the next slide


def main(segments_path: str, audio_dir: str, slides_dir: str, out: str) -> None:
    segs = json.loads(Path(segments_path).read_text(encoding="utf-8"))
    durations = json.loads((Path(audio_dir) / "durations.json").read_text(encoding="utf-8"))
    tmp = Path(tempfile.mkdtemp(prefix="pitch_"))
    parts = []
    for s in segs:
        clip, png, part = Path(audio_dir) / f"{s['id']}.mp3", Path(slides_dir) / f"{s['slide']}.png", tmp / f"{s['id']}.mp4"
        t = durations[s["id"]] + HOLD_AFTER
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "30", "-i", str(png), "-i", str(clip),
                        "-t", f"{t:.2f}", "-af", "apad", "-c:v", "libx264", "-tune", "stillimage", "-crf", "18", "-pix_fmt", "yuv420p",
                        "-vf", "scale=1920:1080", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", str(part)], check=True)
        parts.append(part)
        print(f"{s['id']} {s['slide']:<14} {t:5.1f}s")
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", "-movflags", "+faststart", out], check=True)
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out], capture_output=True, text=True).stdout.strip()
    print(f"{out}: {float(dur) / 60:.1f} min")


if __name__ == "__main__":
    main(*sys.argv[1:])
